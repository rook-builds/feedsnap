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
    mock_fetch.assert_called_once_with("https://example.com/feed", limit=3)


def test_cli_error_exits_nonzero():
    runner = CliRunner()
    with patch("feedsnap.cli.fetch_feed", side_effect=ValueError("bad feed")):
        result = runner.invoke(main, ["https://example.com/bad"])
    assert result.exit_code == 1
