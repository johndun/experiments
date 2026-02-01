"""Markdown to HTML rendering with image path handling and math protection."""

import re
from pathlib import Path
from urllib.parse import quote

import markdown
from markdown.extensions.toc import TocExtension


def protect_math(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Extract math expressions before markdown processing to protect them.

    Returns the text with placeholders and a list of (placeholder, original) pairs.
    """
    placeholders = []
    counter = 0

    def replace_block_math(match: re.Match) -> str:
        nonlocal counter
        placeholder = f"MATHBLOCK{counter}PLACEHOLDER"
        counter += 1
        placeholders.append((placeholder, match.group(0)))
        return placeholder

    def replace_inline_math(match: re.Match) -> str:
        nonlocal counter
        placeholder = f"MATHINLINE{counter}PLACEHOLDER"
        counter += 1
        placeholders.append((placeholder, match.group(0)))
        return placeholder

    # Protect block math first ($$...$$)
    text = re.sub(r"\$\$[\s\S]+?\$\$", replace_block_math, text)

    # Protect inline math ($...$) - but not escaped \$ or empty $$
    text = re.sub(r"(?<!\$)\$(?!\$)([^\$\n]+?)\$(?!\$)", replace_inline_math, text)

    return text, placeholders


def restore_math(text: str, placeholders: list[tuple[str, str]]) -> str:
    """Restore math expressions after markdown processing."""
    for placeholder, original in placeholders:
        text = text.replace(placeholder, original)
    return text


def convert_image_paths(html: str, base_path: Path) -> str:
    """Convert relative image paths to file:// URLs."""

    def replace_src(match: re.Match) -> str:
        src = match.group(1)
        # Skip if already an absolute URL
        if src.startswith(("http://", "https://", "file://", "data:")):
            return match.group(0)

        # Convert relative path to absolute file:// URL
        img_path = base_path / src
        if img_path.exists():
            absolute_path = img_path.resolve()
            # URL encode the path, but keep slashes
            encoded_path = quote(str(absolute_path), safe="/")
            return f'src="file://{encoded_path}"'

        return match.group(0)

    return re.sub(r'src="([^"]+)"', replace_src, html)


def render_markdown(
    text: str, base_path: Path, enable_toc: bool = True
) -> tuple[str, str]:
    """Render markdown to HTML with TOC generation.

    Args:
        text: Markdown text to render
        base_path: Base path for resolving relative image paths
        enable_toc: Whether to generate table of contents

    Returns:
        Tuple of (rendered HTML content, TOC HTML)
    """
    # Protect math expressions
    text, math_placeholders = protect_math(text)

    # Configure markdown extensions
    extensions = [
        "fenced_code",
        "tables",
        "nl2br",
        TocExtension(
            title="",
            toc_class="toc",
            anchorlink=False,
            permalink=False,
        ),
    ]

    md = markdown.Markdown(extensions=extensions)
    content = md.convert(text)

    # Get TOC
    toc = md.toc if enable_toc else ""

    # Add CSS classes to TOC items for indentation
    if toc:
        toc = re.sub(r'<a href="#([^"]+)"', r'<a class="toc-link" href="#\1"', toc)
        # Add level classes based on nesting
        lines = toc.split("\n")
        result_lines = []
        for line in lines:
            if '<li><a class="toc-link"' in line:
                # Count indentation to determine level
                indent = len(line) - len(line.lstrip())
                level = min(4, max(2, indent // 4 + 2))
                line = line.replace(
                    '<li><a class="toc-link"', f'<li class="toc-h{level}"><a'
                )
            result_lines.append(line)
        toc = "\n".join(result_lines)

    # Restore math expressions
    content = restore_math(content, math_placeholders)

    # Convert relative image paths to file:// URLs
    content = convert_image_paths(content, base_path)

    return content, toc
