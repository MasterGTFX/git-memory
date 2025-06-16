"""Tests for git_memory.history module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import git

from git_memory.history import (
    CommitInfo,
    get_commit_diff,
    create_history_structure,
    save_commit_files,
    save_aggregated_files,
    generate_history,
    display_summary
)
from git_memory.config import Config


class TestCommitInfo:
    """Test cases for CommitInfo class."""
    
    def test_commit_info_creation(self):
        """Test creating CommitInfo from git commit."""
        # Create mock commit
        mock_commit = Mock()
        mock_commit.hexsha = "abc123def456789"
        mock_commit.summary = "Test commit message"
        mock_commit.author.name = "Test Author"
        mock_commit.committed_datetime = datetime(2023, 1, 1, 12, 0, 0)
        
        diff_lines = 42
        diff_text = "sample diff text"
        
        commit_info = CommitInfo(mock_commit, diff_lines, diff_text)
        
        assert commit_info.hash == "abc123def456789"
        assert commit_info.short_hash == "abc123d"
        assert commit_info.message == "Test commit message"
        assert commit_info.author == "Test Author"
        assert commit_info.date == datetime(2023, 1, 1, 12, 0, 0)
        assert commit_info.diff_lines == 42
        assert commit_info.diff_text == "sample diff text"


class TestGetCommitDiff:
    """Test cases for get_commit_diff function."""
    
    def test_get_commit_diff_with_parent(self):
        """Test getting diff for commit with parent."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]
        
        # Mock diff_index
        mock_diff_item = Mock()
        mock_diff_item.diff = b"test diff content"
        mock_diff_index = [mock_diff_item]
        mock_commit.diff.return_value = mock_diff_index
        
        diff_text, diff_lines = get_commit_diff(mock_repo, mock_commit)
        
        assert diff_text == "test diff content"
        assert diff_lines == 1  # One line in diff
        mock_commit.diff.assert_called_once_with(mock_parent, create_patch=True)
    
    def test_get_commit_diff_with_parent_string_diff(self):
        """Test getting diff when diff is string instead of bytes."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]
        
        mock_diff_item = Mock()
        mock_diff_item.diff = "test diff content"
        mock_diff_index = [mock_diff_item]
        mock_commit.diff.return_value = mock_diff_index
        
        diff_text, diff_lines = get_commit_diff(mock_repo, mock_commit)
        
        assert diff_text == "test diff content"
        assert diff_lines == 1
    
    def test_get_commit_diff_initial_commit(self):
        """Test getting diff for initial commit (no parents)."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.parents = []
        mock_commit.hexsha = "abc123"
        mock_commit.summary = "Initial commit"
        
        mock_repo.git.diff.return_value = "initial diff content"
        
        diff_text, diff_lines = get_commit_diff(mock_repo, mock_commit)
        
        assert diff_text == "initial diff content"
        assert diff_lines == 1
        mock_repo.git.diff.assert_called_once_with("4b825dc642cb6eb9a060e54bf8d69288fbee4904", "abc123")
    
    def test_get_commit_diff_initial_commit_git_error(self):
        """Test handling git error for initial commit."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.parents = []
        mock_commit.hexsha = "abc123"
        mock_commit.summary = "Initial commit"
        
        mock_repo.git.diff.side_effect = git.exc.GitCommandError("diff", 1)
        
        diff_text, diff_lines = get_commit_diff(mock_repo, mock_commit)
        
        assert diff_text == "Initial commit: Initial commit"
        assert diff_lines == 1
    
    @patch('git_memory.history.console')
    def test_get_commit_diff_exception_handling(self, mock_console):
        """Test exception handling in get_commit_diff."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.hexsha = "abc123def"
        mock_commit.parents = [Mock()]
        mock_commit.diff.side_effect = Exception("Test error")
        
        diff_text, diff_lines = get_commit_diff(mock_repo, mock_commit)
        
        assert diff_text == ""
        assert diff_lines == 0
        mock_console.print.assert_called_once()


