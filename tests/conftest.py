from pathlib import Path

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


@pytest.fixture(autouse=True)
def clean_default_seen_db():
    """Wipe the default seen-entries DB before and after every test.

    Tests that use ``--dedup`` (without ``--seen-db``) write to
    ~/.feedsnap/seen.db.  Without this fixture they bleed state into
    each other and fail non-deterministically depending on test order.
    Tests that use ``--seen-db tmp_path/...`` are unaffected — they
    write to a different path and this fixture only touches the default.
    """
    default = Path.home() / ".feedsnap" / "seen.db"
    default.unlink(missing_ok=True)
    yield
    default.unlink(missing_ok=True)
