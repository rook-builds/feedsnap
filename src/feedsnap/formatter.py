from __future__ import annotations

import json

from .fetcher import Feed


def to_markdown(feed: Feed, show_title: bool = False) -> str:
    """Render a Feed as a clean markdown digest."""
    lines: list[str] = []

    if show_title:
        lines.append(f"# {feed.title}")
        lines.append("")

    for entry in feed.entries:
        lines.append(f"### {entry.title}")

        meta_parts: list[str] = []
        if entry.published:
            meta_parts.append(entry.published)
        if entry.url:
            meta_parts.append(f"<{entry.url}>")
        if meta_parts:
            lines.append("  ".join(meta_parts))

        if entry.summary:
            lines.append("")
            lines.append(entry.summary)

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def to_json(feed: Feed) -> str:
    """Render a Feed as pretty-printed JSON."""
    data = {
        "title": feed.title,
        "url": feed.url,
        "entries": [
            {
                "title": e.title,
                "url": e.url,
                "published": e.published,
                "summary": e.summary,
            }
            for e in feed.entries
        ],
    }
    return json.dumps(data, indent=2) + "\n"
