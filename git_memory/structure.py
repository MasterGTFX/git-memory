"""
Module for repository structure extraction.
"""

from git import Repo, Blob, InvalidGitRepositoryError, NoSuchPathError
from git.exc import BadName # For invalid commit SHAs

def extract_structure(repo_path: str, commit_sha: str) -> dict:
    """
    Extracts the file structure of a Git repository at a specific commit.

    Args:
        repo_path: Path to the Git repository.
        commit_sha: The SHA of the commit to inspect.

    Returns:
        A dictionary with a single key "files", whose value is a list of
        file paths present in the repository at that commit.
        Example: {"files": ["src/main.py", "README.md"]}

    Raises:
        InvalidGitRepositoryError: If repo_path is not a valid git repository.
        BadName: If the commit_sha is invalid.
        Exception: For other potential git errors.
    """
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        # This case might be caught by typer/CLI entry point already,
        # but good to have defense in depth.
        raise
    except NoSuchPathError:
        raise FileNotFoundError(f"Repository path not found: {repo_path}")


    try:
        commit = repo.commit(commit_sha)
    except BadName:
        # Reraise BadName if commit_sha is invalid
        raise
    except Exception as e:
        # Catch other potential errors during commit loading
        raise RuntimeError(f"Error accessing commit {commit_sha}: {e}") from e

    file_paths = []
    try:
        for item in commit.tree.traverse():
            if isinstance(item, Blob):
                file_paths.append(item.path)
    except Exception as e:
        # Catch errors during tree traversal
        raise RuntimeError(f"Error traversing tree for commit {commit_sha}: {e}") from e

    return {"files": sorted(file_paths)} # Sort for consistent output
