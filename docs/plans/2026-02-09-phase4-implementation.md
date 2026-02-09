# Phase 4: Advanced Features Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add professional document features (page numbers, table of contents, PDF metadata) to md2pdf while maintaining backward compatibility and the "simple and reliable" philosophy.

**Architecture:** Enhance existing rendering pipeline with CSS-based headers/footers using WeasyPrint's `@page` rules, implement two-pass rendering for TOC with accurate page numbers, and add PDF metadata support via WeasyPrint's native `pdf_metadata` parameter.

**Tech Stack:** Python 3.11+, uv (package manager), WeasyPrint (PDF generation), pytest (testing), typer (CLI)

---

## Task 1: Page Numbers Configuration

**Files:**
- Modify: `src/md2pdf/config.py`
- Modify: `.env.example`
- Create: `tests/test_page_numbers.py`

### Step 1: Write test for page number config loading

```python
# tests/test_page_numbers.py
"""Tests for page number configuration."""

import os
import pytest
from pathlib import Path
from md2pdf.config import Config


class TestPageNumbersConfig:
    """Tests for page numbers configuration loading."""

    def test_default_page_numbers_disabled(self, clean_env, tmp_path):
        """Test page numbers disabled by default."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.enable_page_numbers is False

    def test_enable_page_numbers_true(self, clean_env, tmp_path):
        """Test enabling page numbers via .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("ENABLE_PAGE_NUMBERS=true\n")

        config = Config.load(env_file)

        assert config.enable_page_numbers is True

    def test_enable_page_numbers_false(self, clean_env, tmp_path):
        """Test explicitly disabling page numbers."""
        env_file = tmp_path / ".env"
        env_file.write_text("ENABLE_PAGE_NUMBERS=false\n")

        config = Config.load(env_file)

        assert config.enable_page_numbers is False

    def test_page_number_position_default(self, clean_env, tmp_path):
        """Test default page number position is center."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.page_number_position == "center"

    def test_page_number_position_left(self, clean_env, tmp_path):
        """Test setting position to left."""
        env_file = tmp_path / ".env"
        env_file.write_text("PAGE_NUMBER_POSITION=left\n")

        config = Config.load(env_file)

        assert config.page_number_position == "left"

    def test_page_number_position_right(self, clean_env, tmp_path):
        """Test setting position to right."""
        env_file = tmp_path / ".env"
        env_file.write_text("PAGE_NUMBER_POSITION=right\n")

        config = Config.load(env_file)

        assert config.page_number_position == "right"

    def test_page_number_position_invalid(self, clean_env, tmp_path):
        """Test invalid position raises error."""
        env_file = tmp_path / ".env"
        env_file.write_text("PAGE_NUMBER_POSITION=invalid\n")

        with pytest.raises(ValueError, match="PAGE_NUMBER_POSITION must be one of"):
            Config.load(env_file)

    def test_page_number_format_default(self, clean_env, tmp_path):
        """Test default page number format."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.page_number_format == "Page {page} of {pages}"

    def test_page_number_format_custom(self, clean_env, tmp_path):
        """Test custom page number format."""
        env_file = tmp_path / ".env"
        env_file.write_text('PAGE_NUMBER_FORMAT={page}/{pages}\n')

        config = Config.load(env_file)

        assert config.page_number_format == "{page}/{pages}"

    def test_page_number_format_truncated(self, clean_env, tmp_path):
        """Test long format string is truncated."""
        env_file = tmp_path / ".env"
        long_format = "x" * 150
        env_file.write_text(f'PAGE_NUMBER_FORMAT={long_format}\n')

        config = Config.load(env_file)

        assert len(config.page_number_format) == 100
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_page_numbers.py -v`

