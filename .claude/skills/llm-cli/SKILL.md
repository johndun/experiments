---
name: llm-cli
description: Submit prompts to Claude models from the command line
---

# llm CLI

A command-line interface for submitting prompts to Anthropic's Claude models.

## Usage

```bash
# Simple prompt (positional)
llm "What is 2+2?"

# Prompt via flag
llm --prompt "Explain recursion"
llm -p "Explain recursion"

# Prompt from file
llm --prompt-file prompt.txt
llm -f prompt.txt
```

## Arguments

| Argument | Description |
|----------|-------------|
| `prompt` | Prompt text (positional) |
| `-p`, `--prompt` | Prompt text (flag form) |
| `-f`, `--prompt-file` | Read prompt from file |

## System Prompts

```bash
# Inline system prompt
llm "Explain this code" --system "You are an expert programmer"
llm "Explain this code" -s "You are an expert programmer"

# System prompt from file
llm "Summarize" --system-file persona.txt
llm "Summarize" -S persona.txt

# Cache system prompt (for repeated queries)
llm "Question 1" -s "You are helpful" --cache-system
llm "Question 2" -s "You are helpful" --cache-system
```

| Argument | Description |
|----------|-------------|
| `-s`, `--system` | System prompt text |
| `-S`, `--system-file` | Read system prompt from file |
| `--cache-system` | Enable prompt caching on system prompt |

## Model Selection

```bash
# Default: claude-opus-4-5-20251101
llm "Complex question"

# Use Haiku for speed
llm --haiku "Quick question"

# Specific model
llm --model claude-sonnet-4-20250514 "Question"
llm -m claude-sonnet-4-20250514 "Question"
```

| Argument | Description |
|----------|-------------|
| `-m`, `--model` | Model ID (default: claude-opus-4-5-20251101) |
| `--haiku` | Use Claude Haiku 4.5 |

## Sampling Control

```bash
# Default: temperature 0 (deterministic)
llm "Factual question"

# Creative sampling (temperature 1.0)
llm --sample "Write a poem"

# Custom temperature (0-1)
llm --temperature 0.7 "Story idea"
llm -t 0.7 "Story idea"
```

| Argument | Description |
|----------|-------------|
| `-t`, `--temperature` | Sampling temperature 0-1 (default: 0) |
| `--sample` | Shortcut for temperature=1.0 |

## Extended Thinking

Enable Claude's extended thinking for complex reasoning:

```bash
# Basic thinking (minimum 1024 tokens)
llm --thinking 10000 "Solve this logic puzzle"
llm --think 10000 "Solve this logic puzzle"
```

| Argument | Description |
|----------|-------------|
| `--thinking`, `--think` | Enable thinking with token budget (min: 1024) |

Note: Temperature is ignored when thinking is enabled.

## Other Options

```bash
# Set max response tokens
llm --max-tokens 500 "Brief answer"

# Show token usage
llm --debug "Hello"

# Custom API key
llm --api-key sk-xxx "Question"
```

| Argument | Description |
|----------|-------------|
| `--max-tokens` | Maximum response tokens (default: 4096) |
| `--debug` | Show token usage (input, output, cache) |
| `--api-key` | Anthropic API key (default: ANTHROPIC_API_KEY env) |

## Examples

### Quick Q&A with Haiku

```bash
llm --haiku "What's the capital of France?"
```

### Code explanation with system prompt

```bash
llm --prompt-file code.py --system "Explain this code concisely"
```

### Creative writing

```bash
llm --sample "Write a haiku about programming"
```

### Complex reasoning with thinking

```bash
llm --thinking 20000 "Solve: If all Bloops are Razzles..."
```

### Repeated queries with caching

```bash
# First query caches the system prompt
llm "Summarize chapter 1" -s "You are a book analyst" --cache-system

# Subsequent queries reuse cached system prompt
llm "Summarize chapter 2" -s "You are a book analyst" --cache-system
```

### Pipeline usage

```bash
# Response to stdout, debug info to stderr
llm --debug "Count to 5" > output.txt 2> debug.txt

# Pipe prompt from another command
echo "What is this?" | xargs -I {} llm "{}"
```

## Mutual Exclusivity

- Only one prompt source allowed: positional, `--prompt`, or `--prompt-file`
- Cannot combine `--sample` with explicit `--temperature`
- Temperature is ignored when `--thinking` is enabled
