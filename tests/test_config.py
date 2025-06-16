"""Tests for git_memory.config module."""

import pytest
import os
from unittest.mock import patch
from git_memory.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        assert Config.version == "0.1.0"
        assert Config.model_provider == "openai"
        assert Config.model == "gpt-4o"
        assert Config.min_diff_lines is None
        assert Config.history_dir_name == ".history"
        assert Config.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert Config.local_base_url == "http://localhost:11434/v1"
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"})
    def test_openai_api_key_from_env(self):
        """Test that OpenAI API key is read from environment."""
        # Need to reload the class to pick up new env var
        from importlib import reload
        from git_memory import config
        reload(config)
        
        assert config.Config.openai_api_key == "test-openai-key"
    
    @patch.dict(os.environ, {"OPENAI_BASE_URL": "https://custom-openai.com"})
    def test_openai_base_url_from_env(self):
        """Test that OpenAI base URL is read from environment."""
        from importlib import reload
        from git_memory import config
        reload(config)
        
        assert config.Config.openai_base_url == "https://custom-openai.com"
    
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-openrouter-key"})
    def test_openrouter_api_key_from_env(self):
        """Test that OpenRouter API key is read from environment."""
        from importlib import reload
        from git_memory import config
        reload(config)
        
        assert config.Config.openrouter_api_key == "test-openrouter-key"
    
    def test_get_api_key_openai(self):
        """Test getting API key for OpenAI provider."""
        with patch.object(Config, 'openai_api_key', 'test-key'):
            assert Config.get_api_key("openai") == 'test-key'
    
    def test_get_api_key_openrouter(self):
        """Test getting API key for OpenRouter provider."""
        with patch.object(Config, 'openrouter_api_key', 'test-openrouter-key'):
            assert Config.get_api_key("openrouter") == 'test-openrouter-key'
    
    def test_get_api_key_local(self):
        """Test getting API key for local provider (should be None)."""
        assert Config.get_api_key("local") is None
    
    def test_get_api_key_unknown_provider(self):
        """Test getting API key for unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            Config.get_api_key("unknown")
    
    def test_get_base_url_openai(self):
        """Test getting base URL for OpenAI provider."""
        with patch.object(Config, 'openai_base_url', 'https://custom-openai.com'):
            assert Config.get_base_url("openai") == 'https://custom-openai.com'
    
    def test_get_base_url_openrouter(self):
        """Test getting base URL for OpenRouter provider."""
        assert Config.get_base_url("openrouter") == "https://openrouter.ai/api/v1"
    
    def test_get_base_url_local(self):
        """Test getting base URL for local provider."""
        assert Config.get_base_url("local") == "http://localhost:11434/v1"
    
    def test_get_base_url_unknown_provider(self):
        """Test getting base URL for unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            Config.get_base_url("unknown")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_no_env_vars_set(self):
        """Test behavior when no environment variables are set."""
        from importlib import reload
        from git_memory import config
        reload(config)
        
        assert config.Config.openai_api_key is None
        assert config.Config.openai_base_url is None
        assert config.Config.openrouter_api_key is None