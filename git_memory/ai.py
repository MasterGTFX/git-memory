"""AI integration for git-memory using instructor for structured output."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import instructor
import openai
from pydantic import BaseModel, Field
from rich.console import Console

from .config import Config

console = Console()


class CommitChange(BaseModel):
    """Represents a single change in a commit."""
    description: str = Field(..., description="Brief description of the change")
    files: List[str] = Field(default_factory=list, description="Files affected by this change")
    impact: str = Field(..., description="Impact level: minor, moderate, major")


class CommitMemory(BaseModel):
    """Structured memory for a single commit."""
    added: List[CommitChange] = Field(default_factory=list, description="New features, files, or functionality added")
    removed: List[CommitChange] = Field(default_factory=list, description="Features, files, or functionality removed")
    changed: List[CommitChange] = Field(default_factory=list, description="Existing functionality that was modified")
    summary: str = Field(..., description="One-sentence summary of the commit's purpose")
    technical_details: str = Field(default="", description="Technical implementation details if relevant")


class ProjectMemory(BaseModel):
    """Aggregated memory for the entire project history."""
    major_features: List[str] = Field(default_factory=list, description="Key features implemented")
    architecture_evolution: List[str] = Field(default_factory=list, description="How the project structure evolved")
    key_decisions: List[str] = Field(default_factory=list, description="Important technical decisions made")
    current_state: str = Field(..., description="Current state and capabilities of the project")
    next_steps: List[str] = Field(default_factory=list, description="Suggested next development steps")


class InstructorAIClient:
    """AI client using instructor for structured output."""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        self.provider = provider
        self.model = model
        self.client = self._create_client()
    
    def _create_client(self) -> instructor.Instructor:
        """Create instructor client for the specified provider."""
        api_key = Config.get_api_key(self.provider)
        base_url = Config.get_base_url(self.provider)
        
        if self.provider == "openai":
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            openai_client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            return instructor.from_openai(openai_client)
        
        elif self.provider == "openrouter":
            if not api_key:
                raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.")
            
            openai_client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            return instructor.from_openai(openai_client)
        
        elif self.provider == "local":
            # For local models (like Ollama)
            openai_client = openai.OpenAI(
                api_key="dummy",  # Local models typically don't need real API keys
                base_url=base_url
            )
            return instructor.from_openai(openai_client)
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def summarize_commit(self, diff_text: str, commit_message: str, commit_hash: str) -> CommitMemory:
        """Generate structured memory for a single commit."""
        try:
            # Load memory prompt
            memory_prompt = self._load_prompt("memory_prompt.md")
            
            system_prompt = f"""You are analyzing a Git commit to extract structured information about changes.

{memory_prompt}

Focus on categorizing changes into 'added', 'removed', and 'changed' with clear descriptions.
Be specific about files affected and the impact level of each change.
"""
            
            user_prompt = f"""Analyze this Git commit:

**Commit Hash:** {commit_hash}
**Commit Message:** {commit_message}

**Diff:**
```diff
{diff_text}
```