Expected: FAIL with "ModuleNotFoundError" or "AttributeError" (config fields don't exist yet)

### Step 3: Add config fields to Config dataclass

Modify `src/md2pdf/config.py`:

```python
# Add to Config dataclass (after existing fields, around line 30):

    # Page Numbers (Phase 4)
    enable_page_numbers: bool = False
    page_number_position: str = "center"  # left, center, right
    page_number_format: str = "Page {page} of {pages}"
```

### Step 4: Add config loading logic

Modify `src/md2pdf/config.py` in the `load()` method (around line 60):

```python
    # Load page number settings
    enable_page_numbers_str = os.getenv("ENABLE_PAGE_NUMBERS", "false").lower()
    enable_page_numbers = enable_page_numbers_str == "true"

    page_number_position = os.getenv("PAGE_NUMBER_POSITION", "center")
    # Validate position
    valid_positions = ["left", "center", "right"]
    if page_number_position not in valid_positions:
        raise ValueError(
            f"PAGE_NUMBER_POSITION must be one of: {', '.join(valid_positions)}. "
            f"Got: {page_number_position}"
        )

    page_number_format = os.getenv("PAGE_NUMBER_FORMAT", "Page {page} of {pages}")
    # Truncate long format strings
    if len(page_number_format) > 100:
        page_number_format = page_number_format[:100]

    return cls(
        page_size=os.getenv("PDF_PAGE_SIZE", "A4"),
        margin_top=os.getenv("PDF_MARGIN_TOP", "2cm"),
        margin_bottom=os.getenv("PDF_MARGIN_BOTTOM", "2cm"),
        margin_left=os.getenv("PDF_MARGIN_LEFT", "2cm"),
        margin_right=os.getenv("PDF_MARGIN_RIGHT", "2cm"),
        font_family=os.getenv("PDF_FONT_FAMILY", "Arial, sans-serif"),
        font_size=os.getenv("PDF_FONT_SIZE", "11pt"),
        code_font=os.getenv("PDF_CODE_FONT", "Courier, monospace"),
        default_output_dir=os.getenv("DEFAULT_OUTPUT_DIR", "output"),
        preserve_structure=os.getenv("PRESERVE_DIRECTORY_STRUCTURE", "true").lower()
        == "true",
        enable_page_numbers=enable_page_numbers,
        page_number_position=page_number_position,
        page_number_format=page_number_format,
    )
```

### Step 5: Run tests to verify they pass

Run: `uv run pytest tests/test_page_numbers.py -v`

Expected: ALL PASS (10 tests)

### Step 6: Update .env.example

Add to `.env.example` (after existing settings):

```bash
# Headers/Footers (Phase 4)
# Enable page numbers in PDF footers
ENABLE_PAGE_NUMBERS=false

# Page number position: left, center, or right
PAGE_NUMBER_POSITION=center

# Page number format (use {page} for current page, {pages} for total pages)
PAGE_NUMBER_FORMAT=Page {page} of {pages}
```

### Step 7: Commit

```bash
git add src/md2pdf/config.py tests/test_page_numbers.py .env.example
git commit -m "feat: add page number configuration

- Add enable_page_numbers, page_number_position, page_number_format to Config
- Load from .env with defaults
- Validate position (left/center/right)
- Truncate format strings at 100 chars
- Add 10 tests for config loading

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Page Number CSS Generation

**Files:**
- Modify: `src/md2pdf/styles.py`
- Modify: `tests/test_styles.py`

### Step 1: Write test for page number CSS generation

Add to `tests/test_styles.py`:

```python
class TestPageNumberCSS:
    """Tests for page number CSS generation."""

    def test_get_page_number_css_disabled(self, mock_config):
        """Test no CSS when page numbers disabled."""
        mock_config.enable_page_numbers = False

        css = get_page_number_css(mock_config)

        assert css == ""

    def test_get_page_number_css_center(self, mock_config):
        """Test page numbers in center position."""
        mock_config.enable_page_numbers = True
        mock_config.page_number_position = "center"
        mock_config.page_number_format = "Page {page} of {pages}"

        css = get_page_number_css(mock_config)

        assert "@bottom-center" in css
        assert "counter(page)" in css
        assert "counter(pages)" in css
        assert "font-size: 9pt" in css
        assert "color: #666" in css

    def test_get_page_number_css_left(self, mock_config):
        """Test page numbers in left position."""
        mock_config.enable_page_numbers = True
        mock_config.page_number_position = "left"

        css = get_page_number_css(mock_config)

        assert "@bottom-left" in css

    def test_get_page_number_css_right(self, mock_config):
        """Test page numbers in right position."""
        mock_config.enable_page_numbers = True
        mock_config.page_number_position = "right"

        css = get_page_number_css(mock_config)

        assert "@bottom-right" in css

    def test_get_page_number_css_custom_format(self, mock_config):
        """Test custom format string."""
        mock_config.enable_page_numbers = True
        mock_config.page_number_format = "{page}/{pages}"

        css = get_page_number_css(mock_config)

        # Should have counter(page) and counter(pages) but not "Page" or "of"
        assert "counter(page)" in css
        assert "counter(pages)" in css
        assert 'content: "" counter(page) "/" counter(pages) ""' in css

    def test_get_page_css_includes_page_numbers(self, mock_config):
        """Test get_page_css includes page numbers when enabled."""
        mock_config.enable_page_numbers = True
        mock_config.page_number_position = "center"

        css = get_page_css(mock_config)

        # Should have both @page setup and page numbers
        assert "@page" in css
        assert "@bottom-center" in css
        assert "counter(page)" in css
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_styles.py::TestPageNumberCSS -v`

Expected: FAIL with "ImportError: cannot import name 'get_page_number_css'"

### Step 3: Implement get_page_number_css function

Add to `src/md2pdf/styles.py` (before get_page_css function):

```python
def get_page_number_css(config: Config) -> str:
    """Generate CSS for page numbers in headers/footers.

    Args:
        config: Configuration with page number settings.

    Returns:
        CSS string for @page margin boxes, or empty string if disabled.
    """
    if not config.enable_page_numbers:
        return ""

    # Map position to CSS margin box
    position_map = {
        "left": "@bottom-left",
        "center": "@bottom-center",
        "right": "@bottom-right",
    }

    margin_box = position_map[config.page_number_position]

    # Convert format string to CSS content
    # Split by placeholders and build content string
    content_parts = []
    remaining = config.page_number_format

    while remaining:
        if "{page}" in remaining:
            before, after = remaining.split("{page}", 1)
            if before:
                content_parts.append(f'"{before}"')
            content_parts.append('counter(page)')
            remaining = after
        elif "{pages}" in remaining:
            before, after = remaining.split("{pages}", 1)
            if before:
                content_parts.append(f'"{before}"')
            content_parts.append('counter(pages)')
            remaining = after
        else:
            # No more placeholders
            if remaining:
                content_parts.append(f'"{remaining}"')
            break

    content_value = " ".join(content_parts)

    return f"""
    {margin_box} {{
        content: {content_value};
        font-size: 9pt;
        color: #666;
        font-family: Arial, sans-serif;
    }}
    """
```

### Step 4: Update get_page_css to include page numbers

Modify `get_page_css()` in `src/md2pdf/styles.py`:

```python
def get_page_css(config: Config) -> str:
    """Generate @page CSS from config.

    Returns only page setup and page numbers.

    Args:
        config: Configuration with page setup values.

    Returns:
        CSS string for @page rules.
    """
    page_number_css = get_page_number_css(config)

    return f"""
@page {{
    size: {config.page_size};
    margin-top: {config.margin_top};
    margin-bottom: {config.margin_bottom};
    margin-left: {config.margin_left};
    margin-right: {config.margin_right};
{page_number_css}
}}
"""
```

### Step 5: Run tests to verify they pass

Run: `uv run pytest tests/test_styles.py::TestPageNumberCSS -v`

Expected: ALL PASS (6 tests)

### Step 6: Run full test suite to check for regressions

Run: `uv run pytest -v`

Expected: All existing tests still pass

### Step 7: Commit

```bash
git add src/md2pdf/styles.py tests/test_styles.py
git commit -m "feat: add page number CSS generation

- Add get_page_number_css() function
- Generate @bottom-left/center/right CSS based on position
- Convert format string placeholders to CSS counter() functions
- Include page numbers in get_page_css() output
- Add 6 tests for CSS generation

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Page Numbers CLI Flag

**Files:**
- Modify: `src/md2pdf/cli.py`
- Modify: `tests/test_cli.py`

### Step 1: Write test for --page-numbers CLI flag

Add to `tests/test_cli.py`:

```python
class TestPageNumbersCLI:
    """Tests for --page-numbers CLI flag."""

    def test_page_numbers_flag_enable(self, tmp_path):
        """Test --page-numbers flag enables page numbers."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file), "--page-numbers"]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_page_numbers_flag_disable(self, tmp_path):
        """Test --no-page-numbers flag disables page numbers."""
        # Create .env with page numbers enabled
        env_file = tmp_path / ".env"
        env_file.write_text("ENABLE_PAGE_NUMBERS=true\n")

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        # Override with --no-page-numbers
        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file), "--no-page-numbers"]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_page_numbers_default_from_env(self, tmp_path):
        """Test page numbers use .env default when flag not provided."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_cli.py::TestPageNumbersCLI -v`

Expected: FAIL (flag doesn't exist yet)

### Step 3: Add --page-numbers flag to CLI

Modify `src/md2pdf/cli.py` main function signature (add after theme/css parameters):

```python
    page_numbers: Optional[bool] = typer.Option(
        None,
        "--page-numbers/--no-page-numbers",
        help="Enable/disable page numbers in PDF footer (overrides .env)",
    ),
```

### Step 4: Apply CLI override to config

In `main()` function body, after config loading (around line 90):

```python
    # Apply CLI overrides to config
    if page_numbers is not None:
        config.enable_page_numbers = page_numbers
```

### Step 5: Run tests to verify they pass

Run: `uv run pytest tests/test_cli.py::TestPageNumbersCLI -v`

Expected: ALL PASS (3 tests)

### Step 6: Manual test

```bash
# Test with page numbers enabled
uv run md2pdf examples/markdown/test_basic.md --page-numbers --output /tmp/test_page_numbers.pdf

# Open PDF and verify page numbers appear at bottom center
```

Expected: PDF generated with page numbers at bottom

### Step 7: Commit

```bash
git add src/md2pdf/cli.py tests/test_cli.py
git commit -m "feat: add --page-numbers CLI flag

- Add --page-numbers/--no-page-numbers flag to CLI
- Apply CLI override to config.enable_page_numbers
- Add 3 tests for flag parsing and overrides

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: PDF Metadata Configuration

**Files:**
- Modify: `src/md2pdf/config.py`
- Modify: `.env.example`
- Modify: `tests/test_page_numbers.py` (rename to `tests/test_phase4_config.py`)

### Step 1: Write tests for metadata config loading

Add to `tests/test_phase4_config.py`:

```python
class TestMetadataConfig:
    """Tests for PDF metadata configuration."""

    def test_metadata_defaults_empty(self, clean_env, tmp_path):
        """Test metadata fields default to None/empty."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.pdf_title is None
        assert config.pdf_author is None
        assert config.pdf_subject is None
        assert config.pdf_keywords is None

    def test_metadata_title_loaded(self, clean_env, tmp_path):
        """Test loading title from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_TITLE=My Document\n")

        config = Config.load(env_file)

        assert config.pdf_title == "My Document"

    def test_metadata_author_loaded(self, clean_env, tmp_path):
        """Test loading author from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_AUTHOR=Jane Doe\n")

        config = Config.load(env_file)

        assert config.pdf_author == "Jane Doe"

    def test_metadata_subject_loaded(self, clean_env, tmp_path):
        """Test loading subject from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_SUBJECT=Technical Documentation\n")

        config = Config.load(env_file)

        assert config.pdf_subject == "Technical Documentation"

    def test_metadata_keywords_loaded(self, clean_env, tmp_path):
        """Test loading keywords from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_KEYWORDS=markdown, pdf, documentation\n")

        config = Config.load(env_file)

        assert config.pdf_keywords == "markdown, pdf, documentation"

    def test_metadata_all_fields(self, clean_env, tmp_path):
        """Test loading all metadata fields together."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
PDF_TITLE=User Guide
PDF_AUTHOR=Jane Doe
PDF_SUBJECT=Product Documentation
PDF_KEYWORDS=guide, manual, help
""")

        config = Config.load(env_file)

        assert config.pdf_title == "User Guide"
        assert config.pdf_author == "Jane Doe"
        assert config.pdf_subject == "Product Documentation"
        assert config.pdf_keywords == "guide, manual, help"
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_phase4_config.py::TestMetadataConfig -v`

Expected: FAIL (config fields don't exist yet)

### Step 3: Add metadata fields to Config dataclass

Modify `src/md2pdf/config.py` (add after page number fields):

```python
    # PDF Metadata (Phase 4)
    pdf_title: Optional[str] = None
    pdf_author: Optional[str] = None
    pdf_subject: Optional[str] = None
    pdf_keywords: Optional[str] = None
```

Add import at top of file:

```python
from typing import Optional
```

### Step 4: Load metadata in Config.load()

Add to `load()` method (after page number loading):

```python
    # Load PDF metadata
    pdf_title = os.getenv("PDF_TITLE") or None
    pdf_author = os.getenv("PDF_AUTHOR") or None
    pdf_subject = os.getenv("PDF_SUBJECT") or None
    pdf_keywords = os.getenv("PDF_KEYWORDS") or None

    return cls(
        # ... existing fields ...
        enable_page_numbers=enable_page_numbers,
        page_number_position=page_number_position,
        page_number_format=page_number_format,
        pdf_title=pdf_title,
        pdf_author=pdf_author,
        pdf_subject=pdf_subject,
        pdf_keywords=pdf_keywords,
    )
```

### Step 5: Run tests to verify they pass

Run: `uv run pytest tests/test_phase4_config.py::TestMetadataConfig -v`

Expected: ALL PASS (6 tests)

### Step 6: Update .env.example

Add to `.env.example`:

```bash
# PDF Metadata (Phase 4)
# Set PDF document properties (all optional)
PDF_TITLE=
PDF_AUTHOR=
PDF_SUBJECT=
PDF_KEYWORDS=
```

### Step 7: Commit

```bash
git add src/md2pdf/config.py tests/test_phase4_config.py .env.example
git commit -m "feat: add PDF metadata configuration

- Add pdf_title, pdf_author, pdf_subject, pdf_keywords to Config
- Load from .env (all optional, default to None)
- Add 6 tests for metadata loading
- Update .env.example with metadata fields

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: PDF Metadata CLI Flags and Converter Integration

**Files:**
- Modify: `src/md2pdf/cli.py`
- Modify: `src/md2pdf/converter.py`
- Modify: `tests/test_converter.py`

### Step 1: Write tests for metadata in converter

Add to `tests/test_converter.py`:

```python
class TestConverterMetadata:
    """Tests for PDF metadata in converter."""

    def test_convert_with_metadata(self, mock_config, tmp_path):
        """Test converter accepts and uses metadata."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test Document\n\nContent here.")

        output_file = tmp_path / "output.pdf"

        metadata = {
            'title': 'Test Document',
            'author': 'Test Author',
            'subject': 'Test Subject',
            'keywords': 'test, document',
        }

        converter.convert_file(md_file, output_file, metadata=metadata)

        assert output_file.exists()
        # Note: Actual metadata verification requires PDF inspection
        # which is tested in integration tests

    def test_convert_with_partial_metadata(self, mock_config, tmp_path):
        """Test converter with only some metadata fields."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        metadata = {
            'title': 'Test Document',
            'author': None,
        }

        converter.convert_file(md_file, output_file, metadata=metadata)

        assert output_file.exists()

    def test_convert_without_metadata(self, mock_config, tmp_path):
        """Test converter defaults title to filename when no metadata."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "my_document.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        converter.convert_file(md_file, output_file, metadata=None)

        assert output_file.exists()
        # Title should default to "my_document" (filename without extension)
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_converter.py::TestConverterMetadata -v`

Expected: FAIL (metadata parameter doesn't exist yet)

### Step 3: Update convert_file to accept metadata

Modify `src/md2pdf/converter.py` - update `convert_file()` signature:

```python
    def convert_file(
        self,
        input_path: Path,
        output_path: Path,
        metadata: Optional[Dict[str, Optional[str]]] = None
    ) -> None:
        """Convert markdown file to PDF.

        Args:
            input_path: Path to input markdown file.
            output_path: Path where PDF will be saved.
            metadata: Optional PDF metadata dict (title, author, subject, keywords).

        Raises:
            InvalidMarkdownError: If file cannot be read or parsed.
            ConversionError: If PDF generation fails.
        """
```

Add import at top:

```python
from typing import Optional, Dict
```

### Step 4: Build metadata dict and pass to WeasyPrint

In `convert_file()` method body, before `document.write_pdf()`:

```python
        # Build PDF metadata with smart defaults
        pdf_metadata = {}

        if metadata:
            # Use provided metadata or fall back to filename for title
            pdf_metadata['title'] = metadata.get('title') or input_path.stem
            pdf_metadata['author'] = metadata.get('author') or ''
            pdf_metadata['subject'] = metadata.get('subject') or ''
            pdf_metadata['keywords'] = metadata.get('keywords') or ''
        else:
            # Default title to filename
            pdf_metadata['title'] = input_path.stem
            pdf_metadata['author'] = ''
            pdf_metadata['subject'] = ''
            pdf_metadata['keywords'] = ''

        # Write PDF with metadata
        document.write_pdf(output_path, pdf_metadata=pdf_metadata)
```

### Step 5: Add metadata CLI flags

Modify `src/md2pdf/cli.py` main function signature (add after page_numbers parameter):

```python
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="PDF title (overrides .env, defaults to filename)",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        help="PDF author (overrides .env)",
    ),
    subject: Optional[str] = typer.Option(
        None,
        "--subject",
        help="PDF subject (overrides .env)",
    ),
    keywords: Optional[str] = typer.Option(
        None,
        "--keywords",
        help="PDF keywords, comma-separated (overrides .env)",
    ),
