"""Configuration management for git-memory."""

import os
from typing import Optional


class Config:
    """Configuration settings for git-memory."""
    
    # Version
    version = "0.1.0"
    
    # Default model settings
    model_provider: str = "openai"
    model: str = "gpt-4o"
    
    # Processing settings
    min_diff_lines: Optional[int] = None
    
    # AI processing settings
    ai_temperature: float = 0.2
    ai_max_tokens: int = 2000
    ai_aggregation_max_tokens: int = 3000
    ai_timeout: int = 30  # seconds
    ai_retry_attempts: int = 2
    
    # API configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL")
    
    # OpenRouter configuration
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Local model configuration
    local_base_url: str = "http://localhost:11434/v1"  # Ollama default
    
    # Output settings
    history_dir_name: str = ".history"
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for specified provider."""
        if provider == "openai":
            return cls.openai_api_key
        elif provider == "openrouter":
            return cls.openrouter_api_key
        elif provider == "local":
            return None  # Local models typically don't need API keys
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @classmethod
    def get_base_url(cls, provider: str) -> Optional[str]:
        """Get base URL for specified provider."""
        if provider == "openai":
            return cls.openai_base_url
        elif provider == "openrouter":
            return cls.openrouter_base_url
        elif provider == "local":
            return cls.local_base_url
        else:
            raise ValueError(f"Unknown provider: {provider}")