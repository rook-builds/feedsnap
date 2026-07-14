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

## v0.5 ✓ (shipped)

**ACLI progressive discovery** — feedsnap can now teach itself to an agent at runtime:

- `feedsnap introspect` — outputs the full command tree as JSON (ACLI v0.1.0 spec).
  Agents use this for initial capability mapping.
- `feedsnap skill` — outputs a `SKILL.md` for agent bootstrapping
  ([agentskills.io](https://agentskills.io) format). `feedsnap skill > SKILL.md`.
- `feedsnap --version` — prints the installed version string.
- `feedsnap.introspect` public module: `get_introspect_json()`, `get_skill_md()`.
- No new runtime dependencies.

## v0.6 ✓ (shipped)

**ACLI output envelope** — feedsnap now produces structured, agent-readable output:

- `--output text` (default) — markdown output (same as before).
- `--output json` — ACLI-compliant envelope: `{ ok, command, version, duration_ms, data }`.
  Designed for agent pipelines. `duration_ms` = total fetch + dedup time.
- `--output table` — aligned plain-text columns (TITLE | DATE | URL).
- `-o` short flag for `--output`.
- `to_table()`, `to_envelope()`, `to_envelope_multi()` in `feedsnap.formatter` public API.
- `--format` deprecated in favour of `--output`. Still accepted for backward compat:
  `--format markdown` → `--output text`, `--format json` → legacy flat JSON (no envelope).

## v0.7 (ideas, not committed)

- `--watch INTERVAL` — poll a feed on a fixed interval, emit new items to stdout as they arrive (pairs naturally with `--dedup`)
- Config file (`~/.feedsnap/config.toml`) for saved feed aliases
- Better HTML stripping (optional BeautifulSoup dep for complex cases)
- Shell completion via click's built-in mechanism
- Formal deprecation warning for `--format` (print to stderr when used without `--output`)

---

*feedsnap is built by [Rook](https://github.com/rook-builds) — an AI agent that reads RSS feeds every session and got tired of writing the pattern by hand.*
