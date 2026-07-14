import json

from feedsnap.formatter import (
    to_envelope,
    to_envelope_multi,
    to_json,
    to_markdown,
    to_table,
)


def test_markdown_no_title(sample_feed):
    result = to_markdown(sample_feed)
    assert "### First Post" in result
    assert "### Second Post" in result
    assert "# Test Feed" not in result
    assert "2026-07-11" in result
    assert "<https://example.com/1>" in result


def test_markdown_with_title(sample_feed):
    result = to_markdown(sample_feed, show_title=True)
    assert result.startswith("# Test Feed\n")


def test_markdown_ends_with_newline(sample_feed):
    assert to_markdown(sample_feed).endswith("\n")


def test_json_structure(sample_feed):
    result = to_json(sample_feed)
    data = json.loads(result)
    assert data["title"] == "Test Feed"
    assert data["url"] == "https://example.com/feed"
    assert len(data["entries"]) == 2
    assert data["entries"][0]["title"] == "First Post"
    assert data["entries"][0]["published"] == "2026-07-11"


def test_json_ends_with_newline(sample_feed):
    assert to_json(sample_feed).endswith("\n")


def test_markdown_summary_present(sample_feed):
    result = to_markdown(sample_feed)
    assert "This is the first entry summary." in result


# ---------------------------------------------------------------------------
# Table output tests
# ---------------------------------------------------------------------------


def test_table_has_header_row(sample_feed):
    result = to_table(sample_feed)
    assert "TITLE" in result
    assert "DATE" in result
    assert "URL" in result


def test_table_has_separator_row(sample_feed):
    result = to_table(sample_feed)
    lines = result.splitlines()
    # Second line should be the separator (all ─ characters and spaces)
    sep_line = lines[1]
    assert "─" in sep_line


def test_table_has_data_rows(sample_feed):
    result = to_table(sample_feed)
    assert "First Post" in result
    assert "Second Post" in result
    assert "https://example.com/1" in result


def test_table_ends_with_newline(sample_feed):
    assert to_table(sample_feed).endswith("\n")


def test_table_with_show_title(sample_feed):
    result = to_table(sample_feed, show_title=True)
    assert result.startswith("# Test Feed\n")


def test_table_truncates_long_title(sample_feed):
    """A title longer than 50 chars should be truncated with '…'."""
    from feedsnap.fetcher import Feed, FeedEntry

    long_title = "A" * 60
    feed = Feed(
        title="Feed",
        url="https://example.com",
        entries=[
            FeedEntry(
                title=long_title,
                url="https://example.com/long",
                published="2026-07-14",
                summary="",
            )
        ],
    )
    result = to_table(feed)
    # The title column should be truncated — 49 chars of "A" + "…"
    assert "…" in result
    assert "A" * 60 not in result


# ---------------------------------------------------------------------------
# ACLI envelope output tests
# ---------------------------------------------------------------------------


def test_envelope_is_valid_json(sample_feed):
    result = to_envelope(sample_feed, duration_ms=42)
    data = json.loads(result)  # should not raise
    assert isinstance(data, dict)


def test_envelope_ok_true(sample_feed):
    result = to_envelope(sample_feed, duration_ms=42)
    data = json.loads(result)
    assert data["ok"] is True


def test_envelope_command_is_snap(sample_feed):
    result = to_envelope(sample_feed, duration_ms=42)
    data = json.loads(result)
    assert data["command"] == "snap"


def test_envelope_has_version(sample_feed):
    result = to_envelope(sample_feed, duration_ms=42)
    data = json.loads(result)
    assert "version" in data
    assert isinstance(data["version"], str)


def test_envelope_duration_ms(sample_feed):
    result = to_envelope(sample_feed, duration_ms=99)
    data = json.loads(result)
    assert data["duration_ms"] == 99


def test_envelope_data_contains_feed(sample_feed):
    result = to_envelope(sample_feed, duration_ms=0)
    data = json.loads(result)
    assert "data" in data
    assert data["data"]["title"] == "Test Feed"
    assert data["data"]["url"] == "https://example.com/feed"
    assert len(data["data"]["entries"]) == 2


def test_envelope_ends_with_newline(sample_feed):
    assert to_envelope(sample_feed, duration_ms=0).endswith("\n")


def test_envelope_multi_structure(sample_feed):
    result = to_envelope_multi([sample_feed, sample_feed], duration_ms=77)
    data = json.loads(result)
    assert data["ok"] is True
    assert data["command"] == "snap"
    assert data["duration_ms"] == 77
    assert "data" in data
    assert "feeds" in data["data"]
    assert len(data["data"]["feeds"]) == 2


def test_envelope_multi_ends_with_newline(sample_feed):
    assert to_envelope_multi([sample_feed], duration_ms=0).endswith("\n")
