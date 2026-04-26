from __future__ import annotations

from http.client import IncompleteRead
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError

import feedparser
from feedparser.util import FeedParserDict


class PodcastFeedConnectionError(Exception):
    """Raised when the RSS feed cannot be fetched."""


def _serialize_feed_value(value: Any) -> Any:
    if isinstance(value, FeedParserDict):
        return {key: _serialize_feed_value(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_serialize_feed_value(item) for item in value]

    if isinstance(value, tuple) and hasattr(value, "tm_year"):
        return {
            "iso": (
                f"{value.tm_year:04d}-{value.tm_mon:02d}-{value.tm_mday:02d}"
                f"T{value.tm_hour:02d}:{value.tm_min:02d}:{value.tm_sec:02d}Z"
            ),
            "parts": list(value),
        }

    return value


def _build_response(parsed_feed: FeedParserDict) -> dict[str, Any]:
    return {
        "href": parsed_feed.get("href"),
        "status": parsed_feed.get("status"),
        "encoding": parsed_feed.get("encoding"),
        "version": parsed_feed.get("version"),
        "namespaces": _serialize_feed_value(parsed_feed.get("namespaces", {})),
        "headers": _serialize_feed_value(parsed_feed.get("headers", {})),
        "etag": parsed_feed.get("etag"),
        "modified": _serialize_feed_value(parsed_feed.get("modified")),
        "feed": _serialize_feed_value(parsed_feed.get("feed", {})),
        "entries": _serialize_feed_value(parsed_feed.get("entries", [])),
        "bozo": bool(parsed_feed.get("bozo", 0)),
        "bozo_exception": (
            str(parsed_feed.bozo_exception)
            if parsed_feed.get("bozo") and hasattr(parsed_feed, "bozo_exception")
            else None
        ),
    }


def _is_connection_error(parsed_feed: FeedParserDict) -> bool:
    if not parsed_feed.get("bozo"):
        return False

    bozo_exception = getattr(parsed_feed, "bozo_exception", None)
    return isinstance(bozo_exception, URLError)


def _fetch_feed_bytes(rss_url: str) -> bytes:
    request = Request(
        rss_url,
        headers={
            "User-Agent": "EasyPodcasts/1.0 (+https://localhost)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    last_error = None
    for _ in range(2):
        try:
            with urlopen(request, timeout=25) as response:
                return response.read()
        except IncompleteRead as exc:
            if exc.partial:
                return exc.partial
            last_error = exc
        except (TimeoutError, URLError) as exc:
            last_error = exc
    if last_error:
        raise PodcastFeedConnectionError(f"Could not fetch RSS feed from URL: {rss_url}") from last_error
    return b""


def parse_podcast_rss(rss_url: str) -> dict[str, Any]:
    parsed_feed = feedparser.parse(rss_url if rss_url.startswith("file:") else _fetch_feed_bytes(rss_url))

    if _is_connection_error(parsed_feed):
        raise PodcastFeedConnectionError(
            f"Could not fetch RSS feed from URL: {rss_url}"
        ) from parsed_feed.bozo_exception

    return _build_response(parsed_feed)
