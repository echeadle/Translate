# Usage Guide - Markdown to PDF Converter

## Quick Start

The simplest way to keep your files organized is to use the `--create-output-dir auto` option:

```bash
# Convert a single file to a timestamped subdirectory
uv run md2pdf document.md --create-output-dir auto

# Convert a whole directory to a timestamped subdirectory
uv run md2pdf my_docs/ --create-output-dir auto
```

This creates output like:
```
output/
└── converted_20260207_101031/
    ├── document.pdf
    └── ...
```

## Why Use --create-output-dir?

**Problem**: When converting markdown files, PDFs can get mixed up with your original markdown files, making your directory messy.

**Solution**: Use `--create-output-dir` to automatically create a separate subdirectory for all your converted PDFs!

### Benefits

✅ **Keeps originals and PDFs separate**
✅ **Each conversion gets its own folder** (with timestamps)
✅ **Easy to find your latest conversion**
✅ **No risk of overwriting or confusion**

## Common Workflows

### 1. Converting Documentation

```bash
# You have a docs/ folder with markdown files
uv run md2pdf docs/ --create-output-dir auto

# Output goes to: output/converted_YYYYMMDD_HHMMSS/
# Your original docs/ folder stays clean!
```

### 2. Creating Named Batches

```bash
# Create a specific batch for a project
uv run md2pdf project_notes/ --create-output-dir project_v1

# Output goes to: output/project_v1/
```

### 3. Multiple Conversions

```bash
# First conversion
uv run md2pdf chapter1.md --create-output-dir draft_1

# Make edits...

# Second conversion
uv run md2pdf chapter1.md --create-output-dir draft_2

# Now you have both versions:
# output/draft_1/chapter1.pdf
# output/draft_2/chapter1.pdf
```

## All Options Explained

### Input/Output Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `INPUT_PATH` | - | File or directory to convert (required) | `docs/` |
| `--output` | `-o` | Exact output file path (single file only) | `-o final.pdf` |
| `--output-dir` | `-d` | Base output directory | `-d pdfs/` |
| `--create-output-dir` | `-c` | Create subdirectory (use 'auto' or name) | `-c auto` |

### Structure Options

| Option | Description | Default |
|--------|-------------|---------|
| `--preserve-structure` | Keep subdirectory structure | Enabled |
| `--no-preserve-structure` | Flatten all files to one directory | Disabled |

### Examples Combining Options

```bash
# Preserve structure in named subdirectory
uv run md2pdf docs/ --create-output-dir manual_v2 --preserve-structure

# Flatten structure with auto subdirectory
uv run md2pdf docs/ --create-output-dir auto --no-preserve-structure

# Custom base directory with auto subdirectory
uv run md2pdf docs/ --output-dir releases/ --create-output-dir auto
# Output: releases/converted_YYYYMMDD_HHMMSS/
```

## Directory Structure

### Recommended Project Layout

```
your_project/
├── docs/                      # Your original markdown files
│   ├── chapter1.md
│   ├── chapter2.md
│   └── images/
├── output/                    # All PDF conversions (gitignored)
│   ├── converted_20260207_101031/
│   ├── converted_20260207_143022/
│   └── final_version/
└── README.md
```

### What Gets Generated

With `--create-output-dir auto`:
```
output/
└── converted_20260207_101031/
    ├── chapter1.pdf
    ├── chapter2.pdf
    └── (preserves any subdirectory structure)
```

With `--create-output-dir my_batch --no-preserve-structure`:
```
output/
└── my_batch/
    ├── chapter1.pdf
    ├── chapter2.pdf
    └── (all files flattened, no subdirs)
```

## Configuration

Create a `.env` file to customize PDF styling:

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Available Settings

```bash
# Page Setup
PDF_PAGE_SIZE=A4                    # A4, A3, Letter, Legal
PDF_MARGIN_TOP=2cm
PDF_MARGIN_BOTTOM=2cm
PDF_MARGIN_LEFT=2cm
PDF_MARGIN_RIGHT=2cm

# Typography
PDF_FONT_FAMILY=Arial, sans-serif
PDF_FONT_SIZE=11pt
PDF_CODE_FONT=Courier, monospace

# Output Defaults
DEFAULT_OUTPUT_DIR=output           # Where --create-output-dir creates subdirs
PRESERVE_DIRECTORY_STRUCTURE=true
```

## Tips & Best Practices

### 1. Always Use --create-output-dir for Projects

```bash
# ✅ GOOD: Keeps everything organized
uv run md2pdf docs/ --create-output-dir auto

# ❌ AVOID: PDFs mix with markdown files
uv run md2pdf docs/
```

### 2. Name Important Batches

```bash
# For releases or important versions
uv run md2pdf docs/ --create-output-dir release_v1.0
uv run md2pdf docs/ --create-output-dir client_presentation
```

### 3. Add Output to .gitignore

```bash
# In your .gitignore
output/
*.pdf  # If you don't want to commit any PDFs
```

### 4. Batch Convert with Timestamps

```bash
# Convert multiple projects, each to its own timestamped folder
uv run md2pdf project1/ --create-output-dir auto
uv run md2pdf project2/ --create-output-dir auto
uv run md2pdf project3/ --create-output-dir auto

# Each gets a unique timestamp!
```

## Troubleshooting

### "PDFs are mixing with my markdown files!"

**Solution**: Use `--create-output-dir auto`

### "I want all PDFs in one flat directory"

```bash
uv run md2pdf docs/ --create-output-dir batch1 --no-preserve-structure
```

### "I need a specific output location"

```bash
# For single files
uv run md2pdf doc.md --output /path/to/specific.pdf

# For directories
uv run md2pdf docs/ --output-dir /path/to/output/
```

### "I want to see what files will be converted"

```bash
# Use find to preview
find docs/ -name "*.md"

# Then convert
uv run md2pdf docs/ --create-output-dir auto
```

## Using Images in Markdown

md2pdf supports embedding images in your PDFs. Images are automatically embedded in the PDF, making the output fully portable.

### Relative Paths

Image paths are resolved relative to the markdown file location:

```markdown
# My Document

![Architecture Diagram](images/architecture.png)
![Screenshot](screenshots/example.jpg)
```

If your markdown is at `/docs/report.md`, the images will be resolved from:
- `/docs/images/architecture.png`
- `/docs/screenshots/example.jpg`

### Absolute Paths

You can also use absolute paths:

```markdown
![Logo](/home/user/assets/logo.png)
```

### Supported Formats

All image formats supported by weasyprint work:
- PNG (recommended for diagrams and screenshots)
- JPEG (good for photos)
- SVG (if supported by your weasyprint installation)
- GIF

### Error Handling

If an image is missing, conversion will fail with a clear error:

```
InvalidMarkdownError: Image not found: images/missing.png (referenced in /path/to/document.md)
```

## Getting Help

```bash
# Show all options
uv run md2pdf --help

# Check version
uv run python -c "import md2pdf; print(md2pdf.__version__)"
```

## Next Steps

- Check out the [README](../README.md) for installation instructions
- Review [IMPLEMENTATION_SUMMARY](IMPLEMENTATION_SUMMARY.md) for technical details
- Try converting the examples: `uv run md2pdf examples/markdown/ --create-output-dir test`
