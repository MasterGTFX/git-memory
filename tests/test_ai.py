"""Tests for the AI module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from git_memory.ai import (
    CommitChange,
    CommitMemory,
    ProjectMemory,
    InstructorAIClient,
    create_ai_client,
    summarize_diff,
    generate_project_memory,
    generate_diagram
)


class TestCommitChange:
    """Test CommitChange Pydantic model."""
    
    def test_commit_change_creation(self):
        """Test creating a CommitChange object."""
        change = CommitChange(
            description="Added user authentication",
            files=["auth.py", "models.py"],
            impact="major"
        )
        
        assert change.description == "Added user authentication"
        assert change.files == ["auth.py", "models.py"]
        assert change.impact == "major"
    
    def test_commit_change_defaults(self):
        """Test CommitChange with default values."""
        change = CommitChange(
            description="Fixed bug",
            impact="minor"
        )
        
        assert change.description == "Fixed bug"
        assert change.files == []
        assert change.impact == "minor"


class TestCommitMemory:
    """Test CommitMemory Pydantic model."""
    
    def test_commit_memory_creation(self):
        """Test creating a CommitMemory object."""
        added_change = CommitChange(
            description="Added login function",
            files=["auth.py"],
            impact="major"
        )
        
        memory = CommitMemory(
            added=[added_change],
            removed=[],
            changed=[],
            summary="Implement user authentication system",
            technical_details="Uses JWT tokens for session management"
        )
        
        assert len(memory.added) == 1
        assert memory.added[0].description == "Added login function"
        assert memory.summary == "Implement user authentication system"
        assert memory.technical_details == "Uses JWT tokens for session management"
    
    def test_commit_memory_defaults(self):
        """Test CommitMemory with default values."""
        memory = CommitMemory(
            summary="Simple fix"
        )
        
        assert memory.added == []
        assert memory.removed == []
        assert memory.changed == []
        assert memory.summary == "Simple fix"
        assert memory.technical_details == ""


class TestProjectMemory:
    """Test ProjectMemory Pydantic model."""
    
    def test_project_memory_creation(self):
        """Test creating a ProjectMemory object."""
        memory = ProjectMemory(
            major_features=["Authentication", "User management"],
            architecture_evolution=["Added MVC pattern", "Introduced database layer"],
            key_decisions=["Chose Flask over Django", "Used PostgreSQL"],
            current_state="Stable web application with user management",
            next_steps=["Add API endpoints", "Implement caching"]
        )
        
        assert len(memory.major_features) == 2
        assert "Authentication" in memory.major_features
        assert memory.current_state == "Stable web application with user management"
        assert len(memory.next_steps) == 2


@pytest.fixture
def mock_instructor_client():
    """Create a mock instructor client."""
    mock_client = Mock()
    return mock_client


@pytest.fixture
def sample_commit_memory():
    """Create sample CommitMemory for testing."""
    return CommitMemory(
        added=[CommitChange(
            description="Added authentication system",
            files=["auth.py"],
            impact="major"
        )],
        changed=[CommitChange(
            description="Updated user model",
            files=["models.py"],
            impact="moderate"
        )],
        removed=[],
        summary="Implement user authentication",
        technical_details="JWT-based authentication with session management"
    )


class TestInstructorAIClient:
    """Test InstructorAIClient class."""
    
    @patch('git_memory.ai.instructor.from_openai')
    @patch('git_memory.ai.openai.OpenAI')
    def test_create_openai_client(self, mock_openai, mock_instructor):
        """Test creating OpenAI client."""
        mock_instructor.return_value = Mock()
        
        with patch('git_memory.ai.Config.get_api_key', return_value="test-key"):
            with patch('git_memory.ai.Config.get_base_url', return_value=None):
                client = InstructorAIClient(provider="openai", model="gpt-4")
                
                assert client.provider == "openai"
                assert client.model == "gpt-4"
                mock_openai.assert_called_once()
                mock_instructor.assert_called_once()
    
    def test_create_client_missing_api_key(self):
        """Test creating client with missing API key."""
        with patch('git_memory.ai.Config.get_api_key', return_value=None):
            with pytest.raises(ValueError, match="OpenAI API key not found"):
                InstructorAIClient(provider="openai")
    
    @patch('git_memory.ai.InstructorAIClient._create_client')
    def test_summarize_commit_success(self, mock_create_client, sample_commit_memory):
        """Test successful commit summarization."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = sample_commit_memory
        mock_create_client.return_value = mock_client
        
        ai_client = InstructorAIClient()
        
        with patch.object(ai_client, '_load_prompt', return_value="Test prompt"):
            result = ai_client.summarize_commit(
                diff_text="+ added authentication",
                commit_message="Add auth",
                commit_hash="abc123"
            )
            
            assert result.summary == "Implement user authentication"
            assert len(result.added) == 1
            mock_client.chat.completions.create.assert_called_once()
    
    @patch('git_memory.ai.InstructorAIClient._create_client')
    def test_summarize_commit_failure(self, mock_create_client):
        """Test commit summarization with AI failure."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_create_client.return_value = mock_client
        
        ai_client = InstructorAIClient()
        
        with patch.object(ai_client, '_load_prompt', return_value="Test prompt"):
            result = ai_client.summarize_commit(
                diff_text="+ some changes",
                commit_message="Fix bug",
                commit_hash="def456"
            )
            
            # Should return fallback memory
            assert result.summary == "Fix bug"
            assert len(result.added) == 1
            assert result.added[0].description == "Changes from commit: Fix bug"
    
    def test_load_prompt_file_not_found(self):
        """Test loading non-existent prompt file."""
        ai_client = InstructorAIClient()
        
        with patch('git_memory.ai.Path.open', side_effect=FileNotFoundError):
            result = ai_client._load_prompt("nonexistent.md")
            assert result == ""


class TestFactoryFunctions:
    """Test module factory functions."""
    
    @patch('git_memory.ai.InstructorAIClient')
    def test_create_ai_client(self, mock_client_class):
        """Test create_ai_client factory function."""
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        
        result = create_ai_client(provider="openai", model="gpt-4")
        
        mock_client_class.assert_called_once_with(provider="openai", model="gpt-4")
        assert result == mock_instance
    
    @patch('git_memory.ai.create_ai_client')
    def test_summarize_diff(self, mock_create_client):
        """Test summarize_diff function."""
        mock_client = Mock()
        mock_memory = Mock()
        mock_client.summarize_commit.return_value = mock_memory
        mock_create_client.return_value = mock_client
        
        result = summarize_diff(
            diff_text="+ code changes",
            commit_message="Add feature",
            commit_hash="abc123"
        )
        
        mock_create_client.assert_called_once_with("openai", "gpt-4o")
        mock_client.summarize_commit.assert_called_once_with("+ code changes", "Add feature", "abc123")
        assert result == mock_memory
    
    @patch('git_memory.ai.create_ai_client')
    def test_generate_project_memory(self, mock_create_client):
        """Test generate_project_memory function."""
        mock_client = Mock()
        mock_project_memory = Mock()
        mock_client.aggregate_memories.return_value = mock_project_memory
        mock_create_client.return_value = mock_client
        
        commit_memories = [Mock(), Mock()]
        
        result = generate_project_memory(
            commit_memories=commit_memories,
            total_commits=5
        )
        
        mock_create_client.assert_called_once_with("openai", "gpt-4o")
        mock_client.aggregate_memories.assert_called_once_with(commit_memories, 5)
        assert result == mock_project_memory


class TestDiagramGeneration:
    """Test diagram generation functionality."""
    
    def test_generate_diagram_basic(self, sample_commit_memory):
        """Test basic diagram generation."""
        project_memory = ProjectMemory(
            major_features=["Authentication", "User Management", "API"],
            architecture_evolution=["Added MVC", "Introduced database"],
            key_decisions=["Chose Flask"],
            current_state="Stable application",
            next_steps=["Add caching"]
        )
        
        result = generate_diagram([sample_commit_memory], project_memory)
        
        assert "graph TD" in result
        assert "Major Features" in result
        assert "Authentication" in result
        assert "Architecture" in result
    
    def test_generate_diagram_empty_features(self):
        """Test diagram generation with empty features."""
        project_memory = ProjectMemory(
            major_features=[],
            architecture_evolution=[],
            key_decisions=[],
            current_state="Empty project",
            next_steps=[]
        )
        
        result = generate_diagram([], project_memory)
        
        assert "graph TD" in result
        assert "Project" in result


@pytest.mark.integration
class TestAIIntegration:
    """Integration tests for AI module (requires API keys)."""
    
    @pytest.mark.skip(reason="Requires API key - run manually")
    def test_real_ai_call(self):
        """Test with real AI API call (manual test)."""
        # This test should only be run manually with real API keys
        client = create_ai_client()
        
        result = client.summarize_commit(
            diff_text="""
+def hello_world():
+    print("Hello, World!")
+    return True
            """,
            commit_message="Add hello world function",
            commit_hash="abc123"
        )
        
        assert isinstance(result, CommitMemory)
        assert result.summary
        assert len(result.added) > 0