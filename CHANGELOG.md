# Changelog

All notable changes to feedsnap are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-07-13

### Added
- `feedsnap introspect` — outputs the full command tree as JSON (ACLI v0.1.0 format).
  Agents can call this for initial capability mapping without reading documentation.
- `feedsnap skill` — outputs a `SKILL.md` for agent bootstrapping in the
  [agentskills.io](https://agentskills.io) format. Redirect to a file:
  `feedsnap skill > SKILL.md`.
- `feedsnap --version` — prints the installed version string and exits.
- New `feedsnap.introspect` module: `get_introspect_json()` and `get_skill_md()`
  are public API for programmatic use.
- Error message when no URL or `--opml` is supplied now mentions
  `feedsnap introspect` for agent discovery.
- Both `-h` and `--help` trigger the help text.

### Fixed
- `__version__` in `feedsnap/__init__.py` was stale at `0.3.0` while
  `pyproject.toml` was at `0.4.0`. Both are now `0.5.0`.

### Notes
- ACLI compliance spec: [ACLI v0.1.0 Draft](https://github.com/alpibrusl/acli).
  feedsnap implements the progressive discovery layer (introspect + skill).
  Output envelope format (`--output json`) is planned for v0.6.

## [0.4.0] - 2026-07-13

### Added
- `--dedup` flag: skip entries already shown in a previous run. Seen entry URLs
  are tracked in `~/.feedsnap/seen.db` (SQLite, created automatically).
- `--seen-db PATH` option: specify a custom SQLite database for the seen-entries
  cache. Useful for keeping separate seen-lists per project or script. Implies
  `--dedup` — either flag alone is sufficient to enable deduplication.
- New `feedsnap.seen_db` module: `get_seen()`, `mark_seen()`, and
  `default_db_path()` are public API for programmatic use.
- Dedup works in both single-feed and OPML multi-feed modes; each feed's seen
  set is scoped by its own URL, so feeds never bleed into each other.

### Details
- Schema: `seen_entries(url TEXT PRIMARY KEY, feed_url TEXT, first_seen TEXT)`.
- `INSERT OR IGNORE` makes repeated runs idempotent — no errors, no duplicates.
- Parent directories for `--seen-db` are created automatically.
- No new runtime dependencies (sqlite3 is stdlib).

## [0.3.0] - 2026-07-12

### Added
- `--opml <file>` flag: accepts an OPML subscriptions file and outputs a combined
  digest from all feeds it contains. Handles flat and nested OPML outlines.
- `parse_opml()` function in `fetcher.py` for OPML XML parsing (stdlib only, no new deps).
- `to_json_multi()` function in `formatter.py` for multi-feed JSON output (`{"feeds": [...]}`).
- Graceful degradation in OPML mode: failed feeds print a warning to stderr and are
  skipped; remaining feeds are still processed.
- In OPML mode, feed title headers are always shown (independent of `--title` flag).

## [0.2.0] — 2026-07-12

### Added

- `--since DATE` option: filter entries by publication date. Accepts ISO format (`YYYY-MM-DD`) or relative shorthand (`Nd` for N days ago, e.g., `--since 2d`). Entries with no published date are always included. The `--limit` applies to the post-filter result set.

## [0.1.0] — 2026-07-12

### Added

- `feedsnap <url>` CLI — turn any RSS 2.0 or Atom 1.0 feed into a clean markdown digest
- `--limit N` / `-n` option — number of entries to return (default: 8)
- `--format [markdown|json]` / `-f` option — output format (default: markdown)
- `--title` flag — include the feed title as an H1 header in markdown output
- HTML stripping in entry summaries (regex-based, no extra deps)
- Summary truncation at 300 characters with word-boundary respect
- JSON output includes `title`, `url`, `published`, and `summary` per entry
- Exit code 1 + stderr message on feed fetch/parse failure
- pytest test suite — 11 tests, all HTTP mocked, no network required
- GitHub Actions CI — runs on Python 3.10, 3.11, 3.12 on every push and PR

[Unreleased]: https://github.com/rook-builds/feedsnap/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/rook-builds/feedsnap/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/rook-builds/feedsnap/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/rook-builds/feedsnap/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/rook-builds/feedsnap/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rook-builds/feedsnap/releases/tag/v0.1.0
