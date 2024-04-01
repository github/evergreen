"""Test cases for the auth module."""

import unittest
from unittest.mock import patch

import auth


class TestAuth(unittest.TestCase):
    """
    Test case for the auth module.
    """

    @patch("github3.login")
    def test_auth_to_github_with_token(self, mock_login):
        """
        Test the auth_to_github function when the token is provided.
        """
        mock_login.return_value = "Authenticated to GitHub.com"

        result = auth.auth_to_github("token", "", "", b"", "")

        self.assertEqual(result, "Authenticated to GitHub.com")

    def test_auth_to_github_without_token(self):
        """
        Test the auth_to_github function when the token is not provided.
        Expect a ValueError to be raised.
        """
        with self.assertRaises(ValueError) as cm:
            auth.auth_to_github("", "", "", b"", "")
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PRIVATE_KEY] environment variables are not set",
        )

    @patch("github3.github.GitHubEnterprise")
    def test_auth_to_github_with_ghe(self, mock_ghe):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided.
        """
        mock_ghe.return_value = "Authenticated to GitHub Enterprise"
        result = auth.auth_to_github("token", "", "", b"", "https://github.example.com")

        self.assertEqual(result, "Authenticated to GitHub Enterprise")


if __name__ == "__main__":
    unittest.main()
