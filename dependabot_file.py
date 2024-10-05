"""This module contains the function to build the dependabot.yml file for a repo"""

import github3
import yaml


def make_dependabot_config(
    ecosystem, group_dependencies, indent, schedule, schedule_day, labels
) -> str:
    """
    Make the dependabot configuration for a specific package ecosystem

    Args:
        ecosystem: the package ecosystem to make the dependabot configuration for
        group_dependencies: whether to group dependencies in the dependabot.yml file
        indent: the number of spaces to indent the dependabot configuration ex: "  "
        schedule: the schedule to run dependabot ex: "daily"
        schedule_day: the day of the week to run dependabot ex: "monday" if schedule is "weekly"
        labels: the list of labels to be added to dependabot configuration

    Returns:
        str: the dependabot configuration for the package ecosystem
    """
    schedule_day_line = ""
    if schedule_day:
        schedule_day_line += f"""
{indent}{indent}{indent}day: '{schedule_day}'"""

    dependabot_config = f"""{indent}- package-ecosystem: '{ecosystem}'
{indent}{indent}directory: '/'
{indent}{indent}schedule:
{indent}{indent}{indent}interval: '{schedule}'{schedule_day_line}
"""

    if labels:
        dependabot_config += f"""{indent}{indent}labels:
"""
        for label in labels:
            dependabot_config += f"""{indent}{indent}{indent}- \"{label}\"
"""

    if group_dependencies:
        dependabot_config += f"""{indent}{indent}groups:
{indent}{indent}{indent}production-dependencies:
{indent}{indent}{indent}{indent}dependency-type: 'production'
{indent}{indent}{indent}development-dependencies:
{indent}{indent}{indent}{indent}dependency-type: 'development'
"""
    return dependabot_config


def build_dependabot_file(
    repo,
    group_dependencies,
    exempt_ecosystems,
    repo_specific_exemptions,
    existing_config,
    schedule,
    schedule_day,
    labels,
) -> str | None:
    """
    Build the dependabot.yml file for a repo based on the repo contents

    Args:
        repo: the repository to build the dependabot.yml file for
        group_dependencies: whether to group dependencies in the dependabot.yml file
        exempt_ecosystems: the list of ecosystems to ignore
        repo_specific_exemptions: the list of ecosystems to ignore for a specific repo
        existing_config: the existing dependabot configuration file or None if it doesn't exist
        schedule: the schedule to run dependabot ex: "daily"
        schedule_day: the day of the week to run dependabot ex: "monday" if schedule is "daily"
        labels: the list of labels to be added to dependabot configuration

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
        "maven": False,
    }
    DEFAULT_INDENT = 2  # pylint: disable=invalid-name
    # create a local copy in order to avoid overwriting the global exemption list
    exempt_ecosystems_list = exempt_ecosystems.copy()
    if existing_config:
        dependabot_file = existing_config.decoded.decode("utf-8")
        ecosystem_line = next(
            line
            for line in dependabot_file.splitlines()
            if "- package-ecosystem:" in line
        )
        indent = " " * (len(ecosystem_line) - len(ecosystem_line.lstrip()))
        if len(indent) < DEFAULT_INDENT:
            print(
                f"Invalid dependabot.yml file. No indentation found. Skipping {repo.full_name}"
            )
            return None
    else:
        indent = " " * DEFAULT_INDENT
        dependabot_file = """---
version: 2
updates:
"""

    add_existing_ecosystem_to_exempt_list(exempt_ecosystems_list, existing_config)

    # If there are repository specific exemptions,
    # overwrite the global exemptions for this repo only
    if repo_specific_exemptions and repo.full_name in repo_specific_exemptions:
        exempt_ecosystems_list = []
        for ecosystem in repo_specific_exemptions[repo.full_name]:
            exempt_ecosystems_list.append(ecosystem)

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
        "maven": ["pom.xml"],
    }

    # Detect package managers where manifest files have known names
    for manager, manifest_files in package_managers.items():
        if manager in exempt_ecosystems_list:
            continue
        for file in manifest_files:
            try:
                if repo.file_contents(file):
                    package_managers_found[manager] = True
                    # If the last thing in the file is not a newline,
                    # add one before adding a new language config to the file
                    if dependabot_file and dependabot_file[-1] != "\n":
                        dependabot_file += "\n"
                    dependabot_file += make_dependabot_config(
                        manager,
                        group_dependencies,
                        indent,
                        schedule,
                        schedule_day,
                        labels,
                    )
                    break
            except github3.exceptions.NotFoundError:
                pass

    # detect package managers with variable file names
    if "terraform" not in exempt_ecosystems_list:
        try:
            for file in repo.directory_contents("/"):
                if file[0].endswith(".tf"):
                    package_managers_found["terraform"] = True
                    dependabot_file += make_dependabot_config(
                        "terraform",
                        group_dependencies,
                        indent,
                        schedule,
                        schedule_day,
                        labels,
                    )
                    break
        except github3.exceptions.NotFoundError:
            pass
    if "github-actions" not in exempt_ecosystems_list:
        try:
            for file in repo.directory_contents(".github/workflows"):
                if file[0].endswith(".yml") or file[0].endswith(".yaml"):
                    package_managers_found["github-actions"] = True
                    dependabot_file += make_dependabot_config(
                        "github-actions",
                        group_dependencies,
                        indent,
                        schedule,
                        schedule_day,
                        labels,
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
