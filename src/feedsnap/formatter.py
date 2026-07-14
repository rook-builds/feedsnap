from __future__ import annotations

import json

from .fetcher import Feed

# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Table output
# ---------------------------------------------------------------------------

_TITLE_W = 50
_DATE_W = 10


def _trunc(s: str, n: int) -> str:
    """Truncate *s* to at most *n* characters, appending '…' if cut."""
    return s if len(s) <= n else s[: n - 1] + "…"


def to_table(feed: Feed, show_title: bool = False) -> str:
    """Render a Feed as a plain-text aligned table.

    Columns: TITLE (50 chars, truncated), DATE (10 chars), URL.

    Example::

        TITLE                                              DATE        URL
        ─────────────────────────────────────────────────  ──────────  ─────────────────────────────
        My Post Title                                      2026-07-14  https://example.com/post
    """
    lines: list[str] = []

    if show_title:
        lines.append(f"# {feed.title}")
        lines.append("")

    header = f"{'TITLE':<{_TITLE_W}}  {'DATE':<{_DATE_W}}  URL"
    sep = f"{'─' * _TITLE_W}  {'─' * _DATE_W}  {'─' * 60}"
    lines.append(header)
    lines.append(sep)

    for entry in feed.entries:
        title_col = _trunc(entry.title or "", _TITLE_W)
        date_col = (entry.published or "")[:_DATE_W]
        url_col = entry.url or ""
        lines.append(f"{title_col:<{_TITLE_W}}  {date_col:<{_DATE_W}}  {url_col}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Legacy JSON output (--format json, backward compat)
# ---------------------------------------------------------------------------


def to_json(feed: Feed) -> str:
    """Render a Feed as pretty-printed JSON.

    This is the legacy output format emitted by ``--format json``.
    For the ACLI-compliant envelope format, use :func:`to_envelope`.
    """
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


def to_json_multi(feeds: list[Feed]) -> str:
    """Render a list of Feeds as pretty-printed JSON.

    This is the legacy multi-feed format emitted by ``--opml … --format json``.
    For the ACLI-compliant envelope format, use :func:`to_envelope_multi`.
    """
    data = {
        "feeds": [
            {
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
            for feed in feeds
        ]
    }
    return json.dumps(data, indent=2) + "\n"


# ---------------------------------------------------------------------------
# ACLI envelope output (--output json)
# ---------------------------------------------------------------------------


def to_envelope(feed: Feed, duration_ms: int) -> str:
    """Render a Feed as an ACLI-compliant JSON envelope.

    Emitted by ``--output json`` (single-feed mode).

    Schema::

        {
          "ok": true,
          "command": "snap",
          "version": "<installed version>",
          "duration_ms": <int>,
          "data": { "title": ..., "url": ..., "entries": [...] }
        }
    """
    from feedsnap import __version__

    payload = {
        "ok": True,
        "command": "snap",
        "version": __version__,
        "duration_ms": duration_ms,
        "data": {
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
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def to_envelope_multi(feeds: list[Feed], duration_ms: int) -> str:
    """Render multiple Feeds as an ACLI-compliant JSON envelope.

    Emitted by ``--opml … --output json`` (OPML multi-feed mode).

    Schema::

        {
          "ok": true,
          "command": "snap",
          "version": "<installed version>",
          "duration_ms": <int>,
          "data": { "feeds": [...] }
        }
    """
    from feedsnap import __version__

    payload = {
        "ok": True,
        "command": "snap",
        "version": __version__,
        "duration_ms": duration_ms,
        "data": {
            "feeds": [
                {
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
                for feed in feeds
            ]
        },
    }
    return json.dumps(payload, indent=2) + "\n"
