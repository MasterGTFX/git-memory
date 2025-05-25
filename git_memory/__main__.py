import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress
from rich.table import Table # Added for summary table
import time

from git_memory.config import Config
from git_memory.history import generate_history, get_commit_groups_info

app = typer.Typer(
    help="AI-powered commit-by-commit memory and structure tracking for Git projects."
)

console = Console()

@app.command()
def main(
    repo_path: str = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Path to the Git repository"),
    min_commits_per_group: int = typer.Option(Config.min_commits, "--min-commits", help="Number of commits to group together"),
    min_diff_lines: int | None = typer.Option(Config.min_diff_lines, "--min-diff-lines", help="Minimum cumulative diff lines to process a group"),
    # model_provider: str = typer.Option(Config.model_provider, "--model-provider", help="Model provider (openai or openrouter)"), # Placeholder, not used by generate_history yet
    # model: str = typer.Option(Config.model, "--model", help="Model name"), # Placeholder, not used by generate_history yet
):
    """Generate AI-based git memory for the specified repository."""
    
    # Update Config with CLI options if they are different from defaults
    # This is important if generate_history or other modules read directly from Config
    Config.min_commits = min_commits_per_group
    Config.min_diff_lines = min_diff_lines
    # Config.model_provider = model_provider # If these were to be used
    # Config.model = model # If these were to be used

    param_text = Text.assemble(
        ("Repository: ", "bold cyan"), (repo_path, "white"), "\n",
        ("Min Commits per Group: ", "bold cyan"), (str(min_commits_per_group), "white"), "\n",
        ("Min Diff Lines per Group: ", "bold cyan"), (str(min_diff_lines) if min_diff_lines is not None else "Not set", "white"), "\n",
        # ("Model Provider: ", "bold cyan"), (model_provider, "white"), "\n", # Placeholder
        # ("Model: ", "bold cyan"), (model, "white") # Placeholder
    )
    console.print(Panel(param_text, title="[bold yellow]Git-Memory Parameters[/bold yellow]", expand=False))

    console.print("\n[yellow]Preparing history generation...[/yellow]")
    start_time = time.perf_counter()

    groups_info = get_commit_groups_info(repo_path, min_commits_per_group)
    if groups_info["error"]:
        console.print(f"[bold red]Error preparing commit groups:[/bold red] {groups_info['error']}")
        raise typer.Exit(code=1)

    total_groups = groups_info["total_groups"]
    all_commits_list = groups_info["all_commits_list"]

    if total_groups == 0:
        console.print("[yellow]No commit groups identified to process.[/yellow]")
        # Initialize stats for empty run for consistency if table is shown
        stats = {
            "groups_processed": 0, "groups_skipped_existing": 0, 
            "groups_skipped_diff_lines": 0, "total_groups_identified": 0, 
            "time_taken": time.perf_counter() - start_time
        }
    else:
        console.print(f"Identified [cyan]{total_groups}[/cyan] commit group(s) to process.")
        console.print("\n[yellow]Starting history generation...[/yellow]")
        try:
            with Progress(console=console, transient=True) as progress: # transient=True cleans up progress on exit
                main_task_id = progress.add_task(
                    f"[cyan]Processing commit history ({total_groups} groups)...[/cyan]", 
                    total=total_groups
                )
                stats = generate_history(
                    repo_path, 
                    min_commits_per_group, 
                    min_diff_lines,
                    all_commits_list, # Pass the fetched list
                    total_groups,     # Pass the total count
                    progress=progress,
                    main_task_id=main_task_id
                )
        except Exception as e:
            console.print(f"[bold red]An error occurred during history generation:[/bold red]\n{e}")
            console.print_exception(show_locals=False) # show_locals=True can be verbose
            raise typer.Exit(code=1)
        
    # end_time = time.perf_counter() # time_taken is now part of stats from generate_history
    # time_taken = stats.get("time_taken", end_time - start_time) # This is now correctly handled by stats["time_taken"]

    console.print("\n[bold green]History generation process finished.[/bold green]")
    
    # Display Summary Table
    summary_table = Table(title="[bold magenta]Git-Memory Run Summary[/bold magenta]", show_header=True, header_style="bold blue")
    summary_table.add_column("Metric", style="cyan", no_wrap=True, width=35)
    summary_table.add_column("Value", style="magenta", justify="right")

    summary_table.add_row("Total Commit Groups Identified", str(stats.get("total_groups_identified", "N/A")))
    summary_table.add_row("Commit Groups Processed", f"[green]{stats.get('groups_processed', 'N/A')}[/green]")
    summary_table.add_row("Groups Skipped (Already Existed)", f"[yellow]{stats.get('groups_skipped_existing', 'N/A')}[/yellow]")
    summary_table.add_row("Groups Skipped (Diff Lines Threshold)", f"[yellow]{stats.get('groups_skipped_diff_lines', 'N/A')}[/yellow]")
    summary_table.add_row("Total Time Taken", f"{stats.get('time_taken', 0.0):.2f}s")
    
    console.print(summary_table)
    console.print(f"Output files are in the [cyan].history/[/cyan] directory.")


if __name__ == "__main__":
    app()