```

### Step 6: Build metadata dict and pass to converter

In `main()` function, after config loading and overrides:

```python
    # Build metadata dict (CLI overrides .env)
    metadata = {
        'title': title or config.pdf_title,
        'author': author or config.pdf_author,
        'subject': subject or config.pdf_subject,
        'keywords': keywords or config.pdf_keywords,
    }
```

Update converter calls to pass metadata:

```python
    # For single file conversion:
    converter.convert_file(input_path, output, metadata=metadata)

    # For batch conversion, pass metadata to each convert_file call
```

### Step 7: Run tests to verify they pass

Run: `uv run pytest tests/test_converter.py::TestConverterMetadata -v`

Expected: ALL PASS (3 tests)

### Step 8: Manual test

```bash
# Test with metadata
uv run md2pdf examples/markdown/test_basic.md \
    --title "Test Document" \
    --author "Test Author" \
    --subject "Testing" \
    --keywords "test, md2pdf" \
    --output /tmp/test_metadata.pdf

# Open PDF, check Properties dialog to verify metadata
```

Expected: PDF has metadata in properties

### Step 9: Commit

```bash
git add src/md2pdf/converter.py src/md2pdf/cli.py tests/test_converter.py
git commit -m "feat: add PDF metadata support

- Add metadata parameter to convert_file()
- Build pdf_metadata dict with smart defaults (title from filename)
- Pass metadata to WeasyPrint's write_pdf()
- Add CLI flags: --title, --author, --subject, --keywords
- CLI flags override .env settings
- Add 3 tests for metadata handling

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Table of Contents Infrastructure

**Files:**
- Modify: `src/md2pdf/converter.py`
- Create: `tests/test_toc.py`

### Step 1: Write tests for header extraction

