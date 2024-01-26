""" Test the evergreen.py module. """
import unittest
import uuid
from unittest.mock import MagicMock, patch

from evergreen import (
    check_pending_issues_for_duplicates,
    check_pending_pulls_for_duplicates,
    commit_changes,
    enable_dependabot_security_updates,
    get_repos_iterator,
    is_dependabot_security_updates_enabled,
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


class TestCommitChanges(unittest.TestCase):
    """Test the commit_changes function in evergreen.py"""

    @patch("uuid.uuid4")
    def test_commit_changes(self, mock_uuid):
        """Test the commit_changes function."""
        mock_uuid.return_value = uuid.UUID(
            "12345678123456781234567812345678"
        )  # Mock UUID generation
        mock_repo = MagicMock()  # Mock repo object
        mock_repo.default_branch = "main"
        mock_repo.ref.return_value.object.sha = "abc123"  # Mock SHA for latest commit
        mock_repo.create_ref.return_value = True
        mock_repo.create_file.return_value = True
        mock_repo.create_pull.return_value = "MockPullRequest"

        title = "Test Title"
        body = "Test Body"
        dependabot_file = 'dependencies:\n  - package_manager: "python"\n    directory: "/"\n    update_schedule: "live"'
        branch_name = "dependabot-12345678-1234-5678-1234-567812345678"
        result = commit_changes(title, body, mock_repo, dependabot_file)

        # Assert that the methods were called with the correct arguments
        mock_repo.create_ref.assert_called_once_with(
            f"refs/heads/{branch_name}", "abc123"
        )
        mock_repo.create_file.assert_called_once_with(
            path=".github/dependabot.yaml",
            message="Create dependabot.yaml",
            content=dependabot_file.encode(),
            branch=branch_name,
        )
        mock_repo.create_pull.assert_called_once_with(
            title=title,
            body=body,
            head=branch_name,
            base="main",
        )

        # Assert that the function returned the expected result
        self.assertEqual(result, "MockPullRequest")


class TestCheckPendingPullsForDuplicates(unittest.TestCase):
    """Test the check_pending_pulls_for_duplicates function."""

    def test_check_pending_pulls_for_duplicates_no_duplicates(self):
        """Test the check_pending_pulls_for_duplicates function where there are no duplicates to be found."""
        mock_repo = MagicMock()  # Mock repo object
        mock_pull_request = MagicMock()
        mock_pull_request.head.ref = "not-dependabot-branch"
        mock_repo.pull_requests.return_value = [mock_pull_request]

        result = check_pending_pulls_for_duplicates("dependabot-branch", mock_repo)

        # Assert that the function returned the expected result
        self.assertEqual(result, False)

    def test_check_pending_pulls_for_duplicates_with_duplicates(self):
        """Test the check_pending_pulls_for_duplicates function where there are duplicates to be found."""
        mock_repo = MagicMock()  # Mock repo object
        mock_pull_request = MagicMock()
        mock_pull_request.head.ref = "dependabot-branch"
        mock_repo.pull_requests.return_value = [mock_pull_request]

        result = check_pending_pulls_for_duplicates(mock_pull_request.head.ref, mock_repo)

        # Assert that the function returned the expected result
        self.assertEqual(result, True)


class TestCheckPendingIssuesForDuplicates(unittest.TestCase):
    """Test the check_pending_Issues_for_duplicates function."""

    def test_check_pending_issues_for_duplicates_no_duplicates(self):
        """Test the check_pending_Issues_for_duplicates function where there are no duplicates to be found."""
        mock_issue = MagicMock()
        mock_issue.title = "Other Issue"
        mock_issue.issues.return_value = [mock_issue]

        result = check_pending_issues_for_duplicates("Enable Dependabot", mock_issue)

        mock_issue.issues.assert_called_once_with(state="open")

        # Assert that the function returned the expected result
        self.assertEqual(result, False)

    def test_check_pending_issues_for_duplicates_with_duplicates(self):
        """Test the check_pending_issues_for_duplicates function where there are duplicates to be found."""
        mock_issue = MagicMock()
        mock_issue.title = "Enable Dependabot"
        mock_issue.issues.return_value = [mock_issue]

        result = check_pending_issues_for_duplicates("Enable Dependabot", mock_issue)

        mock_issue.issues.assert_called_once_with(state="open")

        # Assert that the function returned the expected result
        self.assertEqual(result, True)


class TestGetReposIterator(unittest.TestCase):
    """Test the get_repos_iterator function in evergreen.py"""

    @patch("github3.login")
    def test_get_repos_iterator_with_organization(self, mock_github):
        """Test the get_repos_iterator function with an organization"""
        organization = "my_organization"
        repository_list = []
        github_connection = mock_github.return_value

        mock_organization = MagicMock()
        mock_repositories = MagicMock()
        mock_organization.repositories.return_value = mock_repositories
        github_connection.organization.return_value = mock_organization

        result = get_repos_iterator(organization, repository_list, github_connection)

        # Assert that the organization method was called with the correct argument
        github_connection.organization.assert_called_once_with(organization)

        # Assert that the repositories method was called on the organization object
        mock_organization.repositories.assert_called_once()

        # Assert that the function returned the expected result
        self.assertEqual(result, mock_repositories)

    @patch("github3.login")
    def test_get_repos_iterator_with_repository_list(self, mock_github):
        """Test the get_repos_iterator function with a repository list"""
        organization = None
        repository_list = ["org/repo1", "org/repo2"]
        github_connection = mock_github.return_value

        mock_repository = MagicMock()
        mock_repository_list = [mock_repository, mock_repository]
        github_connection.repository.side_effect = mock_repository_list

        result = get_repos_iterator(organization, repository_list, github_connection)

        # Assert that the repository method was called with the correct arguments for each repository in the list
        expected_calls = [
            unittest.mock.call("org", "repo1"),
            unittest.mock.call("org", "repo2"),
        ]
        github_connection.repository.assert_has_calls(expected_calls)

        # Assert that the function returned the expected result
        self.assertEqual(result, mock_repository_list)


if __name__ == "__main__":
    unittest.main()
