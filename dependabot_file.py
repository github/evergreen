"""This module contains the function to build the dependabot.yml file for a repo"""


import github3


def build_dependabot_file(repo) -> [str | None]:
    """
    Build the dependabot.yml file for a repo based on the repo contents

    Args:
        repo: the repository to build the dependabot.yml file for

    Returns:
        str: the dependabot.yml file for the repo
    """
    compatible_package_manager_found = False
    bundler_found = False
    npm_found = False
    pip_found = False
    cargo_found = False
    gomod_found = False
    composer_found = False
    hex_found = False
    nuget_found = False
    docker_found = False
    dependabot_file = """---
version: 2
updates:
"""
    try:
        if repo.file_contents("Gemfile") and not bundler_found:
            compatible_package_manager_found = True
            bundler_found = True
            dependabot_file += """  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("Gemfile.lock") and not bundler_found:
            compatible_package_manager_found = True
            bundler_found = True
            dependabot_file += """  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents("package.json") and not npm_found:
            compatible_package_manager_found = True
            npm_found = True
            dependabot_file += """  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("package-lock.json") and not npm_found:
            compatible_package_manager_found = True
            npm_found = True
            dependabot_file += """  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("yarn.lock") and not npm_found:
            compatible_package_manager_found = True
            npm_found = True
            dependabot_file += """  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents("requirements.txt") and not pip_found:
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += """  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("Pipfile") and not pip_found:
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += """  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("Pipfile.lock") and not pip_found:
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += """  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("pyproject.toml") and not pip_found:
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += """  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("poetry.lock") and not pip_found:
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += """  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents("Cargo.toml") and not cargo_found:
            compatible_package_manager_found = True
            cargo_found = True
            dependabot_file += """  - package-ecosystem: 'cargo'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("Cargo.lock") and not cargo_found:
            compatible_package_manager_found = True
            cargo_found = True
            dependabot_file += """  - package-ecosystem: 'cargo'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents("go.mod") and not gomod_found:
            compatible_package_manager_found = True
            gomod_found = True
            dependabot_file += """  - package-ecosystem: 'gomod'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents("composer.json") and not composer_found:
            compatible_package_manager_found = True
            composer_found = True
            dependabot_file += """  - package-ecosystem: 'composer'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("composer.lock") and not composer_found:
            compatible_package_manager_found = True
            composer_found = True
            dependabot_file += """  - package-ecosystem: 'composer'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents("mix.exs") and not hex_found:
            compatible_package_manager_found = True
            hex_found = True
            dependabot_file += """  - package-ecosystem: 'hex'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents("mix.lock") and not hex_found:
            compatible_package_manager_found = True
            hex_found = True
            dependabot_file += """  - package-ecosystem: 'hex'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        for file in repo.directory_contents(".github/workflows"):
            if file[0].endswith(".yml") or file[0].endswith(".yaml"):
                compatible_package_manager_found = True
                dependabot_file += """  - package-ecosystem: 'github-actions'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
                break

    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents("Dockerfile") and not docker_found:
            compatible_package_manager_found = True
            docker_found = True
            dependabot_file += """  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        if repo.file_contents(".nuspec") and not nuget_found:
            compatible_package_manager_found = True
            nuget_found = True
            dependabot_file += """  - package-ecosystem: 'nuget'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass
    try:
        if repo.file_contents(".csproj") and not nuget_found:
            compatible_package_manager_found = True
            nuget_found = True
            dependabot_file += """  - package-ecosystem: 'nuget'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    try:
        # detect if the repo has a any terraform files
        terraform_files = False
        for file in repo.directory_contents("/"):
            if file[0].endswith(".tf"):
                terraform_files = True
                break
        if terraform_files:
            compatible_package_manager_found = True
            dependabot_file += """  - package-ecosystem: 'terraform'
    directory: '/'
    schedule:
        interval: 'weekly'
"""
    except github3.exceptions.NotFoundError:
        pass

    if compatible_package_manager_found:
        return dependabot_file
    return None
