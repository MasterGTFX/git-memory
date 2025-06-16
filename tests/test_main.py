"""Tests for git_memory.__main__ module (CLI entry point)."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
import typer

from git_memory.__main__ import app, main
from git_memory.config import Config


class TestCLI:
    """Test cases for CLI entry point."""
    
    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()
    
    @patch('git_memory.__main__.generate_history')
    @patch('git_memory.__main__.console')
    def test_main_command_success(self, mock_console, mock_generate_history, temp_dir):
        """Test successful execution of main command."""
        # Create a fake repo directory
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        result = self.runner.invoke(app, [str(repo_path)])
        
        assert result.exit_code == 0
        mock_generate_history.assert_called_once_with(
            repo_path=repo_path,
            model_provider=Config.model_provider,
            model=Config.model,
            min_diff_lines=Config.min_diff_lines
        )
        
        # Check that success message was printed
        mock_console.print.assert_called()
    
    @patch('git_memory.__main__.generate_history')
    @patch('git_memory.__main__.console')
    def test_main_command_with_options(self, mock_console, mock_generate_history, temp_dir):
        """Test main command with custom options."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        result = self.runner.invoke(app, [
            str(repo_path),
            "--model-provider", "openrouter",
            "--model", "gpt-3.5-turbo",
            "--min-diff-lines", "50"
        ])
        
        assert result.exit_code == 0
        mock_generate_history.assert_called_once_with(
            repo_path=repo_path,
            model_provider="openrouter",
            model="gpt-3.5-turbo",
            min_diff_lines=50
        )
    
    @patch('git_memory.__main__.generate_history')
    @patch('git_memory.__main__.console')
    def test_main_command_exception_handling(self, mock_console, mock_generate_history, temp_dir):
        """Test exception handling in main command."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        # Make generate_history raise an exception
        mock_generate_history.side_effect = ValueError("Test error")
        
        result = self.runner.invoke(app, [str(repo_path)])
        
        assert result.exit_code == 1
        mock_console.print.assert_called()
        # Check that error message was printed
        error_calls = [call for call in mock_console.print.call_args_list 
                      if len(call[0]) > 0 and "Error" in str(call[0][0])]
        assert len(error_calls) > 0
    
    def test_main_command_nonexistent_path(self):
        """Test main command with non-existent repository path."""
        result = self.runner.invoke(app, ["/nonexistent/path"])
        
        assert result.exit_code != 0
        # Typer should handle this path validation error
    
    @patch('git_memory.__main__.generate_history')
    @patch('git_memory.__main__.console')
    def test_main_command_startup_info(self, mock_console, mock_generate_history, temp_dir):
        """Test that startup information is displayed."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        result = self.runner.invoke(app, [str(repo_path)])
        
        assert result.exit_code == 0
        
        # Check that startup panel was printed
        panel_calls = [call for call in mock_console.print.call_args_list]
        assert len(panel_calls) >= 2  # At least startup panel and success message
    
    @patch('git_memory.__main__.generate_history')
    @patch('git_memory.__main__.console')
    def test_main_function_direct_call(self, mock_console, mock_generate_history, temp_dir):
        """Test calling main function directly (not through typer)."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        # Test calling main function directly
        main(
            repo_path=repo_path,
            model_provider="openai",
            model="gpt-4o",
            min_diff_lines=None
        )
        
        mock_generate_history.assert_called_once_with(
            repo_path=repo_path,
            model_provider="openai",
            model="gpt-4o",
            min_diff_lines=None
        )
    
    @patch('git_memory.__main__.generate_history')
    @patch('git_memory.__main__.console')
    def test_main_function_exception_raises_typer_exit(self, mock_console, mock_generate_history, temp_dir):
        """Test that exceptions in main function raise typer.Exit."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        mock_generate_history.side_effect = ValueError("Test error")
        
        with pytest.raises(typer.Exit) as exc_info:
            main(
                repo_path=repo_path,
                model_provider="openai",
                model="gpt-4o",
                min_diff_lines=None
            )
        
        assert exc_info.value.exit_code == 1
    
    def test_app_help(self):
        """Test that app help is displayed correctly."""
        result = self.runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "AI-powered commit-by-commit memory" in result.stdout
        assert "--model-provider" in result.stdout
        assert "--model" in result.stdout
        assert "--min-diff-lines" in result.stdout
    
    @patch('git_memory.__main__.generate_history')
    @patch('git_memory.__main__.console')
    def test_min_diff_lines_none_when_not_specified(self, mock_console, mock_generate_history, temp_dir):
        """Test that min_diff_lines is None when not specified."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        result = self.runner.invoke(app, [str(repo_path)])
        
        assert result.exit_code == 0
        args, kwargs = mock_generate_history.call_args
        assert kwargs['min_diff_lines'] is None