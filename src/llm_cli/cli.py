"""CLI entry point for llm_cli."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from llm_cli.client import create_message

DEFAULT_MODEL = "claude-opus-4-5-20251101"
HAIKU_MODEL = "claude-haiku-4-5-20251001"


@dataclass
class LLMArgs:
    """Submit prompts to Claude models.

    Examples:
        llm "Hello, how are you?"
        llm -p "What is 2+2?"
        llm -f prompt.txt
        llm "Be creative" --sample
        llm "Hello" -s "Be brief" --cache-system
        llm --haiku "Quick question"
        llm "Think step by step" --thinking 10000
    """

    prompt: Annotated[str | None, tyro.conf.Positional] = None
    """User prompt (positional argument)."""

    prompt_flag: Annotated[str | None, tyro.conf.arg(name="prompt", aliases=["-p"])] = (
        None
    )
    """User prompt (flag alternative)."""

    prompt_file: Annotated[Path | None, tyro.conf.arg(aliases=["-f"])] = None
    """Read prompt from file."""

    system: Annotated[str | None, tyro.conf.arg(aliases=["-s"])] = None
    """System prompt."""

    system_file: Annotated[
        Path | None, tyro.conf.arg(name="system-file", aliases=["-S"])
    ] = None
    """Read system prompt from file."""

    cache_system: bool = False
    """Enable prompt caching on system prompt."""

    model: Annotated[str, tyro.conf.arg(aliases=["-m"])] = DEFAULT_MODEL
    """Model to use."""

    haiku: bool = False
    """Use Claude Haiku 4.5 model."""

    temperature: Annotated[float, tyro.conf.arg(aliases=["-t"])] = 0
    """Sampling temperature (0-1)."""

    sample: bool = False
    """Set temperature to 1.0 for creative sampling."""

    thinking: Annotated[int | None, tyro.conf.arg(aliases=["--think"])] = None
    """Enable extended thinking with specified token budget."""

    max_tokens: int = 4096
    """Maximum response tokens."""

    api_key: str | None = None
    """API key. Defaults to ANTHROPIC_API_KEY environment variable."""

    debug: bool = False
    """Show token usage (input, output, cache read, cache write)."""


def resolve_prompt(args: LLMArgs) -> str:
    """Resolve prompt from positional, flag, or file source."""
    sources = [
        args.prompt is not None,
        args.prompt_flag is not None,
        args.prompt_file is not None,
    ]
    source_count = sum(sources)

    if source_count == 0:
        raise SystemExit(
            "Error: No prompt provided. Use positional argument, --prompt/-p, "
            "or --prompt-file/-f."
        )
    if source_count > 1:
        raise SystemExit(
            "Error: Multiple prompt sources provided. Use only one of: "
            "positional argument, --prompt/-p, or --prompt-file/-f."
        )

    if args.prompt is not None:
        return args.prompt
    if args.prompt_flag is not None:
        return args.prompt_flag

    # Must be prompt_file
    assert args.prompt_file is not None
    if not args.prompt_file.exists():
        raise SystemExit(f"Error: Prompt file not found: {args.prompt_file}")
    return args.prompt_file.read_text()


def resolve_system(args: LLMArgs) -> str | None:
    """Resolve system prompt from flag or file source."""
    if args.system is not None and args.system_file is not None:
        raise SystemExit(
            "Error: Multiple system prompt sources provided. "
            "Use only one of: --system/-s or --system-file/-S."
        )

    if args.system is not None:
        return args.system

    if args.system_file is not None:
        if not args.system_file.exists():
            raise SystemExit(f"Error: System file not found: {args.system_file}")
        return args.system_file.read_text()

    return None


def resolve_model(args: LLMArgs) -> str:
    """Resolve model, applying --haiku shortcut if set."""
    if args.haiku:
        return HAIKU_MODEL
    return args.model


def resolve_temperature(args: LLMArgs) -> float:
    """Resolve temperature, applying --sample shortcut if set."""
    if args.sample and args.temperature != 0:
        raise SystemExit(
            "Error: Cannot use both --sample and --temperature. "
            "Use --sample for temperature=1.0, or specify --temperature directly."
        )

    if args.sample:
        return 1.0
    return args.temperature


def main() -> None:
    """Main entry point for the CLI."""
    args = tyro.cli(LLMArgs)

    # Resolve API key
    if args.api_key is None:
        args.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if args.api_key is None:
            raise SystemExit(
                "Error: No API key provided. "
                "Set ANTHROPIC_API_KEY environment variable or use --api-key."
            )

    # Validate temperature range
    if not 0 <= args.temperature <= 1:
        raise SystemExit(
            f"Error: Temperature must be between 0 and 1, got {args.temperature}."
        )

    # Validate thinking budget
    if args.thinking is not None and args.thinking < 1024:
        raise SystemExit(
            f"Error: Thinking budget must be at least 1024 tokens, got {args.thinking}."
        )

    # Warn about temperature being ignored with thinking
    if args.thinking is not None and (args.sample or args.temperature != 0):
        print(
            "Warning: Temperature is ignored when thinking is enabled.",
            file=sys.stderr,
        )

    # Resolve all inputs
    prompt = resolve_prompt(args)
    system = resolve_system(args)
    model = resolve_model(args)
    temperature = resolve_temperature(args)

    # Call the API
    result = create_message(
        api_key=args.api_key,
        model=model,
        prompt=prompt,
        system=system,
        cache_system=args.cache_system,
        temperature=temperature,
        max_tokens=args.max_tokens,
        thinking_budget=args.thinking,
    )

    # Output response to stdout
    print(result.text)

    # Show debug info on stderr if requested
    if args.debug:
        print(
            f"\n[Debug] Tokens - "
            f"input: {result.input_tokens}, "
            f"output: {result.output_tokens}, "
            f"cache_read: {result.cache_read_tokens}, "
            f"cache_write: {result.cache_write_tokens}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
