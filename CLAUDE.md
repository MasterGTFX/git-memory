# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Install dependencies:**
```bash
pip install -e .
```

**Run the tool:**
```bash
git-memory /path/to/repo
# or
python -m git_memory /path/to/repo
```

**With options:**
```bash
git-memory /path/to/repo --min-diff-lines 100 --model-provider openai --model gpt-4o
```

## Architecture Overview

`git-memory` is a Python CLI tool that generates AI-powered commit-by-commit documentation for Git repositories. The tool walks through Git history and creates structured documentation in a `.history/` folder.

### Core Components

- **`__main__.py`**: CLI entry point using Typer. Handles command-line arguments and delegates to history generation
- **`config.py`**: Configuration management with defaults for model provider, API keys, and processing thresholds
- **`history.py`**: Core logic for Git repository traversal, diff extraction, and file generation. Processes commits chronologically from oldest to newest
- **`ai.py`**: AI provider abstraction layer (currently stub implementations for `summarize_diff` and `generate_diagram`)

### Output Structure

The tool creates a `.history/` folder with:
```
.history/
├── memory.md          # Aggregated memory across all commits
├── history.md         # Aggregated patch history
├── structure.mmd      # Aggregated Mermaid structure diagram
└── <commit_hash>/     # Per-commit folders
    ├── memory.md      # AI-generated summary of changes
    ├── diff.patch     # Git diff for the commit
    └── structure.mmd  # Mermaid diagram of project structure
```

### Key Processing Logic

- Commits are processed chronologically (oldest first) to build incremental history
- Diffs are extracted using GitPython, with special handling for initial commits (diff against empty tree)
- `min_diff_lines` threshold allows filtering small commits
- Currently uses placeholder content for AI-generated files (memory.md, structure.mmd)

### Configuration

- API keys read from environment variables (e.g., `OPENAI_API_KEY`)
- Model provider and model configurable via CLI flags or config defaults
- Supports OpenAI, OpenRouter, and local model providers

## Current State

The tool has core Git processing implemented but AI integration is stubbed out. The `ai.py` module contains `NotImplementedError` placeholders for `summarize_diff` and `generate_diagram` functions that need actual AI provider implementations.

## Workflow

- Add completed stuff to memory
- Generate commit message
- Commit and push changes