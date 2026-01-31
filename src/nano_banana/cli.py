"""CLI entry point for nano_banana."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from nano_banana.generator import generate_images


@dataclass
class NanoBananaArgs:
    """Generate images using Gemini AI.

    Examples:
        nano_banana "A cute cat playing piano" -o cat.png
        nano_banana "A sunset over mountains" --out-dir ./images -n 3
    """

    prompt: Annotated[str, tyro.conf.Positional]
    """The prompt describing the image to generate."""

    out: Annotated[Path | None, tyro.conf.arg(aliases=["-o"])] = None
    """Output file path. Only valid when generating a single image."""

    out_dir: Path | None = None
    """Output directory for generated images."""

    n: Annotated[int, tyro.conf.arg(aliases=["-n"])] = 1
    """Number of images to generate."""

    model: str = "gemini-3-pro-image-preview"
    """Gemini model to use for image generation."""

    api_key: str | None = None
    """Gemini API key. Defaults to GEMINI_API_KEY environment variable."""

    overwrite: bool = False
    """Overwrite existing files without prompting."""

    print_text: bool = False
    """Print any text response from the model."""

    json: bool = False
    """Output results as JSON."""


def main() -> None:
    """Main entry point for the CLI."""
    args = tyro.cli(NanoBananaArgs)

    if args.api_key is None:
        args.api_key = os.environ.get("GEMINI_API_KEY")
        if args.api_key is None:
            raise SystemExit(
                "Error: No API key provided. Set GEMINI_API_KEY environment variable "
                "or use --api-key."
            )

    generate_images(args)


if __name__ == "__main__":
    main()
