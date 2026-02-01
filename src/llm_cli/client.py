"""Anthropic client wrapper for LLM CLI."""

from dataclasses import dataclass

import anthropic


@dataclass
class MessageResult:
    """Result from create_message containing text and usage info."""

    text: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int


def create_message(
    api_key: str,
    model: str,
    prompt: str,
    system: str | None = None,
    cache_system: bool = False,
    temperature: float = 0,
    max_tokens: int = 4096,
    thinking_budget: int | None = None,
) -> MessageResult:
    """Create a message using the Anthropic API.

    Args:
        api_key: Anthropic API key.
        model: Model identifier to use.
        prompt: User prompt/message.
        system: Optional system prompt.
        cache_system: Enable prompt caching on system prompt.
        temperature: Sampling temperature (0-1).
        max_tokens: Maximum response tokens.
        thinking_budget: If set, enables extended thinking with this token budget.

    Returns:
        MessageResult with text and usage information.
    """
    client = anthropic.Anthropic(api_key=api_key, max_retries=2)

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    # Temperature cannot be set when thinking is enabled
    if thinking_budget is None:
        kwargs["temperature"] = temperature

    if system is not None:
        if cache_system:
            kwargs["system"] = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ]
        else:
            kwargs["system"] = system

    if thinking_budget is not None:
        kwargs["thinking"] = {
            "type": "enabled",
            "budget_tokens": thinking_budget,
        }

    response = client.messages.create(**kwargs)

    # Concatenate all text blocks from the response, excluding thinking blocks
    text = "".join(
        block.text
        for block in response.content
        if hasattr(block, "text") and block.type == "text"
    )

    # Extract usage information
    usage = response.usage
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0

    return MessageResult(
        text=text,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cache_read_tokens=cache_read,
        cache_write_tokens=cache_write,
    )
