"""
Rate limiting module for GitHub API requests with exponential backoff.
"""

import threading
import time
from typing import Any, Callable


class RateLimiter:
    """
    Thread-safe rate limiter using token bucket algorithm with exponential backoff.

    Attributes:
        requests_per_second (float): Maximum number of requests allowed per second
        enabled (bool): Whether rate limiting is enabled
        backoff_factor (float): Multiplier for exponential backoff (e.g., 2.0 means double wait time)
        max_retries (int): Maximum number of retry attempts on rate limit errors
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        requests_per_second: float = 2.0,
        enabled: bool = True,
        backoff_factor: float = 2.0,
        max_retries: int = 3,
    ):
        """
        Initialize the rate limiter.

        Args:
            requests_per_second: Maximum requests per second (default: 2.0)
            enabled: Whether rate limiting is enabled (default: True)
            backoff_factor: Exponential backoff multiplier (default: 2.0)
            max_retries: Maximum retry attempts (default: 3)
        """
        self.requests_per_second = requests_per_second
        self.enabled = enabled
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries

        # Token bucket algorithm state
        self._tokens = requests_per_second
        self._max_tokens = requests_per_second
        self._last_update = time.time()
        self._lock = threading.Lock()

        # Minimum interval between requests
        self._min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0

    def wait_for_token(self) -> None:
        """
        Wait until a token is available in the bucket (rate limit allows next request).
        This implements the token bucket algorithm for smooth rate limiting.
        """
        if not self.enabled:
            return

        with self._lock:
            now = time.time()
            time_passed = now - self._last_update

            # Refill tokens based on time passed
            self._tokens = min(
                self._max_tokens, self._tokens + time_passed * self.requests_per_second
            )

            # Wait if no tokens available
            if self._tokens < 1.0:
                sleep_time = (1.0 - self._tokens) / self.requests_per_second
                time.sleep(sleep_time)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0

            self._last_update = time.time()

    def execute_with_backoff(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute a function with rate limiting and exponential backoff on errors.

        Args:
            func: Function to execute
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            The return value of func

        Raises:
            Exception: Re-raises the last exception if max_retries is exceeded
        """
        if not self.enabled:
            return func(*args, **kwargs)

        last_exception = None
        initial_wait = 1.0  # Initial wait time in seconds

        for attempt in range(self.max_retries + 1):
            try:
                # Wait for rate limit token before making request
                self.wait_for_token()

                # Execute the function
                result = func(*args, **kwargs)

                # Check if response indicates rate limiting (if it's a requests.Response)
                if hasattr(result, "status_code") and result.status_code == 429:
                    # Rate limit hit, trigger backoff
                    raise RateLimitExceeded("GitHub API rate limit exceeded (429)")

                return result

            except RateLimitExceeded as e:
                last_exception = e

                if attempt < self.max_retries:
                    # Calculate exponential backoff wait time
                    wait_time = initial_wait * (self.backoff_factor**attempt)
                    print(
                        f"Rate limit exceeded, waiting {wait_time:.1f}s before retry {attempt + 1}/{self.max_retries}"
                    )
                    time.sleep(wait_time)
                else:
                    print(f"Max retries ({self.max_retries}) exceeded")
                    raise

        # Should not reach here, but raise last exception if we do
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected: no exception to raise")


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
