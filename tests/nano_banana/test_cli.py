"""Tests for nano_banana.cli module."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from nano_banana.cli import VALID_ASPECT_RATIOS, VALID_IMAGE_SIZES, NanoBananaArgs, main


class TestNanoBananaArgs:
    def test_default_values(self):
        args = NanoBananaArgs(prompt="test prompt")
        assert args.prompt == "test prompt"
        assert args.images == ()
        assert args.out is None
        assert args.out_dir is None
        assert args.n == 1
        assert args.model == "gemini-3-pro-image-preview"
        assert args.aspect_ratio is None
        assert args.image_size is None
        assert args.api_key is None
        assert args.overwrite is False
        assert args.print_text is False
        assert args.json is False

    def test_custom_values(self):
        args = NanoBananaArgs(
            prompt="custom prompt",
            images=(Path("img1.png"), Path("img2.jpg")),
            out=Path("output.png"),
            n=3,
            model="custom-model",
            aspect_ratio="16:9",
            image_size="2K",
            api_key="test-key",
            overwrite=True,
            print_text=True,
            json=True,
        )
        assert args.prompt == "custom prompt"
        assert args.images == (Path("img1.png"), Path("img2.jpg"))
        assert args.out == Path("output.png")
        assert args.n == 3
        assert args.model == "custom-model"
        assert args.aspect_ratio == "16:9"
        assert args.image_size == "2K"
        assert args.api_key == "test-key"
        assert args.overwrite is True
        assert args.print_text is True
        assert args.json is True

    def test_valid_aspect_ratios(self):
        for ratio in VALID_ASPECT_RATIOS:
            args = NanoBananaArgs(prompt="test", aspect_ratio=ratio)
            assert args.aspect_ratio == ratio

    def test_valid_image_sizes(self):
        for size in VALID_IMAGE_SIZES:
            args = NanoBananaArgs(prompt="test", image_size=size)
            assert args.image_size == size


class TestMain:
    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = NanoBananaArgs(prompt="test")
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "No API key provided" in str(exc_info.value)

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            args = NanoBananaArgs(prompt="test")
            mock_cli.return_value = args
            with patch("nano_banana.cli.generate_images") as mock_gen:
                main()
                assert args.api_key == "env-key"
                mock_gen.assert_called_once_with(args)

    def test_api_key_from_arg_overrides_env(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            args = NanoBananaArgs(prompt="test", api_key="arg-key")
            mock_cli.return_value = args
            with patch("nano_banana.cli.generate_images") as mock_gen:
                main()
                assert args.api_key == "arg-key"
                mock_gen.assert_called_once_with(args)

    def test_invalid_aspect_ratio_raises(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            args = NanoBananaArgs(prompt="test", aspect_ratio="invalid")
            mock_cli.return_value = args
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "Invalid aspect ratio" in str(exc_info.value)

    def test_invalid_image_size_raises(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = NanoBananaArgs(prompt="test", image_size="5K")
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "Invalid image size" in str(exc_info.value)

    def test_valid_aspect_ratio_passes(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            args = NanoBananaArgs(prompt="test", aspect_ratio="16:9")
            mock_cli.return_value = args
            with patch("nano_banana.cli.generate_images"):
                main()  # Should not raise

    def test_valid_image_size_passes(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            args = NanoBananaArgs(prompt="test", image_size="2K")
            mock_cli.return_value = args
            with patch("nano_banana.cli.generate_images"):
                main()  # Should not raise

    def test_missing_input_image_raises(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            args = NanoBananaArgs(
                prompt="test", images=(Path("/nonexistent/image.png"),)
            )
            mock_cli.return_value = args
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "Input image not found" in str(exc_info.value)

    def test_valid_input_images_passes(self, monkeypatch, tmp_path):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        # Create a test image file
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake image data")
        with patch("nano_banana.cli.tyro.cli") as mock_cli:
            args = NanoBananaArgs(prompt="test", images=(test_image,))
            mock_cli.return_value = args
            with patch("nano_banana.cli.generate_images"):
                main()  # Should not raise


class TestCLIHelp:
    def test_help_output(self):
        result = subprocess.run(
            [sys.executable, "-m", "nano_banana.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "prompt" in result.stdout.lower()
        assert "--out" in result.stdout or "-o" in result.stdout
        assert "--n" in result.stdout or "-n" in result.stdout