class TestCreateHistoryStructure:
    """Test cases for create_history_structure function."""
    
    def test_create_history_structure(self, temp_dir):
        """Test creating .history directory structure."""
        repo_path = temp_dir
        
        history_dir = create_history_structure(repo_path)
        
        expected_path = repo_path / ".history"
        assert history_dir == expected_path
        assert history_dir.exists()
        assert history_dir.is_dir()
    
    def test_create_history_structure_existing(self, temp_dir):
        """Test creating .history directory when it already exists."""
        repo_path = temp_dir
        existing_history = repo_path / ".history"
        existing_history.mkdir()
        
        history_dir = create_history_structure(repo_path)
        
        assert history_dir == existing_history
        assert history_dir.exists()


class TestSaveCommitFiles:
    """Test cases for save_commit_files function."""
    
    def test_save_commit_files(self, temp_dir, sample_commit_data):
        """Test saving commit files to .history directory."""
        history_dir = temp_dir / ".history"
        history_dir.mkdir()
        
        # Create CommitInfo from sample data
        mock_commit = Mock()
        mock_commit.hexsha = sample_commit_data["hash"]
        mock_commit.summary = sample_commit_data["message"]
        mock_commit.author.name = sample_commit_data["author"]
        mock_commit.committed_datetime = datetime(2023, 1, 1, 12, 0, 0)
        
        commit_info = CommitInfo(
            mock_commit,
            sample_commit_data["diff_lines"],
            sample_commit_data["diff_text"]
        )
        
        save_commit_files(history_dir, commit_info, "openai", "gpt-4o")
        
        commit_dir = history_dir / sample_commit_data["hash"]
        assert commit_dir.exists()
        
        # Check diff.patch file
        diff_file = commit_dir / "diff.patch"
        assert diff_file.exists()
        assert diff_file.read_text() == sample_commit_data["diff_text"]
        
        # Check memory.md file
        memory_file = commit_dir / "memory.md"
        assert memory_file.exists()
        memory_content = memory_file.read_text()
        assert sample_commit_data["short_hash"] in memory_content
        assert sample_commit_data["message"] in memory_content
        assert sample_commit_data["author"] in memory_content
        
        # Check structure.mmd file
        structure_file = commit_dir / "structure.mmd"
        assert structure_file.exists()
        structure_content = structure_file.read_text()
        assert "graph TD" in structure_content
        assert sample_commit_data["short_hash"] in structure_content


class TestSaveAggregatedFiles:
    """Test cases for save_aggregated_files function."""
    
    def test_save_aggregated_files(self, temp_dir):
        """Test saving aggregated history files."""
        history_dir = temp_dir / ".history"
        history_dir.mkdir()
        
        # Create mock commit infos
        mock_commits = []
        for i in range(2):
            mock_commit = Mock()
            mock_commit.hexsha = f"abc{i}23def456"
            mock_commit.summary = f"Test commit {i}"
            mock_commit.author.name = "Test Author"
            mock_commit.committed_datetime = datetime(2023, 1, i+1, 12, 0, 0)
            
            commit_info = CommitInfo(mock_commit, 10 + i, f"diff text {i}")
            mock_commits.append(commit_info)
        
        # Create mock commit memories  
        from git_memory.ai import CommitMemory, CommitChange
        mock_memories = []
        for i in range(2):
            memory = CommitMemory(
                added=[CommitChange(description=f"Added feature {i}", files=[], impact="minor")],
                removed=[],
                changed=[],
                summary=f"Test commit {i}",
                technical_details=""
            )
            mock_memories.append(memory)
        
        save_aggregated_files(history_dir, mock_commits, mock_memories, "openai", "gpt-4o")
        
        # Check history.md
        history_file = history_dir / "history.md"
        assert history_file.exists()
        history_content = history_file.read_text()
        assert "# Git History" in history_content
        assert "Test commit 0" in history_content
        assert "Test commit 1" in history_content
        
        # Check memory.md
        memory_file = history_dir / "memory.md"
        assert memory_file.exists()
        memory_content = memory_file.read_text()
        assert "# Project Memory" in memory_content
        assert "AI memories generated:** 2" in memory_content
        
        # Check structure.mmd
        structure_file = history_dir / "structure.mmd"
        assert structure_file.exists()
        structure_content = structure_file.read_text()
        assert "graph TD" in structure_content


