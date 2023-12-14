"""This file contains the main() and other functions needed to open an issue/PR dependabot is not enabled but could be"""

import uuid

import github3
import auth
import env
from dependabot_file import build_dependabot_file


def main():
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
    ) = env.get_env_vars()

    # Auth to GitHub.com or GHE
    github_connection = auth.auth_to_github(token, ghe)

    # Get the repositories from the organization or list of repositories
    repos = get_repos_iterator(organization, repository_list, github_connection)

    # Iterate through the repositories and open an issue/PR if dependabot is not enabled
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

        # Try to detect package managers and build a dependabot file
        dependabot_file = build_dependabot_file(repo)
        if dependabot_file is None:
            print("\tNo compatible package manager found")
            continue

        print("Opening a " + follow_up_type + " for " + repo.full_name)
        if follow_up_type == "issue":
            issue = repo.create_issue(title, body)
            print("\tCreated issue " + issue.html_url)
        else:
            # Try to detect if the repo already has an open pull request for dependabot
            skip = check_pending_pulls_for_duplicates(repo)

            # Create a dependabot.yaml file, a branch, and a PR
            if not skip:
                commit_changes(title, body, repo, dependabot_file)
    print("Done")


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


def check_pending_pulls_for_duplicates(repo):
    """Check if there are any open pull requests for dependabot"""
    pull_requests = repo.pull_requests(state="open")
    skip = False
    for pull_request in pull_requests:
        if pull_request.head.ref.startswith("dependabot-"):
            print("\tPull request already exists")
            skip = True
            break
    return skip


def commit_changes(title, body, repo, dependabot_file):
    """Commit the changes to the repo and open a pull request"""
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
    print("\tCreated pull request " + pull.html_url)


if __name__ == "__main__":
    main()
