import os
import git
from typing import List, Optional
from git_memory.ai import summarize_diff, generate_diagram # Assuming these exist based on summaries
import typer # Import typer for secho

def generate_history(repo_path: str, commits_per_group: int, min_diff_lines: Optional[int]):
    """
    Generates the .history directory with commit group information.
    """
    repo = git.Repo(repo_path)
    history_dir = os.path.join(repo_path, ".history")

    # Ensure .history directory exists
    os.makedirs(history_dir, exist_ok=True)

    # Get all commits in reverse chronological order
    all_commits = list(repo.iter_commits())
    all_commits.reverse() # Process chronologically

    # Group commits
    commit_groups = []
    current_group = []
    for commit in all_commits:
        current_group.append(commit)
        # Check if the current group size meets the minimum or if it's the last commit
        if len(current_group) >= commits_per_group or commit == all_commits[-1]:
            # Calculate diff for the potential group
            # Note: Diff calculation here is just for potential min_diff_lines check,
            # the actual diff saved is calculated later for the final group.
            # This part could be optimized if min_diff_lines check is not needed here.
            first_commit_in_group_temp = current_group[0]
            last_commit_in_group_temp = current_group[-1]
            parent_of_group_temp = last_commit_in_group_temp.parents[0] if last_commit_in_group_temp.parents else None
            diff_temp = repo.git.diff(parent_of_group_temp, first_commit_in_group_temp.hexsha)

            # Check min_diff_lines threshold (if specified)
            # NOTE: min_diff_lines logic is not implemented yet.
            # This is where you would check len(diff_temp.splitlines()) >= min_diff_lines
            # If the check fails, you might continue adding commits to current_group
            # instead of finalizing the group here.

            # Add the group if it meets criteria (currently just size)
            commit_groups.append(current_group)
            current_group = [] # Start a new group

    # Process each commit group
    for i, commit_group in enumerate(commit_groups):
        # commit_group is already in chronological order
        first_commit_in_group = commit_group[-1] # Newest commit in this chronological group
        last_commit_in_group = commit_group[0] # Oldest commit in this chronological group

        # Use the hash of the oldest commit in the group for the directory name
        group_dir_name = last_commit_in_group.hexsha
        group_dir = os.path.join(history_dir, group_dir_name)
        os.makedirs(group_dir, exist_ok=True)

        # Corrected print statement to show the range of commits
        typer.secho(f"Processing group {i+1}/{len(commit_groups)}: {last_commit_in_group.hexsha}..{first_commit_in_group.hexsha} ({len(commit_group)} commits)...", fg=typer.colors.BLUE)

        # Calculate the diff from the parent of the oldest commit to the newest commit in the group.
        # If parent_of_group is None (initial commit group), diff is from empty tree to first_commit_in_group.
        parent_of_group = last_commit_in_group.parents[0] if last_commit_in_group.parents else None
        diff = repo.git.diff(parent_of_group, first_commit_in_group.hexsha)

        # Save the diff
        with open(os.path.join(group_dir, "diff.patch"), "w", encoding="utf-8") as f:
             f.write(diff)

        # Generate and save memory (stub for now)
        # memory_content = summarize_diff(diff) # Placeholder
        memory_content = f"Memory for commits {last_commit_in_group.hexsha}..{first_commit_in_group.hexsha}" # Stub
        with open(os.path.join(group_dir, "memory.md"), "w", encoding="utf-8") as f:
            f.write(memory_content)

        # Generate and save structure (stub for now)
        # structure_content = generate_diagram(...) # Placeholder
        structure_content = f"Structure diagram for commits {last_commit_in_group.hexsha}..{first_commit_in_group.hexsha}" # Stub
        with open(os.path.join(group_dir, "structure.mmd"), "w", encoding="utf-8") as f:
            f.write(structure_content)

    # Create aggregated files (stubs for now)
    with open(os.path.join(history_dir, "history.md"), "w", encoding="utf-8") as f:
        f.write("Aggregated History\n") # Stub
    with open(os.path.join(history_dir, "memory.md"), "w", encoding="utf-8") as f:
        f.write("Aggregated Memory\n") # Stub
    with open(os.path.join(history_dir, "structure.mmd"), "w", encoding="utf-8") as f:
        f.write("Aggregated Structure\n") # Stub
