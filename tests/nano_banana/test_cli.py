"""Tests for nano_banana.cli module."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from nano_banana.cli import NanoBananaArgs, main


class TestNanoBananaArgs:
    def test_default_values(self):
        args = NanoBananaArgs(prompt="test prompt")
        assert args.prompt == "test prompt"
        assert args.out is None
        assert args.out_dir is None
        assert args.n == 1
        assert args.model == "gemini-2.0-flash-preview-image-generation"
        assert args.api_key is None
        assert args.overwrite is False
        assert args.print_text is False
        assert args.json is False

    def test_custom_values(self):
        args = NanoBananaArgs(
            prompt="custom prompt",
            out=Path("output.png"),
            n=3,
            model="custom-model",
            api_key="test-key",
            overwrite=True,
            print_text=True,
            json=True,
        )
        assert args.prompt == "custom prompt"
        assert args.out == Path("output.png")
        assert args.n == 3
        assert args.model == "custom-model"
        assert args.api_key == "test-key"
        assert args.overwrite is True
        assert args.print_text is True
        assert args.json is True


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
