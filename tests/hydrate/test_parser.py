"""Tests for the embed parser."""

import pytest

from hydrate.errors import (
    BinaryFileError,
    CircularReferenceError,
    MaxDepthExceededError,
    MissingFileError,
)
from hydrate.parser import hydrate_content, hydrate_file


class TestHydrateContent:
    def test_no_embeds(self, tmp_path):
        content = "This is plain text without embeds."
        result = hydrate_content(content, tmp_path)
        assert result == content

    def test_single_embed(self, tmp_path):
        embedded_file = tmp_path / "embedded.txt"
        embedded_file.write_text("embedded content")

        content = "Before {{embedded.txt}} after"
        result = hydrate_content(content, tmp_path)
        assert result == "Before embedded content after"

    def test_multiple_embeds(self, tmp_path):
        (tmp_path / "a.txt").write_text("AAA")
        (tmp_path / "b.txt").write_text("BBB")

        content = "{{a.txt}} and {{b.txt}}"
        result = hydrate_content(content, tmp_path)
        assert result == "AAA and BBB"

    def test_nested_embeds(self, tmp_path):
        inner = tmp_path / "inner.txt"
        inner.write_text("inner content")

        outer = tmp_path / "outer.txt"
        outer.write_text("outer: {{inner.txt}}")

        content = "{{outer.txt}}"
        result = hydrate_content(content, tmp_path)
        assert result == "outer: inner content"

    def test_relative_path_resolution(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        inner = subdir / "inner.txt"
        inner.write_text("inner")

        outer = subdir / "outer.txt"
        outer.write_text("{{inner.txt}}")

        content = "{{subdir/outer.txt}}"
        result = hydrate_content(content, tmp_path)
        assert result == "inner"

    def test_whitespace_in_pattern(self, tmp_path):
        (tmp_path / "file.txt").write_text("content")

        content = "{{  file.txt  }}"
        result = hydrate_content(content, tmp_path)
        assert result == "content"


class TestCircularReferenceDetection:
    def test_self_reference(self, tmp_path):
        file_a = tmp_path / "a.txt"
        file_a.write_text("{{a.txt}}")

        with pytest.raises(CircularReferenceError):
            hydrate_file(file_a)

    def test_two_file_cycle(self, tmp_path):
        file_a = tmp_path / "a.txt"
        file_b = tmp_path / "b.txt"

        file_a.write_text("{{b.txt}}")
        file_b.write_text("{{a.txt}}")

        with pytest.raises(CircularReferenceError):
            hydrate_file(file_a)

    def test_three_file_cycle(self, tmp_path):
        file_a = tmp_path / "a.txt"
        file_b = tmp_path / "b.txt"
        file_c = tmp_path / "c.txt"

        file_a.write_text("{{b.txt}}")
        file_b.write_text("{{c.txt}}")
        file_c.write_text("{{a.txt}}")

        with pytest.raises(CircularReferenceError):
            hydrate_file(file_a)


class TestMissingFileHandling:
    def test_missing_embedded_file(self, tmp_path):
        content = "{{nonexistent.txt}}"
        with pytest.raises(MissingFileError) as exc_info:
            hydrate_content(content, tmp_path)

        assert "nonexistent.txt" in str(exc_info.value)
        assert str(tmp_path) in str(exc_info.value)


class TestMaxDepthHandling:
    def test_max_depth_exceeded(self, tmp_path):
        file_a = tmp_path / "a.txt"
        file_b = tmp_path / "b.txt"

        file_a.write_text("{{b.txt}}")
        file_b.write_text("content")

        with pytest.raises(MaxDepthExceededError):
            hydrate_file(file_a, max_depth=0)

    def test_deep_nesting_within_limit(self, tmp_path):
        files = []
        for i in range(5):
            f = tmp_path / f"level{i}.txt"
            if i < 4:
                f.write_text(f"level{i}: {{{{level{i + 1}.txt}}}}")
            else:
                f.write_text("bottom")
            files.append(f)

        result = hydrate_file(files[0], max_depth=10)
        assert "bottom" in result


class TestBinaryFileHandling:
    def test_binary_file_detection(self, tmp_path):
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        content = "{{binary.bin}}"
        with pytest.raises(BinaryFileError):
            hydrate_content(content, tmp_path)

    def test_binary_input_file(self, tmp_path):
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        with pytest.raises(BinaryFileError):
            hydrate_file(binary_file)


class TestHydrateFile:
    def test_basic_file(self, tmp_path):
        embedded = tmp_path / "embedded.txt"
        embedded.write_text("embedded")

        main = tmp_path / "main.txt"
        main.write_text("main: {{embedded.txt}}")

        result = hydrate_file(main)
        assert result == "main: embedded"

    def test_csv_conversion(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,value\nfoo,1")

        main = tmp_path / "main.md"
        main.write_text("# Data\n\n{{data.csv}}")

        result = hydrate_file(main)
        assert "| name | value |" in result
        assert "| foo | 1 |" in result
