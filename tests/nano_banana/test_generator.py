"""Tests for nano_banana.generator module."""

import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from nano_banana.cli import NanoBananaArgs
from nano_banana.generator import generate_images


def create_test_image_bytes() -> bytes:
    """Create a minimal PNG image as bytes."""
    img = Image.new("RGB", (10, 10), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def mock_client():
    """Create a mock genai.Client with a successful response."""
    with patch("nano_banana.generator.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = create_test_image_bytes()
        mock_part.text = None

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_part]

        mock_client.models.generate_content.return_value = mock_response

        yield mock_client


class TestGenerateImages:
    def test_single_image_generation(self, tmp_path, mock_client):
        output_path = tmp_path / "test.png"
        args = NanoBananaArgs(
            prompt="A test image",
            out=output_path,
            api_key="test-key",
        )

        result = generate_images(args)

        assert result == [str(output_path)]
        assert output_path.exists()
        mock_client.models.generate_content.assert_called_once()

    def test_multiple_image_generation(self, tmp_path, mock_client):
        args = NanoBananaArgs(
            prompt="test",
            n=3,
            out_dir=tmp_path,
            api_key="test-key",
        )

        result = generate_images(args)

        assert len(result) == 3
        assert mock_client.models.generate_content.call_count == 3
        for path_str in result:
            assert Path(path_str).exists()

    def test_jpeg_output(self, tmp_path, mock_client):
        output_path = tmp_path / "test.jpg"
        args = NanoBananaArgs(
            prompt="test",
            out=output_path,
            api_key="test-key",
        )

        result = generate_images(args)

        assert result == [str(output_path)]
        assert output_path.exists()

    def test_json_output(self, tmp_path, mock_client, capsys):
        output_path = tmp_path / "test.png"
        args = NanoBananaArgs(
            prompt="test",
            out=output_path,
            api_key="test-key",
            json=True,
        )

        generate_images(args)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "paths" in output
        assert output["paths"] == [str(output_path)]

    def test_print_text_response(self, tmp_path, capsys):
        with patch("nano_banana.generator.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client

            mock_image_part = MagicMock()
            mock_image_part.inline_data = MagicMock()
            mock_image_part.inline_data.data = create_test_image_bytes()
            mock_image_part.text = None

            mock_text_part = MagicMock()
            mock_text_part.inline_data = None
            mock_text_part.text = "Here's your image!"

            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.candidates[0].content.parts = [
                mock_text_part,
                mock_image_part,
            ]

            mock_client.models.generate_content.return_value = mock_response

            output_path = tmp_path / "test.png"
            args = NanoBananaArgs(
                prompt="test",
                out=output_path,
                api_key="test-key",
                print_text=True,
            )

            generate_images(args)

            captured = capsys.readouterr()
            assert "Here's your image!" in captured.out

    def test_no_image_in_response_raises(self, tmp_path):
        with patch("nano_banana.generator.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client

            mock_part = MagicMock()
            mock_part.inline_data = None
            mock_part.text = "I cannot generate that image."

            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.candidates[0].content.parts = [mock_part]

            mock_client.models.generate_content.return_value = mock_response

            output_path = tmp_path / "test.png"
            args = NanoBananaArgs(
                prompt="test",
                out=output_path,
                api_key="test-key",
            )

            with pytest.raises(RuntimeError, match="No image data in response"):
                generate_images(args)

    def test_creates_output_directory(self, tmp_path, mock_client):
        nested_dir = tmp_path / "a" / "b" / "c"
        output_path = nested_dir / "test.png"
        args = NanoBananaArgs(
            prompt="test",
            out=output_path,
            api_key="test-key",
        )

        generate_images(args)

        assert nested_dir.exists()
        assert output_path.exists()
