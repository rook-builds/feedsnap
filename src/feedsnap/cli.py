from __future__ import annotations

import re
import sys
from datetime import date, timedelta
from pathlib import Path

import click

from .fetcher import Feed, fetch_feed, parse_opml
from .formatter import to_json, to_json_multi, to_markdown
from .seen_db import default_db_path, get_seen, mark_seen


def _parse_since(value: str) -> date:
    """Parse --since value into a date. Accepts YYYY-MM-DD or Nd (e.g., 2d)."""
    m = re.fullmatch(r"(\d+)d", value)
    if m:
        return date.today() - timedelta(days=int(m.group(1)))
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"Invalid --since value '{value}'. "
            "Use YYYY-MM-DD (e.g., 2026-07-11) or Nd (e.g., 2d for 2 days ago)."
        )


def _resolve_db_path(dedup: bool, seen_db: str | None) -> Path | None:
    """Return the SQLite DB path to use for dedup, or None if dedup is off.

    Priority: explicit ``--seen-db PATH`` > ``--dedup`` (default path) > None.
    Either flag alone is sufficient to enable deduplication.
    """
    if seen_db is not None:
        return Path(seen_db)
    if dedup:
        return default_db_path()
    return None


def _apply_dedup(db_path: Path, feed_url: str, feed: Feed) -> Feed:
    """Return a new Feed containing only entries not yet seen, then mark
    those entries as seen in the database.

    Returns a *new* Feed object — the original is not mutated. This
    makes the function safe to call with shared/mock objects in tests.
    """
    seen_urls = get_seen(db_path, feed_url)
    new_entries = [e for e in feed.entries if e.url not in seen_urls]
    mark_seen(db_path, feed_url, [e.url for e in new_entries])
    return Feed(title=feed.title, url=feed.url, entries=new_entries)


@click.command()
@click.argument("url", required=False, default=None)
@click.option(
    "--opml", "opml_file",
    type=click.Path(exists=True, readable=True),
    default=None,
    help="Path to an OPML file containing feed URLs.",
)
@click.option(
    "--limit", "-n",
    default=8,
    show_default=True,
    help="Max entries to return (per feed in OPML mode).",
)
@click.option(
    "--format", "-f", "fmt",
    default="markdown",
    show_default=True,
    type=click.Choice(["markdown", "json"]),
    help="Output format.",
)
@click.option(
    "--title",
    is_flag=True,
    default=False,
    help="Include feed title as H1 header (always on in OPML mode).",
)
@click.option(
    "--since",
    default=None,
    metavar="DATE",
    help="Only include entries published on or after DATE. "
         "Accepts YYYY-MM-DD or Nd (e.g., 2d for 2 days ago).",
)
@click.option(
    "--dedup",
    is_flag=True,
    default=False,
    help=(
        "Skip entries already seen in a previous run. "
        "Seen entry URLs are tracked in ~/.feedsnap/seen.db. "
        "Use --seen-db to specify a custom database path."
    ),
)
@click.option(
    "--seen-db",
    "seen_db",
    default=None,
    type=click.Path(dir_okay=False),
    metavar="PATH",
    help=(
        "Path to a custom SQLite database for tracking seen entries "
        "(implies --dedup). Useful for keeping separate seen-lists per "
        "project or script."
    ),
)
def main(
    url: str | None,
    opml_file: str | None,
    limit: int,
    fmt: str,
    title: bool,
    since: str | None,
    dedup: bool,
    seen_db: str | None,
) -> None:
    """Turn an RSS or Atom feed into a clean digest.

    URL is the feed address (RSS 2.0 or Atom 1.0), or use --opml to
    supply an OPML file with multiple feed URLs.
    """
    # Validate: exactly one of URL or --opml must be provided
    if url and opml_file:
        click.echo("Error: Provide either a URL or --opml, not both.", err=True)
        sys.exit(1)
    if not url and not opml_file:
        click.echo(
            "Error: Provide a feed URL or use --opml <file>.\n\n"
            "Try 'feedsnap --help' for usage.",
            err=True,
        )
        sys.exit(1)

    # Parse --since date
    since_date = None
    if since is not None:
        try:
            since_date = _parse_since(since)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    # Resolve dedup DB path (None = dedup disabled)
    db_path = _resolve_db_path(dedup, seen_db)

    # ── Single-feed mode ─────────────────────────────────────────────────────
    if url:
        try:
            feed = fetch_feed(url, limit=limit, since=since_date)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        if db_path is not None:
            feed = _apply_dedup(db_path, url, feed)

        if fmt == "json":
            click.echo(to_json(feed), nl=False)
        else:
            click.echo(to_markdown(feed, show_title=title), nl=False)
        return

    # ── OPML multi-feed mode ─────────────────────────────────────────────────
    import xml.etree.ElementTree as ET

    try:
        feed_specs = parse_opml(opml_file)
    except ET.ParseError as e:
        click.echo(f"Error: Invalid OPML file: {e}", err=True)
        sys.exit(1)
    except OSError as e:
        click.echo(f"Error: Could not read OPML file: {e}", err=True)
        sys.exit(1)

    if not feed_specs:
        click.echo("Error: No feed URLs found in OPML file.", err=True)
        sys.exit(1)

    feeds = []
    for _feed_title, feed_url in feed_specs:
        try:
            feed = fetch_feed(feed_url, limit=limit, since=since_date)

            if db_path is not None:
                feed = _apply_dedup(db_path, feed_url, feed)

            feeds.append(feed)
        except Exception as e:
            click.echo(f"Warning: Could not fetch {feed_url}: {e}", err=True)
            # Graceful degradation: continue with remaining feeds

    if not feeds:
        click.echo("Error: No feeds could be fetched.", err=True)
        sys.exit(1)

    if fmt == "json":
        click.echo(to_json_multi(feeds), nl=False)
    else:
        # In OPML mode, always show title headers (ignore --title flag)
        parts = [to_markdown(feed, show_title=True) for feed in feeds]
        click.echo("\n".join(parts), nl=False)
