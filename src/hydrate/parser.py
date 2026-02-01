"""Embed pattern parsing and hydration logic."""

import re
from pathlib import Path

from hydrate.converters import convert_file
from hydrate.errors import (
    BinaryFileError,
    CircularReferenceError,
    MaxDepthExceededError,
    MissingFileError,
)

EMBED_PATTERN = re.compile(r"\{\{([^}]+)\}\}")


def _is_binary(content: bytes) -> bool:
    """Check if content appears to be binary."""
    return b"\x00" in content[:8192]


def hydrate_content(
    content: str,
    base_path: Path,
    *,
    max_depth: int = 10,
    current_depth: int = 0,
    visited: set[Path] | None = None,
) -> str:
    """Hydrate embed patterns in content.

    Args:
        content: The content containing embed patterns.
        base_path: The directory to resolve relative paths from.
        max_depth: Maximum recursion depth for nested embeds.
        current_depth: Current recursion depth (internal use).
        visited: Set of visited file paths for cycle detection (internal use).

    Returns:
        The content with all embed patterns replaced.

    Raises:
        CircularReferenceError: If a circular reference is detected.
        MissingFileError: If an embedded file is not found.
        MaxDepthExceededError: If max depth is exceeded.
        BinaryFileError: If attempting to embed a binary file.
    """
    if visited is None:
        visited = set()

    def replace_embed(match: re.Match) -> str:
        relative_path = match.group(1).strip()
        absolute_path = (base_path / relative_path).resolve()

        if current_depth >= max_depth:
            raise MaxDepthExceededError(max_depth, absolute_path)

        if not absolute_path.exists():
            raise MissingFileError(absolute_path, relative_path, base_path)

        if absolute_path in visited:
            cycle = list(visited) + [absolute_path]
            raise CircularReferenceError(cycle)

        try:
            raw_content = absolute_path.read_bytes()
        except OSError as e:
            raise MissingFileError(absolute_path, relative_path, base_path) from e

        if _is_binary(raw_content):
            raise BinaryFileError(absolute_path)

        try:
            file_content = raw_content.decode("utf-8")
        except UnicodeDecodeError as e:
            raise BinaryFileError(absolute_path) from e

        converted_content = convert_file(absolute_path, file_content)

        new_visited = visited | {absolute_path}
        return hydrate_content(
            converted_content,
            absolute_path.parent,
            max_depth=max_depth,
            current_depth=current_depth + 1,
            visited=new_visited,
        )

    return EMBED_PATTERN.sub(replace_embed, content)


def hydrate_file(
    input_path: Path,
    *,
    max_depth: int = 10,
) -> str:
    """Hydrate a file by replacing all embed patterns.

    Args:
        input_path: Path to the input file.
        max_depth: Maximum recursion depth for nested embeds.

    Returns:
        The hydrated content.

    Raises:
        CircularReferenceError: If a circular reference is detected.
        MissingFileError: If an embedded file is not found.
        MaxDepthExceededError: If max depth is exceeded.
        BinaryFileError: If attempting to embed a binary file.
    """
    absolute_path = input_path.resolve()

    raw_content = absolute_path.read_bytes()
    if _is_binary(raw_content):
        raise BinaryFileError(absolute_path)

    try:
        content = raw_content.decode("utf-8")
    except UnicodeDecodeError as e:
        raise BinaryFileError(absolute_path) from e

    return hydrate_content(
        content,
        absolute_path.parent,
        max_depth=max_depth,
        visited={absolute_path},
    )
