from __future__ import annotations

import re
import sys
from datetime import date, timedelta

import click

from .fetcher import fetch_feed
from .formatter import to_json, to_markdown


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
@click.argument("url")
@click.option(
    "--limit", "-n",
    default=8,
    show_default=True,
    help="Max entries to return.",
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
    help="Include feed title as H1 header.",
)
@click.option(
    "--since",
    default=None,
    metavar="DATE",
    help="Only include entries published on or after DATE. "
         "Accepts YYYY-MM-DD or Nd (e.g., 2d for 2 days ago).",
)
def main(url: str, limit: int, fmt: str, title: bool, since: str | None) -> None:
    """Turn an RSS or Atom feed into a clean digest.

    URL is the feed address (RSS 2.0 or Atom 1.0).
    """
    since_date = None
    if since is not None:
        try:
            since_date = _parse_since(since)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    try:
        feed = fetch_feed(url, limit=limit, since=since_date)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if fmt == "json":
        click.echo(to_json(feed), nl=False)
    else:
        click.echo(to_markdown(feed, show_title=title), nl=False)
