# Project Structure

## Overview

This document explains the organization of the Markdown to PDF Converter project.

## Directory Layout

```
Translate/
├── README.md                      # Main documentation
├── pyproject.toml                 # Project configuration & dependencies
├── uv.lock                        # Dependency lock file
├── .env.example                   # Configuration template
├── .env                           # User configuration (gitignored)
├── .gitignore                     # Git exclusions
│
├── src/                           # Source code
│   └── md2pdf/
│       ├── __init__.py           # Package exports
│       ├── __main__.py           # Module entry point
│       ├── cli.py                # Command-line interface
│       ├── converter.py          # Core conversion logic
│       ├── config.py             # Configuration management
│       ├── styles.py             # PDF styling (CSS)
│       └── utils.py              # File utilities
│
├── docs/                          # Documentation
│   ├── PROJECT_STRUCTURE.md      # This file
│   ├── USAGE_GUIDE.md            # Detailed usage examples
│   └── IMPLEMENTATION_SUMMARY.md # Technical implementation details
│
├── examples/                      # Example files for testing
│   ├── markdown/                 # Original markdown files
│   │   ├── test_basic.md
│   │   ├── test_code.md
│   │   ├── test_tables.md
│   │   ├── test_complex.md
│   │   └── quick_start.md
│   └── converted/                # Example PDFs (gitignored)
│       └── (generated PDFs for reference)
│
├── test_docs/                     # Test directory structure
│   ├── section1/
│   │   ├── test_basic.md
│   │   └── test_code.md
│   ├── section2/
│   │   └── test_tables.md
│   └── test_complex.md
│
└── output/                        # Default output directory (gitignored)
    └── converted_YYYYMMDD_HHMMSS/ # Timestamped subdirectories

```

## Key Components

### Source Code (`src/md2pdf/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization, exports main classes |
| `__main__.py` | Enables `python -m md2pdf` usage |
| `cli.py` | Command-line interface using Typer |
| `converter.py` | Core conversion: Markdown → HTML → PDF |
| `config.py` | Load and validate configuration from .env |
| `styles.py` | Generate CSS for professional PDF styling |
| `utils.py` | File discovery and path manipulation |

### Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `USAGE_GUIDE.md` | Comprehensive usage examples and best practices |
| `PROJECT_STRUCTURE.md` | This document - explains project organization |
| `IMPLEMENTATION_SUMMARY.md` | Technical details and implementation notes |

### Examples (`examples/`)

**Purpose**: Provide sample markdown files for testing and demonstration

- `examples/markdown/` - Original markdown source files
- `examples/converted/` - Example PDFs (regenerated as needed)

**Test Files**:
- `test_basic.md` - Headers, lists, basic formatting
- `test_code.md` - Code blocks with syntax highlighting
- `test_tables.md` - Various table formats
- `test_complex.md` - Complex document with all features
- `quick_start.md` - Quick start guide example

### Test Structure (`test_docs/`)

**Purpose**: Test directory structure preservation and batch conversion

Contains a multi-level directory structure with markdown files to verify:
- Subdirectory preservation (`--preserve-structure`)
- Flattening (`--no-preserve-structure`)
- Batch conversion features

## Output Organization

### Default Behavior

Without `--create-output-dir`:
```
# Single file
document.md → document.pdf (same directory)

# Directory
docs/ → output/
```

### With --create-output-dir

Creates organized subdirectories:

```bash
# Auto (timestamped)
uv run md2pdf docs/ --create-output-dir auto

output/
└── converted_20260207_101031/
    └── (all converted PDFs)

# Named
uv run md2pdf docs/ --create-output-dir my_batch

output/
└── my_batch/
    └── (all converted PDFs)
```

### Structure Preservation

With `--preserve-structure` (default):
```
docs/
├── chapter1.md
└── section/
    └── chapter2.md

→ output/converted_XXXXXX/
  ├── chapter1.pdf
  └── section/
      └── chapter2.pdf
```

With `--no-preserve-structure`:
```
docs/
├── chapter1.md
└── section/
    └── chapter2.md

→ output/converted_XXXXXX/
  ├── chapter1.pdf
  └── chapter2.pdf  (flattened)
```

## Configuration

### .env File

Create from template:
```bash
cp .env.example .env
```

Controls:
- PDF page size and margins
- Font families and sizes
- Default output directory
- Structure preservation default

### pyproject.toml

Defines:
- Project metadata
- Python version requirement (≥3.11)
- Dependencies (markdown, weasyprint, typer, rich, python-dotenv)
- Build system (hatchling)
- Entry point script (`md2pdf` command)

## Git Management

### Ignored Files (.gitignore)

The following are excluded from git:

```
# Python artifacts
__pycache__/
*.pyc
*.egg-info/
dist/

# Virtual environment
.venv/

# Configuration (may contain user preferences)
.env

# Output (generated files)
output/
examples/converted/
```

### Tracked Files

- Source code (`src/`)
- Documentation (`docs/`, `README.md`)
- Configuration templates (`.env.example`)
- Example markdown files (`examples/markdown/`)
- Project configuration (`pyproject.toml`)

## Development

### Setting Up

```bash
# Clone/navigate to project
cd Translate

# Install dependencies
uv sync

# Verify installation
uv run md2pdf --help
```

### Testing Changes

```bash
# Test single file
uv run md2pdf examples/markdown/test_basic.md --create-output-dir test

# Test directory
uv run md2pdf examples/markdown/ --create-output-dir test

# Test structure preservation
uv run md2pdf test_docs/ --create-output-dir test --preserve-structure

# Test flattening
uv run md2pdf test_docs/ --create-output-dir test --no-preserve-structure
```

### Making Changes

1. Edit source files in `src/md2pdf/`
2. Run `uv sync` to rebuild if needed
3. Test with example files
4. Update documentation if adding features

## Best Practices

### For Users

1. **Keep originals separate**: Always use `--create-output-dir auto`
2. **Version control**: Commit markdown files, ignore output/
3. **Configuration**: Copy `.env.example` to `.env` for custom styling

### For Development

1. **Source layout**: Keep using `src/` layout for clean imports
2. **Type hints**: Maintain type hints throughout
3. **Documentation**: Update docs when adding features
4. **Examples**: Add test cases to `examples/markdown/`

## Size Considerations

The project is lightweight:

- Source code: ~15 KB (7 Python files)
- Documentation: ~25 KB (4 markdown files)
- Examples: ~8 KB (5 markdown files)
- Total (excluding dependencies): < 50 KB

Dependencies are managed by `uv` in a virtual environment (`.venv/`).

## Future Enhancements

Potential additions (not yet implemented):

- **Phase 2**: Image support (embedded images in PDFs)
- **Phase 3**: Custom CSS themes
- **Phase 4**: Advanced features (TOC, watermarks, watch mode)
- **Phase 5**: Testing framework (pytest, coverage)

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for the full roadmap.
