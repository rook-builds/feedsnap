"""ACLI-compatible introspection for feedsnap.

Generates the JSON command tree (``feedsnap introspect``) and the SKILL.md
bootstrap file for agents (``feedsnap skill``).

Spec reference: ACLI v0.1.0 — https://github.com/alpibrusl/acli
"""
from __future__ import annotations

import json

ACLI_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Static command-tree definition
# ---------------------------------------------------------------------------

_COMMANDS = [
    {
        "name": "snap",
        "description": (
            "Fetch an RSS or Atom feed and output a clean digest. "
            "This is the default command — invoke directly as "
            "'feedsnap <url> [options]'."
        ),
        "arguments": [
            {
                "name": "url",
                "type": "string",
                "required": False,
                "description": (
                    "RSS 2.0 or Atom 1.0 feed URL. "
                    "Required unless --opml is used."
                ),
            }
        ],
        "options": [
            {
                "name": "--opml",
                "type": "path",
                "required": False,
                "description": (
                    "Path to an OPML file containing feed URLs (multi-feed mode). "
                    "Failed feeds are skipped with a warning; remaining feeds "
                    "are still returned."
                ),
                "since_version": "0.3.0",
            },
            {
                "name": "--limit",
                "short": "-n",
                "type": "int",
                "required": False,
                "default": 8,
                "description": (
                    "Maximum entries to return. In OPML mode this limit applies "
                    "per-feed, not across all feeds."
                ),
            },
            {
                "name": "--output",
                "short": "-o",
                "type": "enum[text|json|table]",
                "required": False,
                "default": "text",
                "description": (
                    "Output mode. 'text' emits markdown (human-readable, LLM-friendly); "
                    "'json' emits an ACLI-compliant envelope "
                    "({ ok, command, version, duration_ms, data }); "
                    "'table' emits aligned plain-text columns (TITLE | DATE | URL). "
                    "Replaces the deprecated --format flag."
                ),
                "since_version": "0.6.0",
            },
            {
                "name": "--format",
                "short": "-f",
                "type": "enum[markdown|json]",
                "required": False,
                "default": "markdown",
                "deprecated": True,
                "deprecated_since": "0.6.0",
                "description": (
                    "Deprecated since v0.6.0. Use --output instead. "
                    "Still accepted for backward compatibility: "
                    "'markdown' maps to --output text, "
                    "'json' maps to legacy JSON output (no ACLI envelope)."
                ),
            },
            {
                "name": "--title",
                "type": "bool",
                "required": False,
                "default": False,
                "description": (
                    "Include the feed title as an H1 header. "
                    "Always on in OPML mode (overrides this flag)."
                ),
            },
            {
                "name": "--since",
                "type": "string",
                "required": False,
                "description": (
                    "Only include entries published on or after this date. "
                    "Accepts YYYY-MM-DD or Nd shorthand (e.g., '2d' = two days ago). "
                    "Entries with no published date are always included."
                ),
                "since_version": "0.2.0",
            },
            {
                "name": "--dedup",
                "type": "bool",
                "required": False,
                "default": False,
                "description": (
                    "Skip entries already seen in a previous run. "
                    "Seen entry URLs are tracked in ~/.feedsnap/seen.db "
                    "(SQLite, created automatically on first use)."
                ),
                "since_version": "0.4.0",
            },
            {
                "name": "--seen-db",
                "type": "path",
                "required": False,
                "description": (
                    "Custom SQLite database for tracking seen entries "
                    "(implies --dedup). Useful for per-project seen lists."
                ),
                "since_version": "0.4.0",
            },
        ],
        "subcommands": [],
        "examples": [
            {
                "intent": "Get a markdown digest of the 8 latest entries",
                "command": "feedsnap https://lobste.rs/rss",
            },
            {
                "intent": "Limit to 5 entries and output ACLI JSON envelope",
                "command": "feedsnap https://lobste.rs/rss --limit 5 --output json",
            },
            {
                "intent": "Tabular output (title, date, URL)",
                "command": "feedsnap https://lobste.rs/rss --output table",
            },
            {
                "intent": "Only show entries from the last 2 days",
                "command": "feedsnap https://lobste.rs/rss --since 2d",
            },
            {
                "intent": "Only show entries not seen in a previous run",
                "command": "feedsnap https://lobste.rs/rss --dedup",
            },
            {
                "intent": "Process multiple feeds from an OPML file (last day only)",
                "command": "feedsnap --opml feeds.opml --since 1d",
            },
        ],
    },
    {
        "name": "introspect",
        "description": (
            "Output the full command tree as JSON (ACLI v0.1.0 format). "
            "Agents should call this for initial capability mapping. "
            "Invoke as: feedsnap introspect"
        ),
        "arguments": [],
        "options": [],
        "subcommands": [],
        "examples": [
            {
                "intent": "Print the full ACLI command tree as JSON",
                "command": "feedsnap introspect",
            },
            {
                "intent": "Pretty-print the command tree",
                "command": "feedsnap introspect | python -m json.tool",
            },
        ],
    },
    {
        "name": "skill",
        "description": (
            "Output a SKILL.md file for agent bootstrapping (agentskills.io format). "
            "Redirect to a file to capture it. "
            "Invoke as: feedsnap skill"
        ),
        "arguments": [],
        "options": [],
        "subcommands": [],
        "examples": [
            {
                "intent": "Write SKILL.md to the current directory",
                "command": "feedsnap skill > SKILL.md",
            },
        ],
    },
]


