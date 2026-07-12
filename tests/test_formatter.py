import json

from feedsnap.formatter import to_json, to_markdown


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
