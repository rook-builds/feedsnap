from __future__ import annotations

import re
import time
from dataclasses import dataclass
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


def fetch_feed(url: str, limit: int = 8) -> Feed:
    """Fetch and parse an RSS or Atom feed. Returns a Feed dataclass."""
    parsed = feedparser.parse(url)

    if parsed.bozo and not parsed.entries:
        raise ValueError(f"Could not parse feed at {url}: {parsed.bozo_exception}")

    entries = [
        FeedEntry(
            title=entry.get("title", "(no title)"),
            url=entry.get("link", ""),
            published=_format_date(entry),
            summary=_clean_summary(entry.get("summary", "")),
        )
        for entry in parsed.entries[:limit]
    ]

    return Feed(
        title=parsed.feed.get("title", url),
        url=url,
        entries=entries,
    )


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