class TestGenerateHistory:
    """Test cases for generate_history function."""
    
    @patch('git_memory.history.save_aggregated_files')
    @patch('git_memory.history.save_commit_files')
    @patch('git_memory.history.display_summary')
    @patch('git_memory.history.console')
    def test_generate_history_success(self, mock_console, mock_display, mock_save_commit, mock_save_agg, mock_git_repo):
        """Test successful history generation."""
        repo_path, repo = mock_git_repo
        
        with patch('git_memory.history.git.Repo') as mock_repo_class:
            mock_repo_class.return_value = repo
            
            generate_history(
                repo_path=repo_path,
                model_provider="openai",
                model="gpt-4o",
                min_diff_lines=None
            )
            
            # Verify repo was opened
            mock_repo_class.assert_called_once_with(repo_path)
            
            # Verify files were saved (called for each commit)
            assert mock_save_commit.call_count >= 1
            mock_save_agg.assert_called_once()
            mock_display.assert_called_once()
    
    @patch('git_memory.history.console')
    def test_generate_history_bare_repo(self, mock_console, temp_dir):
        """Test handling of bare repository."""
        with patch('git_memory.history.git.Repo') as mock_repo_class:
            mock_repo = Mock()
            mock_repo.bare = True
            mock_repo_class.return_value = mock_repo
            
            with pytest.raises(ValueError, match="is bare"):
                generate_history(
                    repo_path=temp_dir,
                    model_provider="openai",
                    model="gpt-4o"
                )
    
    @patch('git_memory.history.console')
    def test_generate_history_invalid_repo(self, mock_console, temp_dir):
        """Test handling of invalid git repository."""
        with patch('git_memory.history.git.Repo') as mock_repo_class:
            mock_repo_class.side_effect = git.exc.InvalidGitRepositoryError()
            
            with pytest.raises(ValueError, match="not a valid Git repository"):
                generate_history(
                    repo_path=temp_dir,
                    model_provider="openai",
                    model="gpt-4o"
                )
    
    @patch('git_memory.history.save_aggregated_files')
    @patch('git_memory.history.save_commit_files')
    @patch('git_memory.history.display_summary')
    @patch('git_memory.history.console')
    def test_generate_history_with_min_diff_filter(self, mock_console, mock_display, mock_save_commit, mock_save_agg, mock_git_repo):
        """Test history generation with min_diff_lines filter."""
        repo_path, repo = mock_git_repo
        
        with patch('git_memory.history.git.Repo') as mock_repo_class:
            mock_repo_class.return_value = repo
            
            # Set high min_diff_lines to filter out commits
            generate_history(
                repo_path=repo_path,
                model_provider="openai",
                model="gpt-4o",
                min_diff_lines=1000  # Very high threshold
            )
            
            # Should still call display_summary even if no commits processed
            mock_display.assert_called_once()


class TestDisplaySummary:
    """Test cases for display_summary function."""
    
    @patch('git_memory.history.console')
    def test_display_summary(self, mock_console, temp_dir):
        """Test displaying processing summary."""
        history_dir = temp_dir / ".history"
        history_dir.mkdir()
        
        # Create mock commit info
        mock_commit = Mock()
        mock_commit.hexsha = "abc123def456"
        mock_commit.summary = "Test commit"
        mock_commit.author.name = "Test Author"
        mock_commit.committed_datetime = datetime(2023, 1, 1, 12, 0, 0)
        
        commit_info = CommitInfo(mock_commit, 50, "diff text")
        processed_commits = [commit_info]
        skipped_count = 2
        
        display_summary(processed_commits, skipped_count, history_dir)
        
        # Verify console.print was called multiple times
        assert mock_console.print.call_count >= 3  # Table, files info, etc.
    
    @patch('git_memory.history.console')
    def test_display_summary_no_commits(self, mock_console, temp_dir):
        """Test displaying summary when no commits were processed."""
        history_dir = temp_dir / ".history"
        history_dir.mkdir()
        
        display_summary([], 5, history_dir)
        
        # Should still display table
        assert mock_console.print.call_count >= 2