```python
# tests/test_toc.py
"""Tests for table of contents generation."""

import pytest
from pathlib import Path
from md2pdf.converter import MarkdownConverter


class TestHeaderExtraction:
    """Tests for extract_headers method."""

    def test_generate_anchor_id_simple(self, mock_config):
        """Test anchor ID generation from simple text."""
        converter = MarkdownConverter(mock_config)
        seen_ids = set()

        anchor_id = converter.generate_anchor_id("Introduction", seen_ids)

        assert anchor_id == "introduction"
        assert "introduction" in seen_ids

    def test_generate_anchor_id_with_spaces(self, mock_config):
        """Test anchor ID converts spaces to hyphens."""
        converter = MarkdownConverter(mock_config)
        seen_ids = set()

        anchor_id = converter.generate_anchor_id("Getting Started", seen_ids)

        assert anchor_id == "getting-started"

    def test_generate_anchor_id_with_special_chars(self, mock_config):
        """Test anchor ID removes special characters."""
        converter = MarkdownConverter(mock_config)
        seen_ids = set()

        anchor_id = converter.generate_anchor_id("FAQ's & Tips!", seen_ids)

        assert anchor_id == "faqs-tips"

    def test_generate_anchor_id_duplicate(self, mock_config):
        """Test duplicate anchor IDs get numbered."""
        converter = MarkdownConverter(mock_config)
        seen_ids = set()

        id1 = converter.generate_anchor_id("Introduction", seen_ids)
        id2 = converter.generate_anchor_id("Introduction", seen_ids)
        id3 = converter.generate_anchor_id("Introduction", seen_ids)

        assert id1 == "introduction"
        assert id2 == "introduction-2"
        assert id3 == "introduction-3"

    def test_generate_anchor_id_numbers_only(self, mock_config):
        """Test anchor ID with only numbers."""
        converter = MarkdownConverter(mock_config)
        seen_ids = set()

        anchor_id = converter.generate_anchor_id("2024", seen_ids)

        assert anchor_id == "2024"

    def test_generate_anchor_id_empty_after_sanitize(self, mock_config):
        """Test anchor ID when text becomes empty after sanitization."""
        converter = MarkdownConverter(mock_config)
        seen_ids = set()

        anchor_id = converter.generate_anchor_id("!!!", seen_ids)

        # Should return something reasonable (e.g., "heading-1")
        assert len(anchor_id) > 0


class TestTOCGeneration:
    """Tests for TOC HTML generation."""

    def test_generate_toc_html_empty(self, mock_config):
        """Test TOC generation with no headers."""
        converter = MarkdownConverter(mock_config)

        html = converter.generate_toc_html([])

        assert html == ""

    def test_generate_toc_html_single_h1(self, mock_config):
        """Test TOC with single H1 header."""
        converter = MarkdownConverter(mock_config)

        headers = [
            {'text': 'Introduction', 'level': 1, 'page': 1, 'anchor_id': 'introduction'}
        ]

        html = converter.generate_toc_html(headers)

        assert '<div class="toc">' in html
        assert '<h1>Table of Contents</h1>' in html
        assert '<a href="#introduction">Introduction</a>' in html
        assert '<span class="toc-page">1</span>' in html
        assert 'class="toc-h1"' in html

    def test_generate_toc_html_mixed_levels(self, mock_config):
        """Test TOC with mixed H1 and H2 headers."""
        converter = MarkdownConverter(mock_config)

        headers = [
            {'text': 'Introduction', 'level': 1, 'page': 1, 'anchor_id': 'introduction'},
            {'text': 'Overview', 'level': 2, 'page': 2, 'anchor_id': 'overview'},
            {'text': 'Getting Started', 'level': 1, 'page': 3, 'anchor_id': 'getting-started'},
        ]

        html = converter.generate_toc_html(headers)

        assert 'class="toc-h1"' in html
        assert 'class="toc-h2"' in html
        assert '<a href="#introduction">Introduction</a>' in html
        assert '<a href="#overview">Overview</a>' in html
        assert '<a href="#getting-started">Getting Started</a>' in html

    def test_generate_toc_html_page_numbers(self, mock_config):
        """Test TOC includes correct page numbers."""
        converter = MarkdownConverter(mock_config)

        headers = [
            {'text': 'Chapter 1', 'level': 1, 'page': 5, 'anchor_id': 'chapter-1'},
            {'text': 'Chapter 2', 'level': 1, 'page': 15, 'anchor_id': 'chapter-2'},
        ]

        html = converter.generate_toc_html(headers)

        assert '<span class="toc-page">5</span>' in html
        assert '<span class="toc-page">15</span>' in html
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_toc.py -v`

