"""Utility functions for nano_banana."""

import re
from pathlib import Path


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a filesystem-safe slug.

    Args:
        text: Input text to slugify.
        max_length: Maximum length of the resulting slug.

    Returns:
        A lowercase, hyphen-separated slug.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text[:max_length]


def get_image_format(path: Path) -> str:
    """Get PIL image format from file extension.

    Args:
        path: Path with file extension.

    Returns:
        PIL format string ("PNG" or "JPEG").

    Raises:
        ValueError: If extension is not supported.
    """
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "PNG"
    if suffix in (".jpg", ".jpeg"):
        return "JPEG"
    raise ValueError(f"Unsupported image format: {suffix}. Use .png, .jpg, or .jpeg")


def ensure_parent_dir(path: Path) -> None:
    """Create parent directories if they don't exist.

    Args:
        path: Path whose parent directory should exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)


def pick_output_paths(
    prompt: str,
    n: int,
    out: Path | None = None,
    out_dir: Path | None = None,
    overwrite: bool = False,
) -> list[Path]:
    """Determine output file paths for generated images.

    Args:
        prompt: The generation prompt (used for auto-naming).
        n: Number of images to generate.
        out: Explicit output path (only valid when n=1).
        out_dir: Directory for output files.
        overwrite: Whether to allow overwriting existing files.

    Returns:
        List of output paths.

    Raises:
        ValueError: If --out is used with n > 1, or if files exist without --overwrite.
    """
    if out is not None and n > 1:
        raise ValueError("Cannot use --out with --n > 1. Use --out-dir instead.")

    if out is not None:
        paths = [out]
    else:
        base_dir = out_dir if out_dir is not None else Path.cwd()
        slug = slugify(prompt)
        if n == 1:
            paths = [base_dir / f"{slug}.png"]
        else:
            paths = [base_dir / f"{slug}_{i + 1}.png" for i in range(n)]

    if not overwrite:
        existing = [p for p in paths if p.exists()]
        if existing:
            files_str = ", ".join(str(p) for p in existing)
            raise ValueError(
                f"Files already exist: {files_str}. Use --overwrite to replace."
            )

    return paths
