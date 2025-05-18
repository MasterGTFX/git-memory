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
    # Number of commits to include in each group (minimum, except the last group)
    commits_per_group: int = 1
    # Minimum number of diff lines to include a commit group
    min_diff_lines: Optional[int] = None
    # API key for AI provider (from environment)
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
