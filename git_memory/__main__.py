import typer
from git_memory.config import Config
from git_memory.history import generate_history

app = typer.Typer(
    help="AI-powered commit-by-commit memory and structure tracking for Git projects."
)

@app.command()
def main(
    repo_path: str = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Path to the Git repository"),
    min_commits: int = typer.Option(Config.min_commits, "--min-commits", help="Group commits by number"),
    min_diff_lines: int | None = typer.Option(Config.min_diff_lines, "--min-diff-lines", help="Minimum diff lines threshold"),
    model_provider: str = typer.Option(Config.model_provider, "--model-provider", help="Model provider (openai or openrouter)"),
    model: str = typer.Option(Config.model, "--model", help="Model name"),
):
    """Generate AI-based git memory for the specified repository."""
    typer.secho(f"Repository: {repo_path}", fg=typer.colors.GREEN)
    typer.secho(f"Group commits by: {min_commits}", fg=typer.colors.BLUE)

    typer.secho("Generating history...", fg=typer.colors.YELLOW)
    generate_history(repo_path, min_commits, min_diff_lines)
    typer.secho("History generation complete. See .history/ directory.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()