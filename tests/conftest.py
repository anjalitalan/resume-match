from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def no_real_sleep():
    """Prevents call_with_retry's backoff from actually sleeping during tests.

    Applies to every test automatically (autouse) so retryable-error tests elsewhere
    in the suite (e.g. extraction tests using a 500/timeout side effect) stay fast.
    Tests that want to assert on sleep behavior can still request this fixture by
    name to get the underlying mock.
    """
    with patch("resume_match.gemini_client.time.sleep") as mock_sleep:
        yield mock_sleep
