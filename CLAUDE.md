# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a monorepo for hosting various experiments and projects in isolated directories.

## Before Committing

Run these commands before committing changes:

```bash
# Lint and auto-fix with ruff (including unsafe fixes)
ruff check --fix --unsafe-fixes .
ruff format .

# Run tests with coverage
coverage run -m pytest
coverage report
```
