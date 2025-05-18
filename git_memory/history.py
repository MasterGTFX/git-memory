import os
import git
from typing import Optional
# Assuming other necessary imports like ai functions etc.
import typer # Import typer for secho

# Assuming these exist based on summaries and PROJECT.md
# from git_memory.ai import summarize_diff, generate_diagram

# Placeholder for the actual implementation
def generate_history(repo_path: str, min_diff_lines: Optional[int]):
    """
    Walks through the Git repository history, processing commits
    that meet the minimum diff line threshold.

    Args:
        repo_path: Path to the Git repository.
        min_diff_lines: Minimum number of diff lines for a commit to be processed.
                        If None, all commits are processed.
    """
    try:
        repo = git.Repo(repo_path)
        # Ensure the repo is not bare
        if repo.bare:
            typer.secho(f"Error: Repository at {repo_path} is bare.", fg=typer.colors.RED)
            return

        history_dir = os.path.join(repo_path, ".history")
        os.makedirs(history_dir, exist_ok=True)

        # Iterate through commits in reverse chronological order (latest first)
        # Process from oldest to newest for history building
        commits = list(repo.iter_commits('HEAD'))
        commits.reverse() # Process from oldest to newest

        typer.secho(f"Found {len(commits)} commits.", fg=typer.colors.GREEN)

        # TODO: Implement logic to resume from the last processed commit

        processed_count = 0
        skipped_count = 0

        for i, commit in enumerate(commits):
            commit_hash = commit.hexsha
            commit_summary = commit.summary.splitlines()[0] # Get first line of summary

            # Get the diff for the current commit relative to its parent(s)
            # For merge commits, this might need more complex handling
            # For simplicity, let's compare to the first parent
            diff_text = ""
            diff_lines = 0
            if len(commit.parents) > 0:
                # Compare commit to its first parent
                diff_index = commit.diff(commit.parents[0], create_patch=True)
                # FIX: Access the patch text using .patch instead of .diff
                diff_text = diff_index.patch.decode('utf-8', errors='ignore')
                diff_lines = len(diff_text.splitlines())
            else:
                # Initial commit: diff against empty tree
                # This requires a different diff command
                # git diff 4b825dc642cb6eb9a060e54bf8d69288fbee4904 <commit>
                # 4b825dc642cb6eb9a060e54bf8d69288fbee4904 is the hash of the empty tree
                empty_tree_hash = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
                try:
                    # Using repo.git.diff directly returns the patch text as bytes
                    diff_bytes = repo.git.diff(empty_tree_hash, commit_hash, as_bytes=True)
                    diff_text = diff_bytes.decode('utf-8', errors='ignore')
                    diff_lines = len(diff_text.splitlines())
                except git.exc.GitCommandError as e:
                     typer.secho(f"Warning: Could not generate diff for initial commit {commit_hash[:7]}: {e}", fg=typer.colors.YELLOW)
                     diff_text = ""
                     diff_lines = 0


            typer.secho(f"Processing commit {i+1}/{len(commits)}: {commit_hash[:7]} - {commit_summary} ({diff_lines} lines changed)", fg=typer.colors.BLUE)

            # Apply min_diff_lines filter
            if min_diff_lines is not None and diff_lines < min_diff_lines:
                typer.secho(f"  → Skipping: Diff lines ({diff_lines}) below threshold ({min_diff_lines})", fg=typer.colors.YELLOW)
                skipped_count += 1
                # TODO: Track skipped commits
                continue

            processed_count += 1

            # Create directory .history/<commit_hash>/
            commit_dir = os.path.join(history_dir, commit_hash)
            os.makedirs(commit_dir, exist_ok=True)

            # Save diff_text to .history/<commit_hash>/diff.patch
            diff_file_path = os.path.join(commit_dir, "diff.patch")
            with open(diff_file_path, "w", encoding="utf-8") as f:
                 f.write(diff_text)
            typer.secho("  → Saved diff.patch ✅", fg=typer.colors.GREEN)


            # TODO: Call AI functions (summarize_diff, generate_diagram)
            #    - ai.summarize_diff(diff_text) -> memory_content
            #    - ai.generate_diagram(structure_data) -> structure_content (Need to extract structure_data first)

            # Placeholder stubs for memory and structure
            memory_content = f"Memory for commit {commit_hash[:7]}: {commit_summary}\n\n[Diff details...]" # Stub
            structure_content = f"Structure diagram for commit {commit_hash[:7]}\n\n[Mermaid diagram...]" # Stub

            # Save memory_content to .history/<commit_hash>/memory.md
            memory_file_path = os.path.join(commit_dir, "memory.md")
            with open(memory_file_path, "w", encoding="utf-8") as f:
                f.write(memory_content)
            typer.secho("  → Saved memory.md ✅", fg=typer.colors.GREEN)

            # Save structure_content to .history/<commit_hash>/structure.mmd
            structure_file_path = os.path.join(commit_dir, "structure.mmd")
            with open(structure_file_path, "w", encoding="utf-8") as f:
                f.write(structure_content)
            typer.secho("  → Saved structure.mmd ✅", fg=typer.colors.GREEN)

            # TODO: Update the main .history/ files (memory.md, history.md, structure.mmd)
            # This step depends on how the main files are aggregated -
            # perhaps they are generated *after* processing all commits,
            # or incrementally updated. Let's assume incremental for now.
            # For now, these main files are just stubs created at the end.


        # Create aggregated files (stubs for now) - This logic needs refinement
        # based on how aggregation should work (e.g., concatenating all memory.md files)
        typer.secho("\nGenerating aggregated files (stubs)...", fg=typer.colors.YELLOW)
        with open(os.path.join(history_dir, "history.md"), "w", encoding="utf-8") as f:
            f.write("Aggregated History (Stub)\n") # Stub
        with open(os.path.join(history_dir, "memory.md"), "w", encoding="utf-8") as f:
            f.write("Aggregated Memory (Stub)\n") # Stub
        with open(os.path.join(history_dir, "structure.mmd"), "w", encoding="utf-8") as f:
            f.write("Aggregated Structure (Stub)\n") # Stub
        typer.secho("Aggregated files created.", fg=typer.colors.GREEN)


        typer.secho("\nHistory generation complete.", fg=typer.colors.GREEN)
        typer.secho(f"Processed {processed_count} commits.", fg=typer.colors.GREEN)
        if skipped_count > 0:
             typer.secho(f"Skipped {skipped_count} commits (below min_diff_lines threshold).", fg=typer.colors.YELLOW)

        # TODO: Implement summary table output

    except git.exc.InvalidGitRepositoryError:
        typer.secho(f"Error: {repo_path} is not a valid Git repository.", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
        # Optional: print traceback for debugging
        # import traceback
        # traceback.print_exc()

# TODO: Add functions for saving files, calling AI, etc.
# from .ai import summarize_diff, generate_diagram
# from .config import Config
# import time # for simulation
