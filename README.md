# Evergreen action

[![CodeQL](https://github.com/github/evergreen/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/github/evergreen/actions/workflows/github-code-scanning/codeql) [![Lint Code Base](https://github.com/github/evergreen/actions/workflows/super-linter.yaml/badge.svg)](https://github.com/github/evergreen/actions/workflows/super-linter.yaml) [![Python package](https://github.com/github/evergreen/actions/workflows/python-ci.yml/badge.svg)](https://github.com/github/evergreen/actions/workflows/python-ci.yml)

This is a GitHub Action that given an organization or specified repositories, opens an issue/PR dependabot is not enabled but could be. It also enables [automated security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates#managing-dependabot-security-updates-for-your-repositories) for the repository.

This action was developed by the GitHub OSPO for our own use and developed in a way that we could open source it that it might be useful to you as well! If you want to know more about how we use it, reach out in an issue in this repository.

## Example use cases

- As a part of the security team for my company, I want to make sure that all of the repositories in the company organizations are regularly updating their dependencies to ensure they are using the most secure version of the dependency available.
- As an OSPO or maintainer, I want to automate everything I can to keep maintaining my project(s) easy and efficient.

## Support

If you need support using this project or have questions about it, please [open up an issue in this repository](https://github.com/github/evergreen/issues). Requests made directly to GitHub staff or support team will be redirected here to open an issue. GitHub SLA's and support/services contracts do not apply to this repository.

## Use as a GitHub Action

1. Create a repository to host this GitHub Action or select an existing repository.
1. Select a best fit workflow file from the [examples below](#example-workflows).
1. Copy that example into your repository (from step 1) and into the proper directory for GitHub Actions: `.github/workflows/` directory with the file extension `.yml` (ie. `.github/workflows/evergreen.yml`)
1. Edit the values (`ORGANIZATION`, `REPOSITORY`, `EXEMPT_REPOS`, `TYPE`, `TITLE`, `BODY`) from the sample workflow with your information. If running on a whole organization then no repository is needed. If running the action on just one repository or a list of repositories, then no organization is needed. The type should be either `issue` or `pull` representing the action that you want taken after discovering a repository that should enable dependabot.
1. Optionally, edit the value (`CREATED_AFTER_DATE`) if you are setting up this action to run regularly and only want newly created repositories to be considered. Otherwise, if you want all specified repositories regardless of when they were created to be considered, then leave blank.
1. Also edit the value for `GH_ENTERPRISE_URL` if you are using a GitHub Server and not using github.com. For github.com users, don't put anything in here.
1. Update the value of `GH_TOKEN`. Do this by creating a [GitHub API token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) with permissions to read the repository/organization and write issues or pull requests depending on what you put in for the `TYPE`. Then take the value of the API token you just created, and [create a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets) where the name of the secret is `GH_TOKEN` and the value of the secret the API token. Then finally update the workflow file to use that repository secret by changing `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` to `GH_TOKEN: ${{ secrets.GH_TOKEN }}`. The name of the secret can really be anything. It just needs to match between when you create the secret name and when you refer to it in the workflow file.
1. If you want the resulting issue with the output to appear in a different repository other than the one the workflow file runs in, update the line `token: ${{ secrets.GITHUB_TOKEN }}` with your own GitHub API token stored as a repository secret. This process is the same as described in the step above. More info on creating secrets can be found [here](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
1. Commit the workflow file to the default branch (often `master` or `main`)
1. Wait for the action to trigger based on the `schedule` entry or manually trigger the workflow as shown in the [documentation](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow).

### Configuration

Below are the allowed configuration options:

| field                 | required | default | description |
|-----------------------|----------|---------|-------------|
| `GH_TOKEN`            | True     |   ""    | The GitHub Token used to scan the repository or organization. Must have write access to all repository you are interested in scanning so that an issue or pull request can be created. |
| `GH_ENTERPRISE_URL`   | False    |   ""    | The `GH_ENTERPRISE_URL` is used to connect to an enterprise server instance of GitHub. github.com users should not enter anything here. |
| `ORGANIZATION`        | Required to have `ORGANIZATION` or `REPOSITORY` |         | The name of the GitHub organization which you want this action to work from. ie. github.com/github would be `github` |
| `REPOSITORY`          | Required to have `ORGANIZATION` or `REPOSITORY` |         | The name of the repository and organization which you want this action to work from. ie. `github/evergreen` or a comma separated list of multiple repositories `github/evergreen,super-linter/super-linter` |
| `EXEMPT_REPOS`        | False    |   ""    |  These repositories will be exempt from this action considering them for dependabot enablement. ex: If my org is set to `github` then I might want to exempt a few of the repos but get the rest by setting `EXEMPT_REPOS` to ``github/evergreen,github/contributors` |
| `TYPE`                | False    | pull    | Type refers to the type of action you want taken if this workflow determines that dependabot could be enabled. Valid values are `pull` or `issue`.|
| `TITLE`               | False    | "Enable Dependabot" | The title of the issue or pull request that will be created if dependabot could be enabled. |
| `BODY`                | False    | **Pull Request:** "Dependabot could be enabled for this repository. Please enable it by merging this pull request so that we can keep our dependencies up to date and secure." **Issue:** "Please update the repository to include a Dependabot configuration file. This will ensure our dependencies remain updated and secure.Follow the guidelines in [creating Dependabot configuration files](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file) to set it up properly.Here's an example of the code:" | The body of the issue or pull request that will be created if dependabot could be enabled. |
| `COMMIT_MESSAGE`      | False    | "Create dependabot.yaml" | The commit message for the pull request that will be created if dependabot could be enabled. |
| `CREATED_AFTER_DATE`          | False    | none       | If a value is set, this action will only consider repositories created on or after this date for dependabot enablement. This is useful if you want to only consider newly created repositories. If I set up this action to run weekly and I only want to scan for repos created in the last week that need dependabot enabled, then I would set `CREATED_AFTER_DATE` to 7 days ago. That way only repositories created after 7 days ago will be considered for dependabot enablement. If not set or set to nothing, all repositories will be scanned and a duplicate issue/pull request may occur. Ex: 2023-12-31 for Dec. 31st 2023 |
| `PROJECT_ID`          | False    | ""     | If set, this will assign the issue or pull request to the project with the given ID. ( The project ID on GitHub can be located by navigating to the respective project and observing the URL's end.) **The `ORGANIZATION` variable is required** |
| `DRY_RUN`             | False    | false   | If set to true, this action will not create any issues or pull requests. It will only log the repositories that could have dependabot enabled. This is useful for testing. |

### Example workflows

#### Basic

```yaml
---
name: Weekly dependabot checks
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

permissions:
  issues: write

jobs:
  evergreen:
    name: evergreen
    runs-on: ubuntu-latest

    steps:
      - name: Run evergreen action
        uses: github/evergreen@v1
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ORGANIZATION: <YOUR_ORGANIZATION_GOES_HERE>
```

#### Advanced

```yaml
---
name: Weekly dependabot checks
on:
  workflow_dispatch:
  schedule:
    - cron: '3 2 1 * *'

permissions:
  issues: write

jobs:
  evergreen:
    name: evergreen
    runs-on: ubuntu-latest

    steps:
      - shell: bash
      run: |
        # Get the current date
        current_date=$(date +'%Y-%m-%d')

        # Calculate the previous month
        previous_date=$(date -d "$current_date -7 day" +'%Y-%m-%d')

        echo "$previous_date..$current_date"
        echo "one_week_ago=$previous_date >> "$GITHUB_ENV"

      - name: Run evergreen action
        uses: github/evergreen@v1
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ORGANIZATION: <YOUR_ORGANIZATION_GOES_HERE>
          EXEMPT_REPOS: "org_name/repo_name_1, org_name/repo_name_2"
          TITLE: "Add dependabot configuration"
          BODY: "Please add this dependabot configuration so that we can keep the dependencies in this repo up to date and secure. for help, contact XXX"
          CREATED_AFTER_DATE: ${{ env.one_week_ago }}
          
```

## Local usage without Docker

1. Make sure you have at least Python3.11 installed
1. Copy `.env-example` to `.env`
1. Fill out the `.env` file with a _token_ from a user that has access to the organization to scan (listed below). Tokens should have at least write:org access for organization scanning and write:repository for repository scanning.
1. Fill out the `.env` file with the configuration parameters you want to use
1. `pip3 install -r requirements.txt`
1. Run `python3 ./evergreen.py`, which will output everything in the terminal

## License

[MIT](LICENSE)
