"""Tests for nano_banana.utils module."""

from pathlib import Path

import pytest

from nano_banana.utils import (
    ensure_parent_dir,
    get_image_format,
    pick_output_paths,
    slugify,
)


class TestSlugify:
    def test_basic_text(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self):
        assert slugify("A cute cat! @#$%") == "a-cute-cat"

    def test_multiple_spaces(self):
        assert slugify("too   many   spaces") == "too-many-spaces"

    def test_underscores(self):
        assert slugify("use_underscores_here") == "use-underscores-here"

    def test_max_length(self):
        long_text = "this is a very long prompt that should be truncated"
        result = slugify(long_text, max_length=20)
        assert len(result) <= 20
        assert result == "this-is-a-very-long-"[:20]

    def test_leading_trailing_hyphens(self):
        assert slugify("--hello--") == "hello"

    def test_empty_after_cleaning(self):
        assert slugify("@#$%^&*") == ""


class TestGetImageFormat:
    def test_png(self):
        assert get_image_format(Path("test.png")) == "PNG"

    def test_jpg(self):
        assert get_image_format(Path("test.jpg")) == "JPEG"

    def test_jpeg(self):
        assert get_image_format(Path("test.jpeg")) == "JPEG"

    def test_uppercase_extension(self):
        assert get_image_format(Path("test.PNG")) == "PNG"

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported image format"):
            get_image_format(Path("test.gif"))

    def test_no_extension(self):
        with pytest.raises(ValueError, match="Unsupported image format"):
            get_image_format(Path("test"))


class TestEnsureParentDir:
    def test_creates_parent_directory(self, tmp_path):
        nested_path = tmp_path / "a" / "b" / "c" / "file.png"
        ensure_parent_dir(nested_path)
        assert nested_path.parent.exists()

    def test_existing_directory_ok(self, tmp_path):
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        file_path = existing_dir / "file.png"
        ensure_parent_dir(file_path)
        assert existing_dir.exists()


class TestPickOutputPaths:
    def test_single_image_with_out(self):
        paths = pick_output_paths(
            prompt="test",
            n=1,
            out=Path("output.png"),
        )
        assert paths == [Path("output.png")]

    def test_single_image_auto_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        paths = pick_output_paths(
            prompt="A cute cat",
            n=1,
        )
        assert paths == [Path.cwd() / "a-cute-cat.png"]

    def test_multiple_images_auto_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        paths = pick_output_paths(
            prompt="A cute cat",
            n=3,
        )
        assert len(paths) == 3
        assert paths[0] == Path.cwd() / "a-cute-cat_1.png"
        assert paths[1] == Path.cwd() / "a-cute-cat_2.png"
        assert paths[2] == Path.cwd() / "a-cute-cat_3.png"

    def test_out_dir_single_image(self, tmp_path):
        paths = pick_output_paths(
            prompt="test prompt",
            n=1,
            out_dir=tmp_path,
        )
        assert paths == [tmp_path / "test-prompt.png"]

    def test_out_dir_multiple_images(self, tmp_path):
        paths = pick_output_paths(
            prompt="test",
            n=2,
            out_dir=tmp_path,
        )
        assert paths == [tmp_path / "test_1.png", tmp_path / "test_2.png"]

    def test_out_with_n_greater_than_1_raises(self):
        with pytest.raises(ValueError, match="Cannot use --out with --n > 1"):
            pick_output_paths(
                prompt="test",
                n=2,
                out=Path("output.png"),
            )

    def test_existing_file_without_overwrite_raises(self, tmp_path):
        existing_file = tmp_path / "test.png"
        existing_file.touch()
        with pytest.raises(ValueError, match="Files already exist"):
            pick_output_paths(
                prompt="test",
                n=1,
                out=existing_file,
                overwrite=False,
            )

    def test_existing_file_with_overwrite_ok(self, tmp_path):
        existing_file = tmp_path / "test.png"
        existing_file.touch()
        paths = pick_output_paths(
            prompt="test",
            n=1,
            out=existing_file,
            overwrite=True,
        )
        assert paths == [existing_file]
