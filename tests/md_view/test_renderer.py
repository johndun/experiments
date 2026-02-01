"""Tests for md_view.renderer module."""

from pathlib import Path

import pytest

from md_view.renderer import (
    convert_image_paths,
    protect_math,
    render_markdown,
    restore_math,
)


class TestProtectMath:
    """Tests for math protection functionality."""

    def test_protect_inline_math(self):
        """Inline math should be replaced with placeholders."""
        text = "The formula $x^2$ is quadratic."
        result, placeholders = protect_math(text)

        assert "$x^2$" not in result
        assert len(placeholders) == 1
        assert placeholders[0][1] == "$x^2$"
        assert "MATHINLINE" in result

    def test_protect_block_math(self):
        """Block math should be replaced with placeholders."""
        text = "Here is an equation:\n$$\\int_0^1 x dx$$\nEnd."
        result, placeholders = protect_math(text)

        assert "$$" not in result
        assert len(placeholders) == 1
        assert "\\int_0^1 x dx" in placeholders[0][1]
        assert "MATHBLOCK" in result

    def test_protect_multiple_math(self):
        """Multiple math expressions should all be protected."""
        text = "We have $a$ and $b$ with $$c$$."
        result, placeholders = protect_math(text)

        assert "$" not in result.replace("PLACEHOLDER", "")
        assert len(placeholders) == 3

    def test_no_math(self):
        """Text without math should be unchanged."""
        text = "Just regular text with no math."
        result, placeholders = protect_math(text)

        assert result == text
        assert len(placeholders) == 0

    def test_multiline_block_math(self):
        """Block math spanning multiple lines should be protected."""
        text = "Equation:\n$$\nx = y\n+ z\n$$\nDone."
        result, placeholders = protect_math(text)

        assert len(placeholders) == 1
        assert "x = y" in placeholders[0][1]


class TestRestoreMath:
    """Tests for math restoration functionality."""

    def test_restore_inline_math(self):
        """Inline math placeholders should be restored."""
        original = "$x^2$"
        placeholder = "MATHINLINE0PLACEHOLDER"
        text = f"The formula {placeholder} is quadratic."
        placeholders = [(placeholder, original)]

        result = restore_math(text, placeholders)

        assert result == "The formula $x^2$ is quadratic."

    def test_restore_multiple(self):
        """Multiple placeholders should all be restored."""
        text = "MATHINLINE0PLACEHOLDER and MATHBLOCK1PLACEHOLDER"
        placeholders = [
            ("MATHINLINE0PLACEHOLDER", "$a$"),
            ("MATHBLOCK1PLACEHOLDER", "$$b$$"),
        ]

        result = restore_math(text, placeholders)

        assert result == "$a$ and $$b$$"


class TestConvertImagePaths:
    """Tests for image path conversion."""

    def test_relative_path_conversion(self, tmp_path):
        """Relative paths should be converted to file:// URLs."""
        # Create a test image
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        img_file = img_dir / "test.png"
        img_file.write_bytes(b"fake png")

        html = '<img src="images/test.png" alt="test">'
        result = convert_image_paths(html, tmp_path)

        assert 'src="file://' in result
        assert str(tmp_path) in result or "images/test.png" in result

    def test_absolute_url_unchanged(self, tmp_path):
        """Absolute URLs should remain unchanged."""
        html = '<img src="https://example.com/img.png">'
        result = convert_image_paths(html, tmp_path)

        assert result == html

    def test_file_url_unchanged(self, tmp_path):
        """file:// URLs should remain unchanged."""
        html = '<img src="file:///path/to/img.png">'
        result = convert_image_paths(html, tmp_path)

        assert result == html

    def test_data_url_unchanged(self, tmp_path):
        """data: URLs should remain unchanged."""
        html = '<img src="data:image/png;base64,ABC123">'
        result = convert_image_paths(html, tmp_path)

        assert result == html

    def test_nonexistent_image_unchanged(self, tmp_path):
        """Non-existent relative paths should remain unchanged."""
        html = '<img src="nonexistent.png">'
        result = convert_image_paths(html, tmp_path)

        assert result == html


class TestRenderMarkdown:
    """Tests for the main render_markdown function."""

    def test_basic_rendering(self, tmp_path):
        """Basic markdown should render to HTML."""
        text = "# Hello\n\nWorld"
        content, toc = render_markdown(text, tmp_path)

        assert "<h1" in content
        assert "Hello" in content
        assert "World" in content

    def test_toc_generation(self, tmp_path):
        """Table of contents should be generated."""
        text = "# First\n## Second\n### Third"
        content, toc = render_markdown(text, tmp_path, enable_toc=True)

        assert toc != ""
        assert "First" in toc
        assert "Second" in toc

    def test_toc_disabled(self, tmp_path):
        """TOC should be empty when disabled."""
        text = "# First\n## Second"
        content, toc = render_markdown(text, tmp_path, enable_toc=False)

        assert toc == ""

    def test_fenced_code(self, tmp_path):
        """Fenced code blocks should render correctly."""
        text = "```python\nprint('hello')\n```"
        content, toc = render_markdown(text, tmp_path)

        assert "<code" in content
        assert "print" in content

    def test_tables(self, tmp_path):
        """Tables should render correctly."""
        text = "| A | B |\n|---|---|\n| 1 | 2 |"
        content, toc = render_markdown(text, tmp_path)

        assert "<table" in content
        assert "<th" in content or "<td" in content

    def test_math_preserved(self, tmp_path):
        """Math expressions should be preserved in output."""
        text = "Formula: $x^2$"
        content, toc = render_markdown(text, tmp_path)

        assert "$x^2$" in content


class TestRenderMarkdownWithFixtures:
    """Tests using fixture files."""

    @pytest.fixture
    def fixtures_path(self):
        """Return the path to the fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_sample_md(self, fixtures_path):
        """Sample markdown should render without errors."""
        sample_path = fixtures_path / "sample.md"
        if not sample_path.exists():
            pytest.skip("Fixture file not found")

        text = sample_path.read_text()
        content, toc = render_markdown(text, fixtures_path)

        assert "Sample Markdown Document" in content
        assert "<h1" in content

    def test_math_sample(self, fixtures_path):
        """Math sample should preserve math expressions."""
        math_path = fixtures_path / "math_sample.md"
        if not math_path.exists():
            pytest.skip("Fixture file not found")

        text = math_path.read_text()
        content, toc = render_markdown(text, fixtures_path)

        # Math should be preserved
        assert "$" in content or "\\(" in content

    def test_images_sample(self, fixtures_path):
        """Image paths should be converted correctly."""
        images_path = fixtures_path / "with_images.md"
        if not images_path.exists():
            pytest.skip("Fixture file not found")

        text = images_path.read_text()
        content, toc = render_markdown(text, fixtures_path)

        # Should have image tags
        assert "<img" in content
