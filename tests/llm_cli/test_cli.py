"""Tests for llm_cli.cli module."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from llm_cli.cli import (
    DEFAULT_MODEL,
    HAIKU_MODEL,
    LLMArgs,
    main,
    resolve_model,
    resolve_prompt,
    resolve_system,
    resolve_temperature,
)
from llm_cli.client import MessageResult


def _mock_result(text="response", input_tokens=10, output_tokens=20):
    """Create a mock MessageResult."""
    return MessageResult(
        text=text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=0,
        cache_write_tokens=0,
    )


class TestLLMArgs:
    def test_default_values(self):
        args = LLMArgs()
        assert args.prompt is None
        assert args.prompt_flag is None
        assert args.prompt_file is None
        assert args.system is None
        assert args.system_file is None
        assert args.cache_system is False
        assert args.model == DEFAULT_MODEL
        assert args.haiku is False
        assert args.temperature == 0
        assert args.sample is False
        assert args.thinking is None
        assert args.max_tokens == 4096
        assert args.api_key is None
        assert args.debug is False

    def test_custom_values(self):
        args = LLMArgs(
            prompt="test prompt",
            system="be helpful",
            cache_system=True,
            model="custom-model",
            temperature=0.5,
            thinking=10000,
            max_tokens=1000,
            api_key="test-key",
            debug=True,
        )
        assert args.prompt == "test prompt"
        assert args.system == "be helpful"
        assert args.cache_system is True
        assert args.model == "custom-model"
        assert args.temperature == 0.5
        assert args.thinking == 10000
        assert args.max_tokens == 1000
        assert args.api_key == "test-key"
        assert args.debug is True


class TestResolvePrompt:
    def test_positional_prompt(self):
        args = LLMArgs(prompt="hello")
        assert resolve_prompt(args) == "hello"

    def test_flag_prompt(self):
        args = LLMArgs(prompt_flag="hello flag")
        assert resolve_prompt(args) == "hello flag"

    def test_file_prompt(self, tmp_path):
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("hello from file")
        args = LLMArgs(prompt_file=prompt_file)
        assert resolve_prompt(args) == "hello from file"

    def test_no_prompt_raises(self):
        args = LLMArgs()
        with pytest.raises(SystemExit) as exc_info:
            resolve_prompt(args)
        assert "No prompt provided" in str(exc_info.value)

    def test_multiple_prompts_raises(self):
        args = LLMArgs(prompt="hello", prompt_flag="also hello")
        with pytest.raises(SystemExit) as exc_info:
            resolve_prompt(args)
        assert "Multiple prompt sources" in str(exc_info.value)

    def test_missing_prompt_file_raises(self):
        args = LLMArgs(prompt_file=Path("/nonexistent/file.txt"))
        with pytest.raises(SystemExit) as exc_info:
            resolve_prompt(args)
        assert "Prompt file not found" in str(exc_info.value)


class TestResolveSystem:
    def test_no_system(self):
        args = LLMArgs()
        assert resolve_system(args) is None

    def test_system_string(self):
        args = LLMArgs(system="be brief")
        assert resolve_system(args) == "be brief"

    def test_system_file(self, tmp_path):
        system_file = tmp_path / "system.txt"
        system_file.write_text("system from file")
        args = LLMArgs(system_file=system_file)
        assert resolve_system(args) == "system from file"

    def test_multiple_system_raises(self, tmp_path):
        system_file = tmp_path / "system.txt"
        system_file.write_text("file content")
        args = LLMArgs(system="inline", system_file=system_file)
        with pytest.raises(SystemExit) as exc_info:
            resolve_system(args)
        assert "Multiple system prompt sources" in str(exc_info.value)

    def test_missing_system_file_raises(self):
        args = LLMArgs(system_file=Path("/nonexistent/system.txt"))
        with pytest.raises(SystemExit) as exc_info:
            resolve_system(args)
        assert "System file not found" in str(exc_info.value)


class TestResolveModel:
    def test_default_model(self):
        args = LLMArgs()
        assert resolve_model(args) == DEFAULT_MODEL

    def test_custom_model(self):
        args = LLMArgs(model="custom-model")
        assert resolve_model(args) == "custom-model"

    def test_haiku_shortcut(self):
        args = LLMArgs(haiku=True)
        assert resolve_model(args) == HAIKU_MODEL

    def test_haiku_overrides_model(self):
        args = LLMArgs(model="custom-model", haiku=True)
        assert resolve_model(args) == HAIKU_MODEL


class TestResolveTemperature:
    def test_default_temperature(self):
        args = LLMArgs()
        assert resolve_temperature(args) == 0

    def test_custom_temperature(self):
        args = LLMArgs(temperature=0.7)
        assert resolve_temperature(args) == 0.7

    def test_sample_shortcut(self):
        args = LLMArgs(sample=True)
        assert resolve_temperature(args) == 1.0

    def test_sample_with_temperature_raises(self):
        args = LLMArgs(sample=True, temperature=0.5)
        with pytest.raises(SystemExit) as exc_info:
            resolve_temperature(args)
        assert "Cannot use both --sample and --temperature" in str(exc_info.value)

    def test_sample_with_zero_temperature_ok(self):
        # Zero is the default, so --sample with default temp should work
        args = LLMArgs(sample=True, temperature=0)
        assert resolve_temperature(args) == 1.0


class TestMain:
    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test")
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "No API key provided" in str(exc_info.value)

    def test_api_key_from_env(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            args = LLMArgs(prompt="test")
            mock_cli.return_value = args
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result()
                main()
                assert args.api_key == "env-key"
                mock_create.assert_called_once()

    def test_api_key_from_arg_overrides_env(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            args = LLMArgs(prompt="test", api_key="arg-key")
            mock_cli.return_value = args
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result()
                main()
                assert args.api_key == "arg-key"

    def test_invalid_temperature_raises(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test", temperature=1.5)
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "Temperature must be between 0 and 1" in str(exc_info.value)

    def test_negative_temperature_raises(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test", temperature=-0.5)
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "Temperature must be between 0 and 1" in str(exc_info.value)

    def test_thinking_budget_too_low_raises(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test", thinking=500)
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert "Thinking budget must be at least 1024" in str(exc_info.value)

    def test_thinking_with_temperature_warns(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(
                prompt="test", thinking=2000, temperature=0.5
            )
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result()
                main()
                captured = capsys.readouterr()
                assert "Temperature is ignored when thinking is enabled" in captured.err

    def test_thinking_with_sample_warns(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test", thinking=2000, sample=True)
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result()
                main()
                captured = capsys.readouterr()
                assert "Temperature is ignored when thinking is enabled" in captured.err

    def test_output_to_stdout(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test")
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result(text="Hello from Claude!")
                main()
                captured = capsys.readouterr()
                assert captured.out == "Hello from Claude!\n"

    def test_debug_output(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test", debug=True)
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = MessageResult(
                    text="response",
                    input_tokens=100,
                    output_tokens=50,
                    cache_read_tokens=25,
                    cache_write_tokens=10,
                )
                main()
                captured = capsys.readouterr()
                assert "response" in captured.out
                assert "[Debug] Tokens" in captured.err
                assert "input: 100" in captured.err
                assert "output: 50" in captured.err
                assert "cache_read: 25" in captured.err
                assert "cache_write: 10" in captured.err

    def test_debug_output_on_stderr(self, monkeypatch, capsys):
        """Verify debug output goes to stderr, not stdout."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test", debug=True)
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result(text="response")
                main()
                captured = capsys.readouterr()
                # Response on stdout
                assert "response" in captured.out
                # Debug on stderr
                assert "[Debug]" in captured.err
                assert "[Debug]" not in captured.out

    def test_full_integration(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(
                prompt="test",
                system="be brief",
                cache_system=True,
                haiku=True,
                sample=True,
                max_tokens=500,
            )
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result()
                main()
                mock_create.assert_called_once_with(
                    api_key="test-key",
                    model=HAIKU_MODEL,
                    prompt="test",
                    system="be brief",
                    cache_system=True,
                    temperature=1.0,
                    max_tokens=500,
                    thinking_budget=None,
                )

    def test_thinking_budget_passed(self, monkeypatch, capsys):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        with patch("llm_cli.cli.tyro.cli") as mock_cli:
            mock_cli.return_value = LLMArgs(prompt="test", thinking=10000)
            with patch("llm_cli.cli.create_message") as mock_create:
                mock_create.return_value = _mock_result()
                main()
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["thinking_budget"] == 10000


class TestCLIHelp:
    def test_help_output(self):
        result = subprocess.run(
            [sys.executable, "-m", "llm_cli.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "prompt" in result.stdout.lower()
        assert "--system" in result.stdout or "-s" in result.stdout
        assert "--model" in result.stdout or "-m" in result.stdout
        assert "--haiku" in result.stdout
        assert "--sample" in result.stdout
        assert "--temperature" in result.stdout or "-t" in result.stdout
        assert "--thinking" in result.stdout
        assert "--debug" in result.stdout
