"""
History generation stub for git-memory.
"""

import os
from git import Repo
# import typer # No longer needed for secho/echo
import openai # For openai.APIError
from git.exc import BadName # For extract_structure error handling
from rich.console import Console

from git_memory.ai import summarize_diff, generate_diagram
from git_memory.structure import extract_structure
from git_memory.config import Config 

# Initialize Rich Console for this module
console = Console(stderr=True) # Direct error messages to stderr

def _process_commit_group(
    repo: Repo,
    group: list, # list of Commit objects
    history_dir: str,
    repo_path: str, # needed for extract_structure
    min_diff_lines: int | None,
) -> bool:
    """
"""
History generation stub for git-memory.
"""

import os
import time # For timing
from enum import Enum, auto

from git import Repo
import openai # For openai.APIError
from git.exc import BadName # For extract_structure error handling
from rich.console import Console

from git_memory.ai import summarize_diff, generate_diagram
from git_memory.structure import extract_structure
from git_memory.config import Config 

# Initialize Rich Console for this module
console = Console(stderr=True) # Direct error messages to stderr
from rich.progress import Progress, TaskID # For type hinting
from typing import Optional, List, Dict, Any # For type hinting

class ProcessGroupStatus(Enum):
    PROCESSED = auto()
    SKIPPED_EXISTING = auto()
    SKIPPED_DIFF_LINES = auto()

def get_commit_groups_info(repo_path: str, min_commits_per_group: int) -> Dict[str, Any]:
    """
    Calculates the total number of commit groups and retrieves all chronological, non-merge commits.
    """
    try:
        repo = Repo(repo_path)
    except Exception as e:
        # This error will be handled by the caller in __main__.py
        return {"total_groups": 0, "all_commits_list": [], "error": str(e)}

    all_commits_list: List[Any] = list(repo.iter_commits(reverse=True, no_merges=True))
    
    if not all_commits_list:
        return {"total_groups": 0, "all_commits_list": [], "error": None}
    
    total_groups = (len(all_commits_list) + min_commits_per_group - 1) // min_commits_per_group
    return {"total_groups": total_groups, "all_commits_list": all_commits_list, "error": None}


def _process_commit_group(
    repo: Repo,
    group: list, 
    history_dir: str,
    repo_path: str, 
    min_diff_lines: int | None,
    progress: Optional[Progress] = None, # Added for progress.print
) -> ProcessGroupStatus:
    """
    Processes a group of commits: calculates cumulative diff, generates summary and diagram.
    Returns a ProcessGroupStatus indicating the outcome.
    """
    first_commit_in_group = group[0]
    last_commit_in_group = group[-1]
    group_representative_sha = last_commit_in_group.hexsha
    short_sha = group_representative_sha[:7]
    commit_message_short = last_commit_in_group.summary 

    commit_dir = os.path.join(history_dir, group_representative_sha)

    if os.path.exists(commit_dir):
        (progress.print if progress else console.print)(
            f"Skipping already processed commit group ending in [cyan]{short_sha}[/cyan] (directory exists).",
            style="dim"
        )
        return ProcessGroupStatus.SKIPPED_EXISTING
    
    (progress.print if progress else console.print)(
        f"Processing group ending in [b]{short_sha}[/b] ([italic]{commit_message_short}[/italic])..."
    )

    if first_commit_in_group.parents:
        diff_start_point = first_commit_in_group.parents[0].hexsha
    else:
        diff_start_point = repo.git.hash_object('/dev/null', t='tree')

    diff_text = repo.git.diff(diff_start_point, last_commit_in_group.hexsha)

    if min_diff_lines is not None:
        num_lines = len(diff_text.splitlines())
        if num_lines < min_diff_lines:
            (progress.print if progress else console.print)(
                f"Skipping commit group [cyan]{short_sha}[/cyan], "
                f"diff lines {num_lines} < {min_diff_lines}.",
                style="yellow dim"
            )
            return ProcessGroupStatus.SKIPPED_DIFF_LINES

    os.makedirs(commit_dir, exist_ok=True)

    with open(os.path.join(commit_dir, "diff.patch"), "w", encoding="utf-8") as f:
        f.write(diff_text)

    summary_content = ""
    # API Key Check: Placed here as it affects AI dependent parts.
    # If API key is missing, we'll write placeholders but still mark group as "processed"
    # because diff.patch is created. If full skip is desired, this logic would change.
    api_key_present = bool(Config.api_key)

    try:
        if not diff_text.strip():
            summary_content = f"# Memory for commit group ending in {group_representative_sha}\n\n_No changes in this commit group to summarize._\n"
        elif not api_key_present:
            summary_content = f"# AI Summary Error for commit group {group_representative_sha}\n\nOpenAI API key not set. Cannot generate summary.\n"
        else:
            ai_summary = summarize_diff(diff_text)
            summary_content = f"# Memory for commit group ending in {group_representative_sha}\n\n{ai_summary}\n"
    except ValueError as e: # Typically from API key issues in summarize_diff if not caught by `api_key_present`
        error_message = f"Could not generate summary for group [cyan]{short_sha}[/cyan] (ValueError): {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        summary_content = f"# AI Summary Error for commit group {group_representative_sha}\n\n{error_message}\n"
    except FileNotFoundError as e:
        error_message = f"Could not generate summary for group [cyan]{short_sha}[/cyan] (FileNotFoundError): {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        summary_content = f"# AI Summary Error for commit group {group_representative_sha}\n\n{error_message}\n"
    except openai.APIError as e:
        error_message = f"OpenAI API error while summarizing diff for group [cyan]{short_sha}[/cyan]: {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        summary_content = f"# AI Summary Error for commit group {group_representative_sha}\n\n{error_message}\n"
    except RuntimeError as e:
        error_message = f"Failed to generate summary for group [cyan]{short_sha}[/cyan] (RuntimeError): {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        summary_content = f"# AI Summary Error for commit group {group_representative_sha}\n\n{error_message}\n"
    except Exception as e:
        error_message = f"An unexpected error occurred while generating summary for group [cyan]{short_sha}[/cyan]: {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        summary_content = f"# AI Summary Error for commit group {group_representative_sha}\n\n{error_message}\n"
    
    with open(os.path.join(commit_dir, "memory.md"), "w", encoding="utf-8") as f:
        f.write(summary_content)

    diagram_content = ""
    try:
        structure_data = extract_structure(repo_path, group_representative_sha)
        if not api_key_present:
            diagram_content = f"%% AI Diagram Error for group {group_representative_sha}: OpenAI API key not found. Cannot generate diagram. %%"
        else:
            diagram_content = generate_diagram(structure_data)
    except BadName as e:
        error_message = f"Error extracting structure for group [cyan]{short_sha}[/cyan] (BadName): {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        diagram_content = f"%% Error extracting structure for group {group_representative_sha}: {e} %%"
    except FileNotFoundError as e: # From extract_structure or generate_diagram
        error_message = f"Could not generate diagram for group [cyan]{short_sha}[/cyan] (FileNotFoundError): {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        diagram_content = f"%% AI Diagram Error for group {group_representative_sha}: File not found - {e} %%"
    except ValueError as e: # From generate_diagram (API key)
        error_message = f"Configuration or value error generating diagram for group [cyan]{short_sha}[/cyan] (ValueError): {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        diagram_content = f"%% AI Diagram Error for group {group_representative_sha}: {e} %%"
    except openai.APIError as e:
        error_message = f"OpenAI API error while generating diagram for group [cyan]{short_sha}[/cyan]: {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        diagram_content = f"%% AI Diagram Error for group {group_representative_sha}: OpenAI API Error - {e} %%"
    except RuntimeError as e: # From extract_structure or generate_diagram
        error_message = f"Failed to generate diagram for group [cyan]{short_sha}[/cyan] (RuntimeError): {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        diagram_content = f"%% AI Diagram Error for group {group_representative_sha}: {e} %%"
    except Exception as e:
        error_message = f"An unexpected error occurred while generating diagram for group [cyan]{short_sha}[/cyan]: {e}"
        console.print(f"[bold red]Error:[/bold red] {error_message}")
        diagram_content = f"%% AI Diagram Error for group {group_representative_sha}: Unexpected error - {e} %%"

    with open(os.path.join(commit_dir, "structure.mmd"), "w", encoding="utf-8") as f:
        f.write(diagram_content)
    
    return ProcessGroupStatus.PROCESSED


def generate_history(repo_path: str, min_commits_per_group: int, min_diff_lines: int | None) -> dict:
    """
    Walk through commits in groups, generate history files for each group, including AI summaries and diagrams.
    Commits are processed in chronological order (oldest to newest).
    Returns a dictionary of statistics about the generation process.
    """
    start_time = time.perf_counter()
    stats = {
        "groups_processed": 0,
        "groups_skipped_existing": 0,
        "groups_skipped_diff_lines": 0,
        "total_groups_identified": total_groups_count, # Use the count from get_commit_groups_info
        "time_taken": 0.0
    }

    # Repo object is created here. If __main__ creates it for get_commit_groups_info,
    # it could be passed down to avoid re-creating. For now, keep it simple.
    try:
        repo = Repo(repo_path)
    except Exception as e:
        console.print(f"[bold red]Error loading Git repository at {repo_path}:[/bold red] {e}")
        stats["time_taken"] = time.perf_counter() - start_time
        return stats 

    history_dir = os.path.join(os.getcwd(), ".history")
    os.makedirs(history_dir, exist_ok=True)

    # all_commits_list is now passed as a parameter
    if not all_commits_list:
        console.print("No commits found to process (received empty list).") # Should be caught by caller
        stats["time_taken"] = time.perf_counter() - start_time
        return stats
    
    for i in range(0, len(all_commits_list), min_commits_per_group):
        group = all_commits_list[i:i + min_commits_per_group]
        if not group: 
            continue
        
        # Pass progress to _process_commit_group
        status = _process_commit_group(repo, group, history_dir, repo_path, min_diff_lines, progress)
        
        if status == ProcessGroupStatus.PROCESSED:
            stats["groups_processed"] += 1
        elif status == ProcessGroupStatus.SKIPPED_EXISTING:
            stats["groups_skipped_existing"] += 1
        elif status == ProcessGroupStatus.SKIPPED_DIFF_LINES:
            stats["groups_skipped_diff_lines"] += 1
        
        if progress and main_task_id is not None:
            progress.update(main_task_id, advance=1)

    # Console messages about overall processing are now handled by __main__.py based on returned stats.
    # For example:
    # if stats["groups_processed"] == 0 and (stats["groups_skipped_existing"] > 0 or stats["groups_skipped_diff_lines"] > 0) :
    #      console.print("No new commit groups were processed. All identified groups were skipped.", style="yellow")
    # elif stats["groups_processed"] > 0:
    #     console.print(f"Successfully processed [b]{stats['groups_processed']}[/b] new commit group(s).", style="green")

    console.print("\nGenerating aggregated history files...")


    console.print("\nGenerating aggregated history files...")

    processed_group_shas = sorted([
        d for d in os.listdir(history_dir) 
        if os.path.isdir(os.path.join(history_dir, d)) and len(d) == 40 
    ])

    aggregated_memory_content = []
    for group_sha in processed_group_shas:
        individual_memory_path = os.path.join(history_dir, group_sha, "memory.md")
        if os.path.exists(individual_memory_path):
            with open(individual_memory_path, "r", encoding="utf-8") as f:
                content = f.read()
            aggregated_memory_content.append(f"## Commit Group: {group_sha}\n\n{content}\n\n---\n")
        else:
            aggregated_memory_content.append(f"## Commit Group: {group_sha}\n\n_Memory file not found._\n\n---\n")

    aggregated_memory_file_path = os.path.join(history_dir, "memory.md")
    if not aggregated_memory_content:
        with open(aggregated_memory_file_path, "w", encoding="utf-8") as f:
            f.write("# No history generated or processed yet.\n")
    else:
        with open(aggregated_memory_file_path, "w", encoding="utf-8") as f:
            f.write("".join(aggregated_memory_content))
    console.print(f"Aggregated memory written to [cyan]{aggregated_memory_file_path}[/cyan]")

    aggregated_structure_file_path = os.path.join(history_dir, "structure.mmd")
    if processed_group_shas:
        latest_group_sha = processed_group_shas[-1] 
        latest_structure_path = os.path.join(history_dir, latest_group_sha, "structure.mmd")
        if os.path.exists(latest_structure_path):
            with open(latest_structure_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(aggregated_structure_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            console.print(f"Aggregated structure (from group [cyan]{latest_group_sha[:7]}[/cyan]) written to [cyan]{aggregated_structure_file_path}[/cyan]")
        else:
            with open(aggregated_structure_file_path, "w", encoding="utf-8") as f:
                f.write(f"%% Latest structure.mmd for group {latest_group_sha} not found. %%")
            console.print(f"Latest structure.mmd for group [cyan]{latest_group_sha[:7]}[/cyan] not found. Placeholder written.", style="yellow")
    else:
        with open(aggregated_structure_file_path, "w", encoding="utf-8") as f:
            f.write("%% No structure diagram available as no groups were processed. %%")
        console.print(f"No structure diagram available. Placeholder written to [cyan]{aggregated_structure_file_path}[/cyan]")

    aggregated_patch_content = []
    for group_sha in processed_group_shas:
        individual_patch_path = os.path.join(history_dir, group_sha, "diff.patch")
        if os.path.exists(individual_patch_path):
            with open(individual_patch_path, "r", encoding="utf-8") as f:
                content = f.read()
            aggregated_patch_content.append(f"### Diff for commit group ending in `{group_sha}`\n\n```diff\n{content}\n```\n\n---\n")
        else:
            aggregated_patch_content.append(f"### Diff for commit group ending in `{group_sha}`\n\n_Patch file not found._\n\n---\n")
            
    aggregated_history_file_path = os.path.join(history_dir, "history.md")
    if not aggregated_patch_content:
        with open(aggregated_history_file_path, "w", encoding="utf-8") as f:
            f.write("# No patches recorded or processed yet.\n")
    else:
        with open(aggregated_history_file_path, "w", encoding="utf-8") as f:
            f.write("".join(aggregated_patch_content))
    console.print(f"Aggregated history (patches) written to [cyan]{aggregated_history_file_path}[/cyan]")

    stats["time_taken"] = time.perf_counter() - start_time
    return stats