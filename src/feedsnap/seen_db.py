"""seen_db — SQLite-backed seen-entries cache for feedsnap.

Tracks which entry URLs have already been shown for each feed so that
repeated runs of ``feedsnap --dedup`` only surface genuinely new items.

Schema:
    seen_entries(url TEXT PRIMARY KEY, feed_url TEXT, first_seen TEXT)

All public functions accept a ``db_path: Path`` so callers can supply
any location (useful for testing). ``default_db_path()`` returns the
conventional ``~/.feedsnap/seen.db``.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

_DEFAULT_DB = Path.home() / ".feedsnap" / "seen.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_entries (
    url         TEXT PRIMARY KEY,
    feed_url    TEXT NOT NULL,
    first_seen  TEXT NOT NULL DEFAULT (date('now'))
);
"""


def default_db_path() -> Path:
    """Return the conventional path for the seen-entries database."""
    return _DEFAULT_DB


def _connect(db_path: Path) -> sqlite3.Connection:
    """Open (or create) the database, ensuring parent directories exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def get_seen(db_path: Path, feed_url: str) -> set[str]:
    """Return the set of entry URLs already seen for *feed_url*.

    Creates the database file (and parent directories) if they don't exist yet.
    Returns an empty set for a brand-new feed URL.
    """
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT url FROM seen_entries WHERE feed_url = ?", (feed_url,)
        ).fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


def mark_seen(db_path: Path, feed_url: str, urls: list[str]) -> int:
    """Record *urls* as seen for *feed_url*.

    Uses ``INSERT OR IGNORE`` so repeated calls with the same URLs are
    idempotent — no errors, no duplicates.

    Empty strings in *urls* are silently skipped (entries with no URL
    should never be persisted).

    Returns the number of newly inserted rows.
    """
    if not urls:
        return 0
    conn = _connect(db_path)
    try:
        cursor = conn.executemany(
            "INSERT OR IGNORE INTO seen_entries (url, feed_url) VALUES (?, ?)",
            [(url, feed_url) for url in urls if url],
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
