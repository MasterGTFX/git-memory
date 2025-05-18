"""
Configuration module for git-memory.
"""

import os
from typing import Optional

class Config:
    """
    Configuration settings for git-memory.
    """
    # Default model settings
    model_provider: str = "openai" # or "openrouter", "local" etc.
    model: str = "gpt-4o" # or "gemini-2.5-flash-preview", "llama3" etc.

    # History generation settings
    min_diff_lines: int | None = None # Minimum number of diff lines for a commit to be processed. None means process all.

    # API key for AI provider (from environment)
    # TODO: Make this provider-specific or handle multiple keys
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Add other configuration options here as needed
    # e.g., output directory, etc.