Expected: FAIL (methods don't exist yet)

### Step 3: Implement generate_anchor_id method

Add to `src/md2pdf/converter.py`:

```python
import re
from typing import Set

    def generate_anchor_id(self, text: str, seen_ids: Set[str]) -> str:
        """Generate unique anchor ID from heading text.

        Args:
            text: Heading text to convert to anchor ID.
            seen_ids: Set of already-used IDs to avoid duplicates.

        Returns:
            Unique anchor ID string.
        """
        # Convert to lowercase
        base_id = text.lower()

        # Replace spaces with hyphens
        base_id = base_id.replace(" ", "-")

        # Remove special characters (keep only alphanumeric and hyphens)
        base_id = re.sub(r'[^a-z0-9-]', '', base_id)

        # Remove consecutive hyphens
        base_id = re.sub(r'-+', '-', base_id)

        # Remove leading/trailing hyphens
        base_id = base_id.strip('-')

        # Handle empty result
        if not base_id:
            base_id = "heading"

        # Handle duplicates
        if base_id not in seen_ids:
            seen_ids.add(base_id)
            return base_id

        # Append counter for duplicates
        counter = 2
        while f"{base_id}-{counter}" in seen_ids:
            counter += 1

        unique_id = f"{base_id}-{counter}"
        seen_ids.add(unique_id)
        return unique_id
```

### Step 4: Implement generate_toc_html method

Add to `src/md2pdf/converter.py`:

```python
from typing import List, Dict, Any

    def generate_toc_html(self, headers: List[Dict[str, Any]]) -> str:
        """Generate HTML for table of contents.

        Args:
            headers: List of header dicts from extract_headers().
                Each dict has keys: text, level, page, anchor_id

        Returns:
            HTML string for TOC, or empty string if no headers.
        """
        if not headers:
            return ""

        toc_html = '<div class="toc">\n'
        toc_html += '    <h1>Table of Contents</h1>\n'
        toc_html += '    <ul>\n'

        for header in headers:
            css_class = f"toc-h{header['level']}"
            toc_html += f'        <li class="{css_class}">\n'
            toc_html += f'            <a href="#{header["anchor_id"]}">{header["text"]}</a>\n'
            toc_html += f'            <span class="toc-page">{header["page"]}</span>\n'
            toc_html += '        </li>\n'

        toc_html += '    </ul>\n'
        toc_html += '</div>\n'

        return toc_html
```

### Step 5: Run tests to verify they pass

Run: `uv run pytest tests/test_toc.py -v`

Expected: ALL PASS (11 tests)

### Step 6: Commit

```bash
git add src/md2pdf/converter.py tests/test_toc.py
git commit -m "feat: add TOC infrastructure (anchor ID and HTML generation)

- Add generate_anchor_id() method for unique anchor IDs
- Handle duplicates, special characters, spaces
- Add generate_toc_html() method to build TOC HTML
- Support H1 and H2 headers with page numbers
- Add 11 tests for anchor ID and HTML generation

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Table of Contents Two-Pass Rendering

**Files:**
- Modify: `src/md2pdf/converter.py`
- Modify: `src/md2pdf/cli.py`
- Modify: `tests/test_toc.py`
- Modify: `tests/test_cli.py`

### Step 1: Write test for extract_headers (requires WeasyPrint Document)

Add to `tests/test_toc.py`:

```python
class TestTwoPassRendering:
    """Tests for two-pass TOC rendering."""

    def test_convert_with_toc_flag(self, mock_config, tmp_path):
        """Test conversion with toc_enabled=True."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("""# Introduction

This is the introduction.

## Overview

An overview section.

# Getting Started

Getting started content.
""")

        output_file = tmp_path / "output.pdf"

        # Convert with TOC enabled
        converter.convert_file(md_file, output_file, toc_enabled=True)

        assert output_file.exists()
        # Note: Verifying TOC content requires PDF inspection
        # which is tested in integration tests

    def test_convert_without_toc(self, mock_config, tmp_path):
        """Test normal conversion still works (backward compatibility)."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        # Convert without TOC (default)
        converter.convert_file(md_file, output_file, toc_enabled=False)

        assert output_file.exists()

    def test_convert_toc_no_headers_warning(self, mock_config, tmp_path, capsys):
        """Test warning when document has no headers."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("Just plain text with no headers.")

        output_file = tmp_path / "output.pdf"

        converter.convert_file(md_file, output_file, toc_enabled=True)

        captured = capsys.readouterr()
        assert "No H1/H2 headers found for TOC" in captured.out
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_toc.py::TestTwoPassRendering -v`

Expected: FAIL (toc_enabled parameter doesn't exist yet)

### Step 3: Implement extract_headers method

Add to `src/md2pdf/converter.py`:

```python
    def extract_headers(self, html_content: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract H1 and H2 headers with page numbers from rendered PDF.

        Args:
            html_content: HTML content to render.
            base_url: Base URL for resolving relative paths.

        Returns:
            List of dicts with keys: text, level, page, anchor_id
        """
        from weasyprint import HTML

        # Render to get document structure
        document = HTML(string=html_content, base_url=base_url)

        headers = []
        seen_ids = set()

        try:
            # Render to get bookmark tree
            rendered = document.render()
            bookmarks = rendered.make_bookmark_tree()

            # Extract H1 and H2 only
            for bookmark in bookmarks:
                if hasattr(bookmark, 'level') and bookmark.level in (1, 2):
                    anchor_id = self.generate_anchor_id(bookmark.label, seen_ids)
                    headers.append({
                        'text': bookmark.label,
                        'level': bookmark.level,
                        'page': bookmark.destination[0] if bookmark.destination else 1,
                        'anchor_id': anchor_id,
                    })
        except Exception as e:
            # If extraction fails, return empty list
            # (TOC generation will be skipped)
            console.print(f"[yellow]Warning:[/yellow] Could not extract headers: {e}")
            return []

        return headers
```

Add import at top:

```python
from rich.console import Console
console = Console()
```

### Step 4: Update convert_file to support two-pass rendering

Modify `convert_file()` signature and implementation:

```python
    def convert_file(
        self,
        input_path: Path,
        output_path: Path,
        toc_enabled: bool = False,
        metadata: Optional[Dict[str, Optional[str]]] = None
    ) -> None:
        """Convert markdown file to PDF.

        Args:
            input_path: Path to input markdown file.
            output_path: Path where PDF will be saved.
            toc_enabled: Whether to generate table of contents.
            metadata: Optional PDF metadata dict.

        Raises:
            InvalidMarkdownError: If file cannot be read or parsed.
            ConversionError: If PDF generation fails.
        """
        try:
            markdown_content = input_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise InvalidMarkdownError(f"File not found: {input_path}")
        except Exception as e:
            raise InvalidMarkdownError(f"Error reading {input_path}: {e}")

        try:
            # Convert markdown to HTML
            html_content = self.markdown.convert(markdown_content)

            # Two-pass rendering if TOC enabled
            if toc_enabled:
                # Pass 1: Extract headers
                headers = self.extract_headers(html_content, str(input_path.parent))

                if not headers:
                    console.print("[yellow]Warning:[/yellow] No H1/H2 headers found for TOC")
                else:
                    # Pass 2: Generate and prepend TOC
                    toc_html = self.generate_toc_html(headers)
                    html_content = toc_html + html_content

            # Final render
            from weasyprint import HTML
            document = HTML(string=html_content, base_url=str(input_path.parent))

            # Build metadata
            pdf_metadata = {}
            if metadata:
                pdf_metadata['title'] = metadata.get('title') or input_path.stem
                pdf_metadata['author'] = metadata.get('author') or ''
                pdf_metadata['subject'] = metadata.get('subject') or ''
                pdf_metadata['keywords'] = metadata.get('keywords') or ''
            else:
                pdf_metadata['title'] = input_path.stem
                pdf_metadata['author'] = ''
                pdf_metadata['subject'] = ''
                pdf_metadata['keywords'] = ''

            # Write PDF
            document.write_pdf(output_path, pdf_metadata=pdf_metadata)

        except Exception as e:
            raise ConversionError(f"Error converting {input_path}: {e}")
```

### Step 5: Add --toc CLI flag

Modify `src/md2pdf/cli.py` main signature (add after metadata parameters):

```python
    toc: bool = typer.Option(
        False,
        "--toc/--no-toc",
        help="Generate table of contents from H1 and H2 headers",
    ),
```

Update converter.convert_file calls to pass toc_enabled:

```python
    # For single file:
    converter.convert_file(
        input_path,
        output,
        toc_enabled=toc,
        metadata=metadata
    )

    # For batch: same pattern
```

### Step 6: Run tests to verify they pass

Run: `uv run pytest tests/test_toc.py::TestTwoPassRendering -v`

Expected: ALL PASS (3 tests)

### Step 7: Manual test

```bash
# Create test markdown with headers
cat > /tmp/test_toc.md << EOF
# Introduction

This is the introduction section.

## Purpose

Why this document exists.

# Getting Started

How to get started.

## Installation

Installation instructions.

# Advanced Topics

Advanced content here.
EOF

# Convert with TOC
uv run md2pdf /tmp/test_toc.md --toc --output /tmp/test_toc.pdf

# Open PDF and verify:
# 1. TOC appears at start
# 2. TOC links work
# 3. Page numbers are correct
```

Expected: PDF with TOC at start, clickable links

### Step 8: Commit

```bash
git add src/md2pdf/converter.py src/md2pdf/cli.py tests/test_toc.py
git commit -m "feat: implement two-pass TOC rendering

- Add extract_headers() method to get headers from rendered PDF
- Update convert_file() to support toc_enabled parameter
- Implement two-pass rendering: extract headers, then render with TOC
- Add --toc CLI flag
- Show warning when no headers found
- Add 3 tests for two-pass rendering

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Table of Contents Styling

**Files:**
- Modify: `src/md2pdf/themes/github.css`
- Modify: `src/md2pdf/themes/minimal.css`
- Modify: `src/md2pdf/themes/academic.css`
- Modify: `src/md2pdf/themes/dark.css`
- Modify: `src/md2pdf/themes/modern.css`

### Step 1: Add TOC CSS to github.css

Add to `src/md2pdf/themes/github.css` (at end of file):

```css
/* Table of Contents */
.toc {
    page-break-after: always;
    margin-bottom: 2em;
}

.toc h1 {
    font-size: 1.5em;
    margin-bottom: 1em;
    border-bottom: 2px solid #eaecef;
    padding-bottom: 0.5em;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 0.5em;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}

.toc-h1 {
    font-weight: 600;
}

.toc-h2 {
    padding-left: 1.5em;
    font-weight: 400;
    font-size: 0.95em;
}

.toc a {
    flex-grow: 1;
    text-decoration: none;
    color: #0366d6;
}

.toc a:hover {
    text-decoration: underline;
}

.toc-page {
    margin-left: 1em;
    font-weight: 400;
    color: #666;
    font-size: 0.9em;
}
```

### Step 2: Add TOC CSS to minimal.css

Add to `src/md2pdf/themes/minimal.css`:

```css
/* Table of Contents */
.toc {
    page-break-after: always;
    margin-bottom: 3em;
}

.toc h1 {
    font-size: 2em;
    font-weight: 300;
    margin-bottom: 1.5em;
    letter-spacing: -0.02em;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 1em;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}

.toc-h1 {
    font-weight: 400;
}

.toc-h2 {
    padding-left: 2em;
    font-weight: 300;
}

.toc a {
    flex-grow: 1;
    text-decoration: none;
    color: #495057;
}

.toc a:hover {
    color: #212529;
}

.toc-page {
    margin-left: 1em;
    font-weight: 300;
    color: #6c757d;
}
```

### Step 3: Add TOC CSS to academic.css

Add to `src/md2pdf/themes/academic.css`:

```css
/* Table of Contents */
.toc {
    page-break-after: always;
    margin-bottom: 24pt;
}

.toc h1 {
    font-size: 14pt;
    font-weight: bold;
    margin-bottom: 12pt;
    text-align: center;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 6pt;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}

.toc-h1 {
    font-weight: bold;
}

.toc-h2 {
    padding-left: 2em;
    font-weight: normal;
    font-style: italic;
}

.toc a {
    flex-grow: 1;
    text-decoration: underline;
    color: #000000;
}

.toc-page {
    margin-left: 1em;
    font-weight: normal;
    color: #000000;
}
```

### Step 4: Add TOC CSS to dark.css

Add to `src/md2pdf/themes/dark.css`:

```css
/* Table of Contents */
.toc {
    page-break-after: always;
    margin-bottom: 2em;
    background-color: #0d1117;
}

.toc h1 {
    font-size: 1.5em;
    margin-bottom: 1em;
    border-bottom: 2px solid #30363d;
    padding-bottom: 0.5em;
    color: #ffffff;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 0.5em;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}

.toc-h1 {
    font-weight: 600;
}

.toc-h2 {
    padding-left: 1.5em;
    font-weight: 400;
}

.toc a {
    flex-grow: 1;
    text-decoration: none;
    color: #58a6ff;
}

.toc a:hover {
    text-decoration: underline;
}

.toc-page {
    margin-left: 1em;
    font-weight: 400;
    color: #8b949e;
}
```

### Step 5: Add TOC CSS to modern.css

Add to `src/md2pdf/themes/modern.css`:

```css
/* Table of Contents */
.toc {
    page-break-after: always;
    margin-bottom: 2em;
    padding: 1.5em;
    background: linear-gradient(to right, #f7fafc 0%, #edf2f7 100%);
    border-left: 4px solid #4299e1;
    border-radius: 8px;
}

.toc h1 {
    font-size: 2em;
    font-weight: 700;
    margin-bottom: 1em;
    color: #2d3748;
    border-bottom: 3px solid #4299e1;
    padding-bottom: 0.3em;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 0.75em;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}

.toc-h1 {
    font-weight: 600;
}

.toc-h2 {
    padding-left: 2em;
    font-weight: 500;
}

.toc a {
    flex-grow: 1;
    text-decoration: none;
    color: #3182ce;
    font-weight: 500;
}

.toc a:hover {
    color: #2c5aa0;
    border-bottom: 1px solid #3182ce;
}

.toc-page {
    margin-left: 1em;
    font-weight: 600;
    color: #4a5568;
}
```

### Step 6: Manual test with all themes

```bash
# Test TOC with each theme
for theme in github minimal academic dark modern; do
    uv run md2pdf /tmp/test_toc.md --toc --theme $theme --create-output-dir toc_themes
done

# Open each PDF and verify:
# - TOC styling matches theme aesthetic
# - Links work
# - Page numbers visible
```

Expected: 5 PDFs with themed TOC styling

### Step 7: Commit

```bash
git add src/md2pdf/themes/*.css
git commit -m "feat: add TOC styling to all themes

- Add .toc CSS to github, minimal, academic, dark, modern themes
- Each theme styles TOC to match its aesthetic
- TOC has page-break-after for separation
- H1/H2 indentation and styling
- Links styled per theme

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Integration Testing

**Files:**
- Create: `tests/test_phase4_integration.py`

### Step 1: Write integration tests

```python
# tests/test_phase4_integration.py
"""Integration tests for Phase 4 features."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from md2pdf.cli import main
import typer

runner = CliRunner()


class TestPageNumbersIntegration:
    """Integration tests for page numbers."""

    def test_page_numbers_appear_in_pdf(self, tmp_path):
        """Test page numbers actually appear in generated PDF."""
        md_file = tmp_path / "test.md"
        md_file.write_text("""# Page 1

Content on page 1.

<div style="page-break-after: always;"></div>

# Page 2

Content on page 2.
""")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file), "--page-numbers"]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        # Note: Actual page number verification requires PDF inspection
        # which would need PyPDF or similar

    def test_page_numbers_all_positions(self, tmp_path):
        """Test page numbers work in all positions."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        for position in ["left", "center", "right"]:
            env_file = tmp_path / f".env_{position}"
            env_file.write_text(f"ENABLE_PAGE_NUMBERS=true\nPAGE_NUMBER_POSITION={position}\n")

            output_file = tmp_path / f"output_{position}.pdf"

            # Note: Would need to load specific .env file
            # For now, test with CLI flag override
            result = runner.invoke(
                typer.main.get_command(main),
                [str(md_file), "--output", str(output_file), "--page-numbers"]
            )

            assert result.exit_code == 0
            assert output_file.exists()


class TestTOCIntegration:
    """Integration tests for table of contents."""

    def test_toc_generation_end_to_end(self, tmp_path):
        """Test complete TOC workflow."""
        md_file = tmp_path / "test.md"
        md_file.write_text("""# Introduction

Introduction content.

## Background

Background information.

# Methods

Methods section.

## Approach

Our approach.

# Results

Results here.
""")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file), "--toc"]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_toc_with_all_themes(self, tmp_path):
        """Test TOC works with all themes."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Chapter 1\n\nContent\n\n## Section 1.1\n\nMore content")

        for theme in ["github", "minimal", "academic", "dark", "modern"]:
            output_file = tmp_path / f"output_{theme}.pdf"

            result = runner.invoke(
                typer.main.get_command(main),
                [str(md_file), "--output", str(output_file), "--toc", "--theme", theme]
            )

            assert result.exit_code == 0
            assert output_file.exists()

    def test_toc_no_headers_warning(self, tmp_path, capsys):
        """Test warning shown when document has no headers."""
        md_file = tmp_path / "test.md"
        md_file.write_text("Just plain text with no headers at all.")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file), "--toc"]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        # Warning about no headers should be in output


class TestMetadataIntegration:
    """Integration tests for PDF metadata."""

    def test_metadata_via_cli(self, tmp_path):
        """Test metadata set via CLI flags."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test Document\n\nContent")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [
                str(md_file),
                "--output", str(output_file),
                "--title", "My Test Document",
                "--author", "Test Author",
                "--subject", "Testing",
                "--keywords", "test, pdf, metadata",
            ]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        # Note: Actual metadata verification requires PDF inspection

    def test_metadata_via_env(self, tmp_path):
        """Test metadata loaded from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
PDF_TITLE=Environment Title
PDF_AUTHOR=Environment Author
""")

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        # Note: Would need to load specific .env file
        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()


