"""Hydrate CLI - Embed documents within other documents."""

from hydrate.converters import convert_csv, convert_jsonl, convert_tsv
from hydrate.errors import (
    BinaryFileError,
    CircularReferenceError,
    HydrateError,
    MaxDepthExceededError,
    MissingFileError,
    OutputExistsError,
)
from hydrate.parser import hydrate_content, hydrate_file

__all__ = [
    "hydrate_file",
    "hydrate_content",
    "convert_csv",
    "convert_tsv",
    "convert_jsonl",
    "HydrateError",
    "CircularReferenceError",
    "MissingFileError",
    "MaxDepthExceededError",
    "BinaryFileError",
    "OutputExistsError",
]
