"""CLI entry point for git-memory."""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

from .config import Config
from .history import generate_history

console = Console()
app = typer.Typer(
    help="AI-powered commit-by-commit memory and structure tracking for Git projects.",
    rich_markup_mode="rich"
)


@app.command()
def main(
    repo_path: Path = typer.Argument(
        ..., 
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Path to the Git repository"
    ),
    model_provider: str = typer.Option(
        Config.model_provider,
        "--model-provider",
        help="Model provider (openai, openrouter, local)"
    ),
    model: str = typer.Option(
        Config.model,
        "--model", 
        help="Model name (e.g., gpt-4o, gemini-2.5-flash-preview)"
    ),
    min_diff_lines: Optional[int] = typer.Option(
        Config.min_diff_lines,
        "--min-diff-lines",
        help="Minimum number of diff lines for a commit to be processed"
    ),
):
    """Generate AI-powered memory and structure tracking for a Git repository."""
    
    # Display startup info
    console.print(Panel.fit(
        f"[bold blue]git-memory v{Config.version}[/]\n"
        f"Processing repository: [cyan]{repo_path}[/]\n"
        f"Model: [green]{model_provider}/{model}[/]\n"
        f"Min diff lines: [yellow]{min_diff_lines or 'None'}[/]",
        title="[bold]Git Memory",
        border_style="blue"
    ))
    
    try:
        # Generate history
        generate_history(
            repo_path=repo_path,
            model_provider=model_provider,
            model=model,
            min_diff_lines=min_diff_lines
        )
        
        console.print("\n[bold green]✅ History generation completed successfully![/]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()