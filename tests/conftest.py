import pytest

from feedsnap.fetcher import Feed, FeedEntry


@pytest.fixture
def sample_feed() -> Feed:
    return Feed(
        title="Test Feed",
        url="https://example.com/feed",
        entries=[
            FeedEntry(
                title="First Post",
                url="https://example.com/1",
                published="2026-07-11",
                summary="This is the first entry summary.",
            ),
            FeedEntry(
                title="Second Post",
                url="https://example.com/2",
                published="2026-07-10",
                summary="This is the second entry summary.",
            ),
        ],
    )
