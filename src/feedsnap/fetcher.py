from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import date
from typing import Optional

import feedparser


@dataclass
class FeedEntry:
    title: str
    url: str
    published: Optional[str]
    summary: Optional[str]


@dataclass
class Feed:
    title: str
    url: str
    entries: list[FeedEntry]


def fetch_feed(url: str, limit: int = 8, since: Optional[date] = None) -> Feed:
    """Fetch and parse an RSS or Atom feed. Returns a Feed dataclass.

    If ``since`` is given, entries published before that date are dropped
    (undated entries are always kept), and ``limit`` applies to the
    already-filtered set.
    """
    parsed = feedparser.parse(url)

    if parsed.bozo and not parsed.entries:
        raise ValueError(f"Could not parse feed at {url}: {parsed.bozo_exception}")

    raw = parsed.entries
    if since is not None:
        raw = [e for e in raw if _passes_since(e, since)]
    raw = raw[:limit]

    entries = [
        FeedEntry(
            title=entry.get("title", "(no title)"),
            url=entry.get("link", ""),
            published=_format_date(entry),
            summary=_clean_summary(entry.get("summary", "")),
        )
        for entry in raw
    ]

    return Feed(
        title=parsed.feed.get("title", url),
        url=url,
        entries=entries,
    )


def _passes_since(entry, since: date) -> bool:
    """Return True if entry should be included given the since cutoff."""
    pp = getattr(entry, "published_parsed", None)
    if not pp:
        return True  # No date → always include; can't know if it's old
    return date(*pp[:3]) >= since


def _format_date(entry) -> Optional[str]:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return time.strftime("%Y-%m-%d", entry.published_parsed)
    return None


def _clean_summary(text: str, max_chars: int = 300) -> str:
    """Strip HTML tags, collapse whitespace, truncate at word boundary."""
    text = re.sub(r"<[^>]+>", "", text)
    text = " ".join(text.split())
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "\u2026"
    return text
