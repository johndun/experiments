# Coding Agent Experiments

A repository for Python coding agent experiments and prototypes.

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Initialize the Environment

```bash
# Create virtual environment
uv venv .venv

# Activate the environment
source .venv/bin/activate

# Install dependencies (including dev tools)
uv pip install -e ".[dev]"
```

### Install Claude Code Skills

To make the skills from this repo available globally in Claude Code, copy them to your user skills directory:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Copy all skills from this repo
cp -r .claude/skills/* ~/.claude/skills/
```

## Development

### Linting and Formatting

```bash
ruff check --fix --unsafe-fixes .
ruff format .
```


### Running Tests

```bash
coverage run -m pytest
```
