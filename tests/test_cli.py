import json
from unittest.mock import MagicMock, patch

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


MOCK_FEED_2 = Feed(
    title="Mock Feed 2",
    url="https://example.com/feed2",
    entries=[
        FeedEntry(
            title="Second Feed Entry",
            url="https://example.com/mock2",
            published="2026-07-12",
            summary="Second feed summary.",
        )
    ],
)

SAMPLE_OPML = """\
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>Test</title></head>
  <body>
    <outline text="Feed 1" type="rss" xmlUrl="https://example.com/feed1" />
    <outline text="Feed 2" type="rss" xmlUrl="https://example.com/feed2" />
  </body>
</opml>
"""


def test_cli_opml_markdown(tmp_path):
    opml_file = tmp_path / "feeds.opml"
    opml_file.write_text(SAMPLE_OPML)
    runner = CliRunner()
    with patch("feedsnap.cli.parse_opml", return_value=[
        ("Feed 1", "https://example.com/feed1"),
        ("Feed 2", "https://example.com/feed2"),
    ]), patch("feedsnap.cli.fetch_feed", side_effect=[MOCK_FEED, MOCK_FEED_2]):
        result = runner.invoke(main, ["--opml", str(opml_file)])
    assert result.exit_code == 0
    assert "# Mock Feed" in result.output
    assert "# Mock Feed 2" in result.output
    assert "### Mock Entry" in result.output
    assert "### Second Feed Entry" in result.output


def test_cli_opml_json(tmp_path):
    opml_file = tmp_path / "feeds.opml"
    opml_file.write_text(SAMPLE_OPML)
    runner = CliRunner()
    with patch("feedsnap.cli.parse_opml", return_value=[
        ("Feed 1", "https://example.com/feed1"),
    ]), patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED):
        result = runner.invoke(main, ["--opml", str(opml_file), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "feeds" in data
    assert len(data["feeds"]) == 1
    assert data["feeds"][0]["title"] == "Mock Feed"


def test_cli_url_and_opml_mutually_exclusive(tmp_path):
    opml_file = tmp_path / "feeds.opml"
    opml_file.write_text(SAMPLE_OPML)
    runner = CliRunner()
    result = runner.invoke(main, ["https://example.com/feed", "--opml", str(opml_file)])
    assert result.exit_code == 1


def test_cli_no_url_no_opml_error():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 1


def test_cli_opml_skips_failed_feeds(tmp_path):
    opml_file = tmp_path / "feeds.opml"
    opml_file.write_text(SAMPLE_OPML)
    runner = CliRunner()
    with patch("feedsnap.cli.parse_opml", return_value=[
        ("Feed 1", "https://example.com/feed1"),
        ("Feed 2", "https://example.com/feed2"),
    ]), patch("feedsnap.cli.fetch_feed", side_effect=[
        ValueError("network error"),
        MOCK_FEED,
    ]):
        result = runner.invoke(main, ["--opml", str(opml_file)])
    assert result.exit_code == 0
    assert "Warning" in result.output  # stderr is mixed in CliRunner by default
    assert "Mock Feed" in result.output


def test_cli_opml_all_feeds_fail(tmp_path):
    opml_file = tmp_path / "feeds.opml"
    opml_file.write_text(SAMPLE_OPML)
    runner = CliRunner()
    with patch("feedsnap.cli.parse_opml", return_value=[
        ("Feed 1", "https://example.com/feed1"),
    ]), patch("feedsnap.cli.fetch_feed", side_effect=ValueError("all fail")):
        result = runner.invoke(main, ["--opml", str(opml_file)])
    assert result.exit_code == 1


# ── Dedup tests (--dedup / --seen-db) ────────────────────────────────────────

MOCK_FEED_FOR_DEDUP = Feed(
    title="Dedup Feed",
    url="https://example.com/feed",
    entries=[
        FeedEntry(
            title="Entry One",
            url="https://example.com/entry-1",
            published="2026-07-13",
            summary="First entry.",
        ),
        FeedEntry(
            title="Entry Two",
            url="https://example.com/entry-2",
            published="2026-07-13",
            summary="Second entry.",
        ),
    ],
)


def test_cli_dedup_shows_all_entries_on_first_run(tmp_path):
    """First run with --seen-db should show all entries (nothing seen yet)."""
    db = tmp_path / "seen.db"
    runner = CliRunner()

    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP):
        result = runner.invoke(
            main, ["https://example.com/feed", "--seen-db", str(db)]
        )
    assert result.exit_code == 0
    assert "Entry One" in result.output
    assert "Entry Two" in result.output


def test_cli_dedup_filters_seen_on_second_run(tmp_path):
    """Second run with --seen-db should skip entries seen in the first run."""
    db = tmp_path / "seen.db"
    runner = CliRunner()

    # First run — marks both entries as seen
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP):
        runner.invoke(main, ["https://example.com/feed", "--seen-db", str(db)])

    # Second run — feed still returns the same entries, but dedup filters them
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP):
        result2 = runner.invoke(
            main, ["https://example.com/feed", "--seen-db", str(db)]
        )
    assert result2.exit_code == 0
    assert "Entry One" not in result2.output
    assert "Entry Two" not in result2.output


def test_cli_dedup_flag_uses_default_db_path(tmp_path):
    """--dedup flag should work; monkeypatch default_db_path for isolation."""
    db = tmp_path / "seen.db"
    runner = CliRunner()

    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP), \
         patch("feedsnap.cli.default_db_path", return_value=db):
        result = runner.invoke(main, ["https://example.com/feed", "--dedup"])
    assert result.exit_code == 0
    assert "Entry One" in result.output


def test_cli_seen_db_implies_dedup(tmp_path):
    """--seen-db alone (without --dedup) should enable deduplication."""
    db = tmp_path / "seen.db"
    runner = CliRunner()

    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP):
        runner.invoke(main, ["https://example.com/feed", "--seen-db", str(db)])

    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP):
        result2 = runner.invoke(
            main, ["https://example.com/feed", "--seen-db", str(db)]
        )
    assert result2.exit_code == 0
    assert "Entry One" not in result2.output
    assert "Entry Two" not in result2.output


def test_cli_no_dedup_without_flag():
    """Without --dedup or --seen-db, entries should always be shown."""
    runner = CliRunner()

    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP):
        result1 = runner.invoke(main, ["https://example.com/feed"])
    assert "Entry One" in result1.output

    # Second call — same feed, no DB, same entries should appear again
    with patch("feedsnap.cli.fetch_feed", return_value=MOCK_FEED_FOR_DEDUP):
        result2 = runner.invoke(main, ["https://example.com/feed"])
    assert "Entry One" in result2.output
