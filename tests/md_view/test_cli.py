"""Tests for md_view.cli module."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest


class TestCLIArgs:
    """Tests for CLI argument handling."""

    def test_file_not_found(self, tmp_path, capsys):
        """Should return error for non-existent file."""
        from md_view.cli import main

        nonexistent = tmp_path / "nonexistent.md"

        with patch.object(sys, "argv", ["mdview", str(nonexistent)]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err.lower() or "error" in captured.err.lower()

    def test_not_a_file(self, tmp_path, capsys):
        """Should return error for directory instead of file."""
        from md_view.cli import main

        with patch.object(sys, "argv", ["mdview", str(tmp_path)]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "not a file" in captured.err.lower() or "error" in captured.err.lower()

    def test_successful_render_to_file(self, tmp_path):
        """Should successfully render markdown to output file."""
        from md_view.cli import main

        # Create input file
        input_file = tmp_path / "test.md"
        input_file.write_text("# Hello\n\nWorld")

        output_file = tmp_path / "output.html"

        with patch.object(
            sys, "argv", ["mdview", str(input_file), "-o", str(output_file)]
        ):
            result = main()

        assert result == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Hello" in content
        assert "World" in content

    def test_dark_mode_flag(self, tmp_path):
        """--dark flag should set dark theme."""
        from md_view.cli import main

        input_file = tmp_path / "test.md"
        input_file.write_text("# Test")
        output_file = tmp_path / "output.html"

        with patch.object(
            sys, "argv", ["mdview", str(input_file), "--dark", "-o", str(output_file)]
        ):
            result = main()

        assert result == 0
        content = output_file.read_text()
        assert 'data-theme="dark"' in content

    def test_no_math_flag(self, tmp_path):
        """--no-math flag should disable MathJax."""
        from md_view.cli import main

        input_file = tmp_path / "test.md"
        input_file.write_text("# Test with $math$")
        output_file = tmp_path / "output.html"

        with patch.object(
            sys,
            "argv",
            ["mdview", str(input_file), "--no-math", "-o", str(output_file)],
        ):
            result = main()

        assert result == 0
        content = output_file.read_text()
        assert "MathJax" not in content

    def test_no_toc_flag(self, tmp_path):
        """--no-toc flag should hide sidebar."""
        from md_view.cli import main

        input_file = tmp_path / "test.md"
        input_file.write_text("# Test\n## Section")
        output_file = tmp_path / "output.html"

        with patch.object(
            sys, "argv", ["mdview", str(input_file), "--no-toc", "-o", str(output_file)]
        ):
            result = main()

        assert result == 0
        content = output_file.read_text()
        assert "display: none" in content

    @patch("webbrowser.open")
    def test_browser_open(self, mock_open, tmp_path):
        """Should open browser when no output file specified."""
        from md_view.cli import main

        input_file = tmp_path / "test.md"
        input_file.write_text("# Hello")

        with patch.object(sys, "argv", ["mdview", str(input_file)]):
            result = main()

        assert result == 0
        mock_open.assert_called_once()
        call_arg = mock_open.call_args[0][0]
        assert call_arg.startswith("file://")
        assert ".html" in call_arg


class TestCLIWithFixtures:
    """Tests using fixture files."""

    @pytest.fixture
    def fixtures_path(self):
        """Return the path to the fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_render_sample(self, fixtures_path, tmp_path):
        """Should render sample.md successfully."""
        from md_view.cli import main

        sample_path = fixtures_path / "sample.md"
        if not sample_path.exists():
            pytest.skip("Fixture file not found")

        output_file = tmp_path / "output.html"

        with patch.object(
            sys, "argv", ["mdview", str(sample_path), "-o", str(output_file)]
        ):
            result = main()

        assert result == 0
        content = output_file.read_text()
        assert "Sample Markdown Document" in content

    def test_render_math_sample(self, fixtures_path, tmp_path):
        """Should render math_sample.md with math preserved."""
        from md_view.cli import main

        math_path = fixtures_path / "math_sample.md"
        if not math_path.exists():
            pytest.skip("Fixture file not found")

        output_file = tmp_path / "output.html"

        with patch.object(
            sys, "argv", ["mdview", str(math_path), "-o", str(output_file)]
        ):
            result = main()

        assert result == 0
        content = output_file.read_text()
        assert "MathJax" in content
