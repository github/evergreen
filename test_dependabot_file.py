"""Tests for the dependabot_file.py functions."""

import unittest
from unittest.mock import MagicMock

import github3
from dependabot_file import build_dependabot_file


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

        result = build_dependabot_file(repo, False, [], None)
        self.assertEqual(result, None)

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
            result = build_dependabot_file(repo, False, [], None)
            self.assertEqual(result, expected_result)

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
            result = build_dependabot_file(repo, False, [], None)
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
            result = build_dependabot_file(repo, False, [], None)
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
            result = build_dependabot_file(repo, False, [], None)
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
        result = build_dependabot_file(repo, False, [], None)
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
            result = build_dependabot_file(repo, False, [], None)
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
            result = build_dependabot_file(repo, False, [], None)
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
        result = build_dependabot_file(repo, False, [], None)
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
        result = build_dependabot_file(repo, False, [], None)
        self.assertEqual(result, expected_result)

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
        result = build_dependabot_file(repo, True, [], None)
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_exempt_ecosystems(self):
        """Test that the dependabot.yml file is built correctly with exempted ecosystems"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        result = build_dependabot_file(repo, False, ["docker"], None)
        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main()
