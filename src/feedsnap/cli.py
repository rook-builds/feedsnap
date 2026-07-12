from __future__ import annotations

import sys

import click

from .fetcher import fetch_feed
from .formatter import to_json, to_markdown


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
def main(url: str, limit: int, fmt: str, title: bool) -> None:
    """Turn an RSS or Atom feed into a clean digest.

    URL is the feed address (RSS 2.0 or Atom 1.0).
    """
    try:
        feed = fetch_feed(url, limit=limit)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if fmt == "json":
        click.echo(to_json(feed), nl=False)
    else:
        click.echo(to_markdown(feed, show_title=title), nl=False)
