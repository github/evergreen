"""Test the get_env_vars function"""

import os
import unittest
from unittest.mock import patch

from env import get_env_vars


class TestEnv(unittest.TestCase):
    """Test the get_env_vars function"""

    def setUp(self):
        env_keys = [
            "BATCH_SIZE",
            "BODY",
            "COMMIT_MESSAGE",
            "CREATED_AFTER_DATE",
            "EXEMPT_REPOS",
            "GH_APP_ID",
            "GH_APP_INSTALLATION_ID",
            "GH_APP_PRIVATE_KEY",
            "GH_ENTERPRISE_URL",
            "GH_TOKEN",
            "GROUP_DEPENDENCIES",
            "ORGANIZATION",
            "PROJECT_ID",
            "TITLE",
            "TYPE",
            "UPDATE_EXISTING",
            "REPO_SPECIFIC_EXEMPTIONS",
        ]
        for key in env_keys:
            if key in os.environ:
                del os.environ[key]

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_TOKEN": "my_token",
            "TYPE": "issue",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2020-01-01",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_org(self):
        """Test that all environment variables are set correctly using an organization"""
        expected_result = (
            "my_organization",
            [],
            None,
            None,
            b"",
            "my_token",
            "",
            ["repo4", "repo5"],
            "issue",
            "Dependabot Alert custom title",
            "Dependabot custom body",
            "2020-01-01",
            False,
            "Create dependabot configuration",
            "123",
            False,
            ["internal", "private", "public"],
            None,  # batch_size
            True,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_TOKEN": "my_token",
            "TYPE": "issue",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2020-01-01",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "repo1:gomod;repo2:docker,gomod;",
        },
        clear=True,
    )
    def test_get_env_vars_with_org_and_repo_specific_exemptions(self):
        """Test that all environment variables are set correctly using an organization"""
        expected_result = (
            "my_organization",
            [],
            None,
            None,
            b"",
            "my_token",
            "",
            ["repo4", "repo5"],
            "issue",
            "Dependabot Alert custom title",
            "Dependabot custom body",
            "2020-01-01",
            False,
            "Create dependabot configuration",
            "123",
            False,
            ["internal", "private", "public"],
            None,  # batch_size
            True,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {
                "repo1": ["gomod"],
                "repo2": ["docker", "gomod"],
            },  # repo_specific_exemptions
        )
        result = get_env_vars(True)
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
            "REPO_SPECIFIC_EXEMPTIONS": "org1/repo1-docker;org2/repo2",
        },
        clear=True,
    )
    def test_get_env_vars_repo_specific_exemptions_improper_format(self):
        """Test that REPO_SPECIFIC_EXEMPTIONS is handled correctly when improperly formatted"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "not enough values to unpack (expected 2, got 1)",
        )

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
            "REPO_SPECIFIC_EXEMPTIONS": "org1/repo1:docker;org2/repo2:gomod",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = (
            None,
            ["org/repo1", "org2/repo2"],
            None,
            None,
            b"",
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
            ["internal", "private", "public"],
            None,  # batch_size
            True,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {
                "org1/repo1": ["docker"],
                "org2/repo2": ["gomod"],
            },  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
        },
        clear=True,
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = (
            "my_organization",
            [],
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["internal", "private", "public"],
            None,  # batch_size
            True,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "UPDATE_EXISTING": "true",
        },
        clear=True,
    )
    def test_get_env_vars_with_update_existing(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = (
            "my_organization",
            [],
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["internal", "private", "public"],
            None,  # batch_size
            True,  # enable_security_updates
            [],  # exempt_ecosystems
            True,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(os.environ, {})
    def test_get_env_vars_missing_org_or_repo(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "ORGANIZATION and REPOSITORY environment variables were not set. Please set one",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "678910",
            "GH_APP_PRIVATE_KEY": "hello",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_auth_with_github_app_installation(self):
        """Test that an error is raised if at least one type of authentication
        required environment variables are not set"""
        expected_result = (
            "my_organization",
            [],
            12345,
            678910,
            b"hello",
            "",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. Please enable it by merging "
            "this pull request so that we can keep our dependencies up to date and "
            "secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["internal", "private", "public"],
            None,  # batch_size
            True,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_missing_at_least_one_auth(self):
        """Test that an error is raised if at least one type of authentication
        required environment variables are not set"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "GH_TOKEN environment variable not set",
        )

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
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["internal", "private", "public"],
            None,  # batch_size
            True,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
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
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["internal", "private", "public"],
            None,  # batch_size
            False,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
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
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["internal", "private"],
            None,  # batch_size
            False,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
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
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["public"],
            None,  # batch_size
            False,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
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
            get_env_vars(True)

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
            get_env_vars(True)

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
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["private", "public"],
            None,  # batch_size
            False,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "EXEMPT_ECOSYSTEMS": "gomod,docker",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_exempt_ecosystems(self):
        """Test that filter_visibility is set correctly when there are exempt ecosystems"""
        expected_result = (
            "my_organization",
            [],
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["private", "public"],
            None,  # batch_size
            False,  # enable_security_updates
            ["gomod", "docker"],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

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
    def test_get_env_vars_with_no_batch_size(self):
        """Test that filter_visibility is set correctly when there is no batch size provided"""
        expected_result = (
            "my_organization",
            [],
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["private", "public"],
            None,  # batch_size
            False,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "BATCH_SIZE": str(5),  # os.environ expect str as values
        },
        clear=True,
    )
    def test_get_env_vars_with_batch_size(self):
        """Test that filter_visibility is set correctly when there is a batch size"""
        expected_result = (
            "my_organization",
            [],
            None,
            None,
            b"",
            "my_token",
            "",
            [],
            "pull",
            "Enable Dependabot",
            "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that \
we can keep our dependencies up to date and secure.",
            "",
            False,
            "Create/Update dependabot.yaml",
            None,
            False,
            ["private", "public"],
            5,  # batch_size
            False,  # enable_security_updates
            [],  # exempt_ecosystems
            False,  # update_existing
            {},  # repo_specific_exemptions
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "BATCH_SIZE": str(-1),  # os.environ expect str as values
        },
        clear=True,
    )
    def test_get_env_vars_with_invalid_batch_size_int(self):
        """Test that invalid batch size with negative 1 throws exception"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "BATCH_SIZE": "whatever",
        },
        clear=True,
    )
    def test_get_env_vars_with_invalid_batch_size_str(self):
        """Test that invalid batch size of string throws exception"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "CREATED_AFTER_DATE": "20200101",
        },
        clear=True,
    )
    def test_get_env_vars_with_badly_formatted_created_after_date(self):
        """Test that"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "CREATED_AFTER_DATE '20200101' environment variable not in YYYY-MM-DD",
        )


if __name__ == "__main__":
    unittest.main()
