"""
Sets up the environment variables for the action.
"""

import os
from os.path import dirname, join

from dotenv import load_dotenv


def get_env_vars() -> (
    tuple[
        str | None,
        list[str],
        str,
        str,
        list[str],
        str,
        str,
        str,
        str | None,
        bool,
        str,
        str | None,
        bool | None,
        bool | None,
    ]
):
    """
    Get the environment variables for use in the action.

    Args:
        None

    Returns:
        organization (str): The organization to search for repositories in
        repository_list (list[str]): A list of repositories to search for
        token (str): The GitHub token to use for authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        exempt_repositories_list (list[str]): A list of repositories to exempt from the action
        follow_up_type (str): The type of follow up to open (issue or pull)
        title (str): The title of the follow up
        body (str): The body of the follow up
        created_after_date (str): The date to filter repositories by
        dry_run (bool): Whether or not to actually open issues/pull requests
        commit_message (str): The commit message of the follow up
        group_dependencies (bool): Whether to group dependencies in the dependabot.yml file
        enable_security_updates (bool): Whether to enable security updates in target repositories
    """
    # Load from .env file if it exists
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    organization = os.getenv("ORGANIZATION")
    repositories_str = os.getenv("REPOSITORY")
    # Either organization or repository must be set
    if not organization and not repositories_str:
        raise ValueError(
            "ORGANIZATION and REPOSITORY environment variables were not set. Please set one"
        )

    if repositories_str and repositories_str.find("/") == 0:
        raise ValueError(
            "REPOSITORY environment variable was not set correctly. Please set it to a comma separated list of repositories in the format org/repo"
        )

    # Separate repositories_str into a list based on the comma separator
    repositories_list = []
    if repositories_str:
        repositories_list = [
            repository.strip() for repository in repositories_str.split(",")
        ]

    token = os.getenv("GH_TOKEN")
    # required env variable
    if not token:
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = os.getenv("GH_ENTERPRISE_URL", default="").strip()

    exempt_repos = os.getenv("EXEMPT_REPOS")
    exempt_repositories_list = []
    if exempt_repos:
        exempt_repositories_list = [
            repository.strip() for repository in exempt_repos.split(",")
        ]

    follow_up_type = os.getenv("TYPE")
    # make sure that follow_up_type is either "issue" or "pull"
    if follow_up_type:
        if follow_up_type not in ("issue", "pull"):
            raise ValueError("TYPE environment variable not 'issue' or 'pull'")
    else:
        follow_up_type = "pull"

    title = os.getenv("TITLE")
    # make sure that title is a string with less than 70 characters
    if title:
        if len(title) > 70:
            raise ValueError("TITLE environment variable is too long")
    else:
        title = "Enable Dependabot"

    body = os.getenv("BODY")
    if body and len(body) > 65536:
        raise ValueError("BODY environment variable is too long")

    if not body:
        default_bodies = {
            "pull": "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that we can keep our dependencies up to date and secure.",
            "issue": (
                "Please update the repository to include a Dependabot configuration file.\n"
                "This will ensure our dependencies remain updated and secure.\n"
                "Follow the guidelines in [creating Dependabot configuration files]"
                "(https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file) "
                "to set it up properly.\n\n"
                "Here's an example of the code:"
            ),
        }
        body = body = default_bodies[follow_up_type]

    commit_message = os.getenv("COMMIT_MESSAGE")
    if commit_message:
        if len(commit_message) > 65536:
            raise ValueError("COMMIT_MESSAGE environment variable is too long")
    else:
        commit_message = "Create dependabot.yaml"

    created_after_date = os.getenv("CREATED_AFTER_DATE")
    # make sure that created_after_date is a date in the format YYYY-MM-DD
    if created_after_date and len(created_after_date) != 10:
        raise ValueError("CREATED_AFTER_DATE environment variable not in YYYY-MM-DD")

    group_dependencies = os.getenv("GROUP_DEPENDENCIES")
    group_dependencies = group_dependencies.lower() if group_dependencies else None
    if group_dependencies:
        if group_dependencies not in ("true", "false"):
            raise ValueError(
                "GROUP_DEPENDENCIES environment variable not 'true' or 'false'"
            )
        group_dependencies_bool = group_dependencies == "true"
    else:
        group_dependencies_bool = False

    # enable_security_updates is optional but true by default to maintain backward compatibility
    enable_security_updates = os.getenv("ENABLE_SECURITY_UPDATES")
    enable_security_updates = (
        enable_security_updates.lower() if enable_security_updates else "true"
    )
    if enable_security_updates:
        if enable_security_updates not in ("true", "false"):
            raise ValueError(
                "ENABLE_SECURITY_UPDATES environment variable not 'true' or 'false'"
            )
        enable_security_updates_bool = enable_security_updates == "true"
    else:
        enable_security_updates_bool = False

    dry_run = os.getenv("DRY_RUN")
    dry_run = dry_run.lower() if dry_run else None
    if dry_run:
        if dry_run not in ("true", "false"):
            raise ValueError("DRY_RUN environment variable not 'true' or 'false'")
        dry_run_bool = dry_run == "true"
    else:
        dry_run_bool = False

    project_id = os.getenv("PROJECT_ID")
    if project_id and not project_id.isnumeric():
        raise ValueError("PROJECT_ID environment variable is not numeric")
    return (
        organization,
        repositories_list,
        token,
        ghe,
        exempt_repositories_list,
        follow_up_type,
        title,
        body,
        created_after_date,
        dry_run_bool,
        commit_message,
        project_id,
        group_dependencies_bool,
        enable_security_updates_bool,
    )
