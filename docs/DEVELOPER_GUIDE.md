# Claude Instructions for md2pdf Project

## Project Overview

**md2pdf** is a Python CLI tool that converts Markdown files to professional PDF documents. It uses a clean conversion pipeline: Markdown → HTML → Styled HTML + CSS → PDF.

### Key Technologies
- **Python 3.11+** with type hints
- **uv** for package management (not pip!)
- **markdown** library with extensions (tables, fenced_code, codehilite)
- **weasyprint** for HTML/CSS to PDF conversion
- **typer** for CLI interface
- **rich** for beautiful terminal output
- **python-dotenv** for configuration

## Architecture Principles

### 1. Clean Separation of Concerns
Each module has a single, clear responsibility:
- `cli.py` - User interface, argument parsing, output formatting
- `converter.py` - Core conversion logic
- `config.py` - Configuration loading and validation
- `styles.py` - PDF styling (CSS generation)
- `utils.py` - File operations and path utilities

### 2. File Organization Philosophy
**Keep originals and generated files separate!** This is a core design principle:
- Original markdown files: User-managed locations
- Generated PDFs: `output/` directory with subdirectories
- The `--create-output-dir` option is the recommended default

### 3. Conversion Pipeline
```
Markdown file → markdown.Markdown → HTML
           ↓
HTML + CSS from styles.py → WeasyPrint → PDF
```

## Code Conventions

### Style Guidelines

1. **Type Hints**: Use throughout for clarity
   ```python
   def convert_file(self, input_path: Path, output_path: Path) -> None:
   ```

2. **Docstrings**: Google style for all public functions
   ```python
   """Convert a markdown file to PDF.

   Args:
       input_path: Path to input markdown file.
       output_path: Path where PDF will be saved.

   Raises:
       InvalidMarkdownError: If file cannot be read.
       ConversionError: If PDF generation fails.
   """
   ```

3. **Error Handling**: Use custom exceptions
   - `MD2PDFError` - Base exception
   - `InvalidMarkdownError` - File/parsing issues
   - `ConversionError` - PDF generation failures

4. **Path Objects**: Always use `pathlib.Path`, never strings
   ```python
   # ✅ GOOD
   output_path = Path("output") / "file.pdf"

   # ❌ AVOID
   output_path = "output/file.pdf"
   ```

### Project Structure Rules

```
src/md2pdf/           # Source code - always use src-layout
├── __init__.py       # Exports: MarkdownConverter, Config, __version__
├── __main__.py       # Entry point for python -m md2pdf
├── cli.py            # CLI using typer.run(main), not Typer() app
├── converter.py      # MarkdownConverter class
├── config.py         # Config dataclass with .load() classmethod
├── styles.py         # get_default_css(config) function
└── utils.py          # Pure functions, no state

docs/                 # All documentation
examples/markdown/    # Test/example markdown files
examples/converted/   # Example PDFs (gitignored)
output/               # All generated conversions (gitignored)
```

## Key Features and Implementation

### 1. Auto-Organize Output (`--create-output-dir`)

This is a **critical feature** - always preserve this functionality!

**Why it exists**: Users need to keep original markdown files separate from generated PDFs.

**How it works**:
```python
# In cli.py, after config loading:
if create_output_dir is not None:
    if create_output_dir.lower() == "auto":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subdir_name = f"converted_{timestamp}"
    else:
        subdir_name = create_output_dir

    base_output = output_dir or Path(config.default_output_dir)
    output_dir = base_output / subdir_name
```

**Testing changes**: Always test this feature when modifying CLI:
```bash
uv run md2pdf examples/markdown/test_basic.md --create-output-dir auto
uv run md2pdf examples/markdown/ --create-output-dir test_run
```

### 2. Directory Structure Preservation

Users can choose to preserve or flatten directory structure:

- `--preserve-structure` (default): Maintains subdirectories
- `--no-preserve-structure`: Flattens all files to output root

**Implementation**: See `utils.py:get_output_path()`

### 3. Markdown Extensions

Currently enabled extensions:
```python
markdown.Markdown(extensions=[
    "fenced_code",    # ```python code```
    "tables",         # | Header | Header |
    "codehilite",     # Syntax highlighting
    "nl2br",          # Newline to <br>
])
```

**Adding new extensions**:
1. Add to `converter.py:MarkdownConverter.__init__()`
2. Update `styles.py` if new CSS is needed
3. Add test file to `examples/markdown/`
4. Update README.md features list