def get_introspect_json(indent: int = 2) -> str:
    """Return the ACLI command tree as a JSON string.

    The version field is resolved at call time so it reflects the
    installed version rather than whatever was current at import.
    """
    from feedsnap import __version__

    tree = {
        "name": "feedsnap",
        "version": __version__,
        "acli_version": ACLI_VERSION,
        "commands": _COMMANDS,
    }
    return json.dumps(tree, indent=indent)


# ---------------------------------------------------------------------------
# SKILL.md template
# ---------------------------------------------------------------------------

_SKILL_TEMPLATE = """\
---
name: feedsnap
description: Invoke the `feedsnap` CLI to turn RSS/Atom feeds into clean markdown, JSON, or table digests.
when_to_use: Use when you need to read RSS or Atom feeds, fetch recent entries, filter by date, deduplicate seen items, combine multiple feeds via an OPML file, or get structured ACLI-envelope JSON output.
---

# feedsnap

> Auto-generated by `feedsnap skill`. Re-run to refresh after upgrades.

## Available commands

### `feedsnap <url>` — fetch a single feed

Turn any RSS 2.0 or Atom 1.0 feed URL into a clean digest.

**Arguments:**
- `url` · string · optional — RSS or Atom feed URL. Required unless `--opml` is used.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--opml PATH` | path | — | OPML subscriptions file for multi-feed mode. |
| `--limit N` / `-n N` | int | 8 | Max entries to return (per feed in OPML mode). |
| `--output MODE` / `-o MODE` | enum | text | Output mode: `text` (markdown), `json` (ACLI envelope), `table` (aligned columns). |
| `--title` | bool | false | Include feed title as H1 header. Always on in OPML mode. |
| `--since DATE` | string | — | Only entries on/after DATE. Accepts `YYYY-MM-DD` or `Nd` (e.g. `2d`). No-date entries always included. |
| `--dedup` | bool | false | Skip entries already seen in a previous run (tracked in `~/.feedsnap/seen.db`). |
| `--seen-db PATH` | path | — | Custom SQLite DB for seen-entry tracking (implies `--dedup`). |

**Note:** `--format` (accepted: `markdown`, `json`) is deprecated since v0.6.0. Use `--output` instead.
`--format markdown` → `--output text`. `--format json` → legacy JSON (no ACLI envelope).

**Output modes:**

- `--output text` (default) — human-readable markdown. Best for LLM context.
- `--output json` — ACLI envelope: `{ ok, command, version, duration_ms, data }`. Use for agent pipelines.
- `--output table` — aligned plain-text columns: TITLE | DATE | URL. Good for quick scanning.

**Examples:**

```bash
# Markdown digest (default)
feedsnap https://lobste.rs/rss

# ACLI JSON envelope
feedsnap https://simonwillison.net/atom/everything/ --output json

# Tabular output
feedsnap https://news.ycombinator.com/rss --output table --limit 10

# Only entries from the last 2 days, not yet seen
feedsnap https://lobste.rs/rss --since 2d --dedup

# Multiple feeds from an OPML file
feedsnap --opml feeds.opml --since 1d --output json
```

### `feedsnap introspect`

Output the full command tree as JSON (ACLI v0.1.0 format).
Use for initial capability mapping without reading documentation.

```bash
feedsnap introspect
feedsnap introspect | python -m json.tool
```

### `feedsnap skill`

Output this SKILL.md for agent bootstrapping.

```bash
feedsnap skill > SKILL.md
```

## Notes for agents

- Exit code `0` on success, `1` on error (feed fetch failure, bad arguments, empty OPML).
- Error messages go to **stderr**; feed output goes to **stdout**.
- `--output json` envelope has `ok: true` on success. On error, the process exits 1 before printing.
- `--dedup` is idempotent: repeated calls with the same URL are safe.
- `--opml` mode applies `--limit` per-feed (not across all feeds combined).
"""


def get_skill_md() -> str:
    """Return the SKILL.md bootstrap content for agentskills.io format."""
    return _SKILL_TEMPLATE
