"""
History generation stub for git-memory.
"""

import os
from git import Repo

def generate_history(repo_path: str, min_commits: int, min_diff_lines: int | None) -> None:
    """
    Walk through commits and generate stub history files for each commit.
    """
    repo = Repo(repo_path)
    history_dir = os.path.join(os.getcwd(), ".history")
    os.makedirs(history_dir, exist_ok=True)

    commits = list(repo.iter_commits(max_count=min_commits))
    for commit in commits:
        commit_dir = os.path.join(history_dir, commit.hexsha)
        os.makedirs(commit_dir, exist_ok=True)

        # Write dummy memory
        with open(os.path.join(commit_dir, "memory.md"), "w") as f:
            f.write(f"# Memory for commit {commit.hexsha}\n\n_Dummy memory_\n")

        # Write dummy structure diagram
        with open(os.path.join(commit_dir, "structure.mmd"), "w") as f:
            f.write(f"%% Dummy diagram for commit {commit.hexsha}\n")

        # Write diff patch
        parent = commit.parents[0] if commit.parents else None
        diff = repo.git.diff(parent, commit.hexsha)
        with open(os.path.join(commit_dir, "diff.patch"), "w", encoding="utf-8") as f:
            f.write(diff)

    # Stub aggregated files
    with open(os.path.join(history_dir, "memory.md"), "w") as f:
        f.write("## Dummy aggregated memory\n")

    with open(os.path.join(history_dir, "structure.mmd"), "w") as f:
        f.write("%% Dummy aggregated diagram\n")

    with open(os.path.join(history_dir, "history.md"), "w") as f:
        f.write("## Dummy aggregated patches\n")