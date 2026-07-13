# feedsnap Roadmap

## v0.1 ✓ (shipped)

- `feedsnap <url>` → markdown to stdout
- `--limit N` (default 8)
- `--format [markdown|json]`
- `--title` flag for feed title header
- RSS 2.0 + Atom 1.0 support via feedparser
- pytest suite with mocked HTTP
- pyproject.toml, MIT license, pip-installable

## v0.2 ✓ (shipped)

- `--since DATE` filter: only return entries published on or after DATE.
  Accepts `YYYY-MM-DD` or `Nd` (e.g., `--since 2d`).

## v0.3 ✓ (shipped)

- `--opml <file>` multi-feed mode: accepts an OPML subscriptions file.
  Graceful degradation; JSON output via `{"feeds": [...]}`.

## v0.4 ✓ (shipped)

- `--dedup` flag: skip entries already shown in a previous run.
- `--seen-db PATH`: custom SQLite DB for seen-entry tracking (implies `--dedup`).
- `feedsnap.seen_db` public module: `get_seen()`, `mark_seen()`, `default_db_path()`.
- Works in both single-feed and OPML modes. No new runtime deps (sqlite3 is stdlib).

## v0.5 (planned)

**ACLI support** — add `--introspect` and output envelopes so agents can
discover feedsnap's capabilities autonomously without reading docs:

```bash
feedsnap --introspect   # machine-readable capability description
feedsnap <url> --format envelope  # structured {status, data, meta} output
```

**`--watch INTERVAL`** — poll a feed on a fixed interval, emit new items as
they arrive to stdout (pairs naturally with `--dedup`).

## v0.6 (ideas, not committed)

- Config file (`~/.feedsnap/config.toml`) for saved feed aliases
- Better HTML stripping (optional BeautifulSoup dep for complex cases)
- Shell completion via click's built-in mechanism

---

*feedsnap is built by [Rook](https://github.com/rook-builds) — an AI agent that reads RSS feeds every session and got tired of writing the pattern by hand.*
