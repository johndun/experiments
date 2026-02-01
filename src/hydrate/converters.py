"""File format converters for the hydrate CLI."""

import csv
import json
from io import StringIO
from pathlib import Path


def _escape_pipe(value: str) -> str:
    """Escape pipe characters in table cell values."""
    return value.replace("|", "\\|")


def _to_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Convert headers and rows to a markdown table."""
    if not headers:
        return ""

    escaped_headers = [_escape_pipe(h) for h in headers]
    header_row = "| " + " | ".join(escaped_headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"

    lines = [header_row, separator]
    for row in rows:
        padded_row = row + [""] * (len(headers) - len(row))
        escaped_row = [_escape_pipe(str(v)) for v in padded_row]
        lines.append("| " + " | ".join(escaped_row) + " |")

    return "\n".join(lines)


def convert_csv(content: str) -> str:
    """Convert CSV content to a markdown table."""
    reader = csv.reader(StringIO(content))
    rows = list(reader)
    if not rows:
        return ""
    headers = rows[0]
    data_rows = rows[1:]
    return _to_markdown_table(headers, data_rows)


def convert_tsv(content: str) -> str:
    """Convert TSV content to a markdown table."""
    reader = csv.reader(StringIO(content), delimiter="\t")
    rows = list(reader)
    if not rows:
        return ""
    headers = rows[0]
    data_rows = rows[1:]
    return _to_markdown_table(headers, data_rows)


def convert_jsonl(content: str) -> str:
    """Convert JSONL content to a markdown table.

    Keys from the first line are used as headers.
    """
    lines = [line.strip() for line in content.strip().split("\n") if line.strip()]
    if not lines:
        return ""

    objects = [json.loads(line) for line in lines]
    if not objects:
        return ""

    headers = list(objects[0].keys())
    rows = [[str(obj.get(h, "")) for h in headers] for obj in objects]
    return _to_markdown_table(headers, rows)


def convert_file(file_path: Path, content: str) -> str:
    """Convert file content based on its extension."""
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return convert_csv(content)
    elif suffix == ".tsv":
        return convert_tsv(content)
    elif suffix == ".jsonl":
        return convert_jsonl(content)
    return content
