from __future__ import annotations

import re
import sys
from datetime import date, timedelta

import click

from .fetcher import fetch_feed, parse_opml
from .formatter import to_json, to_json_multi, to_markdown


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
def main(
    url: str | None,
    opml_file: str | None,
    limit: int,
    fmt: str,
    title: bool,
    since: str | None,
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

    # ── Single-feed mode ─────────────────────────────────────────────────────
    if url:
        try:
            feed = fetch_feed(url, limit=limit, since=since_date)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

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
