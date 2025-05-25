"""
Configuration module for git-memory.
"""

import os
from typing import Optional

class Config:
    """
    CLI configuration options and defaults.
    """
    # Default model provider: openai or openrouter
    model_provider: str = "openai"
    # Default AI model name
    model: str = "gpt-4o"
    # Minimum number of commits to group
    min_commits: int = 1
    # Minimum number of diff lines to include a commit group
    min_diff_lines: Optional[int] = None
    # API key for AI provider (from environment)
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    # OpenAI API base URL (optional)
    openai_api_base: Optional[str] = os.getenv("OPENAI_API_BASE", None)