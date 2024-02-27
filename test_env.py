"""Test the get_env_vars function"""
import os
import unittest
from unittest.mock import patch

from env import get_env_vars


class TestEnv(unittest.TestCase):
    """Test the get_env_vars function"""

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "TYPE": "issue",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2023-01-01",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
        },
    )
    def test_get_env_vars_with_org(self):
        """Test that all environment variables are set correctly using an organization"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            ["repo4", "repo5"],
            "issue",
            "Dependabot Alert custom title",
            "Dependabot custom body",
            "2023-01-01",
            False,
            "Create dependabot configuration",
            "123",
            False,
            ["public", "private", "internal"],
            True,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "REPOSITORY": "org/repo1,org2/repo2",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "TYPE": "pull",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2023-01-01",
            "DRY_RUN": "true",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = (
            None,
            ["org/repo1", "org2/repo2"],
            "my_token",
            "",
            ["repo4", "repo5"],
            "pull",
            "Dependabot Alert custom title",
            "Dependabot custom body",
            "2023-01-01",
            True,
            "Create dependabot configuration",
            "123",
            False,
            ["public", "private", "internal"],
            True,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
        },
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            None,
            False,
            "Create dependabot.yaml",
            None,
            False,
            ["public", "private", "internal"],
            True,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(os.environ, {})
    def test_get_env_vars_missing_org_or_repo(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError):
            get_env_vars()

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
        },
        clear=True,
    )
    def test_get_env_vars_missing_token(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError):
            get_env_vars()

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "DRY_RUN": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_no_dry_run(self):
        """Test that all environment variables are set correctly when DRY_RUN is false"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            None,
            False,
            "Create dependabot.yaml",
            None,
            False,
            ["public", "private", "internal"],
            True,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_disabled_security_updates(self):
        """Test that all environment variables are set correctly when DRY_RUN is false"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            None,
            False,
            "Create dependabot.yaml",
            None,
            False,
            ["public", "private", "internal"],
            False,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,internal",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_multiple_values(self):
        """Test that filter_visibility is set correctly when multiple values are provided"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            None,
            False,
            "Create dependabot.yaml",
            None,
            False,
            ["private", "internal"],
            False,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "public",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_single_value(self):
        """Test that filter_visibility is set correctly when a single value is provided"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            None,
            False,
            "Create dependabot.yaml",
            None,
            False,
            ["public"],
            False,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "foobar",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_invalid_single_value(self):
        """Test that filter_visibility throws an error when an invalid value is provided"""
        with self.assertRaises(ValueError):
            get_env_vars()

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "public, foobar, private",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_invalid_multiple_value(self):
        """Test that filter_visibility throws an error when an invalid value is provided"""
        with self.assertRaises(ValueError):
            get_env_vars()

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_no_duplicates(self):
        """Test that filter_visibility is set correctly when there are duplicate values"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            None,
            False,
            "Create dependabot.yaml",
            None,
            False,
            ["private", "public"],
            False,  # enable_security_updates
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
