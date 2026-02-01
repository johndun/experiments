"""Tests for the CLI."""

import subprocess
import sys

import pytest

from hydrate.cli import HydrateArgs, get_input_path, validate_output
from hydrate.errors import OutputExistsError


class TestGetInputPath:
    def test_positional_input(self):
        from pathlib import Path

        args = HydrateArgs(input_positional=Path("test.txt"))
        result = get_input_path(args)
        assert result == Path("test.txt")

    def test_flag_input(self):
        from pathlib import Path

        args = HydrateArgs(input=Path("test.txt"))
        result = get_input_path(args)
        assert result == Path("test.txt")

    def test_both_inputs_exits(self):
        from pathlib import Path

        args = HydrateArgs(input_positional=Path("a.txt"), input=Path("b.txt"))
        with pytest.raises(SystemExit):
            get_input_path(args)

    def test_no_input_exits(self):
        args = HydrateArgs()
        with pytest.raises(SystemExit):
            get_input_path(args)


class TestValidateOutput:
    def test_same_path_allowed(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("content")
        validate_output(file, file)

    def test_existing_output_raises(self, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("content")
        output_file = tmp_path / "output.txt"
        output_file.write_text("existing")

        with pytest.raises(OutputExistsError):
            validate_output(input_file, output_file)

    def test_nonexistent_output_ok(self, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("content")
        output_file = tmp_path / "output.txt"

        validate_output(input_file, output_file)


class TestCliIntegration:
    def test_basic_hydration(self, tmp_path):
        embedded = tmp_path / "embedded.txt"
        embedded.write_text("embedded content")

        main = tmp_path / "main.txt"
        main.write_text("before {{embedded.txt}} after")

        output = tmp_path / "output.txt"

        result = subprocess.run(
            [sys.executable, "-m", "hydrate.cli", str(main), "-o", str(output)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output.read_text() == "before embedded content after"

    def test_input_flag(self, tmp_path):
        embedded = tmp_path / "embedded.txt"
        embedded.write_text("content")

        main = tmp_path / "main.txt"
        main.write_text("{{embedded.txt}}")

        output = tmp_path / "output.txt"

        result = subprocess.run(
            [sys.executable, "-m", "hydrate.cli", "-i", str(main), "-o", str(output)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output.read_text() == "content"

    def test_in_place_update(self, tmp_path):
        embedded = tmp_path / "embedded.txt"
        embedded.write_text("embedded")

        main = tmp_path / "main.txt"
        main.write_text("{{embedded.txt}}")

        result = subprocess.run(
            [sys.executable, "-m", "hydrate.cli", str(main), "-o", str(main)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert main.read_text() == "embedded"

    def test_missing_input_error(self, tmp_path):
        output = tmp_path / "output.txt"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "hydrate.cli",
                str(tmp_path / "nonexistent.txt"),
                "-o",
                str(output),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "not found" in result.stderr

    def test_output_exists_error(self, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("content")

        output_file = tmp_path / "output.txt"
        output_file.write_text("existing")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "hydrate.cli",
                str(input_file),
                "-o",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "already exists" in result.stderr

    def test_csv_conversion(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,value\nfoo,1")

        main = tmp_path / "main.md"
        main.write_text("{{data.csv}}")

        output = tmp_path / "output.md"

        result = subprocess.run(
            [sys.executable, "-m", "hydrate.cli", str(main), "-o", str(output)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        content = output.read_text()
        assert "| name | value |" in content
        assert "| foo | 1 |" in content
