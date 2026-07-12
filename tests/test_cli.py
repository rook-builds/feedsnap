import json
from unittest.mock import patch

from click.testing import CliRunner

from feedsnap.cli import main
from feedsnap.fetcher import Feed, FeedEntry

MOCK_FEED = Feed(
    title="Mock Feed",
    url="https://example.com/feed",
    entries=[
        FeedEntry(
            title="Mock Entry",
            url="https://example.com/mock",
            published="2026-07-12",
            summary="A mock summary for testing.",
        )
    ],
)


def test_cli_default_markdown():
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED):
        result = runner.invoke(main, ["https://example.com/feed"])
    assert result.exit_code == 0
    assert "### Mock Entry" in result.output
    assert "2026-07-12" in result.output


def test_cli_json_format():
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED):
        result = runner.invoke(main, ["https://example.com/feed", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["title"] == "Mock Feed"
    assert len(data["entries"]) == 1


def test_cli_with_title():
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED):
        result = runner.invoke(main, ["https://example.com/feed", "--title"])
    assert result.exit_code == 0
    assert "# Mock Feed" in result.output


def test_cli_limit_passed_through():
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED) as mock_fetch:
        runner.invoke(main, ["https://example.com/feed", "--limit", "3"])
    mock_fetch.assert_called_once_with("https://example.com/feed", limit=3, since=None)


def test_cli_error_exits_nonzero():
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", side_effect=ValueError("bad feed")):
        result = runner.invoke(main, ["https://example.com/bad"])
    assert result.exit_code == 1


def test_cli_since_passed_through():
    """--since DATE is parsed and passed to fetch_feed as a date object."""
    from datetime import date
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED) as mock_fetch:
        runner.invoke(main, ["https://example.com/feed", "--since", "2026-07-11"])
    mock_fetch.assert_called_once_with(
        "https://example.com/feed", limit=8, since=date(2026, 7, 11)
    )


def test_cli_since_relative_passed_through():
    """--since Nd is converted to an absolute date before passing to fetch_feed."""
    from datetime import date, timedelta
    runner = CliRunner()
    today = date.today()
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED) as mock_fetch:
        runner.invoke(main, ["https://example.com/feed", "--since", "3d"])
    mock_fetch.assert_called_once_with(
        "https://example.com/feed", limit=8, since=today - timedelta(days=3)
    )


def test_cli_since_invalid_exits_nonzero():
    """--since with an unparseable value exits 1 with an error message."""
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED):
        result = runner.invoke(main, ["https://example.com/feed", "--since", "notadate"])
    assert result.exit_code == 1
