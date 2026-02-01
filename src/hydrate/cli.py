"""CLI entry point for the hydrate tool."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from hydrate.errors import HydrateError, OutputExistsError
from hydrate.parser import hydrate_file


@dataclass
class HydrateArgs:
    """Embed documents using {{path/to/doc}} syntax.

    Processes a document and replaces all {{path/to/file}} patterns
    with the contents of the referenced files. Supports recursive
    embedding and automatic conversion of CSV, TSV, and JSONL files
    to markdown tables.
    """

    input_positional: Annotated[
        Path | None,
        tyro.conf.Positional,
        tyro.conf.arg(name="input_file"),
    ] = None
    """Input file (positional argument)."""

    input: Annotated[
        Path | None,
        tyro.conf.arg(aliases=["-i"]),
    ] = None
    """Input file path (alternative to positional)."""

    output: Annotated[
        Path,
        tyro.conf.arg(aliases=["-o"]),
    ] = Path("-")
    """Output file path. Use same path as input for in-place update."""

    max_depth: int = 5
    """Maximum recursion depth for nested embeds."""


def get_input_path(args: HydrateArgs) -> Path:
    """Get the input path from args, validating exactly one is provided."""
    if args.input_positional is not None and args.input is not None:
        print(
            "Error: Cannot specify both positional input and -i/--input",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.input_positional is not None:
        return args.input_positional

    if args.input is not None:
        return args.input

    print("Error: Input file is required (positional or -i/--input)", file=sys.stderr)
    sys.exit(1)


def validate_output(input_path: Path, output_path: Path) -> None:
    """Validate that output won't accidentally overwrite existing files."""
    if output_path.resolve() == input_path.resolve():
        return

    if output_path.exists():
        raise OutputExistsError(output_path)


def main() -> None:
    """Main entry point for the hydrate CLI."""
    args = tyro.cli(HydrateArgs)

    input_path = get_input_path(args)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        validate_output(input_path, args.output)
        result = hydrate_file(input_path, max_depth=args.max_depth)
        args.output.write_text(result)
        print(f"Hydrated {input_path} -> {args.output}")
    except HydrateError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
