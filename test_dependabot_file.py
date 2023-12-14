"""Tests for the dependabot_file.py functions."""

import unittest
from unittest.mock import MagicMock

from dependabot_file import (
    build_dependabot_file,
)


class TestDependabotFile(unittest.TestCase):
    """
    Test the dependabot_file.py functions.
    """

    def test_build_dependabot_file_with_bundler(self):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()

        # return true for bundler only
        repo.file_contents.side_effect = lambda filename: filename == "Gemfile.lock"
        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
        result = build_dependabot_file(repo)
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_npm(self):
        """Test that the dependabot.yml file is built correctly with npm"""
        repo = MagicMock()
        repo.file_contents.side_effect = (
            lambda filename: filename == "package-lock.json"
        )

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
        result = build_dependabot_file(repo)
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_pip(self):
        """Test that the dependabot.yml file is built correctly with pip"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "requirements.txt"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
        result = build_dependabot_file(repo)
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cargo(self):
        """Test that the dependabot.yml file is built correctly with Cargo"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Cargo.toml"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'cargo'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
        result = build_dependabot_file(repo)
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
        result = build_dependabot_file(repo)
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_composer(self):
        """Test that the dependabot.yml file is built correctly with Composer"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "composer.json"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'composer'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
        result = build_dependabot_file(repo)
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_hex(self):
        """Test that the dependabot.yml file is built correctly with Hex"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "mix.exs"

        expected_result = """---
version: 2
updates:
  - package-ecosystem: 'hex'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
        result = build_dependabot_file(repo)
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
        result = build_dependabot_file(repo)
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
        result = build_dependabot_file(repo)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
