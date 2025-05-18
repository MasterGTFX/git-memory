import typer
from git_memory.config import Config
from git_memory.history import generate_history

app = typer.Typer(
    help="AI-powered commit-by-commit memory and structure tracking for Git projects."
)

@app.command()
def main(
    repo_path: str = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Path to the Git repository"),
    commits_per_group: int = typer.Option(Config.commits_per_group, "--commits-per-group", help="Number of commits to include in each group (minimum, except the last group)"),
    min_diff_lines: int | None = typer.Option(Config.min_diff_lines, "--min-diff-lines", help="Minimum diff lines threshold"),
    model_provider: str = typer.Option(Config.model_provider, "--model-provider", help="Model provider (openai or openrouter)"),
    model: str = typer.Option(Config.model, "--model", help="Model name"),
):
    """Generate AI-based git memory for the specified repository."""
    typer.secho(f"Repository: {repo_path}", fg=typer.colors.GREEN)
    typer.secho(f"Group commits by: {commits_per_group}", fg=typer.colors.BLUE)

    typer.secho("Generating history...", fg=typer.colors.YELLOW)
    generate_history(repo_path, commits_per_group, min_diff_lines)
    typer.secho("History generation complete. See .history/ directory.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
