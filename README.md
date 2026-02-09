# Markdown to PDF Converter

A Python command-line tool that converts markdown files to professional-looking PDFs.

## Features

- Convert single markdown files or entire directories
- **Auto-organize output** with timestamped or named subdirectories (keeps originals and PDFs separate!)
- Professional PDF styling with configurable fonts and margins
- Support for code blocks, tables, lists, headers, and more
- Directory structure preservation option
- Beautiful terminal output with progress indicators
- Configuration via `.env` file

## Installation

This project uses `uv` for package management. First, install `uv` if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, initialize the project:

```bash
cd /path/to/Translate
uv sync
```

## Usage

### Convert a single file

```bash
# Output to default location (same directory as input)
uv run md2pdf document.md

# Output to timestamped subdirectory (keeps things organized!)
uv run md2pdf document.md --create-output-dir auto

# Output to named subdirectory
uv run md2pdf document.md --create-output-dir my_pdfs

# Specify exact output path
uv run md2pdf document.md --output my_document.pdf
```

### Convert a directory

```bash
# Convert all markdown files in a directory
uv run md2pdf docs/

# Auto-create timestamped subdirectory (RECOMMENDED - keeps originals separate)
uv run md2pdf docs/ --create-output-dir auto

# Create named subdirectory for this batch
uv run md2pdf docs/ --create-output-dir project_docs

# Specify custom output directory
uv run md2pdf docs/ --output-dir pdfs/

# Flatten directory structure (don't preserve subdirectories)
uv run md2pdf docs/ --no-preserve-structure
```

### Using Themes

Choose from 5 built-in themes:

```bash
# GitHub-flavored (default)
uv run md2pdf document.md --theme github

# Clean and minimal
uv run md2pdf document.md --theme minimal

# Academic paper style
uv run md2pdf document.md --theme academic

# Dark mode
uv run md2pdf document.md --theme dark

# Modern with colorful accents
uv run md2pdf document.md --theme modern
```

### Custom CSS

Use your own stylesheet:

```bash
uv run md2pdf document.md --css mystyle.css
```

**Note:** You cannot use `--theme` and `--css` together. Choose one or the other.

## Configuration

Copy `.env.example` to `.env` and customize settings:

```bash
cp .env.example .env
```

Available configuration options:

- **PDF_PAGE_SIZE**: Page size (default: A4)
- **PDF_MARGIN_TOP/BOTTOM/LEFT/RIGHT**: Page margins (default: 2cm)
- **PDF_FONT_FAMILY**: Main font family (default: Arial, sans-serif)
- **PDF_FONT_SIZE**: Base font size (default: 11pt)
- **PDF_CODE_FONT**: Font for code blocks (default: Courier, monospace)
- **DEFAULT_OUTPUT_DIR**: Default output directory (default: output)
- **PRESERVE_DIRECTORY_STRUCTURE**: Preserve subdirectories (default: true)

## Testing

This project includes a comprehensive test suite with 80%+ code coverage.

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src/md2pdf --cov-report=term-missing

# Verbose output
uv run pytest -v
```

See [docs/TESTING.md](docs/TESTING.md) for detailed testing guide.

## Supported Markdown Features

- Headers (h1-h6)
- Paragraphs and line breaks
- **Bold** and *italic* text
- Lists (ordered and unordered)
- Code blocks with syntax highlighting
- Inline code
- Tables
- Blockquotes
- Horizontal rules
- **Images** - Embed images from local files (relative or absolute paths)

## Requirements

- Python >= 3.11
- Dependencies managed via `uv`

## Documentation

- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Usage Guide**: [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)
- **Themes Guide**: [docs/THEMES.md](docs/THEMES.md)
- **Developer Guide**: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- **Project Structure**: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- **Testing Guide**: [docs/TESTING.md](docs/TESTING.md)

## License

MIT
