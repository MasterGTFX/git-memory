"""Integration tests for git-memory."""

import pytest
from pathlib import Path
import git
from git_memory.history import generate_history


class TestIntegration:
    """Integration tests for the complete git-memory workflow."""
    
    @pytest.mark.integration
    def test_full_workflow_with_real_repo(self, temp_dir):
        """Test complete workflow with a real git repository."""
        # Create a real git repository
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        repo = git.Repo.init(repo_path)
        
        # Configure git (required for commits)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()
        
        # Create first commit
        file1 = repo_path / "README.md"
        file1.write_text("# Test Project\n\nThis is a test project for git-memory.\n")
        repo.index.add([str(file1)])
        repo.index.commit("Initial commit: Add README")
        
        # Create second commit
        file2 = repo_path / "main.py"
        file2.write_text("""#!/usr/bin/env python3
\"\"\"Main module for test project.\"\"\"

def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
""")
        repo.index.add([str(file2)])
        repo.index.commit("Add main.py with hello world functionality")
        
        # Create third commit - modify existing files
        file1.write_text(file1.read_text() + "\n## Features\n\n- Hello world functionality\n")
        file2.write_text(file2.read_text().replace('print("Hello, world!")', 'print("Hello, git-memory!")'))
        repo.index.add([str(file1), str(file2)])
        repo.index.commit("Update README and modify greeting")
        
        # Run git-memory on the repository
        generate_history(
            repo_path=repo_path,
            model_provider="openai",
            model="gpt-4o",
            min_diff_lines=None
        )
        
        # Verify .history directory was created
        history_dir = repo_path / ".history"
        assert history_dir.exists()
        assert history_dir.is_dir()
        
        # Verify aggregated files exist
        assert (history_dir / "memory.md").exists()
        assert (history_dir / "history.md").exists()
        assert (history_dir / "structure.mmd").exists()
        
        # Verify individual commit directories exist
        commits = list(repo.iter_commits('HEAD'))
        commits.reverse()  # Oldest first
        
        for commit in commits:
            commit_dir = history_dir / commit.hexsha
            assert commit_dir.exists(), f"Commit directory {commit.hexsha} should exist"
            
            # Check individual commit files
            assert (commit_dir / "diff.patch").exists()
            assert (commit_dir / "memory.md").exists()
            assert (commit_dir / "structure.mmd").exists()
            
            # Verify diff.patch has content
            diff_content = (commit_dir / "diff.patch").read_text()
            assert len(diff_content.strip()) > 0, "Diff file should not be empty"
            
            # Verify memory.md has structured content
            memory_content = (commit_dir / "memory.md").read_text()
            assert commit.hexsha in memory_content
            assert commit.summary in memory_content
            assert "Changes Summary" in memory_content
        
        # Verify aggregated memory.md content
        memory_content = (history_dir / "memory.md").read_text()
        assert "Project Memory" in memory_content
        assert f"Total commits processed: {len(commits)}" in memory_content
        
        # Verify aggregated history.md content
        history_content = (history_dir / "history.md").read_text()
        assert "Git History" in history_content
        for commit in commits:
            assert commit.hexsha[:7] in history_content
            assert commit.summary in history_content
    
    @pytest.mark.integration
    def test_workflow_with_min_diff_filter(self, temp_dir):
        """Test workflow with min_diff_lines filter."""
        # Create a real git repository
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        repo = git.Repo.init(repo_path)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()
        
        # Create small commit (should be filtered out)
        small_file = repo_path / "small.txt"
        small_file.write_text("x")
        repo.index.add([str(small_file)])
        repo.index.commit("Small change")
        
        # Create large commit (should be processed)
        large_file = repo_path / "large.txt"
        large_content = "\n".join([f"Line {i}" for i in range(50)])  # 50 lines
        large_file.write_text(large_content)
        repo.index.add([str(large_file)])
        repo.index.commit("Large change with many lines")
        
        # Run git-memory with min_diff_lines filter
        generate_history(
            repo_path=repo_path,
            model_provider="openai",
            model="gpt-4o",
            min_diff_lines=20  # Should filter out the small commit
        )
        
        history_dir = repo_path / ".history"
        assert history_dir.exists()
        
        # Should have fewer commit directories due to filtering
        all_commits = list(repo.iter_commits('HEAD'))
        commit_dirs = [d for d in history_dir.iterdir() if d.is_dir()]
        
        # Should have fewer directories than total commits due to filtering
        assert len(commit_dirs) < len(all_commits)
        
        # Verify the large commit was processed
        large_commit = [c for c in all_commits if "Large change" in c.summary][0]
        assert (history_dir / large_commit.hexsha).exists()
    
    @pytest.mark.integration
    def test_empty_repository_handling(self, temp_dir):
        """Test handling of empty repository."""
        repo_path = temp_dir / "empty_repo"
        repo_path.mkdir()
        
        # Initialize empty repo
        repo = git.Repo.init(repo_path)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()
        
        # Try to run git-memory on empty repo
        generate_history(
            repo_path=repo_path,
            model_provider="openai",
            model="gpt-4o",
            min_diff_lines=None
        )
        
        # Should create .history directory even for empty repo
        history_dir = repo_path / ".history"
        assert history_dir.exists()
        
        # Should create aggregated files even with no commits
        assert (history_dir / "memory.md").exists()
        assert (history_dir / "history.md").exists()
        assert (history_dir / "structure.mmd").exists()
        
        # Verify content indicates no commits
        memory_content = (history_dir / "memory.md").read_text()
        assert "Total commits processed: 0" in memory_content