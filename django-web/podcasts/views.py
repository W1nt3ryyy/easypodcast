import base64
import hashlib
import hmac
import json
import re
import time
from datetime import timedelta
from functools import wraps
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import (
    Bookmark,
    ListenProgress,
    PodcastFeed,
    PodcastFolder,
    PodcastFolderItem,
    Subscription,
)
from .services import PodcastFeedConnectionError, parse_podcast_rss

RSS_CACHE_TTL = timedelta(hours=6)
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7
DEFAULT_EPISODE_PAGE_SIZE = 80
MAX_EPISODE_PAGE_SIZE = 120
ITUNES_GENRES = {
    "all": ("", "top podcasts"),
    "business": ("1321", "business podcasts"),
    "comedy": ("1303", "comedy podcasts"),
    "education": ("1304", "education podcasts"),
    "health": ("1512", "health fitness podcasts"),
    "news": ("1311", "news podcasts"),
    "religion": ("1314", "religion spirituality podcasts"),
    "science": ("1533", "science podcasts"),
    "technology": ("1318", "technology podcasts"),
}


def _json_body(request):
    return json.loads(request.body or b"{}")


def _json_request(url: str, timeout: int = 12) -> dict:
    request = Request(url, headers={"User-Agent": "EasyPodcasts/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _jwt_sign(data: str) -> str:
    secret = (settings.SECRET_KEY or "dev-secret").encode("utf-8")
    return _b64encode(hmac.new(secret, data.encode("ascii"), hashlib.sha256).digest())


def _jwt_encode(payload: dict) -> str:
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("utf-8"))
    body = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _jwt_sign(f"{header}.{body}")
    return f"{header}.{body}.{signature}"


def _jwt_decode(token: str) -> dict | None:
    try:
        header, body, signature = token.split(".")
        expected = _jwt_sign(f"{header}.{body}")
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(_b64decode(body))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def _get_request_user(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    payload = _jwt_decode(header.removeprefix("Bearer ").strip())
    if not payload:
        return None
    User = get_user_model()
    try:
        return User.objects.get(id=payload.get("user_id"))
    except User.DoesNotExist:
        return None


def _require_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        request.jwt_user = _get_request_user(request)
        if not request.jwt_user:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def _user_payload(user):
    return {"id": user.id, "username": user.username, "email": user.email}


def _issue_token(user) -> str:
    now = int(time.time())
    return _jwt_encode({"user_id": user.id, "iat": now, "exp": now + TOKEN_TTL_SECONDS})


def _extract_category(feed_info: dict) -> str:
    categories = feed_info.get("tags") or feed_info.get("itunes_categories") or []
    if isinstance(categories, list) and categories:
        first = categories[0]
        if isinstance(first, dict):
            return first.get("term") or first.get("label") or first.get("text") or ""
        return str(first)
    category = feed_info.get("category") or feed_info.get("itunes_category") or ""
    if isinstance(category, dict):
        return category.get("text") or category.get("term") or ""
    return str(category)


def _image_from_feed(feed_info: dict) -> str:
    image = feed_info.get("image") or feed_info.get("itunes_image") or {}
    if isinstance(image, dict):
        return image.get("href") or image.get("url") or ""
    return ""


def _image_from_entry(entry: dict, fallback: str = "") -> str:
    for key in ("itunes_image", "image"):
        image = entry.get(key) or {}
        if isinstance(image, dict) and (image.get("href") or image.get("url")):
            return image.get("href") or image.get("url")
    return fallback


def _audio_from_entry(entry: dict) -> str:
    for link in entry.get("links") or []:
        if link.get("rel") == "enclosure" or str(link.get("type", "")).startswith("audio/"):
            return link.get("href") or ""
    return ""


def _duration_to_seconds(value) -> float:
    if not value:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text.isdigit():
        return float(text)
    parts = text.split(":")
    if all(part.isdigit() for part in parts):
        total = 0
        for part in parts:
            total = total * 60 + int(part)
        return float(total)
    return 0.0


def _compact_feed_payload(parsed: dict) -> dict:
    feed_info = parsed.get("feed", {}) or {}
    feed_image = _image_from_feed(feed_info)
    entries = []
    for entry in parsed.get("entries") or []:
        audio_url = _audio_from_entry(entry)
        image_url = _image_from_entry(entry, feed_image)
        entries.append(
            {
                "title": entry.get("title") or "Без названия",
                "published": entry.get("published") or entry.get("updated") or "",
                "summary": entry.get("summary") or entry.get("description") or "",
                "itunes_duration": entry.get("itunes_duration") or "",
                "duration_seconds": _duration_to_seconds(entry.get("itunes_duration")),
                "audio_url": audio_url,
                "image_url": image_url,
                "links": entry.get("links") or [],
                "itunes_image": {"href": image_url} if image_url else {},
                "image": {"href": image_url} if image_url else {},
            }
        )
    return {
        "feed": {
            "title": feed_info.get("title") or "",
            "author": feed_info.get("author") or feed_info.get("publisher") or "",
            "description": feed_info.get("description") or feed_info.get("summary") or "",
            "summary": feed_info.get("summary") or "",
            "image": {"href": feed_image} if feed_image else {},
            "link": feed_info.get("link") or "",
        },
        "entries": entries,
        "entry_count": len(parsed.get("entries") or []),
    }


def _serialize_feed(feed: PodcastFeed, user=None) -> dict:
    data = {
        "id": feed.id,
        "url": feed.url,
        "title": feed.title,
        "description": feed.description,
        "image_url": feed.image_url,
        "category": feed.category,
    }
    if user and user.is_authenticated:
        data["is_bookmarked"] = Bookmark.objects.filter(user=user, feed=feed).exists()
        data["is_subscribed"] = Subscription.objects.filter(user=user, feed=feed).exists()
    return data


def _apply_feed_metadata(feed: PodcastFeed, parsed: dict, extra_category: str = "") -> PodcastFeed:
    feed_info = parsed.get("feed", {})
    feed.title = feed_info.get("title") or feed.title
    feed.description = feed_info.get("description") or feed_info.get("summary") or feed.description
    feed.image_url = _image_from_feed(feed_info) or feed.image_url
    feed.category = extra_category or _extract_category(feed_info) or feed.category
    feed.rss_cache = _compact_feed_payload(parsed)
    feed.rss_cache_updated_at = timezone.now()
    feed.save()
    return feed


def _apply_directory_metadata(feed: PodcastFeed, body: dict) -> PodcastFeed:
    changed = False
    for field, key in (("title", "title"), ("description", "description"), ("image_url", "image_url"), ("category", "category")):
        value = body.get(key)
        if value and not getattr(feed, field):
            setattr(feed, field, value)
            changed = True
    if changed:
        feed.save(update_fields=["title", "description", "image_url", "category"])
    return feed


def _get_cached_feed(feed: PodcastFeed) -> dict:
    if feed.rss_cache and feed.rss_cache_updated_at and timezone.now() - feed.rss_cache_updated_at < RSS_CACHE_TTL:
        if len(feed.rss_cache.get("entries", [])) >= feed.rss_cache.get("entry_count", 0):
            return feed.rss_cache
    if feed.rss_cache and feed.rss_cache_updated_at and timezone.now() - feed.rss_cache_updated_at < timedelta(minutes=10):
        return feed.rss_cache
    try:
        parsed = parse_podcast_rss(feed.url)
        _apply_feed_metadata(feed, parsed)
        return feed.rss_cache
    except PodcastFeedConnectionError:
        if feed.rss_cache:
            return feed.rss_cache
        return {
            "feed": {
                "title": feed.title,
                "author": "",
                "description": feed.description or "RSS-лента сейчас не отвечает. Попробуйте открыть подкаст позже.",
                "summary": feed.description or "",
                "image": {"href": feed.image_url} if feed.image_url else {},
                "link": "",
            },
            "entries": [],
            "entry_count": 0,
            "fetch_error": "RSS-лента сейчас не отвечает",
        }


def _episode_page(payload: dict, request) -> dict:
    try:
        offset = max(0, int(request.GET.get("offset", 0)))
    except ValueError:
        offset = 0
    try:
        limit = int(request.GET.get("limit", DEFAULT_EPISODE_PAGE_SIZE))
    except ValueError:
        limit = DEFAULT_EPISODE_PAGE_SIZE
    limit = max(1, min(MAX_EPISODE_PAGE_SIZE, limit))
    entries = payload.get("entries", [])
    page = {**payload}
    page["entries"] = entries[offset:offset + limit]
    page["offset"] = offset
    page["limit"] = limit
    page["has_more"] = offset + limit < len(entries)
    page["next_offset"] = offset + limit if page["has_more"] else None
    return page


def _resolve_podcast_url(url: str) -> str:
    if "podcasts.apple.com" not in url:
        return url
    match = re.search(r"/id(\d+)", url)
    if not match:
        return url
    params = urlencode({"id": match.group(1), "entity": "podcast"})
    payload = _json_request(f"https://itunes.apple.com/lookup?{params}")
    for item in payload.get("results", []):
        if item.get("feedUrl"):
            return item["feedUrl"]
    return url


def _directory_item(item: dict) -> dict | None:
    feed_url = item.get("feedUrl")
    if not feed_url:
        return None
    return {
        "id": item.get("collectionId") or item.get("trackId"),
        "title": item.get("collectionName") or item.get("trackName"),
        "author": item.get("artistName"),
        "url": feed_url,
        "image_url": item.get("artworkUrl600") or item.get("artworkUrl100"),
        "category": item.get("primaryGenreName") or "",
    }


def _itunes_search(term: str, genre_id: str = "", limit: int = 24) -> list[dict]:
    params = {
        "media": "podcast",
        "entity": "podcast",
        "limit": limit,
        "term": term,
        "country": "US",
    }
    if genre_id:
        params["genreId"] = genre_id
    payload = _json_request(f"https://itunes.apple.com/search?{urlencode(params)}")
    seen = set()
    items = []
    for raw in payload.get("results", []):
        item = _directory_item(raw)
        if not item or item["url"] in seen:
            continue
        seen.add(item["url"])
        items.append(item)
    return items


def get_feeds(request):
    user = _get_request_user(request)
    feeds = PodcastFeed.objects.all().only("id", "url", "title", "description", "image_url", "category").order_by("title", "id")
    category = request.GET.get("category")
    if category:
        feeds = feeds.filter(category__iexact=category)
    return JsonResponse({"status": "ok", "items": [_serialize_feed(feed, user) for feed in feeds]})


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        body = _json_body(request)
        username = (body.get("username") or "").strip()
        password = body.get("password") or ""
        email = (body.get("email") or "").strip()
        if not username or not password:
            return JsonResponse({"error": "username and password are required"}, status=400)
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "username already exists"}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({"status": "ok", "token": _issue_token(user), "user": _user_payload(user)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        body = _json_body(request)
        user = authenticate(username=body.get("username"), password=body.get("password"))
        if not user:
            return JsonResponse({"error": "Invalid username or password"}, status=400)
        return JsonResponse({"status": "ok", "token": _issue_token(user), "user": _user_payload(user)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def me(request):
    user = _get_request_user(request)
    if not user:
        return JsonResponse({"error": "Authentication required"}, status=401)
    return JsonResponse({"status": "ok", "user": _user_payload(user)})


@csrf_exempt
@require_http_methods(["POST"])
@_require_auth
def update_profile(request):
    body = _json_body(request)
    username = (body.get("username") or "").strip()
    email = (body.get("email") or "").strip()
    password = body.get("password") or ""
    user = request.jwt_user
    User = get_user_model()
    if not username:
        return JsonResponse({"error": "username is required"}, status=400)
    if User.objects.exclude(id=user.id).filter(username=username).exists():
        return JsonResponse({"error": "username already exists"}, status=400)
    user.username = username
    user.email = email
    if password:
        user.set_password(password)
    user.save()
    return JsonResponse({"status": "ok", "token": _issue_token(user), "user": _user_payload(user)})


@csrf_exempt
@require_http_methods(["POST"])
def add_feed(request):
    try:
        body = _json_body(request)
        url = _resolve_podcast_url((body.get("url") or "").strip())
        if not url:
            return JsonResponse({"error": "URL is required"}, status=400)
        feed, created = PodcastFeed.objects.get_or_create(url=url)
        if body.get("title") or body.get("image_url"):
            _apply_directory_metadata(feed, body)
            return JsonResponse({"status": "ok", "created": created, "item": _serialize_feed(feed, _get_request_user(request))})
        try:
            parsed = parse_podcast_rss(url)
            _apply_feed_metadata(feed, parsed, body.get("category") or "")
        except PodcastFeedConnectionError:
            _apply_directory_metadata(feed, body)
            if not feed.title:
                raise
        return JsonResponse({"status": "ok", "created": created, "item": _serialize_feed(feed, _get_request_user(request))})
    except PodcastFeedConnectionError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def parse_feed(request, feed_id):
    try:
        feed = PodcastFeed.objects.get(id=feed_id)
        return JsonResponse({"status": "ok", "data": _episode_page(_get_cached_feed(feed), request)})
    except PodcastFeed.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def preview_feed(request):
    try:
        body = _json_body(request)
        url = _resolve_podcast_url((body.get("url") or "").strip())
        if not url:
            return JsonResponse({"error": "URL is required"}, status=400)
        parsed = parse_podcast_rss(url)
        compact = _compact_feed_payload(parsed)
        feed_info = compact["feed"]
        compact = _episode_page(compact, request)
        return JsonResponse(
            {
                "status": "ok",
                "item": {
                    "id": None,
                    "url": url,
                    "title": body.get("title") or feed_info.get("title") or "Без названия",
                    "description": feed_info.get("description") or body.get("description") or "",
                    "image_url": (feed_info.get("image") or {}).get("href") or body.get("image_url") or "",
                    "category": body.get("category") or "",
                    "is_preview": True,
                },
                "data": compact,
            }
        )
    except PodcastFeedConnectionError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def search_podcasts(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 2:
        return JsonResponse({"status": "ok", "items": []})
    try:
        return JsonResponse({"status": "ok", "items": _itunes_search(query, limit=25)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=502)


def popular_podcasts(request):
    genre_key = (request.GET.get("genre") or "all").lower()
    genre_id, term = ITUNES_GENRES.get(genre_key, ITUNES_GENRES["all"])
    try:
        if genre_key == "all":
            payload = _json_request("https://itunes.apple.com/search?" + urlencode({"media": "podcast", "entity": "podcast", "limit": 25, "term": "podcast", "country": "US"}))
            items = [item for item in (_directory_item(raw) for raw in payload.get("results", [])) if item]
        else:
            items = _itunes_search(term, genre_id=genre_id, limit=25)
        return JsonResponse({"status": "ok", "items": items, "genre": genre_key})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=502)


@csrf_exempt
@require_http_methods(["POST"])
def save_progress(request):
    try:
        body = _json_body(request)
        url = body.get("episode_url")
        current_time = float(body.get("current_time") or 0.0)
        duration = float(body.get("duration") or 0.0)
        if not url:
            return JsonResponse({"error": "episode_url is required"}, status=400)
        user = _get_request_user(request)
        completed = bool(duration and current_time >= max(duration - 30, duration * 0.92))
        progress, _created = ListenProgress.objects.update_or_create(
            user=user,
            episode_url=url,
            defaults={
                "current_time": current_time,
                "duration": duration,
                "episode_title": (body.get("episode_title") or "")[:400],
                "podcast_title": (body.get("podcast_title") or "")[:255],
                "podcast_url": body.get("podcast_url") or "",
                "image_url": body.get("image_url") or "",
                "completed": completed,
            },
        )
        return JsonResponse({"status": "ok", "current_time": progress.current_time, "completed": progress.completed})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_progress(request):
    url = request.GET.get("episode_url")
    if not url:
        return JsonResponse({"error": "episode_url is required"}, status=400)
    try:
        progress = ListenProgress.objects.get(user=_get_request_user(request), episode_url=url)
        return JsonResponse(
            {
                "status": "ok",
                "current_time": progress.current_time,
                "duration": progress.duration,
                "completed": progress.completed,
            }
        )
    except ListenProgress.DoesNotExist:
        return JsonResponse({"status": "ok", "current_time": 0.0, "duration": 0.0, "completed": False})


def _progress_payload(progress: ListenProgress) -> dict:
    return {
        "episode_url": progress.episode_url,
        "episode_title": progress.episode_title,
        "podcast_title": progress.podcast_title,
        "podcast_url": progress.podcast_url,
        "image_url": progress.image_url,
        "current_time": progress.current_time,
        "duration": progress.duration,
        "completed": progress.completed,
        "updated_at": progress.updated_at.isoformat(),
    }


@_require_auth
def history(request):
    items = ListenProgress.objects.filter(user=request.jwt_user).exclude(episode_title="")[:50]
    return JsonResponse({"status": "ok", "items": [_progress_payload(item) for item in items]})


def _library_payload(user):
    folders = []
    for folder in PodcastFolder.objects.filter(user=user).order_by("name"):
        folders.append(
            {
                "id": folder.id,
                "name": folder.name,
                "items": [_serialize_feed(item.feed, user) for item in folder.items.select_related("feed").order_by("feed__title")],
            }
        )
    return {
        "status": "ok",
        "bookmarks": [_serialize_feed(bookmark.feed, user) for bookmark in Bookmark.objects.filter(user=user).select_related("feed")],
        "subscriptions": [_serialize_feed(subscription.feed, user) for subscription in Subscription.objects.filter(user=user).select_related("feed")],
        "folders": folders,
    }


@_require_auth
def library(request):
    return JsonResponse(_library_payload(request.jwt_user))


@csrf_exempt
@require_http_methods(["POST"])
@_require_auth
def toggle_bookmark(request):
    feed = PodcastFeed.objects.get(id=_json_body(request).get("feed_id"))
    existing = Bookmark.objects.filter(user=request.jwt_user, feed=feed).first()
    if existing:
        existing.delete()
        active = False
    else:
        Bookmark.objects.create(user=request.jwt_user, feed=feed)
        active = True
    return JsonResponse({"status": "ok", "active": active})


@csrf_exempt
@require_http_methods(["POST"])
@_require_auth
def toggle_subscription(request):
    feed = PodcastFeed.objects.get(id=_json_body(request).get("feed_id"))
    existing = Subscription.objects.filter(user=request.jwt_user, feed=feed).first()
    if existing:
        existing.delete()
        active = False
    else:
        Subscription.objects.create(user=request.jwt_user, feed=feed)
        active = True
    return JsonResponse({"status": "ok", "active": active})


@csrf_exempt
@require_http_methods(["GET", "POST"])
@_require_auth
def folders(request):
    if request.method == "POST":
        name = (_json_body(request).get("name") or "").strip()
        if not name:
            return JsonResponse({"error": "name is required"}, status=400)
        PodcastFolder.objects.get_or_create(user=request.jwt_user, name=name)
    return JsonResponse(_library_payload(request.jwt_user))


@csrf_exempt
@require_http_methods(["POST"])
@_require_auth
def add_to_folder(request, folder_id):
    folder = PodcastFolder.objects.get(id=folder_id, user=request.jwt_user)
    feed = PodcastFeed.objects.get(id=_json_body(request).get("feed_id"))
    PodcastFolderItem.objects.get_or_create(folder=folder, feed=feed)
    return JsonResponse(_library_payload(request.jwt_user))
