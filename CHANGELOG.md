# Changelog

All notable changes to feedsnap are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/rook-builds/feedsnap/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/rook-builds/feedsnap/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/rook-builds/feedsnap/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rook-builds/feedsnap/releases/tag/v0.1.0
