"""This module contains the function to build the dependabot.yml file for a repo"""

import github3
import yaml


def make_dependabot_config(ecosystem, group_dependencies) -> str:
    """
    Make the dependabot configuration for a specific package ecosystem

    Args:
        ecosystem: the package ecosystem to make the dependabot configuration for
        group_dependencies: whether to group dependencies in the dependabot.yml file

    Returns:
        str: the dependabot configuration for the package ecosystem
    """
    dependabot_config = f"""  - package-ecosystem: '{ecosystem}'
    directory: '/'
    schedule:
      interval: 'weekly'
"""
    if group_dependencies:
        dependabot_config += """    groups:
      production-dependencies:
        dependency-type: 'production'
      development-dependencies:
        dependency-type: 'development'
"""
    return dependabot_config


def build_dependabot_file(
    repo, group_dependencies, exempt_ecosystems, existing_config
) -> str | None:
    """
    Build the dependabot.yml file for a repo based on the repo contents

    Args:
        repo: the repository to build the dependabot.yml file for
        group_dependencies: whether to group dependencies in the dependabot.yml file
        exempt_ecosystems: the list of ecosystems to ignore
        existing_config: the existing dependabot configuration file or None if it doesn't exist

    Returns:
        str: the dependabot.yml file for the repo
    """
    package_managers_found = {
        "bundler": False,
        "npm": False,
        "pip": False,
        "cargo": False,
        "gomod": False,
        "composer": False,
        "mix": False,
        "nuget": False,
        "docker": False,
        "terraform": False,
        "github-actions": False,
    }

    if existing_config:
        dependabot_file = existing_config.decoded.decode("utf-8")
    else:
        dependabot_file = """---
version: 2
updates:
"""

    add_existing_ecosystem_to_exempt_list(exempt_ecosystems, existing_config)

    package_managers = {
        "bundler": ["Gemfile", "Gemfile.lock"],
        "npm": ["package.json", "package-lock.json", "yarn.lock"],
        "pip": [
            "requirements.txt",
            "Pipfile",
            "Pipfile.lock",
            "pyproject.toml",
            "poetry.lock",
        ],
        "cargo": ["Cargo.toml", "Cargo.lock"],
        "gomod": ["go.mod"],
        "composer": ["composer.json", "composer.lock"],
        "mix": ["mix.exs", "mix.lock"],
        "nuget": [
            ".nuspec",
            ".csproj",
        ],
        "docker": ["Dockerfile"],
    }

    # Detect package managers where manifest files have known names
    for manager, manifest_files in package_managers.items():
        if manager in exempt_ecosystems:
            continue
        for file in manifest_files:
            try:
                if repo.file_contents(file):
                    package_managers_found[manager] = True
                    dependabot_file += make_dependabot_config(
                        manager, group_dependencies
                    )
                    break
            except github3.exceptions.NotFoundError:
                pass

    # detect package managers with variable file names
    if "terraform" not in exempt_ecosystems:
        try:
            for file in repo.directory_contents("/"):
                if file[0].endswith(".tf"):
                    package_managers_found["terraform"] = True
                    dependabot_file += make_dependabot_config(
                        "terraform", group_dependencies
                    )
                    break
        except github3.exceptions.NotFoundError:
            pass
    if "github-actions" not in exempt_ecosystems:
        try:
            for file in repo.directory_contents(".github/workflows"):
                if file[0].endswith(".yml") or file[0].endswith(".yaml"):
                    package_managers_found["github-actions"] = True
                    dependabot_file += make_dependabot_config(
                        "github-actions", group_dependencies
                    )
                    break
        except github3.exceptions.NotFoundError:
            pass

    if any(package_managers_found.values()):
        return dependabot_file
    return None


def add_existing_ecosystem_to_exempt_list(exempt_ecosystems, existing_config):
    """
    Add the existing package ecosystems found in the dependabot.yml
    to the exempt list so we don't get duplicate entries and maintain configuration settings
    """
    if existing_config:
        existing_config_obj = yaml.safe_load(existing_config.decoded)
        if existing_config_obj:
            for entry in existing_config_obj.get("updates", []):
                exempt_ecosystems.append(entry["package-ecosystem"])
