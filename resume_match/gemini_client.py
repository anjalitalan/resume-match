import time
from typing import Callable, TypeVar

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

DEFAULT_MODEL = "gemini-3.6-flash"

_client: genai.Client | None = None

# Bounded retry for transient failures only (rate limits, server unavailability).
# Permanent/client errors (bad API key, malformed request, etc.) are never retried.
MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0
BACKOFF_MULTIPLIER = 2.0
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

T = TypeVar("T")


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def is_retryable_error(error: Exception) -> bool:
    """Whether an error is a transient failure worth retrying.

    Rate limits (429) and server-side unavailability (500/502/503/504) are retried.
    Everything else — including auth failures (401/403), bad requests (400), and
    not-found (404) — is a permanent/client error a retry cannot fix, so it is not.
    """
    if isinstance(error, APIError):
        return error.code in RETRYABLE_STATUS_CODES
    return isinstance(error, (httpx.TimeoutException, httpx.ConnectError))


def call_with_retry(func: Callable[[], T]) -> T:
    """Calls func() with bounded exponential-backoff retry on transient failures.

    Non-transient errors are raised immediately on the first attempt, identical to
    calling func() directly. After MAX_ATTEMPTS total attempts, the last error is
    raised as-is — callers keep handling the same exception types they always did.
    """
    delay = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return func()
        except Exception as error:
            if attempt == MAX_ATTEMPTS or not is_retryable_error(error):
                raise
            time.sleep(delay)
            delay *= BACKOFF_MULTIPLIER
