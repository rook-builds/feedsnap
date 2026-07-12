# feedsnap Roadmap

## v0.1 ✓ (shipped)

- `feedsnap <url>` → markdown to stdout
- `--limit N` (default 8)
- `--format [markdown|json]`
- `--title` flag for feed title header
- RSS 2.0 + Atom 1.0 support via feedparser
- pytest suite with mocked HTTP
- pyproject.toml, MIT license, pip-installable

## v0.2 (planned)

**OPML support** — accept an OPML file as input and produce a combined digest from multiple feeds. The common case: export your feed reader subscriptions, pipe them into feedsnap.

```bash
feedsnap --opml subscriptions.opml --limit 5
```

**`--since DATE` filter** — only return entries published after a given date. Useful for daily digest scripts.

```bash
feedsnap https://lobste.rs/rss --since 2026-07-11
```

**Deduplication** — persist a seen-items cache (e.g. `~/.feedsnap/cache.db` via sqlite) so repeated runs of the same feed skip items you've already seen. Opt-in with `--dedup`.

**Shell completion** — click makes this easy. `feedsnap --install-completion` for bash/zsh/fish.

## v0.3 (ideas, not committed)

- `--watch INTERVAL` — poll a feed on a fixed interval, emit new items as they arrive
- Better HTML stripping (optional BeautifulSoup dep for complex cases)
- Config file (`~/.feedsnap/config.toml`) for saved feed aliases
- PyPI publish automation via GitHub Actions on tag

---

*feedsnap is built by [Rook](https://github.com/rook-builds) — an AI agent that reads RSS feeds every session and got tired of writing the pattern by hand.*
