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
                "name": "--format",
                "short": "-f",
                "type": "enum[markdown|json]",
                "required": False,
                "default": "markdown",
                "description": (
                    "Output format. 'markdown' for human reading or LLM context; "
                    "'json' for piping to jq or other tools."
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
                "intent": "Limit to 5 entries and output JSON",
                "command": "feedsnap https://lobste.rs/rss --limit 5 --format json",
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
description: Invoke the `feedsnap` CLI to turn RSS/Atom feeds into clean markdown or JSON digests.
when_to_use: Use when you need to read RSS or Atom feeds, fetch recent entries, filter by date, deduplicate seen items, or combine multiple feeds via an OPML file.
---

# feedsnap

> Auto-generated by `feedsnap skill`. Re-run to refresh after upgrades.

## Available commands

### `feedsnap <url>` — fetch a single feed

Turn any RSS 2.0 or Atom 1.0 feed URL into a clean markdown digest.

**Arguments:**
- `url` · string · optional — RSS or Atom feed URL. Required unless `--opml` is used.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--opml PATH` | path | — | OPML subscriptions file for multi-feed mode. |
| `--limit N` / `-n N` | int | 8 | Max entries to return (per feed in OPML mode). |
| `--format [markdown\\|json]` / `-f` | enum | markdown | Output format. |
| `--title` | bool | false | Include feed title as H1 header. Always on in OPML mode. |
| `--since DATE` | string | — | Only entries on/after DATE. Accepts `YYYY-MM-DD` or `Nd` (e.g. `2d`). No-date entries are always included. |
| `--dedup` | bool | false | Skip entries already seen in a previous run. Tracks URLs in `~/.feedsnap/seen.db`. |
| `--seen-db PATH` | path | — | Custom SQLite DB for seen-entry tracking (implies `--dedup`). |

**Examples:**
```bash
# Markdown digest of the 8 latest entries
feedsnap https://lobste.rs/rss

# JSON output, 5 entries
feedsnap https://lobste.rs/rss --limit 5 --format json

# Only entries from the last 2 days
feedsnap https://lobste.rs/rss --since 2d

# Only new entries since last run (deduplication)
feedsnap https://lobste.rs/rss --dedup

# Multiple feeds from OPML, last day only
feedsnap --opml feeds.opml --since 1d
```

**See also:** `feedsnap introspect`, `feedsnap skill`

---

### `feedsnap introspect` — machine-readable command tree

Output the full capability tree as JSON (ACLI v{acli_version} format). Use this for initial agent capability mapping.

**Examples:**
```bash
feedsnap introspect
feedsnap introspect | python -m json.tool
```

**See also:** `feedsnap skill`

---

### `feedsnap skill` — generate this file

Output this SKILL.md to stdout. Redirect to a file to capture it.

**Examples:**
```bash
feedsnap skill > SKILL.md
```

---

## Output format

| Flag | Format | Best for |
|------|--------|----------|
| (default) | Markdown | Human reading, LLM context |
| `--format json` | JSON | Piping to `jq`, scripting |

**JSON schema (single feed):**
```json
{{
  "title": "Feed title",
  "url": "https://example.com/feed",
  "entries": [
    {{
      "title": "Entry title",
      "url": "https://example.com/entry",
      "published": "2026-07-13",
      "summary": "Truncated summary text (≤300 chars)..."
    }}
  ]
}}
```

**JSON schema (OPML multi-feed, `--format json`):**
```json
{{
  "feeds": [ /* array of single-feed objects above */ ]
}}
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (network failure, invalid URL, bad OPML, no feeds fetched) |

## Further discovery

```bash
feedsnap --help                        # Human-readable usage
feedsnap introspect                    # Machine-readable command tree (JSON)
feedsnap introspect | python -m json.tool  # Pretty-printed
```

Built by [Rook](https://github.com/rook-builds) — ACLI spec v{acli_version}
"""


def get_skill_md() -> str:
    """Return the SKILL.md content for agent bootstrapping."""
    return _SKILL_TEMPLATE.format(acli_version=ACLI_VERSION)
