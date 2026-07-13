# feedsnap — Recent Changes (Agent Summary)

> This file summarises changes an agent needs to be aware of.
> Full CHANGELOG: https://github.com/rook-builds/feedsnap/blob/main/CHANGELOG.md

## v0.5.0 (2026-07-13) — CURRENT

**New commands:**
- `feedsnap introspect` → JSON command tree (ACLI v0.1.0)
- `feedsnap skill` → SKILL.md for agent bootstrapping
- `feedsnap --version` → installed version string

**New public API:** `feedsnap.introspect.get_introspect_json()`, `get_skill_md()`

**Bug fix:** `__version__` was stale at `0.3.0`; now correctly `0.5.0`.

## v0.4.0 (2026-07-13)

**New flags:** `--dedup`, `--seen-db PATH`
**New module:** `feedsnap.seen_db` — SQLite-backed seen-entry cache.
Run `feedsnap <url> --dedup` to skip entries shown in a previous run.

## v0.3.0 (2026-07-12)

**New flag:** `--opml PATH` — process multiple feeds from an OPML file.
Failed feeds are skipped with a warning; remaining feeds are still returned.

## v0.2.0 (2026-07-12)

**New flag:** `--since DATE` — filter by publication date.
Accepts `YYYY-MM-DD` or `Nd` (e.g., `2d` = two days ago).

## v0.1.0 (2026-07-12)

Initial release: `feedsnap <url>` → markdown digest.
