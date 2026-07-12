import time
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from feedsnap.fetcher import fetch_feed


def _make_entry(title: str, pub_date: date | None):
    """Build a minimal mock feedparser entry."""
    entry = MagicMock()
    entry.get.side_effect = lambda key, default="": {"title": title, "link": "", "summary": ""}.get(key, default)
    if pub_date:
        entry.published_parsed = time.struct_time(
            (pub_date.year, pub_date.month, pub_date.day, 0, 0, 0, 0, 0, 0)
        )
    else:
        entry.published_parsed = None
    return entry


def _make_parsed(entries, feed_title="Test Feed"):
    parsed = MagicMock()
    parsed.bozo = False
    parsed.entries = entries
    parsed.feed.get.side_effect = lambda key, default="": {"title": feed_title}.get(key, default)
    return parsed


def test_fetch_feed_since_filters_old_entries():
    old_entry = _make_entry("Old", date(2026, 7, 1))
    new_entry = _make_entry("New", date(2026, 7, 11))
    with patch("feedsnap.fetcher.feedparser.parse", return_value=_make_parsed([old_entry, new_entry])):
        feed = fetch_feed("https://example.com/feed", since=date(2026, 7, 10))
    assert len(feed.entries) == 1
    assert feed.entries[0].title == "New"


def test_fetch_feed_since_inclusive():
    """Entry on exactly the since date should be included."""
    entry = _make_entry("Exact", date(2026, 7, 10))
    with patch("feedsnap.fetcher.feedparser.parse", return_value=_make_parsed([entry])):
        feed = fetch_feed("https://example.com/feed", since=date(2026, 7, 10))
    assert len(feed.entries) == 1


def test_fetch_feed_since_no_date_passes():
    """Entries with no published_parsed are always included."""
    entry = _make_entry("Undated", None)
    with patch("feedsnap.fetcher.feedparser.parse", return_value=_make_parsed([entry])):
        feed = fetch_feed("https://example.com/feed", since=date(2026, 7, 15))
    assert len(feed.entries) == 1


def test_fetch_feed_limit_applies_after_filter():
    """limit should apply to the already-filtered set."""
    entries = [_make_entry(f"Entry {i}", date(2026, 7, 11)) for i in range(5)]
    with patch("feedsnap.fetcher.feedparser.parse", return_value=_make_parsed(entries)):
        feed = fetch_feed("https://example.com/feed", limit=3, since=date(2026, 7, 11))
    assert len(feed.entries) == 3


def test_fetch_feed_no_since_returns_all():
    """Without --since, behavior is identical to v0.1."""
    entries = [_make_entry(f"Entry {i}", date(2026, 7, i + 1)) for i in range(5)]
    with patch("feedsnap.fetcher.feedparser.parse", return_value=_make_parsed(entries)):
        feed = fetch_feed("https://example.com/feed")
    assert len(feed.entries) == 5
