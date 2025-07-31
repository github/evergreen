"""Tests for the exceptions module."""

import unittest
from unittest.mock import Mock

import github3.exceptions
from exceptions import OptionalFileNotFoundError, check_optional_file


class TestOptionalFileNotFoundError(unittest.TestCase):
    """Test the OptionalFileNotFoundError exception."""

    def test_optional_file_not_found_error_inherits_from_not_found_error(self):
        """Test that OptionalFileNotFoundError inherits from github3.exceptions.NotFoundError."""
        mock_resp = Mock()
        mock_resp.status_code = 404
        error = OptionalFileNotFoundError(resp=mock_resp)
        self.assertIsInstance(error, github3.exceptions.NotFoundError)

    def test_optional_file_not_found_error_creation(self):
        """Test OptionalFileNotFoundError can be created."""
        mock_resp = Mock()
        mock_resp.status_code = 404
        error = OptionalFileNotFoundError(resp=mock_resp)
        self.assertIsInstance(error, OptionalFileNotFoundError)

    def test_optional_file_not_found_error_with_response(self):
        """Test OptionalFileNotFoundError with HTTP response."""
        mock_resp = Mock()
        mock_resp.status_code = 404
        error = OptionalFileNotFoundError(resp=mock_resp)

        # Should be created successfully
        self.assertIsInstance(error, OptionalFileNotFoundError)

    def test_can_catch_as_github3_not_found_error(self):
        """Test that OptionalFileNotFoundError can be caught as github3.exceptions.NotFoundError."""
        mock_resp = Mock()
        mock_resp.status_code = 404

        try:
            raise OptionalFileNotFoundError(resp=mock_resp)
        except github3.exceptions.NotFoundError as e:
            self.assertIsInstance(e, OptionalFileNotFoundError)
        except Exception:
            self.fail(
                "OptionalFileNotFoundError should be catchable as github3.exceptions.NotFoundError"
            )

    def test_can_catch_specifically(self):
        """Test that OptionalFileNotFoundError can be caught specifically."""
        mock_resp = Mock()
        mock_resp.status_code = 404

        try:
            raise OptionalFileNotFoundError(resp=mock_resp)
        except OptionalFileNotFoundError as e:
            self.assertIsInstance(e, OptionalFileNotFoundError)
        except Exception:
            self.fail("OptionalFileNotFoundError should be catchable specifically")

    def test_optional_file_not_found_error_properties(self):
        """Test OptionalFileNotFoundError has expected properties."""
        mock_resp = Mock()
        mock_resp.status_code = 404

        error = OptionalFileNotFoundError(resp=mock_resp)
        self.assertEqual(error.code, 404)
        self.assertEqual(error.response, mock_resp)


class TestCheckOptionalFile(unittest.TestCase):
    """Test the check_optional_file utility function."""

    def test_check_optional_file_with_existing_file(self):
        """Test check_optional_file when file exists."""
        mock_repo = Mock()
        mock_file_contents = Mock()
        mock_file_contents.size = 100
        mock_repo.file_contents.return_value = mock_file_contents

        result = check_optional_file(mock_repo, "config.yml")

        self.assertEqual(result, mock_file_contents)
        mock_repo.file_contents.assert_called_once_with("config.yml")

    def test_check_optional_file_with_empty_file(self):
        """Test check_optional_file when file exists but is empty."""
        mock_repo = Mock()
        mock_file_contents = Mock()
        mock_file_contents.size = 0
        mock_repo.file_contents.return_value = mock_file_contents

        result = check_optional_file(mock_repo, "config.yml")

        self.assertIsNone(result)
        mock_repo.file_contents.assert_called_once_with("config.yml")

    def test_check_optional_file_with_missing_file(self):
        """Test check_optional_file when file doesn't exist."""
        mock_repo = Mock()
        mock_resp = Mock()
        mock_resp.status_code = 404

        original_error = github3.exceptions.NotFoundError(resp=mock_resp)
        mock_repo.file_contents.side_effect = original_error

        with self.assertRaises(OptionalFileNotFoundError) as context:
            check_optional_file(mock_repo, "missing.yml")

        # Check that the original exception is chained
        self.assertEqual(context.exception.__cause__, original_error)
        self.assertEqual(context.exception.response, mock_resp)
        mock_repo.file_contents.assert_called_once_with("missing.yml")

    def test_check_optional_file_can_catch_as_not_found_error(self):
        """Test that OptionalFileNotFoundError from check_optional_file can be caught as NotFoundError."""
        mock_repo = Mock()
        mock_resp = Mock()
        mock_resp.status_code = 404

        mock_repo.file_contents.side_effect = github3.exceptions.NotFoundError(
            resp=mock_resp
        )

        try:
            check_optional_file(mock_repo, "missing.yml")
        except github3.exceptions.NotFoundError as e:
            self.assertIsInstance(e, OptionalFileNotFoundError)
        except Exception:
            self.fail(
                "Should be able to catch OptionalFileNotFoundError as NotFoundError"
            )


if __name__ == "__main__":
    unittest.main()
