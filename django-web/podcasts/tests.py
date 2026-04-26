from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from django.contrib.auth import get_user_model
from django.test import TestCase
from feedparser.util import FeedParserDict

from podcasts.services import PodcastFeedConnectionError, parse_podcast_rss
from podcasts.models import PodcastFeed


class PodcastRSSParserTests(TestCase):
    fixtures_path = Path(__file__).resolve().parent / "test_data"

    def test_parse_podcast_rss_returns_rich_podcast_metadata(self) -> None:
        rss_url = (self.fixtures_path / "rich-podcast.xml").resolve().as_uri()

        data = parse_podcast_rss(rss_url)

        self.assertEqual(data["feed"]["title"], "Deep Space Radio")
        self.assertEqual(data["feed"]["author"], "Easy Podcasts")
        self.assertEqual(data["feed"]["image"]["href"], "https://example.com/podcasts/deep-space.jpg")
        self.assertEqual(len(data["entries"]), 2)
        self.assertEqual(data["entries"][0]["title"], "Episode 1")
        self.assertEqual(data["entries"][0]["links"][0]["href"], "https://cdn.example.com/ep1.mp3")
        self.assertEqual(data["entries"][0]["links"][0]["rel"], "enclosure")
        self.assertEqual(data["entries"][0]["published_parsed"]["iso"], "2024-01-01T09:00:00Z")
        self.assertFalse(data["bozo"])

    def test_parse_podcast_rss_returns_minimal_feed_data(self) -> None:
        rss_url = (self.fixtures_path / "minimal-podcast.xml").resolve().as_uri()

        data = parse_podcast_rss(rss_url)

        self.assertEqual(data["feed"]["title"], "Minimal Podcast")
        self.assertEqual(data["feed"]["link"], "https://example.com/minimal")
        self.assertEqual(len(data["entries"]), 1)
        self.assertEqual(data["entries"][0]["title"], "Pilot")
        self.assertIsNone(data["bozo_exception"])

    def test_parse_podcast_rss_raises_on_connection_error(self) -> None:
        mocked_feed = FeedParserDict(
            bozo=1,
            bozo_exception=URLError("temporary DNS failure"),
            entries=[],
            feed={},
        )

        with patch("podcasts.services.feedparser.parse", return_value=mocked_feed):
            with self.assertRaises(PodcastFeedConnectionError):
                parse_podcast_rss("https://unreachable.example.com/feed.xml")


class PodcastAPITests(TestCase):
    def test_profile_update_changes_user_and_reissues_token(self) -> None:
        User = get_user_model()
        User.objects.create_user(username="max", email="old@example.com", password="secret123")
        login_response = self.client.post(
            "/api/podcasts/auth/login/",
            data=json.dumps({"username": "max", "password": "secret123"}),
            content_type="application/json",
        )
        token = login_response.json()["token"]

        response = self.client.post(
            "/api/podcasts/auth/profile/",
            data=json.dumps({"username": "maxim", "email": "new@example.com", "password": "nextsecret123"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["username"], "maxim")
        self.assertTrue(response.json()["token"])
        self.assertTrue(User.objects.get(username="maxim").check_password("nextsecret123"))

    def test_popular_podcasts_serializes_apple_feed(self) -> None:
        class MockResponse:
            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps(self.payload).encode("utf-8")

        search_payload = {
            "results": [
                {
                    "collectionName": "Design Talk",
                    "artistName": "Easy Podcasts",
                    "collectionId": 123,
                    "feedUrl": "https://example.com/feed.xml",
                    "artworkUrl100": "https://example.com/cover.jpg",
                    "primaryGenreName": "Technology",
                }
            ]
        }

        with patch("podcasts.views.urlopen", return_value=MockResponse(search_payload)):
            response = self.client.get("/api/podcasts/popular/?genre=technology")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["title"], "Design Talk")
        self.assertEqual(response.json()["items"][0]["url"], "https://example.com/feed.xml")

    def test_add_feed_from_directory_metadata_does_not_require_immediate_rss_fetch(self) -> None:
        response = self.client.post(
            "/api/podcasts/add/",
            data=json.dumps(
                {
                    "url": "https://slow.example.com/feed.xml",
                    "title": "Slow Directory Podcast",
                    "image_url": "https://example.com/cover.jpg",
                    "category": "Technology",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["item"]["title"], "Slow Directory Podcast")
        self.assertTrue(PodcastFeed.objects.filter(url="https://slow.example.com/feed.xml").exists())
