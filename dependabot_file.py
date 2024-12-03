"""This module contains the function to build the dependabot.yml file for a repo"""

import base64
import copy
import io

import github3
import ruamel.yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString

# Define data structure for dependabot.yaml
data = {
    "version": 2,
    "registries": {},
    "updates": [],
}

yaml = ruamel.yaml.YAML()
stream = io.StringIO()


def make_dependabot_config(
    ecosystem,
    group_dependencies,
    schedule,
    schedule_day,
    labels,
    dependabot_config,
    extra_dependabot_config,
) -> str:
    """
    Make the dependabot configuration for a specific package ecosystem

    Args:
        ecosystem: the package ecosystem to make the dependabot configuration for
        group_dependencies: whether to group dependencies in the dependabot.yml file
        schedule: the schedule to run dependabot ex: "daily"
        schedule_day: the day of the week to run dependabot ex: "monday" if schedule is "weekly"
        labels: the list of labels to be added to dependabot configuration
        dependabot_config: extra dependabot configs
        extra_dependabot_config: File with the configuration to add dependabot configs (ex: private registries)

    Returns:
        str: the dependabot configuration for the package ecosystem
    """

    dependabot_config["updates"].append(
        {
            "package-ecosystem": SingleQuotedScalarString(ecosystem),
            "directory": SingleQuotedScalarString("/"),
        }
    )

    if extra_dependabot_config:
        ecosystem_config = extra_dependabot_config.get(ecosystem)
        if ecosystem_config:
            if "registries" not in dependabot_config:
                dependabot_config.update({"registries": {}})
            dependabot_config["registries"][ecosystem] = ecosystem_config
            dependabot_config["updates"][-1].update(
                {"registries": [SingleQuotedScalarString(ecosystem)]}
            )
    else:
        dependabot_config.pop("registries", None)

    if schedule_day:
        dependabot_config["updates"][-1].update(
            {
                "schedule": {
                    "interval": SingleQuotedScalarString(schedule),
                    "day": SingleQuotedScalarString(schedule_day),
                },
            }
        )
    else:
        dependabot_config["updates"][-1].update(
            {
                "schedule": {"interval": SingleQuotedScalarString(schedule)},
            }
        )

    if labels:
        quoted_labels = []
        for label in labels:
            quoted_labels.append(SingleQuotedScalarString(label))
        dependabot_config["updates"][-1].update({"labels": quoted_labels})

    if group_dependencies:
        dependabot_config["updates"][-1].update(
            {
                "groups": {
                    "production-dependencies": {
                        "dependency-type": SingleQuotedScalarString("production")
                    },
                    "development-dependencies": {
                        "dependency-type": SingleQuotedScalarString("development")
                    },
                }
            }
        )

    return yaml.dump(dependabot_config, stream)


def build_dependabot_file(
    repo,
    group_dependencies,
    exempt_ecosystems,
    repo_specific_exemptions,
    existing_config,
    schedule,
    schedule_day,
    labels,
    extra_dependabot_config,
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
        extra_dependabot_config: File with the configuration to add dependabot configs (ex: private registries)

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

    # create a local copy in order to avoid overwriting the global exemption list
    exempt_ecosystems_list = exempt_ecosystems.copy()
    if existing_config:
        yaml.preserve_quotes = True
        try:
            dependabot_file = yaml.load(base64.b64decode(existing_config.content))
        except ruamel.yaml.YAMLError as e:
            print(f"YAML indentation error: {e}")
            raise
    else:
        dependabot_file = copy.deepcopy(data)

    add_existing_ecosystem_to_exempt_list(exempt_ecosystems_list, dependabot_file)

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
        "gradle": ["build.gradle", "build.gradle.kts"],
    }

    # Detect package managers where manifest files have known names
    for manager, manifest_files in package_managers.items():
        if manager in exempt_ecosystems_list:
            continue
        for file in manifest_files:
            try:
                if repo.file_contents(file):
                    package_managers_found[manager] = True
                    make_dependabot_config(
                        manager,
                        group_dependencies,
                        schedule,
                        schedule_day,
                        labels,
                        dependabot_file,
                        extra_dependabot_config,
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
                    make_dependabot_config(
                        "terraform",
                        group_dependencies,
                        schedule,
                        schedule_day,
                        labels,
                        dependabot_file,
                        extra_dependabot_config,
                    )
                    break
        except github3.exceptions.NotFoundError:
            pass
    if "github-actions" not in exempt_ecosystems_list:
        try:
            for file in repo.directory_contents(".github/workflows"):
                if file[0].endswith(".yml") or file[0].endswith(".yaml"):
                    package_managers_found["github-actions"] = True
                    make_dependabot_config(
                        "github-actions",
                        group_dependencies,
                        schedule,
                        schedule_day,
                        labels,
                        dependabot_file,
                        extra_dependabot_config,
                    )
                    break
        except github3.exceptions.NotFoundError:
            pass
    if "devcontainers" not in exempt_ecosystems_list:
        try:
            for file in repo.directory_contents(".devcontainer"):
                if file[0] == "devcontainer.json":
                    package_managers_found["devcontainers"] = True
                    make_dependabot_config(
                        "devcontainers",
                        group_dependencies,
                        schedule,
                        schedule_day,
                        labels,
                        dependabot_file,
                        extra_dependabot_config,
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
        for entry in existing_config.get("updates", []):
            exempt_ecosystems.append(entry["package-ecosystem"])
