"""Tests for feedsnap.seen_db — SQLite seen-entries cache."""
from __future__ import annotations

import pytest

from feedsnap.seen_db import default_db_path, get_seen, mark_seen


# ── default_db_path ──────────────────────────────────────────────────────────

def test_default_db_path_is_under_home_feedsnap():
    p = default_db_path()
    assert p.name == "seen.db"
    assert p.parent.name == ".feedsnap"


# ── get_seen ─────────────────────────────────────────────────────────────────

def test_get_seen_returns_empty_set_for_new_db(tmp_path):
    db = tmp_path / "seen.db"
    result = get_seen(db, "https://example.com/feed")
    assert result == set()


def test_get_seen_creates_database_file(tmp_path):
    db = tmp_path / "seen.db"
    assert not db.exists()
    get_seen(db, "https://example.com/feed")
    assert db.exists()


def test_get_seen_creates_nested_parent_directories(tmp_path):
    db = tmp_path / "a" / "b" / "c" / "seen.db"
    assert not db.parent.exists()
    get_seen(db, "https://example.com/feed")
    assert db.exists()


# ── mark_seen + get_seen ─────────────────────────────────────────────────────

def test_mark_seen_and_get_seen_roundtrip(tmp_path):
    db = tmp_path / "seen.db"
    feed_url = "https://example.com/feed"
    urls = ["https://example.com/1", "https://example.com/2"]

    count = mark_seen(db, feed_url, urls)
    assert count == 2

    seen = get_seen(db, feed_url)
    assert seen == set(urls)


def test_mark_seen_is_idempotent(tmp_path):
    """Calling mark_seen twice with the same URLs should not create duplicates."""
    db = tmp_path / "seen.db"
    feed_url = "https://example.com/feed"
    urls = ["https://example.com/1"]

    mark_seen(db, feed_url, urls)
    mark_seen(db, feed_url, urls)  # INSERT OR IGNORE — no error

    # Only one entry in the DB for this URL
    seen = get_seen(db, feed_url)
    assert seen == {"https://example.com/1"}


def test_get_seen_isolates_by_feed_url(tmp_path):
    """Seen sets are scoped per feed_url; entries for one feed
    don't bleed into another."""
    db = tmp_path / "seen.db"
    feed_a = "https://a.com/feed"
    feed_b = "https://b.com/feed"

    mark_seen(db, feed_a, ["https://a.com/1"])
    mark_seen(db, feed_b, ["https://b.com/1"])

    assert get_seen(db, feed_a) == {"https://a.com/1"}
    assert get_seen(db, feed_b) == {"https://b.com/1"}
    assert "https://a.com/1" not in get_seen(db, feed_b)
    assert "https://b.com/1" not in get_seen(db, feed_a)


# ── edge cases ───────────────────────────────────────────────────────────────

def test_mark_seen_empty_list_returns_zero(tmp_path):
    db = tmp_path / "seen.db"
    count = mark_seen(db, "https://example.com/feed", [])
    assert count == 0


def test_mark_seen_skips_empty_string_urls(tmp_path):
    """Empty-string URLs should be silently skipped."""
    db = tmp_path / "seen.db"
    feed_url = "https://example.com/feed"
    urls = ["https://example.com/1", "", "https://example.com/3"]

    mark_seen(db, feed_url, urls)
    seen = get_seen(db, feed_url)

    assert "" not in seen
    assert "https://example.com/1" in seen
    assert "https://example.com/3" in seen


def test_multiple_feeds_share_same_db(tmp_path):
    """Multiple feeds writing to the same DB file don't interfere."""
    db = tmp_path / "shared.db"

    for i in range(5):
        feed_url = f"https://example{i}.com/feed"
        mark_seen(db, feed_url, [f"https://example{i}.com/entry"])

    for i in range(5):
        feed_url = f"https://example{i}.com/feed"
        seen = get_seen(db, feed_url)
        assert seen == {f"https://example{i}.com/entry"}
