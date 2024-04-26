"""This module contains the function to build the dependabot.yml file for a repo"""

import github3


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


def build_dependabot_file(repo, group_dependencies, exempt_ecosystems) -> str | None:
    """
    Build the dependabot.yml file for a repo based on the repo contents

    Args:
        repo: the repository to build the dependabot.yml file for
        group_dependencies: whether to group dependencies in the dependabot.yml file
        exempt_ecosystems: the list of ecosystems to ignore

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
        if (
            repo.file_contents("Gemfile")
            and not bundler_found
            and "bundler" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            bundler_found = True
            dependabot_file += make_dependabot_config("bundler", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("Gemfile.lock")
            and not bundler_found
            and "bundler" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            bundler_found = True
            dependabot_file += make_dependabot_config("bundler", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass

    try:
        if (
            repo.file_contents("package.json")
            and not npm_found
            and "npm" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            npm_found = True
            dependabot_file += make_dependabot_config("npm", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("package-lock.json")
            and not npm_found
            and "npm" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            npm_found = True
            dependabot_file += make_dependabot_config("npm", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("yarn.lock")
            and not npm_found
            and "npm" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            npm_found = True
            dependabot_file += make_dependabot_config("npm", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass

    try:
        if (
            repo.file_contents("requirements.txt")
            and not pip_found
            and "pip" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += make_dependabot_config("pip", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("Pipfile")
            and not pip_found
            and "pip" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += make_dependabot_config("pip", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("Pipfile.lock")
            and not pip_found
            and "pip" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += make_dependabot_config("pip", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("pyproject.toml")
            and not pip_found
            and "pip" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += make_dependabot_config("pip", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("poetry.lock")
            and not pip_found
            and "pip" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            pip_found = True
            dependabot_file += make_dependabot_config("pip", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass

    try:
        if (
            repo.file_contents("Cargo.toml")
            and not cargo_found
            and "cargo" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            cargo_found = True
            dependabot_file += make_dependabot_config("cargo", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("Cargo.lock")
            and not cargo_found
            and "cargo" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            cargo_found = True
            dependabot_file += make_dependabot_config("cargo", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass

    try:
        if (
            repo.file_contents("go.mod")
            and not gomod_found
            and "gomod" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            gomod_found = True
            dependabot_file += make_dependabot_config("gomod", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass

    try:
        if (
            repo.file_contents("composer.json")
            and not composer_found
            and "composer" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            composer_found = True
            dependabot_file += make_dependabot_config("composer", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("composer.lock")
            and not composer_found
            and "composer" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            composer_found = True
            dependabot_file += make_dependabot_config("composer", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass

    try:
        if (
            repo.file_contents("mix.exs")
            and not hex_found
            and "hex" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            hex_found = True
            dependabot_file += make_dependabot_config("mix", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass
    try:
        if (
            repo.file_contents("mix.lock")
            and not hex_found
            and "hex" not in exempt_ecosystems
        ):
            compatible_package_manager_found = True
            hex_found = True
            dependabot_file += make_dependabot_config("mix", group_dependencies)
    except github3.exceptions.NotFoundError:
        pass

    if "github-actions" not in exempt_ecosystems:
        try:
            for file in repo.directory_contents(".github/workflows"):
                if file[0].endswith(".yml") or file[0].endswith(".yaml"):
                    compatible_package_manager_found = True
                    dependabot_file += make_dependabot_config(
                        "github-actions", group_dependencies
                    )
                    break
        except github3.exceptions.NotFoundError:
            pass

    if "docker" not in exempt_ecosystems:
        try:
            if repo.file_contents("Dockerfile") and not docker_found:
                compatible_package_manager_found = True
                docker_found = True
                dependabot_file += make_dependabot_config("docker", group_dependencies)
        except github3.exceptions.NotFoundError:
            pass

    if "nuget" not in exempt_ecosystems:
        try:
            if repo.file_contents(".nuspec") and not nuget_found:
                compatible_package_manager_found = True
                nuget_found = True
                dependabot_file += make_dependabot_config("nuget", group_dependencies)
        except github3.exceptions.NotFoundError:
            pass
        try:
            if repo.file_contents(".csproj") and not nuget_found:
                compatible_package_manager_found = True
                nuget_found = True
                dependabot_file += make_dependabot_config("nuget", group_dependencies)
        except github3.exceptions.NotFoundError:
            pass

    if "terraform" not in exempt_ecosystems:
        try:
            # detect if the repo has a any terraform files
            terraform_files = False
            for file in repo.directory_contents("/"):
                if file[0].endswith(".tf"):
                    terraform_files = True
                    break
            if terraform_files:
                compatible_package_manager_found = True
                dependabot_file += make_dependabot_config(
                    "terraform", group_dependencies
                )
        except github3.exceptions.NotFoundError:
            pass

    if compatible_package_manager_found:
        return dependabot_file
    return None