class TestCombinedFeatures:
    """Test all Phase 4 features together."""

    def test_all_features_combined(self, tmp_path):
        """Test TOC + page numbers + metadata together."""
        md_file = tmp_path / "test.md"
        md_file.write_text("""# Introduction

Introduction content here.

## Overview

Overview section.

# Main Content

Main content section.

## Details

Detailed information.

# Conclusion

Conclusion text.
""")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [
                str(md_file),
                "--output", str(output_file),
                "--toc",
                "--page-numbers",
                "--title", "Complete Test",
                "--author", "Test Suite",
                "--theme", "modern",
            ]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_backward_compatibility(self, tmp_path):
        """Test existing functionality still works (no Phase 4 features)."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Simple Test\n\nSimple content")

        output_file = tmp_path / "output.pdf"

        # Convert without any Phase 4 flags
        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()
```

### Step 2: Run tests to verify they pass

Run: `uv run pytest tests/test_phase4_integration.py -v`

Expected: ALL PASS (10 tests)

### Step 3: Run full test suite

Run: `uv run pytest -v`

Expected: All tests pass (previous 96 + new ~26 = 122+ tests)

### Step 4: Check coverage

Run: `uv run pytest --cov=src/md2pdf --cov-report=term-missing`

Expected: 89%+ coverage maintained

### Step 5: Commit

```bash
git add tests/test_phase4_integration.py
git commit -m "test: add Phase 4 integration tests

- Test page numbers in PDFs
- Test TOC generation end-to-end
- Test TOC with all themes
- Test metadata via CLI and .env
- Test all features combined
- Test backward compatibility
- Add 10 integration tests

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/USAGE_GUIDE.md`
- Create: `docs/PHASE4_FEATURES.md`

### Step 1: Update README.md

Add after "Custom CSS" section (around line 96):

```markdown
### Page Numbers

Add page numbers to your PDFs:

```bash
# Enable page numbers
uv run md2pdf document.md --page-numbers

# Configure via .env
echo "ENABLE_PAGE_NUMBERS=true" >> .env
echo "PAGE_NUMBER_POSITION=center" >> .env  # left, center, or right
uv run md2pdf document.md
```

### Table of Contents

Generate a table of contents from your document headers:

```bash
# Add TOC to PDF
uv run md2pdf document.md --toc

# Combine with page numbers and themes
uv run md2pdf document.md --toc --page-numbers --theme academic
```

### PDF Metadata

Set PDF document properties:

```bash
# Via CLI
uv run md2pdf document.md \
    --title "User Guide" \
    --author "Your Name" \
    --subject "Documentation" \
    --keywords "guide, manual, help"

# Via .env
echo "PDF_TITLE=User Guide" >> .env
echo "PDF_AUTHOR=Your Name" >> .env
uv run md2pdf document.md
```
```

### Step 2: Update USAGE_GUIDE.md

Add new section after "Styling Your PDFs":

```markdown
## Advanced Features

### Page Numbers

Add page numbers to the footer of your PDFs.

**Enable via .env:**

```bash
# .env
ENABLE_PAGE_NUMBERS=true
PAGE_NUMBER_POSITION=center  # Options: left, center, right
PAGE_NUMBER_FORMAT=Page {page} of {pages}  # Customize format
```

**Enable via CLI:**

```bash
# Enable for single conversion
md2pdf document.md --page-numbers

# Override .env setting
md2pdf document.md --no-page-numbers
```

**Format options:**
- Use `{page}` for current page number
- Use `{pages}` for total pages
- Examples:
  - `Page {page} of {pages}` → "Page 1 of 5"
  - `{page}/{pages}` → "1/5"
  - `- {page} -` → "- 1 -"

### Table of Contents

Generate a table of contents from H1 and H2 headers in your document.

**Usage:**

```bash
# Generate TOC
md2pdf document.md --toc

# Combine with other features
md2pdf document.md --toc --page-numbers --theme academic
```

**How it works:**
- Extracts H1 and H2 headers from your document
- Generates TOC at the beginning of the PDF
- Includes clickable links to each section
- Shows page numbers for each header
- Styled to match your chosen theme

**Tips:**
- TOC works best with structured documents that use headers
- Only H1 and H2 headers are included (not H3-H6)
- TOC appears on separate pages before your content
- Links in the TOC are clickable in PDF viewers

### PDF Metadata

Set document properties that appear in PDF viewers.

**Configure via .env:**

```bash
# .env
PDF_TITLE=User Guide
PDF_AUTHOR=Jane Doe
PDF_SUBJECT=Product Documentation
PDF_KEYWORDS=guide, manual, help, tutorial
```

**Override via CLI:**

```bash
md2pdf document.md \
    --title "User Guide" \
    --author "Jane Doe" \
    --subject "Documentation" \
    --keywords "guide, manual"
```

**Metadata fields:**
- **Title**: Document title (defaults to filename if not set)
- **Author**: Document author/creator
- **Subject**: Document description/subject
- **Keywords**: Comma-separated keywords for search

**View metadata:**
- Open PDF in viewer
- Check Document Properties (usually in File menu)
- Metadata appears in Properties dialog

### Combining Features

All Phase 4 features work together:

```bash
# Complete example: TOC + page numbers + metadata + theme
md2pdf report.md \
    --toc \
    --page-numbers \
    --title "Annual Report 2024" \
    --author "Company Name" \
    --subject "Financial Report" \
    --keywords "annual, report, financial" \
    --theme academic \
    --create-output-dir reports
```
```

### Step 3: Create PHASE4_FEATURES.md

```markdown
# Phase 4 Features Guide

Comprehensive guide to Phase 4 advanced features: page numbers, table of contents, and PDF metadata.

## Overview

Phase 4 adds three professional document features while maintaining md2pdf's simplicity:

1. **Page Numbers** - Configurable footer page numbers
2. **Table of Contents** - Auto-generated from document headers
3. **PDF Metadata** - Document properties (title, author, etc.)

All features are:
- **Opt-in** - Enable only what you need
- **Configurable** - Via .env or CLI flags
- **Theme-compatible** - Work with all 5 themes
- **Backward compatible** - Existing workflows unchanged

## Page Numbers

### Quick Start

```bash
# Enable page numbers
md2pdf document.md --page-numbers
```

### Configuration

**Position:**
- `left` - Bottom left corner
- `center` - Bottom center (default)
- `right` - Bottom right corner

**Format:**
- Use `{page}` for current page number
- Use `{pages}` for total pages
- Default: `Page {page} of {pages}`

**.env Configuration:**

```bash
ENABLE_PAGE_NUMBERS=true
PAGE_NUMBER_POSITION=center
PAGE_NUMBER_FORMAT=Page {page} of {pages}
```

**CLI Flags:**

```bash
# Enable
md2pdf document.md --page-numbers

# Disable (override .env)
md2pdf document.md --no-page-numbers
```

### Examples

```bash
# Center position (default)
md2pdf report.md --page-numbers

# Custom format via .env
echo 'PAGE_NUMBER_FORMAT={page}/{pages}' >> .env
md2pdf report.md --page-numbers

# Left position
echo 'PAGE_NUMBER_POSITION=left' >> .env
md2pdf report.md --page-numbers
```

### Styling

- Font size: 9pt (smaller than body text)
- Color: Gray (#666) - unobtrusive
- Position: Bottom of page
- Respects theme aesthetic

## Table of Contents

### Quick Start

```bash
# Generate TOC
md2pdf document.md --toc
```

### How It Works

1. **Scans your document** for H1 and H2 headers
2. **Extracts header text and page numbers**
3. **Generates TOC** at the beginning of PDF
4. **Creates clickable links** to each section

### What Gets Included

- **H1 headers** - Top-level sections
- **H2 headers** - Subsections (indented)
- **H3-H6 ignored** - Only two levels for simplicity

### TOC Structure

```
Table of Contents

Introduction ........................ 1
  Background ........................ 2
Getting Started ..................... 3
  Installation ...................... 4
  Configuration ..................... 5
Advanced Topics ..................... 6
```

### Examples

```bash
# Basic TOC
md2pdf documentation.md --toc

# TOC with page numbers
md2pdf documentation.md --toc --page-numbers

# TOC with theme
md2pdf documentation.md --toc --theme academic

# Complete professional document
md2pdf report.md --toc --page-numbers --theme academic
```

### Edge Cases

**No headers found:**
- Warning displayed: "No H1/H2 headers found for TOC"
- PDF still generated without TOC

**Duplicate header text:**
- Anchors numbered automatically: `#introduction`, `#introduction-2`

**Special characters in headers:**
- Sanitized automatically for valid anchor IDs

### Theme Styling

Each theme styles the TOC to match its aesthetic:

- **GitHub**: Clean, familiar look
- **Minimal**: Extra spacing, light typography
- **Academic**: Formal, centered heading
- **Dark**: Light text on dark background
- **Modern**: Colorful accents, gradient background

## PDF Metadata

### Quick Start

```bash
# Via CLI
md2pdf document.md --title "User Guide" --author "Jane Doe"
```

### Metadata Fields

**Title** - Document title
- Defaults to filename if not set
- Appears in PDF viewer title bar

**Author** - Document creator
- Optional (empty if not set)

**Subject** - Document description
- Optional (empty if not set)

**Keywords** - Comma-separated tags
- Optional (empty if not set)
- Used for PDF search/indexing

### Configuration

**.env:**

```bash
PDF_TITLE=User Guide
PDF_AUTHOR=Jane Doe
PDF_SUBJECT=Product Documentation
PDF_KEYWORDS=guide, manual, help
```

**CLI Flags:**

```bash
md2pdf document.md \
    --title "User Guide" \
    --author "Jane Doe" \
    --subject "Documentation" \
    --keywords "guide, manual"
```

**CLI overrides .env** - Explicit values take precedence

### Examples

```bash
# Set title and author
md2pdf report.md --title "Annual Report 2024" --author "Company Name"

# Full metadata
md2pdf guide.md \
    --title "User Guide" \
    --author "Documentation Team" \
    --subject "Product Help" \
    --keywords "guide, manual, tutorial, help"

# Configure in .env for all documents
cat >> .env << EOF
PDF_AUTHOR=Your Name
PDF_KEYWORDS=documentation, markdown, pdf
EOF
```

### Viewing Metadata

1. Open PDF in any viewer (Adobe, Preview, etc.)
2. Open Properties dialog (usually in File menu)
3. Metadata appears in Document Properties

## Combining Features

All features work together seamlessly:

```bash
# Professional report
md2pdf annual_report.md \
    --toc \
    --page-numbers \
    --title "Annual Report 2024" \
    --author "Company Name" \
    --subject "Financial Report" \
    --theme academic

# User documentation
md2pdf user_guide.md \
    --toc \
    --page-numbers \
    --title "User Guide v2.0" \
    --author "Documentation Team" \
    --keywords "guide, manual, tutorial" \
    --theme github

# Technical documentation with minimal theme
md2pdf api_docs.md \
    --toc \
    --page-numbers \
    --title "API Documentation" \
    --subject "Developer Guide" \
    --theme minimal
```

## Best Practices

### When to Use TOC

**Good use cases:**
- Long documents (5+ pages)
- Multi-chapter documents
- Technical documentation
- User guides and manuals

**Not recommended:**
- Short documents (1-2 pages)
- Documents without clear structure
- Documents with few headers

### When to Use Page Numbers

**Good use cases:**
- Any multi-page document
- Documents for printing
- Reports and formal documents
- Reference documentation

**Not recommended:**
- Single-page documents

### Metadata Tips

1. **Always set title** - More professional than filename
2. **Set author for shared documents** - Clarifies ownership
3. **Use keywords for searchable PDFs** - Better organization
4. **Keep metadata concise** - Clear and descriptive

## FAQ

**Q: Can I customize TOC depth?**
A: Not yet. Currently fixed at H1 and H2 for simplicity.

**Q: Can I style page numbers differently?**
A: Position and format are configurable. Color/font are fixed to avoid theme conflicts.

**Q: Does TOC affect page numbers?**
A: TOC pages are included in the page count. If TOC is 2 pages, your content starts on page 3.

**Q: Can I put page numbers in the header?**
A: Not yet. Currently only footer position is supported.

**Q: What if my headers have special characters?**
A: They're automatically sanitized for valid HTML anchor IDs.

**Q: Can I disable TOC for certain sections?**
A: No. TOC includes all H1 and H2 headers. Use H3-H6 for sections you want to exclude.

## Troubleshooting

**TOC links don't work:**
- Ensure using a PDF viewer that supports hyperlinks
- Try a different viewer (Adobe Reader, Preview, etc.)

**Page numbers not appearing:**
- Check `ENABLE_PAGE_NUMBERS=true` in .env
- Or use `--page-numbers` flag
- Verify PDF has multiple pages

**Metadata not visible:**
- Open Document Properties in your PDF viewer
- Some viewers hide empty fields

**TOC styling looks wrong:**
- Ensure using one of the 5 built-in themes
- Custom CSS may need TOC styles added

## See Also

- [THEMES.md](THEMES.md) - Theme customization guide
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Complete usage examples
- [README.md](../README.md) - Quick start guide
```

### Step 4: Commit documentation

```bash
git add README.md docs/USAGE_GUIDE.md docs/PHASE4_FEATURES.md
git commit -m "docs: add Phase 4 feature documentation

- Update README with page numbers, TOC, metadata examples
- Add comprehensive Phase 4 section to USAGE_GUIDE
- Create PHASE4_FEATURES.md guide with:
  - Detailed usage for each feature
  - Configuration examples
  - Best practices and tips
  - FAQ and troubleshooting

Part of Phase 4: Advanced Features

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Final Testing and Verification

**Files:**
- None (testing only)

### Step 1: Run full test suite

```bash
uv run pytest -v
```

Expected: 122+ tests passing, no failures

### Step 2: Check coverage

```bash
uv run pytest --cov=src/md2pdf --cov-report=term-missing
```

Expected: 89%+ coverage

### Step 3: Manual testing - Page Numbers

```bash
# Test all positions
for pos in left center right; do
    echo "ENABLE_PAGE_NUMBERS=true" > /tmp/.env_$pos
    echo "PAGE_NUMBER_POSITION=$pos" >> /tmp/.env_$pos
    uv run md2pdf examples/markdown/test_complex.md --page-numbers --output /tmp/pages_$pos.pdf
done

# Open PDFs and verify page numbers appear in correct positions
```

### Step 4: Manual testing - TOC

```bash
# Create test document with headers
cat > /tmp/toc_test.md << 'EOF'
# Introduction

Introduction content here with some text to make it multi-page.

## Purpose

Why this document exists and what it covers.

## Scope

What's included and what's not.

# Getting Started

How to begin using this.

## Prerequisites

What you need before starting.

## Installation

Step-by-step installation guide.

# Advanced Topics

Advanced content for experienced users.

## Configuration

How to configure advanced settings.

## Troubleshooting

Common issues and solutions.

# Conclusion

Summary and next steps.
EOF

# Test with all themes
for theme in github minimal academic dark modern; do
    uv run md2pdf /tmp/toc_test.md --toc --theme $theme --create-output-dir toc_final
done

# Verify in each PDF:
# - TOC appears at start
# - All headers listed
# - Links work
# - Page numbers correct
# - Styling matches theme
```

### Step 5: Manual testing - Metadata

```bash
# Test metadata
uv run md2pdf examples/markdown/test_basic.md \
    --title "Phase 4 Test Document" \
    --author "md2pdf Test Suite" \
    --subject "Testing Phase 4 Metadata" \
    --keywords "test, phase4, metadata, pdf" \
    --output /tmp/metadata_test.pdf

# Open PDF, check Properties dialog:
# - Title: "Phase 4 Test Document"
# - Author: "md2pdf Test Suite"
# - Subject: "Testing Phase 4 Metadata"
# - Keywords: "test, phase4, metadata, pdf"
```

### Step 6: Manual testing - Combined

```bash
# Test all features together
uv run md2pdf /tmp/toc_test.md \
    --toc \
    --page-numbers \
    --title "Complete Feature Test" \
    --author "Test Suite" \
    --subject "Phase 4 Integration Test" \
    --keywords "toc, page numbers, metadata" \
    --theme modern \
    --output /tmp/complete_test.pdf

# Verify in PDF:
# - TOC present with links
# - Page numbers at bottom
# - Metadata in properties
# - Modern theme styling
```

### Step 7: Backward compatibility test

```bash
# Ensure existing usage still works
uv run md2pdf examples/markdown/ --create-output-dir backward_compat_test

# Verify:
# - All files converted
# - No errors
# - Output identical to Phase 3
```

### Step 8: Document test results

Create test report summary and verify all success criteria met.

---

## Summary

**Implementation Order:**
1. ✅ Task 1: Page Numbers Configuration
2. ✅ Task 2: Page Number CSS Generation
3. ✅ Task 3: Page Numbers CLI Flag
4. ✅ Task 4: PDF Metadata Configuration
5. ✅ Task 5: PDF Metadata CLI Flags and Converter Integration
6. ✅ Task 6: Table of Contents Infrastructure
7. ✅ Task 7: Table of Contents Two-Pass Rendering
8. ✅ Task 8: Table of Contents Styling
9. ✅ Task 9: Integration Testing
10. ✅ Task 10: Documentation
11. ✅ Task 11: Final Testing and Verification

**Expected Outcome:**
- 3 new features working (page numbers, TOC, metadata)
- 122+ tests passing
- 89%+ coverage maintained
- Complete documentation
- Backward compatible
- No new dependencies

**Files Modified:** 15
**Files Created:** 4
**Tests Added:** ~26
**Commits:** 11

**Success Criteria Checklist:**
- [ ] Page numbers appear at configured position
- [ ] Page numbers respect format template
- [ ] --toc flag generates table of contents
- [ ] TOC links navigate correctly
- [ ] TOC styled consistently across themes
- [ ] PDF metadata appears in properties
- [ ] Metadata defaults to filename for title
- [ ] CLI flags override .env settings
- [ ] All features work together
- [ ] Backward compatible
- [ ] 122+ tests passing with 89%+ coverage
- [ ] Documentation complete
- [ ] No new dependencies
