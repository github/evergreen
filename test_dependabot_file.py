# pylint: disable=too-many-public-methods
"""Tests for the dependabot_file.py functions."""

import unittest
from unittest.mock import MagicMock

import github3
import yaml
from dependabot_file import add_existing_ecosystem_to_exempt_list, build_dependabot_file


class TestDependabotFile(unittest.TestCase):
    """
    Test the dependabot_file.py functions.
    """

    def test_not_found_error(self):
        """Test that the dependabot.yml file is built correctly with no package manager"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)

        result = build_dependabot_file(repo, False, [], {}, None, "", "", [])
        self.assertEqual(result, None)

    def test_build_dependabot_file_with_schedule_day(self):
        """Test that the dependabot.yml file is built correctly with weekly schedule day"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
      day: 'tuesday'
"""
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "tuesday", []
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_bundler(self):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
            result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_existing_config_bundler_no_update(self):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda f, filename="Gemfile": f == filename

        # expected_result is None because the existing config already contains the all applicable ecosystems
        expected_result = None
        existing_config = MagicMock()
        existing_config.decoded = b'---\nversion: 2\nupdates:\n  - package-ecosystem: "bundler"\n\
    directory: "/"\n    schedule:\n      interval: "weekly"\n    commit-message:\n      prefix: "chore(deps)"\n'
        result = build_dependabot_file(
            repo, False, [], {}, existing_config, "weekly", "", []
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_2_space_indent_existing_config_bundler_with_update(
        self,
    ):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda f, filename="Gemfile": f == filename

        # expected_result maintains existing ecosystem with custom configuration
        # and adds new ecosystem
        expected_result = """---
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(deps)"
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        existing_config = MagicMock()
        existing_config.decoded = b'---\nversion: 2\nupdates:\n  - package-ecosystem: "pip"\n    directory: "/"\n\
    schedule:\n      interval: "weekly"\n    commit-message:\n      prefix: "chore(deps)"\n'
        result = build_dependabot_file(
            repo, False, [], {}, existing_config, "weekly", "", []
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_2_space_indent_existing_config_bundler_with_update_and_no_newline(
        self,
    ):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda f, filename="Gemfile": f == filename

        # expected_result maintains existing ecosystem with custom configuration
        # and adds new ecosystem
        expected_result = """---
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(deps)"
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        existing_config = MagicMock()
        existing_config.decoded = b'---\nversion: 2\nupdates:\n  - package-ecosystem: "pip"\n    directory: "/"\n\
    schedule:\n      interval: "weekly"\n    commit-message:\n      prefix: "chore(deps)"'
        result = build_dependabot_file(
            repo, False, [], {}, existing_config, "weekly", "", []
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_weird_space_indent_existing_config_bundler_with_update(
        self,
    ):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda f, filename="Gemfile": f == filename

        # expected_result maintains existing ecosystem with custom configuration
        # and adds new ecosystem
        existing_config = MagicMock()
        existing_config.decoded = b'---\nversion: 2\nupdates:\n- package-ecosystem: "pip"\n  directory: "/"\n\
  schedule:\n    interval: "weekly"\n  commit-message:\n    prefix: "chore(deps)"\n'
        result = build_dependabot_file(
            repo, False, [], {}, existing_config, "weekly", "", []
        )
        self.assertEqual(result, None)

    def test_build_dependabot_file_with_npm(self):
        """Test that the dependabot.yml file is built correctly with npm"""
        repo = MagicMock()
        filename_list = ["package.json", "package-lock.json", "yarn.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
            result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_pip(self):
        """Test that the dependabot.yml file is built correctly with pip"""
        repo = MagicMock()
        filename_list = [
            "requirements.txt",
            "Pipfile",
            "Pipfile.lock",
            "pyproject.toml",
            "poetry.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
            result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cargo(self):
        """Test that the dependabot.yml file is built correctly with Cargo"""
        repo = MagicMock()
        filename_list = [
            "Cargo.toml",
            "Cargo.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'cargo'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
            result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_gomod(self):
        """Test that the dependabot.yml file is built correctly with Go module"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "go.mod"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'gomod'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_composer(self):
        """Test that the dependabot.yml file is built correctly with Composer"""
        repo = MagicMock()
        filename_list = [
            "composer.json",
            "composer.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'composer'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
            result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_hex(self):
        """Test that the dependabot.yml file is built correctly with Hex"""
        repo = MagicMock()
        filename_list = [
            "mix.exs",
            "mix.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'mix'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
            result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_nuget(self):
        """Test that the dependabot.yml file is built correctly with NuGet"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename.endswith(".csproj")

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'nuget'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_docker(self):
        """Test that the dependabot.yml file is built correctly with Docker"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_terraform_with_files(self):
        """Test that the dependabot.yml file is built correctly with Terraform"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)
        repo.directory_contents.side_effect = lambda path: (
            [("main.tf", None)] if path == "/" else []
        )

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'terraform'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_terraform_without_files(self):
        """Test that the dependabot.yml file is built correctly with Terraform"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)

        # Test absence of Terraform files
        repo.directory_contents.side_effect = lambda path: [] if path == "/" else []
        result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
        self.assertIsNone(result)

        # Test empty repository
        response = MagicMock()
        response.status_code = 404
        repo.directory_contents.side_effect = github3.exceptions.NotFoundError(
            resp=response
        )
        result = build_dependabot_file(repo, False, [], {}, None, "weekly", "", [])
        self.assertIsNone(result)

    def test_build_dependabot_file_with_github_actions(self):
        """Test that the dependabot.yml file is built correctly with GitHub Actions"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)
        repo.directory_contents.side_effect = lambda path: (
            [("test.yml", None)] if path == ".github/workflows" else []
        )

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'github-actions'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        result = build_dependabot_file(repo, False, [], None, None, "weekly", "", [])
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_github_actions_without_files(self):
        """Test that the dependabot.yml file is None when no YAML files are found in the .github/workflows/ directory."""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)
        repo.directory_contents.side_effect = github3.exceptions.NotFoundError(
            resp=response
        )

        result = build_dependabot_file(repo, False, [], None, None, "weekly", "", [])
        self.assertEqual(result, None)

    def test_build_dependabot_file_with_groups(self):
        """Test that the dependabot.yml file is built correctly with grouped dependencies"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
    groups:
      production-dependencies:
        dependency-type: 'production'
      development-dependencies:
        dependency-type: 'development'
"""
        result = build_dependabot_file(repo, True, [], {}, None, "weekly", "", [])
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_exempt_ecosystems(self):
        """Test that the dependabot.yml file is built correctly with exempted ecosystems"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        result = build_dependabot_file(
            repo, False, ["docker"], {}, None, "weekly", "", []
        )
        self.assertEqual(result, None)

    def test_build_dependabot_file_with_repo_specific_exempt_ecosystems(self):
        """Test that the dependabot.yml file is built correctly with exempted ecosystems"""
        repo = MagicMock()
        repo.full_name = "test/test"
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        result = build_dependabot_file(
            repo, False, [], {"test/test": ["docker"]}, None, "weekly", "", []
        )
        self.assertEqual(result, None)

    def test_add_existing_ecosystem_to_exempt_list(self):
        """Test that existing ecosystems are added to the exempt list"""
        exempt_ecosystems = ["npm", "pip", "github-actions"]
        existing_config = MagicMock()
        existing_config.decoded = yaml.dump(
            {
                "updates": [
                    {"package-ecosystem": "npm"},
                    {"package-ecosystem": "pip"},
                    {"package-ecosystem": "bundler"},
                ]
            }
        ).encode()

        add_existing_ecosystem_to_exempt_list(exempt_ecosystems, existing_config)

        # Check new ecosystem is added to exempt list
        self.assertIn("bundler", exempt_ecosystems)
        # Keep existing ecosystems in exempt list
        for ecosystem in exempt_ecosystems:
            self.assertIn(ecosystem, exempt_ecosystems)

    def test_build_dependabot_file_for_multiple_repos_with_few_existing_config(self):
        """
        Test the case where there are multiple repos with few existing dependabot config
        """
        existing_config_repo = MagicMock()
        existing_config_repo.file_contents.side_effect = (
            lambda f, filename="Gemfile": f == filename
        )

        existing_config = MagicMock()
        existing_config.decoded = b'---\nversion: 2\nupdates:\n  - package-ecosystem: "bundler"\n\
    directory: "/"\n    schedule:\n      interval: "weekly"\n    commit-message:\n      prefix: "chore(deps)"\n'
        exempt_ecosystems = []
        result = build_dependabot_file(
            existing_config_repo,
            False,
            exempt_ecosystems,
            {},
            existing_config,
            "weekly",
            "",
            [],
        )
        self.assertEqual(result, None)

        no_existing_config_repo = MagicMock()
        filename_list = ["package.json", "package-lock.json", "yarn.lock"]
        for filename in filename_list:
            no_existing_config_repo.file_contents.side_effect = (
                lambda f, filename=filename: f == filename
            )
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        result = build_dependabot_file(
            no_existing_config_repo,
            False,
            exempt_ecosystems,
            {},
            None,
            "weekly",
            "",
            [],
        )
        self.assertEqual(result, expected_result)

    def test_check_multiple_repos_with_no_dependabot_config(self):
        """
        Test the case where there is a single repo
        """
        mock_repo_1 = MagicMock()
        mock_repo_1.file_contents.side_effect = lambda filename: filename == "go.mod"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'gomod'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        exempt_ecosystems = []
        result = build_dependabot_file(
            mock_repo_1, False, exempt_ecosystems, {}, None, "weekly", "", []
        )
        self.assertEqual(result, expected_result)

        no_existing_config_repo = MagicMock()
        filename_list = ["package.json", "package-lock.json", "yarn.lock"]
        for filename in filename_list:
            no_existing_config_repo.file_contents.side_effect = (
                lambda f, filename=filename: f == filename
            )
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
        result = build_dependabot_file(
            no_existing_config_repo,
            False,
            exempt_ecosystems,
            {},
            None,
            "weekly",
            "",
            [],
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_label(self):
        """Test that the dependabot.yml file is built correctly with one label set"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
    labels:
      - "dependencies"
"""
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", ["dependencies"]
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_labels(self):
        """Test that the dependabot.yml file is built correctly with multiple labels set"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = """---
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
    labels:
      - "dependencies"
      - "test1"
      - "test2"
"""
            result = build_dependabot_file(
                repo,
                False,
                [],
                {},
                None,
                "weekly",
                "",
                ["dependencies", "test1", "test2"],
            )
            self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