### 4. PDF Styling

GitHub-flavored aesthetic with professional typography:
- Code blocks: Light gray background (#f6f8fa)
- Tables: Borders, alternating row colors
- Headers: Sized appropriately with bottom borders
- Fonts: Configurable via .env

**Modifying styles**: Edit `styles.py:get_default_css()`
- Uses f-strings with config values
- Returns complete CSS string
- Applied to HTML before PDF generation

## Development Workflow

### Setting Up
```bash
cd /home/echeadle/Translate
uv sync  # Install dependencies (NOT pip install!)
```

### Running the Tool
```bash
# Development
uv run md2pdf <args>

# Or as module
uv run python -m md2pdf <args>
```

### Making Changes

1. **Edit source files** in `src/md2pdf/`
2. **No rebuild needed** for most changes (interpreted Python)
3. **If changing pyproject.toml**: Run `uv sync`
4. **Test your changes** with examples:
   ```bash
   uv run md2pdf examples/markdown/test_basic.md --create-output-dir test
   ```

### Testing Checklist

When making changes, test:
- [ ] Single file conversion
- [ ] Single file with `--create-output-dir auto`
- [ ] Directory conversion
- [ ] Directory with `--create-output-dir auto`
- [ ] Structure preservation (`--preserve-structure`)
- [ ] Structure flattening (`--no-preserve-structure`)
- [ ] Custom output paths (`--output`, `--output-dir`)
- [ ] Error handling (nonexistent files)
- [ ] Help system (`--help`)

### Common Modifications

#### Adding a CLI Option

1. Add parameter to `cli.py:main()`:
   ```python
   new_option: bool = typer.Option(
       False,
       "--new-option",
       help="Description of what this does",
   ),
   ```

2. Handle the option in the function body
3. Update docstring examples
4. Update README.md usage section
5. Test with `uv run md2pdf --help`

#### Adding Markdown Features

1. Check if extension exists: [Python-Markdown Extensions](https://python-markdown.github.io/extensions/)
2. Add to `converter.py:MarkdownConverter.__init__()` extensions list
3. Add CSS styling in `styles.py` if needed
4. Create test file in `examples/markdown/test_feature.md`
5. Test conversion and verify PDF output

#### Changing PDF Styling

1. Edit `styles.py:get_default_css()`
2. Test with multiple example files to verify changes
3. Consider adding config option in `.env.example` if user-configurable
4. Update `config.py:Config` if new config option added

## Configuration System

### .env File Structure

```bash
# Page Setup
PDF_PAGE_SIZE=A4
PDF_MARGIN_TOP=2cm
# ... (see .env.example for full list)

# Output Defaults
DEFAULT_OUTPUT_DIR=output
PRESERVE_DIRECTORY_STRUCTURE=true
```

### Adding New Config Options

1. Add to `.env.example` with comment
2. Add field to `config.py:Config` dataclass
3. Load in `Config.load()` with default value
4. Add validation in `Config.validate()` if needed
5. Use in relevant code (usually `styles.py` or `cli.py`)

## Important Files

### Core Files (Never Delete!)
- `src/md2pdf/cli.py` - Entry point, all user interaction
- `src/md2pdf/converter.py` - Heart of the conversion logic
- `src/md2pdf/styles.py` - PDF appearance definition
- `pyproject.toml` - Project definition, dependencies

### Configuration
- `.env.example` - Template (tracked in git)
- `.env` - User config (gitignored)
- `.gitignore` - Keep output/ and .venv/ excluded!

### Documentation
- `README.md` - Main user documentation
- `QUICK_START.md` - Quick reference
- `docs/USAGE_GUIDE.md` - Comprehensive examples
- `docs/PROJECT_STRUCTURE.md` - Architecture explanation
- `CLAUDE.md` - This file

## Error Handling Patterns

### In CLI (cli.py)

Use Rich console for formatted output:
```python
try:
    converter.convert_file(input_path, output)
    console.print(f"[green]✓[/green] Created: {output}")
except (InvalidMarkdownError, ConversionError) as e:
    console.print(f"[red]✗ Error:[/red] {e}")
    sys.exit(1)
```

### In Converter (converter.py)

Raise specific exceptions with clear messages:
```python
try:
    markdown_content = input_path.read_text(encoding="utf-8")
except FileNotFoundError:
    raise InvalidMarkdownError(f"File not found: {input_path}")
except Exception as e:
    raise InvalidMarkdownError(f"Error reading {input_path}: {e}")
```

### In Batch Processing

**Continue on individual failures**, report summary at end:
```python
results = []
for md_file in markdown_files:
    result = {"input": md_file, "success": False, "error": None}
    try:
        self.convert_file(md_file, output_path)
        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    results.append(result)
return results  # CLI displays summary
```

## Git Workflow

### What's Tracked
- Source code (`src/`)
- Documentation (`docs/`, `README.md`, etc.)
- Example markdown files (`examples/markdown/`)
- Configuration templates (`.env.example`)
- Project files (`pyproject.toml`, `uv.lock`)

### What's Ignored
- User config (`.env`)
- Virtual environment (`.venv/`)
- Generated PDFs (`output/`, `examples/converted/`)
- Python cache (`__pycache__/`, `*.pyc`)

### Making Commits

```bash
# After making changes
git add .
git commit -m "Description of changes

Details about what changed and why.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## Things to AVOID

### ❌ Don't Do These

1. **Don't use pip** - This project uses `uv`
   ```bash
   # ❌ WRONG
   pip install markdown

   # ✅ CORRECT
   uv add markdown
   ```

2. **Don't create files in root** - Keep root clean
   - Source code → `src/md2pdf/`
   - Documentation → `docs/`
   - Examples → `examples/markdown/`

3. **Don't remove --create-output-dir** - This is a core feature for organization

4. **Don't mix PDFs with markdown files** - Always use subdirectories

5. **Don't hardcode paths** - Use `config.default_output_dir`

6. **Don't skip type hints** - They're required for clarity

7. **Don't commit generated files** - Check `.gitignore` first

8. **Don't use complex CLI structure** - Keep it simple with `typer.run(main)`

## Future Enhancements Roadmap

### Phase 2: Image Support
- Handle relative image paths
- Support remote URLs (http/https)
- Embed images in PDFs

### Phase 3: Custom Styling
- Custom CSS file support (`--css` flag)
- Multiple built-in themes
- CSS overrides via .env

### Phase 4: Advanced Features
- Watch mode (auto-convert on changes)
- Table of contents generation
- Headers/footers
- Watermarks
- PDF metadata (author, date, title)

### Phase 5: Testing & Quality
- pytest test suite
- Code coverage
- CI/CD with GitHub Actions
- Ruff linting, mypy type checking

**Before adding features**: Consider if they align with the core goal (simple, reliable markdown → PDF conversion).

## Troubleshooting Common Issues

### "Import errors after changes"
```bash
uv sync  # Reinstall package
```

### "CLI changes not taking effect"
Package needs rebuild after CLI changes:
```bash
uv sync
```

### "PDFs not generating"
Check WeasyPrint dependencies:
```bash
uv run python -c "import weasyprint; print(weasyprint.__version__)"
```

### "Styles not applying"
Verify CSS in `styles.py:get_default_css()` - check for syntax errors.

## Quick Reference Commands

```bash
# Run the tool
uv run md2pdf <file> --create-output-dir auto

# Show help
uv run md2pdf --help

# Test all examples
uv run md2pdf examples/markdown/ --create-output-dir test

# Check git status
git status

# View structure
tree -L 2 -I '.venv|__pycache__|output'

# Read documentation
cat QUICK_START.md
cat docs/USAGE_GUIDE.md
```

## Questions to Ask Before Making Changes

1. **Does this keep the project simple?** - Avoid feature creep
2. **Will this confuse users?** - Prioritize clarity
3. **Does this maintain file organization?** - Don't break `--create-output-dir`
4. **Is this well-documented?** - Update docs when adding features
5. **Is this tested?** - Use examples to verify changes work

## Getting Help

- **User docs**: `README.md`, `QUICK_START.md`
- **Developer docs**: `docs/PROJECT_STRUCTURE.md`
- **Examples**: `examples/markdown/`
- **This file**: Project conventions and guidelines

## Summary for AI Assistants

When working on this project:
1. ✅ Always use `uv`, never `pip`
2. ✅ Keep `--create-output-dir` feature working
3. ✅ Maintain clean file separation (code/docs/examples/output)
4. ✅ Test changes with examples directory
5. ✅ Update documentation when adding features
6. ✅ Use type hints and docstrings
7. ✅ Follow the existing architecture patterns
8. ✅ Keep it simple - this is a focused tool, not a framework

The project is designed to be simple, reliable, and user-friendly. Any changes should support these goals.
