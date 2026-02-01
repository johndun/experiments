"""CLI entry point for mdview."""

import sys
import tempfile
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from .errors import FileNotFoundError, RenderError
from .renderer import render_markdown
from .template import render_template


@dataclass
class Args:
    """Markdown Viewer CLI - Convert markdown to HTML and view in browser."""

    file: Annotated[Path, tyro.conf.Positional]
    """Path to the markdown file to view."""

    dark: bool = False
    """Start in dark mode."""

    no_math: bool = False
    """Disable MathJax rendering."""

    no_toc: bool = False
    """Disable table of contents sidebar."""

    output: Annotated[Path | None, tyro.conf.arg(aliases=["-o"])] = None
    """Save HTML to file instead of opening in browser."""


def main() -> int:
    """Main entry point for mdview CLI."""
    args = tyro.cli(Args)

    # Validate input file
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    if not args.file.is_file():
        print(f"Error: Not a file: {args.file}", file=sys.stderr)
        return 1

    try:
        # Read markdown content
        markdown_text = args.file.read_text(encoding="utf-8")

        # Get the directory containing the markdown file for relative path resolution
        base_path = args.file.parent.resolve()

        # Render markdown to HTML
        content, toc = render_markdown(
            markdown_text, base_path, enable_toc=not args.no_toc
        )

        # Generate full HTML
        html = render_template(
            content=content,
            toc=toc,
            title=args.file.stem,
            dark_mode=args.dark,
            enable_math=not args.no_math,
            enable_toc=not args.no_toc,
        )

        if args.output:
            # Save to specified file
            args.output.write_text(html, encoding="utf-8")
            print(f"Saved to: {args.output}")
        else:
            # Create temp file and open in browser
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".html",
                delete=False,
                encoding="utf-8",
            ) as f:
                f.write(html)
                temp_path = f.name

            webbrowser.open(f"file://{temp_path}")
            print(f"Opened in browser: {temp_path}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RenderError as e:
        print(f"Error rendering markdown: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
