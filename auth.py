"""This is the module that contains functions related to authenticating to GitHub with a personal access token."""

import github3


def auth_to_github(
    token: str,
    gh_app_id: int | None,
    gh_app_installation_id: int | None,
    gh_app_private_key_bytes: bytes,
    ghe: str,
) -> github3.GitHub:
    """
    Connect to GitHub.com or GitHub Enterprise, depending on env variables.

    Args:
        token (str): the GitHub personal access token
        gh_app_id (int | None): the GitHub App ID
        gh_app_installation_id (int | None): the GitHub App Installation ID
        gh_app_private_key_bytes (bytes): the GitHub App Private Key
        ghe (str): the GitHub Enterprise URL

    Returns:
        github3.GitHub: the GitHub connection object
    """
    if gh_app_id and gh_app_private_key_bytes and gh_app_installation_id:
        gh = github3.github.GitHub()
        gh.login_as_app_installation(
            gh_app_private_key_bytes, gh_app_id, gh_app_installation_id
        )
        github_connection = gh
    elif ghe and token:
        github_connection = github3.github.GitHubEnterprise(ghe, token=token)
    elif token:
        github_connection = github3.login(token=token)
    else:
        raise ValueError(
            "GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PRIVATE_KEY] environment variables are not set"
        )

    if not github_connection:
        raise ValueError("Unable to authenticate to GitHub")
    return github_connection  # type: ignore
