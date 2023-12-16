""" Test the evergreen.py module. """
import unittest
from unittest.mock import patch

from evergreen import (
    is_dependabot_security_updates_enabled,
    enable_dependabot_security_updates,
)


class TestDependabotSecurityUpdates(unittest.TestCase):
    """Test the Dependabot security updates functions in evergreen.py"""

    def test_is_dependabot_security_updates_enabled(self):
        """
        Test the is_dependabot_security_updates_enabled function.

        This test checks if the is_dependabot_security_updates_enabled function correctly
        detects if Dependabot security updates are enabled.

        It mocks the requests.get method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }
        expected_response = {"enabled": True}

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = expected_response

            result = is_dependabot_security_updates_enabled(owner, repo, access_token)

            mock_get.assert_called_once_with(
                expected_url, headers=expected_headers, timeout=20
            )
            self.assertTrue(result)

    def test_is_dependabot_security_updates_disabled(self):
        """
        Test the is_dependabot_security_updates_enabled function when security updates are disabled.

        This test checks if the is_dependabot_security_updates_enabled function correctly
        detects if Dependabot security updates are disabled.

        It mocks the requests.get method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"enabled": False}

            result = is_dependabot_security_updates_enabled(owner, repo, access_token)

            mock_get.assert_called_once_with(
                expected_url, headers=expected_headers, timeout=20
            )
            self.assertFalse(result)

    def test_is_dependabot_security_updates_not_found(self):
        """
        Test the is_dependabot_security_updates_enabled function when the endpoint is not found.

        This test checks if the is_dependabot_security_updates_enabled function correctly
        handles the case when the endpoint is not found.

        It mocks the requests.get method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404

            result = is_dependabot_security_updates_enabled(owner, repo, access_token)

            mock_get.assert_called_once_with(
                expected_url, headers=expected_headers, timeout=20
            )
            self.assertFalse(result)

    def test_enable_dependabot_security_updates(self):
        """
        Test the enable_dependabot_security_updates function.

        This test checks if the enable_dependabot_security_updates function successfully enables
        Dependabot security updates.

        It mocks the requests.put method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.put") as mock_put:
            mock_put.return_value.status_code = 204

            with patch("builtins.print") as mock_print:
                enable_dependabot_security_updates(owner, repo, access_token)

                mock_put.assert_called_once_with(
                    expected_url, headers=expected_headers, timeout=20
                )
                mock_print.assert_called_once_with(
                    "\tDependabot security updates enabled successfully."
                )

    def test_enable_dependabot_security_updates_failed(self):
        """
        Test the enable_dependabot_security_updates function when enabling fails.

        This test checks if the enable_dependabot_security_updates function handles the case
        when enabling Dependabot security updates fails.

        It mocks the requests.put method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.put") as mock_put:
            mock_put.return_value.status_code = 500

            with patch("builtins.print") as mock_print:
                enable_dependabot_security_updates(owner, repo, access_token)

                mock_put.assert_called_once_with(
                    expected_url, headers=expected_headers, timeout=20
                )
                mock_print.assert_called_once_with(
                    "\tFailed to enable Dependabot security updates."
                )


if __name__ == "__main__":
    unittest.main()
