# Quick Start Guide

## The Recommended Way (Keeps Files Organized!)

```bash
# Single file - PDF goes to timestamped subdirectory
uv run md2pdf your_document.md --create-output-dir auto

# Directory - All PDFs in one timestamped subdirectory
uv run md2pdf your_docs/ --create-output-dir auto
```

**Output location**: `output/converted_YYYYMMDD_HHMMSS/`

✅ Your original files stay clean and separate!

## Other Common Uses

```bash
# Named batch (good for versions)
uv run md2pdf report.md --create-output-dir version_1

# Specific output file
uv run md2pdf doc.md --output final_report.pdf

# Directory with named batch
uv run md2pdf docs/ --create-output-dir project_delivery
```

## Getting Help

```bash
# Show all options
uv run md2pdf --help

# Read the detailed guide
cat docs/USAGE_GUIDE.md
```

## Project Structure

```
Translate/
├── README.md                 # Full documentation
├── QUICK_START.md           # This file
├── src/md2pdf/              # Program code
├── docs/                    # Detailed guides
├── examples/
│   ├── markdown/           # Example markdown files
│   └── converted/          # Example PDFs
└── output/                  # Your conversions go here
    └── converted_*/        # Each run in its own folder
```

## Tips

💡 **Always use `--create-output-dir auto`** - This keeps your workspace clean by putting all PDFs in separate folders with timestamps.

💡 **For important versions**, use named subdirectories:
```bash
uv run md2pdf docs/ --create-output-dir client_presentation
uv run md2pdf docs/ --create-output-dir final_draft
```

💡 **Check your conversions**:
```bash
ls -lt output/  # List all conversion folders, newest first
```

## Documentation

- **This file** - Quick commands to get started
- **README.md** - Full documentation and features
- **docs/USAGE_GUIDE.md** - Detailed examples and workflows
- **docs/PROJECT_STRUCTURE.md** - Project organization explained