Generate structured memory for this commit."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=CommitMemory,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=Config.ai_temperature,
                max_tokens=Config.ai_max_tokens
            )
            
            return response
            
        except Exception as e:
            console.print(f"[yellow]Warning: AI commit analysis failed: {e}[/]")
            return self._fallback_commit_memory(commit_message, diff_text)
    
    def aggregate_memories(self, commit_memories: List[CommitMemory], total_commits: int) -> ProjectMemory:
        """Generate aggregated project memory from individual commit memories."""
        try:
            # Load aggregation prompt
            aggregation_prompt = self._load_prompt("aggregation_prompt.md")
            
            system_prompt = f"""You are analyzing the complete history of a Git repository to extract high-level insights.

{aggregation_prompt}

Focus on identifying major features, architectural evolution, and key technical decisions.
"""
            
            # Prepare commit summaries for analysis
            commit_summaries = []
            for i, memory in enumerate(commit_memories):
                summary = f"Commit {i+1}: {memory.summary}"
                if memory.added:
                    summary += f" | Added: {len(memory.added)} items"
                if memory.changed:
                    summary += f" | Changed: {len(memory.changed)} items"
                if memory.removed:
                    summary += f" | Removed: {len(memory.removed)} items"
                commit_summaries.append(summary)
            
            user_prompt = f"""Analyze this project's complete Git history:

**Total Commits:** {total_commits}
**Commits Analyzed:** {len(commit_memories)}

**Commit Timeline:**
{chr(10).join(commit_summaries)}

**Detailed Changes:**
{self._format_memories_for_aggregation(commit_memories)}

Generate high-level project memory and insights."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=ProjectMemory,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=Config.ai_temperature,
                max_tokens=Config.ai_aggregation_max_tokens
            )
            
            return response
            
        except Exception as e:
            console.print(f"[yellow]Warning: AI aggregation failed: {e}[/]")
            return self._fallback_project_memory(commit_memories, total_commits)
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt from prompts directory."""
        prompt_path = Path(__file__).parent.parent / "prompts" / filename
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            console.print(f"[yellow]Warning: Prompt file {filename} not found[/]")
            return ""
    
    def _format_memories_for_aggregation(self, memories: List[CommitMemory]) -> str:
        """Format commit memories for aggregation prompt."""
        formatted = []
        for i, memory in enumerate(memories):
            commit_info = f"## Commit {i+1}: {memory.summary}\n"
            
            if memory.added:
                commit_info += "**Added:**\n"
                for change in memory.added:
                    commit_info += f"- {change.description} ({change.impact} impact)\n"
            
            if memory.changed:
                commit_info += "**Changed:**\n"
                for change in memory.changed:
                    commit_info += f"- {change.description} ({change.impact} impact)\n"
            
            if memory.removed:
                commit_info += "**Removed:**\n"
                for change in memory.removed:
                    commit_info += f"- {change.description} ({change.impact} impact)\n"
            
            formatted.append(commit_info)
        
        return "\n".join(formatted)
    
    def _fallback_commit_memory(self, commit_message: str, diff_text: str) -> CommitMemory:
        """Generate fallback commit memory when AI fails."""
        lines_changed = len(diff_text.splitlines()) if diff_text else 0
        
        return CommitMemory(
            added=[CommitChange(
                description=f"Changes from commit: {commit_message}",
                files=[],
                impact="moderate" if lines_changed > 50 else "minor"
            )],
            removed=[],
            changed=[],
            summary=commit_message,
            technical_details=f"Fallback memory - {lines_changed} lines changed"
        )
    
    def _fallback_project_memory(self, memories: List[CommitMemory], total_commits: int) -> ProjectMemory:
        """Generate fallback project memory when AI fails."""
        return ProjectMemory(
            major_features=["Feature extraction failed - using fallback"],
            architecture_evolution=["Architecture analysis failed - using fallback"],
            key_decisions=["Decision analysis failed - using fallback"],
            current_state=f"Project with {total_commits} commits and {len(memories)} analyzed commits",
            next_steps=["Complete AI integration", "Improve error handling"]
        )


# Factory function for creating AI clients
def create_ai_client(provider: str = "openai", model: str = "gpt-4o") -> InstructorAIClient:
    """Create AI client with specified provider and model."""
    return InstructorAIClient(provider=provider, model=model)


# Main functions used by history.py
def summarize_diff(diff_text: str, commit_message: str, commit_hash: str, 
                  provider: str = "openai", model: str = "gpt-4o") -> CommitMemory:
    """Analyze a Git diff and generate structured memory."""
    client = create_ai_client(provider, model)
    return client.summarize_commit(diff_text, commit_message, commit_hash)


def generate_project_memory(commit_memories: List[CommitMemory], total_commits: int,
                          provider: str = "openai", model: str = "gpt-4o") -> ProjectMemory:
    """Generate aggregated project memory from commit memories."""
    client = create_ai_client(provider, model)
    return client.aggregate_memories(commit_memories, total_commits)


def generate_diagram(commit_memories: List[CommitMemory], project_memory: ProjectMemory) -> str:
    """Generate Mermaid diagram from project memory (placeholder for now)."""
    # TODO: Implement Mermaid diagram generation
    # For now, return a basic structure based on the project memory
    
    diagram = "graph TD\n"
    diagram += "    A[Project] --> B[Major Features]\n"
    
    for i, feature in enumerate(project_memory.major_features[:5]):  # Limit to 5 features
        feature_id = f"F{i+1}"
        diagram += f"    B --> {feature_id}[\"{feature[:30]}...\"]\n"
    
    diagram += "    A --> C[Architecture]\n"
    for i, arch in enumerate(project_memory.architecture_evolution[:3]):  # Limit to 3 items
        arch_id = f"A{i+1}"
        diagram += f"    C --> {arch_id}[\"{arch[:30]}...\"]\n"
    
    return diagram