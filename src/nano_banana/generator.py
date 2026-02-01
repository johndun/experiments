"""Image generation using Gemini API."""

from __future__ import annotations

import io
import json
import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING

from google import genai
from PIL import Image

from nano_banana.utils import ensure_parent_dir, get_image_format, pick_output_paths

if TYPE_CHECKING:
    from nano_banana.cli import NanoBananaArgs


def load_image_as_part(image_path: Path) -> genai.types.Part:
    """Load an image file and return it as a Gemini Part.

    Args:
        image_path: Path to the image file.

    Returns:
        A Gemini Part containing the image data.
    """
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/png"

    with open(image_path, "rb") as f:
        image_data = f.read()

    return genai.types.Part.from_bytes(data=image_data, mime_type=mime_type)


def generate_images(args: NanoBananaArgs) -> list[str]:
    """Generate images using the Gemini API.

    Args:
        args: CLI arguments containing prompt, output paths, and API settings.

    Returns:
        List of paths where images were saved.
    """
    output_paths = pick_output_paths(
        prompt=args.prompt,
        n=args.n,
        out=args.out,
        out_dir=args.out_dir,
        overwrite=args.overwrite,
    )

    client = genai.Client(api_key=args.api_key)

    # Build content parts: input images first, then the text prompt
    content_parts: list[genai.types.Part | str] = []
    for image_path in args.images:
        content_parts.append(load_image_as_part(image_path))
    content_parts.append(args.prompt)

    saved_paths: list[str] = []
    text_responses: list[str] = []

    for i, output_path in enumerate(output_paths):
        image_config = None
        if args.aspect_ratio is not None or args.image_size is not None:
            image_config = genai.types.ImageConfig(
                aspect_ratio=args.aspect_ratio,
                image_size=args.image_size,
            )

        response = client.models.generate_content(
            model=args.model,
            contents=content_parts,
            config=genai.types.GenerateContentConfig(
                response_modalities=["image", "text"],
                image_config=image_config,
            ),
        )

        # Check for valid response
        if not response.candidates:
            block_reason = getattr(response, "prompt_feedback", None)
            raise RuntimeError(
                f"No candidates in response for image {i + 1}. "
                f"Prompt feedback: {block_reason}"
            )

        candidate = response.candidates[0]
        if candidate.content is None or candidate.content.parts is None:
            finish_reason = getattr(candidate, "finish_reason", None)
            safety_ratings = getattr(candidate, "safety_ratings", None)
            raise RuntimeError(
                f"No content in response for image {i + 1}. "
                f"Finish reason: {finish_reason}, Safety ratings: {safety_ratings}"
            )

        image_saved = False
        for part in candidate.content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                image = Image.open(io.BytesIO(image_data))

                ensure_parent_dir(output_path)
                image_format = get_image_format(output_path)
                image.save(output_path, format=image_format)
                saved_paths.append(str(output_path))
                image_saved = True
                break
            elif part.text is not None:
                text_responses.append(part.text)

        if not image_saved:
            raise RuntimeError(f"No image data in response for image {i + 1}")

    if args.json:
        result = {
            "paths": saved_paths,
            "text": text_responses if text_responses else None,
        }
        print(json.dumps(result, indent=2))
    else:
        for path in saved_paths:
            print(f"Saved: {path}")
        if args.print_text and text_responses:
            for text in text_responses:
                print(f"Model: {text}")

    return saved_paths
