---
name: hydrate-cli
description: Embed documents within other documents using {{path/to/doc}} syntax
---

# hydrate CLI

A CLI tool for embedding documents within other documents using `{{path/to/doc}}` syntax.

## Usage

```bash
# Positional input
hydrate input.md -o output.md

# Flag input
hydrate -i input.md -o output.md

# In-place update (same input and output)
hydrate input.md -o input.md
```

## Arguments

| Argument | Description |
|----------|-------------|
| `input_file` | Input file (positional) |
| `-i`, `--input` | Input file path (alternative to positional) |
| `-o`, `--output` | Output file path (required) |
| `--max-depth` | Maximum recursion depth for nested embeds (default: 10) |

## Embed Syntax

Use double curly braces to embed a file:

```markdown
# My Document

{{path/to/embedded-file.md}}

Some text here.

{{another/file.txt}}
```

Paths are resolved **relative to the containing document**, not the current working directory. This means if `a.md` embeds `{{subdir/b.md}}`, and `b.md` embeds `{{c.txt}}`, then `c.txt` is resolved relative to `subdir/`.

## File Conversions

Certain file types are automatically converted to markdown tables:

| Extension | Conversion |
|-----------|------------|
| `.csv` | → Markdown table |
| `.tsv` | → Markdown table |
| `.jsonl` | → Markdown table (first line keys = headers) |
| Other | Embedded as-is |

### Example: CSV to Table

**data.csv:**
```csv
name,value
foo,1
bar,2
```

**template.md:**
```markdown
# Report

{{data.csv}}
```

**Output:**
```markdown
# Report

| name | value |
| --- | --- |
| foo | 1 |
| bar | 2 |
```

## Safety Features

- **Output protection**: Refuses to overwrite existing files unless input and output are the same (in-place update)
- **Circular reference detection**: Detects and reports cycles in embed chains
- **Binary file detection**: Refuses to embed binary files
- **Max depth limit**: Prevents runaway recursion (default: 10 levels)

## Error Messages

| Condition | Behavior |
|-----------|----------|
| Missing input file | Exit with error |
| Output file exists (≠ input) | Exit with error |
| Circular reference | Exit with cycle info |
| Missing embedded file | Exit showing both absolute and relative paths |
| Max depth exceeded | Exit with warning |
| Binary file | Exit with error |

## Examples

### Basic hydration

```bash
echo "# Doc\n{{data.csv}}" > template.md
echo "name,value\nfoo,1" > data.csv
hydrate template.md -o output.md
cat output.md
```

### Nested embeds

```bash
# Create nested structure
echo "Inner content" > inner.txt
echo "Outer: {{inner.txt}}" > outer.txt
echo "Main: {{outer.txt}}" > main.txt

# Hydrate (resolves both levels)
hydrate main.txt -o result.txt
cat result.txt  # "Main: Outer: Inner content"
```

### In-place update

```bash
hydrate template.md -o template.md
```
