#!/usr/bin/env bash
# feedsnap — runnable example invocations
# ACLI .cli/examples/snap.sh · v0.5.0

set -euo pipefail

FEED="https://lobste.rs/rss"

echo "=== Basic markdown digest (8 entries) ==="
feedsnap "$FEED"

echo ""
echo "=== JSON output, 5 entries ==="
feedsnap "$FEED" --limit 5 --format json

echo ""
echo "=== Only entries from the last 2 days ==="
feedsnap "$FEED" --since 2d

echo ""
echo "=== With feed title header ==="
feedsnap "$FEED" --title --limit 3

echo ""
echo "=== Deduplicated (only new since last run) ==="
feedsnap "$FEED" --dedup

echo ""
echo "=== Custom dedup DB path ==="
feedsnap "$FEED" --seen-db /tmp/feedsnap-example.db

echo ""
echo "=== ACLI introspect (command tree as JSON) ==="
feedsnap introspect | python -m json.tool

echo ""
echo "=== ACLI skill (SKILL.md for agent bootstrapping) ==="
feedsnap skill
