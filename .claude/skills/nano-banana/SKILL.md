---
name: nano-banana
description: Generate images using the Gemini AI API from the command line
---

# nano-banana

Generate images using the Gemini AI API from the command line.

## Command

```bash
nano_banana "<prompt>" [options]
```

## Arguments

| Argument | Alias | Description |
|----------|-------|-------------|
| `prompt` | (positional) | The prompt describing the image to generate (required) |
| `--out` | `-o` | Output file path (for single image) |
| `--out-dir` | | Output directory (for multiple images) |
| `--n` | `-n` | Number of images to generate (default: 1) |
| `--model` | | Gemini model to use (default: gemini-3-pro-image-preview) |
| `--aspect-ratio` | `-a` | Aspect ratio for generated images |
| `--image-size` | `-s` | Resolution of generated images |
| `--api-key` | | Gemini API key (defaults to GEMINI_API_KEY env var) |
| `--overwrite` | | Overwrite existing files without prompting |
| `--print-text` | | Print any text response from the model |
| `--json` | | Output results as JSON |

## Aspect Ratios

Valid aspect ratios: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

## Image Sizes

Valid image sizes: `1K`, `2K`, `4K`

Higher resolutions provide more detail but take longer to generate.

## Examples

### Basic usage
```bash
nano_banana "A cute cat playing piano" -o cat.png
```

### Generate multiple images
```bash
nano_banana "A sunset over mountains" --out-dir ./images -n 3
```

### Specify aspect ratio for portrait
```bash
nano_banana "A professional headshot" -o portrait.png --aspect-ratio 3:4
```

### Landscape image at high resolution
```bash
nano_banana "A panoramic mountain vista" -o vista.png --aspect-ratio 21:9 --image-size 4K
```

### Square social media image
```bash
nano_banana "Abstract art pattern" -o social.png -a 1:1 -s 2K
```

### Get JSON output
```bash
nano_banana "test prompt" --out result.png --json
```

## Environment

Set `GEMINI_API_KEY` environment variable to avoid passing `--api-key` each time:

```bash
export GEMINI_API_KEY="your-api-key"
```

## Output Formats

Supports PNG (`.png`) and JPEG (`.jpg`, `.jpeg`) output formats, determined by the file extension.
