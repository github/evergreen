"""This is the module that contains functions related to authenticating to GitHub with a personal access token."""

import github3


def auth_to_github(token: str, ghe: str) -> github3.GitHub:
    """
    Connect to GitHub.com or GitHub Enterprise, depending on env variables.

    Args:
        token (str): the GitHub personal access token
        ghe (str): the GitHub Enterprise URL

    Returns:
        github3.GitHub: the GitHub connection object
    """
    if not token:
        raise ValueError("GH_TOKEN environment variable not set")

    if ghe:
        github_connection = github3.github.GitHubEnterprise(ghe, token=token)
    else:
        github_connection = github3.login(token=token)

    if not github_connection:
        raise ValueError("Unable to authenticate to GitHub")
    return github_connection  # type: ignore
