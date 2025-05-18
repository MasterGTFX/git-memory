import typer
from typing import Optional

from .config import Config
from .history import generate_history

app = typer.Typer(
    help="AI-powered commit-by-commit memory and structure tracking for Git projects."
)

@app.command()
def main(
    repo_path: str = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Path to the Git repository."),
    min_diff_lines: int | None = typer.Option(Config.min_diff_lines, "--min-diff-lines", help="Minimum number of diff lines for a commit to be processed."),
    model_provider: str = typer.Option(Config.model_provider, "--model-provider", help="Model provider (e.g., openai, openrouter)."),
    model: str = typer.Option(Config.model, "--model", help="Model name"),
):
    """
    Generates AI-powered memory and structure tracking for a Git repository.
    """
    typer.echo(f"Processing repository: {repo_path}")
    typer.echo(f"Minimum diff lines: {min_diff_lines}")
    typer.echo(f"Model provider: {model_provider}")
    typer.echo(f"Model: {model}")

    # Call the history generation function
    generate_history(repo_path=repo_path, min_diff_lines=min_diff_lines)

if __name__ == "__main__":
    app()
