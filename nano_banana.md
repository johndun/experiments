Here is an example script. I have not verified that this runs.

```python
#!/usr/bin/env python3
"""
nanobanana.py — minimal CLI for Gemini "native image" generation via Google Gen AI Python SDK.

Usage:
  export GEMINI_API_KEY="..."
  python nanobanana.py "A cute capybara astronaut, watercolor" -o out.png
  python nanobanana.py "A futuristic city at sunrise" --model gemini-3-pro-image-preview --out-dir ./imgs --n 3

Notes:
- This uses the Google Gen AI Python SDK ("google-genai").
- It looks for an API key in GEMINI_API_KEY by default, but you can pass --api-key too.
- It saves any image parts returned in the response (inlineData -> base64 -> bytes).
"""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from google import genai  # pip install google-genai


DEFAULT_MODEL = "gemini-3-pro-image-preview"


def slugify(s: str, max_len: int = 60) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_\-]+", "", s)
    return (s[:max_len] or "image").strip("_")


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def pick_output_paths(
    out: Optional[Path],
    out_dir: Optional[Path],
    prompt: str,
    model: str,
    count: int,
) -> list[Path]:
    """
    Decide output file paths. If --out is provided and count>1, we create out_01.png, out_02.png, ...
    If --out-dir is used, we auto-name files.
    """
    if out and out_dir:
        raise ValueError("Use either --out or --out-dir, not both.")

    paths: list[Path] = []

    if out:
        # Preserve extension if present; default .png
        ext = out.suffix if out.suffix else ".png"
        stem = out.with_suffix("").name
        parent = out.parent if out.parent else Path(".")
        for i in range(count):
            suffix = "" if count == 1 else f"_{i+1:02d}"
            paths.append(parent / f"{stem}{suffix}{ext}")
        return paths

    # Default: out-dir (or current dir)
    out_dir = out_dir or Path(".")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{ts}_{slugify(prompt)}_{slugify(model, 30)}"
    for i in range(count):
        suffix = "" if count == 1 else f"_{i+1:02d}"
        paths.append(out_dir / f"{base}{suffix}.png")
    return paths


def extract_inline_image_bytes(response) -> Iterable[bytes]:
    """
    Extract raw image bytes from a Gemini generate_content response.

    The SDK returns a structured response with candidates -> content -> parts.
    For "native image" responses, image data appears as base64 in inlineData.
    """
    # Defensive parsing because SDK response objects can change shape.
    candidates = getattr(response, "candidates", None) or []
    for cand in candidates:
        content = getattr(cand, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", None) or []
        for part in parts:
            inline_data = getattr(part, "inline_data", None) or getattr(part, "inlineData", None)
            if not inline_data:
                continue
            data_b64 = getattr(inline_data, "data", None)
            if not data_b64:
                continue
            try:
                yield base64.b64decode(data_b64)
            except Exception:
                # If it's already bytes or otherwise not base64, skip.
                continue


def extract_text_parts(response) -> list[str]:
    texts: list[str] = []
    candidates = getattr(response, "candidates", None) or []
    for cand in candidates:
        content = getattr(cand, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", None) or []
        for part in parts:
            t = getattr(part, "text", None)
            if t:
                texts.append(str(t))
    return texts


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate images with Gemini (Nano Banana) via google-genai SDK.")
    p.add_argument("prompt", help="Text prompt to generate an image.")
    p.add_argument("-o", "--out", type=Path, help="Output file path (e.g., out.png).")
    p.add_argument("--out-dir", type=Path, help="Output directory (auto-names images).")
    p.add_argument("-n", type=int, default=1, help="Number of images to save (best-effort). Default: 1")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name. Default: {DEFAULT_MODEL}")
    p.add_argument("--api-key", help="Override GEMINI_API_KEY env var.")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    p.add_argument("--print-text", action="store_true", help="Print any text parts returned.")
    p.add_argument("--json", action="store_true", help="Print raw response JSON (debug).")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Missing API key. Set GEMINI_API_KEY or pass --api-key.", file=sys.stderr)
        return 2

    if args.n < 1:
        print("ERROR: --n must be >= 1", file=sys.stderr)
        return 2

    try:
        out_paths = pick_output_paths(args.out, args.out_dir, args.prompt, args.model, args.n)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Refuse to overwrite unless --overwrite
    if not args.overwrite:
        existing = [p for p in out_paths if p.exists()]
        if existing:
            print(
                "ERROR: Output file(s) already exist. Use --overwrite or choose a different --out/--out-dir.\n"
                + "\n".join(f" - {p}" for p in existing),
                file=sys.stderr,
            )
            return 2

    client = genai.Client(api_key=api_key)

    # Simple request: just send the prompt as content.
    # You can extend this to include generationConfig / imageConfig as needed.
    try:
        response = client.models.generate_content(
            model=args.model,
            contents=[{"role": "user", "parts": [{"text": args.prompt}]}],
        )
    except Exception as e:
        print(f"ERROR: API call failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        # Many SDK objects provide .model_dump_json() / .to_json() / dict-like dumps.
        dumped = None
        for attr in ("model_dump_json", "to_json", "json"):
            fn = getattr(response, attr, None)
            if callable(fn):
                try:
                    dumped = fn()
                    break
                except Exception:
                    pass
        if dumped is None:
            # Last resort: repr
            dumped = repr(response)
        print(dumped)

    if args.print_text:
        for t in extract_text_parts(response):
            print(t)

    images = list(extract_inline_image_bytes(response))
    if not images:
        print("ERROR: No image data found in response.", file=sys.stderr)
        return 1

    # Save up to n images, or however many the model returned.
    saved = 0
    for idx, (img_bytes, out_path) in enumerate(zip(images, out_paths), start=1):
        ensure_parent_dir(out_path)
        out_path.write_bytes(img_bytes)
        print(f"Saved [{idx}] {out_path}")
        saved += 1

    if saved < len(out_paths):
        # The model returned fewer images than requested.
        print(f"Note: requested {len(out_paths)} image(s) but received {len(images)}.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```