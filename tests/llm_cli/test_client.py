"""Tests for llm_cli.client module."""

from unittest.mock import MagicMock, patch

from llm_cli.client import MessageResult, create_message


class TestMessageResult:
    def test_dataclass_fields(self):
        result = MessageResult(
            text="Hello",
            input_tokens=10,
            output_tokens=20,
            cache_read_tokens=5,
            cache_write_tokens=3,
        )
        assert result.text == "Hello"
        assert result.input_tokens == 10
        assert result.output_tokens == 20
        assert result.cache_read_tokens == 5
        assert result.cache_write_tokens == 3


class TestCreateMessage:
    def _mock_response(self, text="Hello back!", cache_read=0, cache_write=0):
        """Create a mock response with usage info."""
        mock_block = MagicMock()
        mock_block.text = text
        mock_block.type = "text"

        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 20
        mock_usage.cache_read_input_tokens = cache_read
        mock_usage.cache_creation_input_tokens = cache_write

        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_response.usage = mock_usage
        return mock_response

    def test_basic_message(self):
        """Test basic message creation without system prompt."""
        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = self._mock_response()

            result = create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
            )

            assert result.text == "Hello back!"
            assert result.input_tokens == 10
            assert result.output_tokens == 20
            mock_anthropic.assert_called_once_with(api_key="test-key", max_retries=2)
            mock_client.messages.create.assert_called_once()
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["model"] == "test-model"
            assert call_kwargs["max_tokens"] == 4096
            assert call_kwargs["temperature"] == 0
            assert call_kwargs["messages"] == [{"role": "user", "content": "Hello"}]
            assert "system" not in call_kwargs

    def test_with_system_prompt(self):
        """Test message with system prompt (no caching)."""
        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = self._mock_response()

            result = create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
                system="Be helpful",
            )

            assert result.text == "Hello back!"
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["system"] == "Be helpful"

    def test_with_cached_system_prompt(self):
        """Test message with cached system prompt."""
        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = self._mock_response(
                cache_read=100, cache_write=50
            )

            result = create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
                system="Be helpful",
                cache_system=True,
            )

            assert result.text == "Hello back!"
            assert result.cache_read_tokens == 100
            assert result.cache_write_tokens == 50
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["system"] == [
                {
                    "type": "text",
                    "text": "Be helpful",
                    "cache_control": {"type": "ephemeral"},
                }
            ]

    def test_custom_temperature_and_max_tokens(self):
        """Test custom temperature and max_tokens."""
        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = self._mock_response()

            create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
                temperature=0.7,
                max_tokens=1000,
            )

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["temperature"] == 0.7
            assert call_kwargs["max_tokens"] == 1000

    def test_multiple_text_blocks(self):
        """Test concatenation of multiple text blocks."""
        mock_block1 = MagicMock()
        mock_block1.text = "Hello "
        mock_block1.type = "text"
        mock_block2 = MagicMock()
        mock_block2.text = "World"
        mock_block2.type = "text"

        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 20
        mock_usage.cache_read_input_tokens = 0
        mock_usage.cache_creation_input_tokens = 0

        mock_response = MagicMock()
        mock_response.content = [mock_block1, mock_block2]
        mock_response.usage = mock_usage

        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = mock_response

            result = create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
            )

            assert result.text == "Hello World"

    def test_thinking_blocks_excluded(self):
        """Test that thinking blocks are excluded from output."""
        mock_thinking = MagicMock()
        mock_thinking.type = "thinking"
        mock_thinking.thinking = "Let me think..."

        mock_text = MagicMock()
        mock_text.text = "The answer is 42"
        mock_text.type = "text"

        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 100
        mock_usage.cache_read_input_tokens = 0
        mock_usage.cache_creation_input_tokens = 0

        mock_response = MagicMock()
        mock_response.content = [mock_thinking, mock_text]
        mock_response.usage = mock_usage

        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = mock_response

            result = create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
                thinking_budget=10000,
            )

            assert result.text == "The answer is 42"
            assert "think" not in result.text.lower()

    def test_thinking_budget_sets_thinking_param(self):
        """Test that thinking_budget enables extended thinking."""
        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = self._mock_response()

            create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
                thinking_budget=10000,
            )

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["thinking"] == {
                "type": "enabled",
                "budget_tokens": 10000,
            }
            # Temperature should not be set when thinking is enabled
            assert "temperature" not in call_kwargs

    def test_no_thinking_includes_temperature(self):
        """Test that temperature is included when thinking is not enabled."""
        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = self._mock_response()

            create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
                temperature=0.5,
            )

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["temperature"] == 0.5
            assert "thinking" not in call_kwargs

    def test_cache_tokens_default_to_zero(self):
        """Test that cache tokens default to zero when not present."""
        mock_block = MagicMock()
        mock_block.text = "Response"
        mock_block.type = "text"

        mock_usage = MagicMock(spec=["input_tokens", "output_tokens"])
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 20

        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_response.usage = mock_usage

        with patch("llm_cli.client.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = mock_response

            result = create_message(
                api_key="test-key",
                model="test-model",
                prompt="Hello",
            )

            assert result.cache_read_tokens == 0
            assert result.cache_write_tokens == 0
