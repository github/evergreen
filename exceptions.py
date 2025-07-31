"""Custom exceptions for the evergreen application."""

import github3.exceptions


class OptionalFileNotFoundError(github3.exceptions.NotFoundError):
    """Exception raised when an optional file is not found.

    This exception inherits from github3.exceptions.NotFoundError but provides
    a more explicit name for cases where missing files are expected and should
    not be treated as errors. This is typically used for optional configuration
    files or dependency files that may not exist in all repositories.

    Args:
        resp: The HTTP response object from the failed request
    """


def check_optional_file(repo, filename):
    """
    Example utility function demonstrating OptionalFileNotFoundError usage.

    This function shows how the new exception type can be used to provide
    more explicit error handling for optional files that may not exist.

    Args:
        repo: GitHub repository object
        filename: Name of the optional file to check

    Returns:
        File contents object if file exists, None if optional file is missing

    Raises:
        OptionalFileNotFoundError: When the file is not found (expected for optional files)
        Other exceptions: For unexpected errors (permissions, network issues, etc.)
    """
    try:
        file_contents = repo.file_contents(filename)
        if file_contents.size > 0:
            return file_contents
        return None
    except github3.exceptions.NotFoundError as e:
        # Re-raise as our more specific exception type for better semantic clarity
        raise OptionalFileNotFoundError(resp=e.response) from e
