from unittest.mock import call

import httpx
import pytest
from google.genai.errors import APIError

from resume_match.gemini_client import (
    BACKOFF_MULTIPLIER,
    INITIAL_BACKOFF_SECONDS,
    MAX_ATTEMPTS,
    call_with_retry,
    is_retryable_error,
)


def _api_error(code: int) -> APIError:
    return APIError(code, {"error": {"message": "boom"}}, None)


@pytest.mark.parametrize("code", [429, 500, 502, 503, 504])
def test_is_retryable_error_true_for_transient_status_codes(code):
    assert is_retryable_error(_api_error(code)) is True


@pytest.mark.parametrize("code", [400, 401, 403, 404])
def test_is_retryable_error_false_for_permanent_status_codes(code):
    assert is_retryable_error(_api_error(code)) is False


def test_is_retryable_error_true_for_network_timeout_and_connect_error():
    assert is_retryable_error(httpx.TimeoutException("timed out")) is True
    assert is_retryable_error(httpx.ConnectError("no connection")) is True


def test_is_retryable_error_false_for_unrelated_exception():
    assert is_retryable_error(ValueError("not a gemini error")) is False


def test_call_with_retry_returns_result_immediately_when_func_succeeds(no_real_sleep):
    result = call_with_retry(lambda: "ok")

    assert result == "ok"
    no_real_sleep.assert_not_called()


def test_call_with_retry_retries_transient_error_then_succeeds(no_real_sleep):
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise _api_error(503)
        return "recovered"

    result = call_with_retry(flaky)

    assert result == "recovered"
    assert attempts["count"] == 3
    assert no_real_sleep.call_args_list == [
        call(INITIAL_BACKOFF_SECONDS),
        call(INITIAL_BACKOFF_SECONDS * BACKOFF_MULTIPLIER),
    ]


def test_call_with_retry_gives_up_after_max_attempts(no_real_sleep):
    attempts = {"count": 0}

    def always_fails():
        attempts["count"] += 1
        raise _api_error(503)

    with pytest.raises(APIError):
        call_with_retry(always_fails)

    assert attempts["count"] == MAX_ATTEMPTS
    assert no_real_sleep.call_count == MAX_ATTEMPTS - 1


def test_call_with_retry_does_not_retry_permanent_error(no_real_sleep):
    attempts = {"count": 0}

    def bad_api_key():
        attempts["count"] += 1
        raise _api_error(401)

    with pytest.raises(APIError):
        call_with_retry(bad_api_key)

    assert attempts["count"] == 1
    no_real_sleep.assert_not_called()


def test_call_with_retry_does_not_retry_unrelated_bug(no_real_sleep):
    attempts = {"count": 0}

    def buggy():
        attempts["count"] += 1
        raise ValueError("programming error, not a Gemini failure")

    with pytest.raises(ValueError):
        call_with_retry(buggy)

    assert attempts["count"] == 1
    no_real_sleep.assert_not_called()
