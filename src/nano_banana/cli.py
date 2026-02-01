"""CLI entry point for nano_banana."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from nano_banana.generator import generate_images

VALID_ASPECT_RATIOS = (
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
)
VALID_IMAGE_SIZES = ("1K", "2K", "4K")


@dataclass
class NanoBananaArgs:
    """Generate images using Gemini AI.

    Examples:
        nano_banana "A cute cat playing piano" -o cat.png
        nano_banana "A sunset over mountains" --out-dir ./images -n 3
        nano_banana "A portrait photo" -o portrait.png --aspect-ratio 3:4
        nano_banana "A landscape scene" -o scene.png --aspect-ratio 16:9 --image-size 2K
        nano_banana "Make this photo black and white" -i photo.jpg -o bw-photo.png
        nano_banana "Combine these images" -i img1.png -i img2.png -o combined.png
    """

    prompt: Annotated[str, tyro.conf.Positional]
    """The prompt describing the image to generate."""

    images: Annotated[tuple[Path, ...], tyro.conf.arg(aliases=["-i"])] = ()
    """Input image paths to include with the prompt."""

    out: Annotated[Path | None, tyro.conf.arg(aliases=["-o"])] = None
    """Output file path. Only valid when generating a single image."""

    out_dir: Path | None = None
    """Output directory for generated images."""

    n: Annotated[int, tyro.conf.arg(aliases=["-n"])] = 1
    """Number of images to generate."""

    model: str = "gemini-3-pro-image-preview"
    """Gemini model to use for image generation."""

    aspect_ratio: Annotated[str | None, tyro.conf.arg(aliases=["-a"])] = None
    """Aspect ratio for generated images (e.g., 1:1, 16:9, 3:4)."""

    image_size: Annotated[str | None, tyro.conf.arg(aliases=["-s"])] = None
    """Resolution of generated images. Valid options: 1K, 2K, 4K."""

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

    if args.aspect_ratio is not None and args.aspect_ratio not in VALID_ASPECT_RATIOS:
        raise SystemExit(
            f"Error: Invalid aspect ratio '{args.aspect_ratio}'. "
            f"Valid options: {', '.join(VALID_ASPECT_RATIOS)}"
        )

    if args.image_size is not None and args.image_size not in VALID_IMAGE_SIZES:
        raise SystemExit(
            f"Error: Invalid image size '{args.image_size}'. "
            f"Valid options: {', '.join(VALID_IMAGE_SIZES)}"
        )

    for image_path in args.images:
        if not image_path.exists():
            raise SystemExit(f"Error: Input image not found: {image_path}")

    generate_images(args)


if __name__ == "__main__":
    main()
