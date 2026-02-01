"""Custom exception classes for the hydrate CLI."""

from pathlib import Path


class HydrateError(Exception):
    """Base exception for hydrate errors."""


class CircularReferenceError(HydrateError):
    """Raised when a circular reference is detected in embeds."""

    def __init__(self, cycle: list[Path]) -> None:
        self.cycle = cycle
        cycle_str = " -> ".join(str(p) for p in cycle)
        super().__init__(f"Circular reference detected: {cycle_str}")


class MissingFileError(HydrateError):
    """Raised when an embedded file is not found."""

    def __init__(
        self, absolute_path: Path, relative_path: str, source_file: Path
    ) -> None:
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.source_file = source_file
        super().__init__(
            f"Missing embedded file: {relative_path}\n"
            f"  Resolved to: {absolute_path}\n"
            f"  Referenced in: {source_file}"
        )


class MaxDepthExceededError(HydrateError):
    """Raised when max embedding depth is exceeded."""

    def __init__(self, max_depth: int, current_file: Path) -> None:
        self.max_depth = max_depth
        self.current_file = current_file
        super().__init__(
            f"Maximum embedding depth ({max_depth}) exceeded at: {current_file}"
        )


class BinaryFileError(HydrateError):
    """Raised when attempting to embed a binary file."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        super().__init__(f"Cannot embed binary file: {file_path}")


class OutputExistsError(HydrateError):
    """Raised when output file already exists and would be overwritten."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        super().__init__(
            f"Output file already exists: {output_path}\n"
            "Use the same path for input and output to update in-place."
        )
