"""Pytest configuration and fixtures for git-memory tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import git
from git_memory.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_git_repo(temp_dir):
    """Create a mock Git repository for testing."""
    repo_path = temp_dir / "test_repo"
    repo_path.mkdir()
    
    # Initialize git repo
    repo = git.Repo.init(repo_path)
    
    # Create initial commit
    test_file = repo_path / "test.txt"
    test_file.write_text("Initial content")
    repo.index.add([str(test_file)])
    initial_commit = repo.index.commit("Initial commit")
    
    # Create second commit
    test_file.write_text("Modified content")
    repo.index.add([str(test_file)])
    second_commit = repo.index.commit("Second commit")
    
    # Create third commit with multiple files
    file2 = repo_path / "file2.txt"
    file2.write_text("Second file content")
    test_file.write_text("Modified content again")
    repo.index.add([str(test_file), str(file2)])
    third_commit = repo.index.commit("Add second file and modify first")
    
    return repo_path, repo


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = Mock(spec=Config)
    config.version = "0.1.0"
    config.model_provider = "openai"
    config.model = "gpt-4o"
    config.min_diff_lines = None
    config.history_dir_name = ".history"
    config.openai_api_key = "test-key"
    config.openai_base_url = None
    config.openrouter_api_key = None
    config.openrouter_base_url = "https://openrouter.ai/api/v1"
    config.local_base_url = "http://localhost:11434/v1"
    return config


@pytest.fixture
def sample_commit_data():
    """Sample commit data for testing."""
    return {
        "hash": "abc123def456",
        "short_hash": "abc123d",
        "message": "Test commit message",
        "author": "Test Author",
        "diff_lines": 50,
        "diff_text": """diff --git a/test.txt b/test.txt
index 1234567..abcdefg 100644
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,4 @@
 line 1
 line 2
+new line
 line 3"""
    }


@pytest.fixture
def mock_console():
    """Mock Rich console for testing."""
    from unittest.mock import Mock
    console = Mock()
    console.print = Mock()
    return console