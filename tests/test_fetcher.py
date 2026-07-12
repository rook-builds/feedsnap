import time
import xml.etree.ElementTree as ET
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from feedsnap.fetcher import fetch_feed, parse_opml


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


FLAT_OPML = """\
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>Test Feeds</title></head>
  <body>
    <outline text="Feed One" type="rss" xmlUrl="https://example.com/feed1" />
    <outline text="Feed Two" type="rss" xmlUrl="https://example.com/feed2" />
  </body>
</opml>
"""

NESTED_OPML = """\
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>Test Feeds</title></head>
  <body>
    <outline text="Category" title="Tech">
      <outline text="Feed One" title="Feed One Title" type="rss" xmlUrl="https://example.com/feed1" />
    </outline>
    <outline text="Feed Two" type="rss" xmlUrl="https://example.com/feed2" />
  </body>
</opml>
"""

OPML_NO_FEEDS = """\
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>Empty</title></head>
  <body>
    <outline text="Just a category" />
  </body>
</opml>
"""

OPML_TITLE_VS_TEXT = """\
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head></head>
  <body>
    <outline text="text attr" title="title attr" type="rss" xmlUrl="https://example.com/f1" />
    <outline text="only text" type="rss" xmlUrl="https://example.com/f2" />
  </body>
</opml>
"""


def test_parse_opml_flat(tmp_path):
    f = tmp_path / "feeds.opml"
    f.write_text(FLAT_OPML)
    result = parse_opml(str(f))
    assert len(result) == 2
    assert result[0] == ("Feed One", "https://example.com/feed1")
    assert result[1] == ("Feed Two", "https://example.com/feed2")


def test_parse_opml_nested(tmp_path):
    f = tmp_path / "nested.opml"
    f.write_text(NESTED_OPML)
    result = parse_opml(str(f))
    assert len(result) == 2
    urls = [url for _, url in result]
    assert "https://example.com/feed1" in urls
    assert "https://example.com/feed2" in urls


def test_parse_opml_no_feeds(tmp_path):
    f = tmp_path / "empty.opml"
    f.write_text(OPML_NO_FEEDS)
    result = parse_opml(str(f))
    assert result == []


def test_parse_opml_title_preferred_over_text(tmp_path):
    f = tmp_path / "title.opml"
    f.write_text(OPML_TITLE_VS_TEXT)
    result = parse_opml(str(f))
    assert result[0][0] == "title attr"
    assert result[1][0] == "only text"


def test_parse_opml_invalid_xml(tmp_path):
    f = tmp_path / "bad.opml"
    f.write_text("this is not xml <<< >>>")
    with pytest.raises(ET.ParseError):
        parse_opml(str(f))
