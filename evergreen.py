"""This file contains the main() and other functions needed to open an issue/PR dependabot is not enabled but could be"""

import uuid

import github3
import requests
import auth
import env
from dependabot_file import build_dependabot_file


def main():  # pragma: no cover
    """Run the main program"""

    # Get the environment variables
    (
        organization,
        repository_list,
        token,
        ghe,
        exempt_repositories_list,
        follow_up_type,
        title,
        body,
        created_after_date,
        dry_run,
    ) = env.get_env_vars()

    # Auth to GitHub.com or GHE
    github_connection = auth.auth_to_github(token, ghe)

    # Get the repositories from the organization or list of repositories
    repos = get_repos_iterator(organization, repository_list, github_connection)

    # Iterate through the repositories and open an issue/PR if dependabot is not enabled
    count_eligible = 0
    for repo in repos:
        # Check all the things to see if repo is eligble for a pr/issue
        if repo.full_name in exempt_repositories_list:
            continue
        if repo.archived:
            continue
        try:
            if repo.file_contents(".github/dependabot.yml").size > 0:
                continue
        except github3.exceptions.NotFoundError:
            pass
        try:
            if repo.file_contents(".github/dependabot.yaml").size > 0:
                continue
        except github3.exceptions.NotFoundError:
            pass
        if created_after_date and repo.created_at < created_after_date:
            continue

        print("Checking " + repo.full_name)
        # Try to detect package managers and build a dependabot file
        dependabot_file = build_dependabot_file(repo)
        if dependabot_file is None:
            print("\tNo compatible package manager found")
            continue

        # If dry_run is set, just print the dependabot file
        if dry_run:
            if follow_up_type == "issue":
                skip = check_pending_issues_for_duplicates(title, repo)
                if not skip:
                    print("\tEligible for configuring dependabot.")
                    count_eligible += 1
                    print("\tConfiguration:\n" + dependabot_file)
            if follow_up_type == "pull":
                # Try to detect if the repo already has an open pull request for dependabot
                skip = check_pending_pulls_for_duplicates(title, repo)
                if not skip:
                    print("\tEligible for configuring dependabot.")
                    count_eligible += 1
                    print("\tConfiguration:\n" + dependabot_file)
            continue

        # Get dependabot security updates enabled if possible
        if not is_dependabot_security_updates_enabled(repo.owner, repo.name, token):
            enable_dependabot_security_updates(repo.owner, repo.name, token)
        if follow_up_type == "issue":
            skip = check_pending_issues_for_duplicates(title, repo)
            if not skip:
                count_eligible += 1
                issue = repo.create_issue(title, body)
                print("\tCreated issue " + issue.html_url)
        else:
            count_eligible += 1
            # Try to detect if the repo already has an open pull request for dependabot
            skip = check_pending_pulls_for_duplicates(title, repo)

            # Create a dependabot.yaml file, a branch, and a PR
            if not skip:
                try:
                    pull = commit_changes(title, body, repo, dependabot_file)
                    print("\tCreated pull request " + pull.html_url)
                except github3.exceptions.NotFoundError:
                    print("\tFailed to create pull request. Check write permissions.")
                    continue

    print("Done. " + str(count_eligible) + " repositories were eligible.")


def is_dependabot_security_updates_enabled(owner, repo, access_token):
    """Check if Dependabot security updates are enabled at the /repos/:owner/:repo/automated-security-fixes endpoint using the requests library"""
    url = f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.london-preview+json",
    }

    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code == 200:
        return response.json()["enabled"]
    return False


def enable_dependabot_security_updates(owner, repo, access_token):
    """Enable Dependabot security updates at the /repos/:owner/:repo/automated-security-fixes endpoint using the requests library"""
    url = f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.london-preview+json",
    }

    response = requests.put(url, headers=headers, timeout=20)
    if response.status_code == 204:
        print("\tDependabot security updates enabled successfully.")
    else:
        print("\tFailed to enable Dependabot security updates.")


def get_repos_iterator(organization, repository_list, github_connection):
    """Get the repositories from the organization or list of repositories"""
    repos = []
    if organization:
        repos = github_connection.organization(organization).repositories()
    else:
        # Get the repositories from the repository_list
        for repo in repository_list:
            repos.append(
                github_connection.repository(repo.split("/")[0], repo.split("/")[1])
            )

    return repos


def check_pending_pulls_for_duplicates(title, repo) -> bool:
    """Check if there are any open pull requests for dependabot and return the bool skip"""
    pull_requests = repo.pull_requests(state="open")
    skip = False
    for pull_request in pull_requests:
        if pull_request.head.ref.startswith(title):
            print("\tPull request already exists: " + pull_request.html_url)
            skip = True
            break
    return skip


def check_pending_issues_for_duplicates(title, repo) -> bool:
    """Check if there are any open issues for dependabot and return the bool skip"""
    issues = repo.issues(state="open")
    skip = False
    for issue in issues:
        if issue.title.startswith(title):
            print("\tIssue already exists: " + issue.html_url)
            skip = True
            break
    return skip


def commit_changes(title, body, repo, dependabot_file):
    """Commit the changes to the repo and open a pull reques and return the pull request object"""
    default_branch = repo.default_branch
    # Get latest commit sha from default branch
    default_branch_commit = repo.ref("heads/" + default_branch).object.sha
    front_matter = "refs/heads/"
    branch_name = "dependabot-" + str(uuid.uuid4())
    repo.create_ref(front_matter + branch_name, default_branch_commit)
    repo.create_file(
        path=".github/dependabot.yaml",
        message="Create dependabot.yaml",
        content=dependabot_file.encode(),  # Convert to bytes object
        branch=branch_name,
    )

    pull = repo.create_pull(
        title=title, body=body, head=branch_name, base=repo.default_branch
    )
    return pull


if __name__ == "__main__":
    main()  # pragma: no cover
