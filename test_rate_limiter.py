"""Tests for the rate_limiter module."""

import threading
import time
import unittest
from unittest.mock import MagicMock, patch

from rate_limiter import RateLimiter, RateLimitExceeded


class TestRateLimiter(unittest.TestCase):
    """Test the RateLimiter class."""

    def test_rate_limiter_initialization_default_values(self):
        """Test RateLimiter initialization with default values."""
        limiter = RateLimiter()
        self.assertEqual(limiter.requests_per_second, 2.0)
        self.assertTrue(limiter.enabled)
        self.assertEqual(limiter.backoff_factor, 2.0)
        self.assertEqual(limiter.max_retries, 3)

    def test_rate_limiter_initialization_custom_values(self):
        """Test RateLimiter initialization with custom values."""
        limiter = RateLimiter(
            requests_per_second=5.0, enabled=False, backoff_factor=3.0, max_retries=5
        )
        self.assertEqual(limiter.requests_per_second, 5.0)
        self.assertFalse(limiter.enabled)
        self.assertEqual(limiter.backoff_factor, 3.0)
        self.assertEqual(limiter.max_retries, 5)

    def test_rate_limiter_disabled_no_delay(self):
        """Test that disabled rate limiter doesn't add delay."""
        limiter = RateLimiter(requests_per_second=1.0, enabled=False)

        start_time = time.time()
        for _ in range(5):
            limiter.wait_for_token()
        elapsed = time.time() - start_time

        # Should complete almost instantly (allowing small overhead)
        self.assertLess(elapsed, 0.1)

    def test_rate_limiter_enabled_enforces_delay(self):
        """Test that enabled rate limiter enforces delay between requests."""
        limiter = RateLimiter(requests_per_second=10.0, enabled=True)

        # Make enough requests to exhaust initial tokens and trigger delays
        start_time = time.time()
        for _ in range(
            15
        ):  # 15 requests should take at least 1.4 seconds (needs 1.5s of tokens, starts with 1.0s worth)
            limiter.wait_for_token()
        elapsed = time.time() - start_time

        # Should take at least 0.4 seconds (15 requests - 10 initial tokens = 5 delayed tokens / 10 rps = 0.5s minimum)
        self.assertGreaterEqual(elapsed, 0.4)

    def test_execute_with_backoff_success(self):
        """Test execute_with_backoff with successful function execution."""
        limiter = RateLimiter(requests_per_second=10.0, enabled=True)

        mock_func = MagicMock(return_value="success")
        result = limiter.execute_with_backoff(mock_func, "arg1", kwarg1="value1")

        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("arg1", kwarg1="value1")

    def test_execute_with_backoff_disabled(self):
        """Test execute_with_backoff when rate limiting is disabled."""
        limiter = RateLimiter(enabled=False)

        mock_func = MagicMock(return_value="success")
        result = limiter.execute_with_backoff(mock_func)

        self.assertEqual(result, "success")
        mock_func.assert_called_once()

    def test_execute_with_backoff_rate_limit_then_success(self):
        """Test execute_with_backoff with rate limit error then success."""
        limiter = RateLimiter(
            requests_per_second=10.0, enabled=True, backoff_factor=2.0, max_retries=3
        )

        # First call raises RateLimitExceeded, second call succeeds
        mock_func = MagicMock(
            side_effect=[RateLimitExceeded("Rate limit hit"), "success"]
        )

        with patch("time.sleep") as mock_sleep:
            result = limiter.execute_with_backoff(mock_func)

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)
        # Should have slept once with initial wait time of 1.0
        mock_sleep.assert_called_once()

    def test_execute_with_backoff_429_response(self):
        """Test execute_with_backoff with 429 status code response."""
        limiter = RateLimiter(
            requests_per_second=10.0, enabled=True, backoff_factor=2.0, max_retries=2
        )

        # Create mock response with 429 status
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200

        mock_func = MagicMock(side_effect=[mock_response_429, mock_response_success])

        with patch("time.sleep") as mock_sleep:
            result = limiter.execute_with_backoff(mock_func)

        self.assertEqual(result, mock_response_success)
        self.assertEqual(mock_func.call_count, 2)
        mock_sleep.assert_called_once()

    def test_execute_with_backoff_max_retries_exceeded(self):
        """Test execute_with_backoff when max retries is exceeded."""
        limiter = RateLimiter(
            requests_per_second=10.0, enabled=True, backoff_factor=2.0, max_retries=2
        )

        # Always raise RateLimitExceeded
        mock_func = MagicMock(side_effect=RateLimitExceeded("Rate limit hit"))

        with patch("time.sleep") as mock_sleep:
            with self.assertRaises(RateLimitExceeded):
                limiter.execute_with_backoff(mock_func)

        # Should have tried max_retries + 1 times (initial + 2 retries = 3 total)
        self.assertEqual(mock_func.call_count, 3)
        # Should have slept 2 times (once for each retry, not for final failure)
        self.assertEqual(mock_sleep.call_count, 2)

    def test_execute_with_backoff_exponential_backoff_timing(self):
        """Test that exponential backoff timing increases correctly."""
        limiter = RateLimiter(
            requests_per_second=10.0, enabled=True, backoff_factor=2.0, max_retries=3
        )

        mock_func = MagicMock(side_effect=RateLimitExceeded("Rate limit hit"))

        with patch("time.sleep") as mock_sleep:
            try:
                limiter.execute_with_backoff(mock_func)
            except RateLimitExceeded:
                pass

        # Verify exponential backoff: 1.0, 2.0, 4.0
        calls = mock_sleep.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertAlmostEqual(calls[0][0][0], 1.0, places=1)  # First retry
        self.assertAlmostEqual(calls[1][0][0], 2.0, places=1)  # Second retry
        self.assertAlmostEqual(calls[2][0][0], 4.0, places=1)  # Third retry

    def test_execute_with_backoff_non_rate_limit_exception(self):
        """Test that non-rate-limit exceptions are raised immediately."""
        limiter = RateLimiter(requests_per_second=10.0, enabled=True, max_retries=3)

        mock_func = MagicMock(side_effect=ValueError("Some other error"))

        with self.assertRaises(ValueError) as context:
            limiter.execute_with_backoff(mock_func)

        self.assertEqual(str(context.exception), "Some other error")
        # Should only be called once, no retries for non-rate-limit errors
        self.assertEqual(mock_func.call_count, 1)

    def test_wait_for_token_refills_over_time(self):
        """Test that tokens refill over time allowing burst requests."""
        limiter = RateLimiter(requests_per_second=5.0, enabled=True)

        # Wait for tokens to refill
        time.sleep(0.5)

        # Should be able to make a couple requests quickly
        start_time = time.time()
        limiter.wait_for_token()
        limiter.wait_for_token()
        elapsed = time.time() - start_time

        # Should complete quickly due to token refill
        self.assertLess(elapsed, 0.5)

    def test_rate_limiter_thread_safety(self):
        """Test that rate limiter is thread-safe."""
        limiter = RateLimiter(requests_per_second=10.0, enabled=True)
        results = []

        def make_request():
            limiter.wait_for_token()
            results.append(time.time())

        # Use more threads to exhaust initial tokens
        threads = [threading.Thread(target=make_request) for _ in range(15)]

        start_time = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        elapsed = time.time() - start_time

        # All threads should complete
        self.assertEqual(len(results), 15)

        # Should take at least 0.4 seconds for 15 requests at 10 rps
        # (15 requests - 10 initial tokens = 5 delayed / 10 rps = 0.5s)
        self.assertGreaterEqual(elapsed, 0.4)


if __name__ == "__main__":
    unittest.main()
