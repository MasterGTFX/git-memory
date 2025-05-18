"""
AI provider abstraction module.
"""

from git_memory.config import Config

def summarize_diff(diff_text: str) -> str:
    """
    Summarize a diff string into natural-language memory.
    """
    raise NotImplementedError

def generate_diagram(structure_data: dict) -> str:
    """
    Generate Mermaid diagram from project structure data.
    """
    raise NotImplementedError