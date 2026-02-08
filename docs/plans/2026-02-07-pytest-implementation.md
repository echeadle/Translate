# Pytest Test Suite Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build comprehensive pytest test suite with 80%+ code coverage for md2pdf

**Architecture:** Integration-focused testing using real dependencies (markdown, weasyprint). Tests create actual PDFs and verify real-world behavior. Test structure mirrors source layout for easy navigation.

**Tech Stack:** pytest, pytest-cov, pytest-mock, typer.testing.CliRunner

---

## Task 1: Setup Dependencies and Structure

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/__init__.py`

**Step 1: Add pytest dependencies to pyproject.toml**

```bash
# Current working directory
pwd
# Expected: /home/echeadle/Translate/.worktrees/pytest-test-suite
```

Add dev dependencies section to `pyproject.toml` after line 13:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
]
```

**Step 2: Install dependencies**

Run: `uv sync --extra dev`
Expected: Dependencies installed successfully

**Step 3: Create tests directory structure**

Run:
```bash
mkdir -p tests/fixtures/nested
touch tests/__init__.py
```

Expected: Directory structure created

**Step 4: Verify pytest works**

Run: `uv run pytest --version`
Expected: `pytest 8.x.x`

**Step 5: Commit**

```bash
git add pyproject.toml tests/__init__.py
git commit -m "feat: add pytest test suite infrastructure

Add pytest, pytest-cov, pytest-mock as dev dependencies.
Create tests/ directory structure.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Create Test Fixtures

**Files:**
- Create: `tests/fixtures/simple.md`
- Create: `tests/fixtures/tables.md`
- Create: `tests/fixtures/code_blocks.md`
- Create: `tests/fixtures/complex.md`
- Create: `tests/fixtures/empty.md`
- Create: `tests/fixtures/invalid.md`
- Create: `tests/fixtures/nested/subdoc.md`

**Step 1: Create simple.md fixture**

```markdown
# Simple Test
Basic paragraph with **bold** and *italic*.

- List item 1
- List item 2

1. Numbered item
2. Another item
```

**Step 2: Create tables.md fixture**

```markdown
# Table Test

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Data A   | Data B   | Data C   |
| Row 3    | More     | Data     |
```

**Step 3: Create code_blocks.md fixture**

```markdown
# Code Test

Python code block:
```python
def hello_world():
    print("Hello, World!")
    return True
```

Inline `code` text example.

JavaScript example:
```javascript
const greeting = "Hello";
console.log(greeting);
```
```

**Step 4: Create complex.md fixture**

```markdown
# Complex Document Test

## Introduction
This document tests **all** markdown features.

### Lists
- Unordered item
  - Nested item
- Another item

1. Ordered item
2. Second item

### Code
```python
def test():
    return "test"
```

### Tables
| Col 1 | Col 2 |
|-------|-------|
| A     | B     |

### Blockquote
> This is a quote
> Multiple lines

---

### Emphasis
**Bold text** and *italic text* and ***both***.
```

**Step 5: Create edge case fixtures**

Create `empty.md` (0 bytes empty file)

Create `invalid.md`:
```markdown
# Test
[Broken link](
Unclosed **bold
```

Create `nested/subdoc.md`:
```markdown
# Nested Document
Testing directory structure preservation.
```

**Step 6: Verify fixtures created**

Run: `ls -la tests/fixtures/ && ls -la tests/fixtures/nested/`
Expected: All 7 files exist

**Step 7: Commit**

```bash
git add tests/fixtures/
git commit -m "feat: add test fixture markdown files

Add 7 test markdown files covering:
- Simple markdown (bold, italic, lists)
- Tables
- Code blocks with syntax highlighting
- Complex documents (all features)
- Edge cases (empty, invalid)
- Nested directories

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Create Shared Fixtures (conftest.py)

**Files:**
- Create: `tests/conftest.py`

**Step 1: Write conftest.py with shared fixtures**

```python
"""Shared pytest fixtures for md2pdf tests."""

import shutil
from pathlib import Path

import pytest

from md2pdf.config import Config
from md2pdf.converter import MarkdownConverter


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with input/output directories.

    Returns:
        Path: Workspace directory containing input/ and output/ subdirs.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "input").mkdir()
    (workspace / "output").mkdir()
    return workspace


@pytest.fixture
def sample_markdown_files(temp_workspace):
    """Copy sample markdown files to temp workspace.

    Args:
        temp_workspace: Temporary workspace directory.

    Returns:
        dict: Mapping of fixture names to Path objects.
    """
    fixtures_dir = Path(__file__).parent / "fixtures"
    input_dir = temp_workspace / "input"

    files = {}

    # Copy all non-nested fixtures
    for fixture_file in ["simple.md", "tables.md", "code_blocks.md",
                          "complex.md", "empty.md", "invalid.md"]:
        src = fixtures_dir / fixture_file
        if src.exists():
            dst = input_dir / fixture_file
            shutil.copy(src, dst)
            files[fixture_file.replace(".md", "")] = dst

    # Copy nested fixture
    nested_src = fixtures_dir / "nested" / "subdoc.md"
    if nested_src.exists():
        nested_dir = input_dir / "nested"
        nested_dir.mkdir()
        nested_dst = nested_dir / "subdoc.md"
        shutil.copy(nested_src, nested_dst)
        files["nested_subdoc"] = nested_dst

    return files


@pytest.fixture
def mock_config():
    """Create Config object with default test values.

    Returns:
        Config: Test configuration.
    """
    return Config(
        page_size="A4",
        margin_top="2cm",
        margin_bottom="2cm",
        margin_left="2cm",
        margin_right="2cm",
        font_family="Arial, sans-serif",
        font_size="11pt",
        code_font="Courier, monospace",
        default_output_dir="output",
        preserve_structure=True,
    )


@pytest.fixture
def converter(mock_config):
    """Create MarkdownConverter instance with test config.

    Args:
        mock_config: Test configuration.

    Returns:
        MarkdownConverter: Ready-to-use converter instance.
    """
    return MarkdownConverter(mock_config)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables to prevent .env pollution.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Clear all PDF_* and DEFAULT_* environment variables
    env_vars = [
        "PDF_PAGE_SIZE",
        "PDF_MARGIN_TOP",
        "PDF_MARGIN_BOTTOM",
        "PDF_MARGIN_LEFT",
        "PDF_MARGIN_RIGHT",
        "PDF_FONT_FAMILY",
        "PDF_FONT_SIZE",
        "PDF_CODE_FONT",
        "DEFAULT_OUTPUT_DIR",
        "PRESERVE_DIRECTORY_STRUCTURE",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
```

**Step 2: Verify fixtures work**

Run: `uv run pytest --collect-only tests/`
Expected: Collection successful (no tests yet, but fixtures should be found)

**Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "feat: add shared pytest fixtures

Add conftest.py with reusable fixtures:
- temp_workspace: isolated workspace for each test
- sample_markdown_files: copies test fixtures to temp
- mock_config: default Config for testing
- converter: ready-to-use MarkdownConverter
- clean_env: prevents .env pollution

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Test Utils Module

**Files:**
- Create: `tests/test_utils.py`

**Step 1: Write test for find_markdown_files**

```python
"""Tests for utility functions."""

from pathlib import Path

from md2pdf.utils import ensure_directory, find_markdown_files, get_output_path


class TestFindMarkdownFiles:
    """Tests for find_markdown_files function."""

    def test_find_markdown_files_single(self, tmp_path):
        """Test finding single markdown file in directory."""
        # Create test files
        (tmp_path / "test.md").touch()
        (tmp_path / "other.txt").touch()

        # Find markdown files
        result = find_markdown_files(tmp_path)

        # Verify
        assert len(result) == 1
        assert result[0].name == "test.md"
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/test_utils.py::TestFindMarkdownFiles::test_find_markdown_files_single -v`
Expected: PASSED

**Step 3: Add test for recursive search**

```python
    def test_find_markdown_files_recursive(self, tmp_path):
        """Test finding markdown files in subdirectories."""
        # Create nested structure
        (tmp_path / "test1.md").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "test2.md").touch()
        (subdir / "test3.md").touch()

        # Find markdown files
        result = find_markdown_files(tmp_path)

        # Verify - should find all 3 files
        assert len(result) == 3
        assert all(f.suffix == ".md" for f in result)
```

**Step 4: Run test**

Run: `uv run pytest tests/test_utils.py::TestFindMarkdownFiles::test_find_markdown_files_recursive -v`
Expected: PASSED

**Step 5: Add edge case tests**

```python
    def test_find_markdown_files_empty_directory(self, tmp_path):
        """Test finding files in empty directory."""
        result = find_markdown_files(tmp_path)
        assert len(result) == 0

    def test_find_markdown_files_mixed_extensions(self, tmp_path):
        """Test that only .md files are returned."""
        (tmp_path / "test.md").touch()
        (tmp_path / "readme.txt").touch()
        (tmp_path / "doc.markdown").touch()  # Different extension

        result = find_markdown_files(tmp_path)

        # Only .md files
        assert len(result) == 1
        assert result[0].name == "test.md"
```

**Step 6: Run all find_markdown_files tests**

Run: `uv run pytest tests/test_utils.py::TestFindMarkdownFiles -v`
Expected: All 4 tests PASSED

**Step 7: Add tests for get_output_path**

```python
class TestGetOutputPath:
    """Tests for get_output_path function."""

    def test_get_output_path_preserve_structure(self, tmp_path):
        """Test path calculation with structure preservation."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        subdir = input_dir / "docs"
        subdir.mkdir()
        input_path = subdir / "test.md"
        input_path.touch()

        output_dir = tmp_path / "output"

        result = get_output_path(input_path, input_dir, output_dir, preserve_structure=True)

        # Should preserve 'docs' subdirectory
        assert result == output_dir / "docs" / "test.pdf"

    def test_get_output_path_flatten(self, tmp_path):
        """Test path calculation without structure preservation."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        subdir = input_dir / "docs"
        subdir.mkdir()
        input_path = subdir / "test.md"
        input_path.touch()

        output_dir = tmp_path / "output"

        result = get_output_path(input_path, input_dir, output_dir, preserve_structure=False)

        # Should flatten to output root
        assert result == output_dir / "test.pdf"

    def test_get_output_path_edge_cases(self, tmp_path):
        """Test deep nesting."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        deep = input_dir / "a" / "b" / "c"
        deep.mkdir(parents=True)
        input_path = deep / "test.md"
        input_path.touch()

        output_dir = tmp_path / "output"

        result = get_output_path(input_path, input_dir, output_dir, preserve_structure=True)

        # Should preserve deep nesting
        assert result == output_dir / "a" / "b" / "c" / "test.pdf"
```

**Step 8: Run get_output_path tests**

Run: `uv run pytest tests/test_utils.py::TestGetOutputPath -v`
Expected: All 3 tests PASSED

**Step 9: Add tests for ensure_directory**

```python
class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_ensure_directory(self, tmp_path):
        """Test directory creation."""
        new_dir = tmp_path / "new" / "nested" / "dir"

        ensure_directory(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_already_exists(self, tmp_path):
        """Test idempotent directory creation."""
        new_dir = tmp_path / "existing"
        new_dir.mkdir()

        # Should not raise error
        ensure_directory(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()
```

**Step 10: Run all utils tests**

Run: `uv run pytest tests/test_utils.py -v`
Expected: All 9 tests PASSED

**Step 11: Commit**

```bash
git add tests/test_utils.py
git commit -m "test: add comprehensive tests for utils module

Test coverage:
- find_markdown_files: single, recursive, empty, mixed extensions
- get_output_path: preserve structure, flatten, edge cases
- ensure_directory: creation, idempotency

All 9 tests passing.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Test Config Module

**Files:**
- Create: `tests/test_config.py`

**Step 1: Write test for default config loading**

```python
"""Tests for configuration management."""

import os
from pathlib import Path

import pytest

from md2pdf.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_load_default_config(self, clean_env):
        """Test config loading with no .env file."""
        config = Config.load()

        # Verify defaults
        assert config.page_size == "A4"
        assert config.margin_top == "2cm"
        assert config.margin_bottom == "2cm"
        assert config.margin_left == "2cm"
        assert config.margin_right == "2cm"
        assert config.font_family == "Arial, sans-serif"
        assert config.font_size == "11pt"
        assert config.code_font == "Courier, monospace"
        assert config.default_output_dir == "output"
        assert config.preserve_structure is True
```

**Step 2: Run test**

Run: `uv run pytest tests/test_config.py::TestConfig::test_load_default_config -v`
Expected: PASSED

**Step 3: Add test for custom .env file**

```python
    def test_load_from_env_file(self, tmp_path, monkeypatch):
        """Test loading custom values from .env file."""
        # Create custom .env
        env_file = tmp_path / ".env"
        env_file.write_text("""
PDF_PAGE_SIZE=Letter
PDF_MARGIN_TOP=1in
PDF_FONT_FAMILY=Times, serif
PDF_FONT_SIZE=12pt
PRESERVE_DIRECTORY_STRUCTURE=false
""")

        # Load config
        config = Config.load(env_file)

        # Verify custom values
        assert config.page_size == "Letter"
        assert config.margin_top == "1in"
        assert config.font_family == "Times, serif"
        assert config.font_size == "12pt"
        assert config.preserve_structure is False
```

**Step 4: Run test**

Run: `uv run pytest tests/test_config.py::TestConfig::test_load_from_env_file -v`
Expected: PASSED

**Step 5: Add validation tests**

```python
    def test_config_validation(self, mock_config):
        """Test config validation passes for valid config."""
        # Should not raise
        mock_config.validate()

    def test_invalid_page_size(self, mock_config):
        """Test validation catches invalid page size."""
        mock_config.page_size = "INVALID"

        with pytest.raises(ValueError, match="Invalid page size"):
            mock_config.validate()

    def test_invalid_margin_no_unit(self, mock_config):
        """Test validation catches margin without unit."""
        mock_config.margin_top = "2"  # Missing unit

        with pytest.raises(ValueError, match="Invalid margin_top"):
            mock_config.validate()
```

**Step 6: Run validation tests**

Run: `uv run pytest tests/test_config.py::TestConfig -v`
Expected: All 5 tests PASSED

**Step 7: Add parametrized tests**

```python
    @pytest.mark.parametrize("page_size", ["A4", "Letter", "A3", "A5", "Legal"])
    def test_various_page_sizes(self, page_size, mock_config):
        """Test different valid PDF page sizes."""
        mock_config.page_size = page_size
        mock_config.validate()  # Should not raise

    def test_boolean_parsing_true(self, tmp_path):
        """Test PRESERVE_DIRECTORY_STRUCTURE parsing for true values."""
        env_file = tmp_path / ".env"
        env_file.write_text("PRESERVE_DIRECTORY_STRUCTURE=true")

        config = Config.load(env_file)
        assert config.preserve_structure is True

    def test_boolean_parsing_false(self, tmp_path):
        """Test PRESERVE_DIRECTORY_STRUCTURE parsing for false values."""
        env_file = tmp_path / ".env"
        env_file.write_text("PRESERVE_DIRECTORY_STRUCTURE=false")

        config = Config.load(env_file)
        assert config.preserve_structure is False

    def test_missing_env_falls_back_to_defaults(self, tmp_path):
        """Test partial .env file uses defaults for missing values."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_PAGE_SIZE=Letter")  # Only one value

        config = Config.load(env_file)

        # Custom value
        assert config.page_size == "Letter"
        # Defaults for rest
        assert config.margin_top == "2cm"
        assert config.font_family == "Arial, sans-serif"
```

**Step 8: Run all config tests**

Run: `uv run pytest tests/test_config.py -v`
Expected: All 10 tests PASSED (5 parametrized page sizes count as 5)

**Step 9: Commit**

```bash
git add tests/test_config.py
git commit -m "test: add comprehensive tests for config module

Test coverage:
- Default config loading
- Custom .env file loading
- Config validation (valid and invalid)
- Boolean parsing (true/false)
- Parametrized page size testing
- Partial .env fallback to defaults

All 10 tests passing.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Test Styles Module

**Files:**
- Create: `tests/test_styles.py`

**Step 1: Write test for default CSS generation**

```python
"""Tests for PDF styling and CSS generation."""

import pytest

from md2pdf.styles import get_default_css


class TestStyles:
    """Tests for get_default_css function."""

    def test_get_default_css(self, mock_config):
        """Test CSS generation with default config."""
        css = get_default_css(mock_config)

        # Verify CSS is generated
        assert isinstance(css, str)
        assert len(css) > 0

        # Check for key CSS components
        assert "@page" in css
        assert "body" in css
        assert "code" in css
        assert "table" in css

    def test_css_with_custom_fonts(self, mock_config):
        """Test CSS generation with custom font settings."""
        mock_config.font_family = "Georgia, serif"
        mock_config.code_font = "Monaco, monospace"

        css = get_default_css(mock_config)

        # Verify custom fonts in CSS
        assert "Georgia, serif" in css
        assert "Monaco, monospace" in css

    def test_css_with_custom_margins(self, mock_config):
        """Test CSS generation with custom margins."""
        mock_config.margin_top = "3cm"
        mock_config.margin_bottom = "3cm"
        mock_config.margin_left = "2.5cm"
        mock_config.margin_right = "2.5cm"

        css = get_default_css(mock_config)

        # Verify margins in @page rule
        assert "margin-top: 3cm" in css or "margin: 3cm" in css
```

**Step 2: Run tests**

Run: `uv run pytest tests/test_styles.py::TestStyles -v`
Expected: All 3 tests PASSED

**Step 3: Add tests for specific CSS styling**

```python
    def test_css_with_custom_font_size(self, mock_config):
        """Test CSS generation with custom font size."""
        mock_config.font_size = "14pt"

        css = get_default_css(mock_config)

        assert "14pt" in css

    def test_css_includes_code_styling(self, mock_config):
        """Test code block styles present."""
        css = get_default_css(mock_config)

        # Code blocks should have background
        assert "pre" in css or "code" in css
        assert "#f6f8fa" in css or "background" in css

    def test_css_includes_table_styling(self, mock_config):
        """Test table styles present."""
        css = get_default_css(mock_config)

        # Tables should have styling
        assert "table" in css
        assert "border" in css

    def test_css_includes_header_styling(self, mock_config):
        """Test header styles present for h1-h6."""
        css = get_default_css(mock_config)

        # Headers should be styled
        assert "h1" in css
        assert "h2" in css
```

**Step 4: Run tests**

Run: `uv run pytest tests/test_styles.py::TestStyles -v`
Expected: All 7 tests PASSED

**Step 5: Add parametrized page size test**

```python
    @pytest.mark.parametrize("size,expected", [
        ("A4", "A4"),
        ("Letter", "Letter"),
        ("A3", "A3"),
    ])
    def test_page_size_in_css(self, size, expected, mock_config):
        """Test different page sizes appear in CSS."""
        mock_config.page_size = size

        css = get_default_css(mock_config)

        # Page size should appear in @page rule
        assert expected in css
        assert "@page" in css

    def test_css_configuration_injection(self, mock_config):
        """Test all config values properly injected into CSS."""
        # Set all custom values
        mock_config.page_size = "Letter"
        mock_config.margin_top = "1in"
        mock_config.font_family = "Helvetica, sans-serif"
        mock_config.font_size = "10pt"
        mock_config.code_font = "Consolas, monospace"

        css = get_default_css(mock_config)

        # All values should appear
        assert "Letter" in css
        assert "1in" in css
        assert "Helvetica, sans-serif" in css
        assert "10pt" in css
        assert "Consolas, monospace" in css
```

**Step 6: Run all styles tests**

Run: `uv run pytest tests/test_styles.py -v`
Expected: All 11 tests PASSED (3 parametrized count as 3)

**Step 7: Commit**

```bash
git add tests/test_styles.py
git commit -m "test: add comprehensive tests for styles module

Test coverage:
- Default CSS generation
- Custom fonts, margins, font sizes
- Code block styling
- Table styling
- Header styling
- Parametrized page size testing
- Configuration value injection

All 11 tests passing.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Test Converter Module

**Files:**
- Create: `tests/test_converter.py`

**Step 1: Write test for simple markdown conversion**

```python
"""Tests for markdown to PDF conversion."""

import pytest

from md2pdf.converter import (
    ConversionError,
    InvalidMarkdownError,
    MarkdownConverter,
)


class TestMarkdownConverter:
    """Tests for MarkdownConverter class."""

    def test_convert_simple_markdown(self, converter, sample_markdown_files, temp_workspace):
        """Test basic markdown to PDF conversion."""
        input_file = sample_markdown_files["simple"]
        output_file = temp_workspace / "output" / "simple.pdf"

        # Convert
        converter.convert_file(input_file, output_file)

        # Verify PDF created
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_convert_with_tables(self, converter, sample_markdown_files, temp_workspace):
        """Test table rendering in PDF."""
        input_file = sample_markdown_files["tables"]
        output_file = temp_workspace / "output" / "tables.pdf"

        converter.convert_file(input_file, output_file)

        # Verify PDF created with tables
        assert output_file.exists()
        assert output_file.stat().st_size > 0
```

**Step 2: Run tests**

Run: `uv run pytest tests/test_converter.py::TestMarkdownConverter -v`
Expected: Both tests PASSED

**Step 3: Add more feature tests**

```python
    def test_convert_with_code_blocks(self, converter, sample_markdown_files, temp_workspace):
        """Test syntax highlighting in code blocks."""
        input_file = sample_markdown_files["code_blocks"]
        output_file = temp_workspace / "output" / "code_blocks.pdf"

        converter.convert_file(input_file, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_convert_complex_document(self, converter, sample_markdown_files, temp_workspace):
        """Test all features combined."""
        input_file = sample_markdown_files["complex"]
        output_file = temp_workspace / "output" / "complex.pdf"

        converter.convert_file(input_file, output_file)

        assert output_file.exists()
        # Complex document should be larger
        assert output_file.stat().st_size > 1000
```

**Step 4: Run tests**

Run: `uv run pytest tests/test_converter.py::TestMarkdownConverter -v`
Expected: All 4 tests PASSED

**Step 5: Add edge case and error handling tests**

```python
    def test_convert_empty_file(self, converter, sample_markdown_files, temp_workspace):
        """Test handling of empty markdown file."""
        input_file = sample_markdown_files["empty"]
        output_file = temp_workspace / "output" / "empty.pdf"

        # Should still create PDF (might be mostly blank)
        converter.convert_file(input_file, output_file)

        assert output_file.exists()

    def test_convert_nonexistent_file(self, converter, temp_workspace):
        """Test error handling for missing file."""
        input_file = temp_workspace / "nonexistent.md"
        output_file = temp_workspace / "output" / "out.pdf"

        with pytest.raises(InvalidMarkdownError, match="File not found"):
            converter.convert_file(input_file, output_file)

    def test_convert_invalid_output_path(self, converter, sample_markdown_files):
        """Test error when output path is unwritable."""
        input_file = sample_markdown_files["simple"]
        # Try to write to root (likely unwritable)
        output_file = Path("/root/test.pdf")

        with pytest.raises(ConversionError):
            converter.convert_file(input_file, output_file)

    def test_pdf_file_validity(self, converter, sample_markdown_files, temp_workspace):
        """Verify generated PDFs are valid."""
        input_file = sample_markdown_files["simple"]
        output_file = temp_workspace / "output" / "valid.pdf"

        converter.convert_file(input_file, output_file)

        # PDF should start with %PDF header
        with open(output_file, "rb") as f:
            header = f.read(4)
            assert header == b"%PDF"
```

**Step 6: Run all converter tests so far**

Run: `uv run pytest tests/test_converter.py::TestMarkdownConverter -v`
Expected: All 8 tests PASSED

**Step 7: Add batch conversion tests**

```python
    def test_batch_conversion(self, converter, sample_markdown_files, temp_workspace):
        """Test converting multiple files at once."""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        results = converter.convert_directory(input_dir, output_dir, preserve_structure=True)

        # Should have results for each file (7 files in fixtures)
        assert len(results) >= 3  # At least simple, tables, code_blocks

        # Check successful conversions
        successful = [r for r in results if r["success"]]
        assert len(successful) >= 3

        # Verify output files exist
        for result in successful:
            assert result["output"].exists()

    def test_batch_conversion_flatten(self, converter, sample_markdown_files, temp_workspace):
        """Test batch conversion without structure preservation."""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        results = converter.convert_directory(input_dir, output_dir, preserve_structure=False)

        # All files should be in output root
        for result in results:
            if result["success"]:
                # No subdirectories in path
                assert result["output"].parent == output_dir

    def test_batch_error_recovery(self, converter, temp_workspace):
        """Test batch continues after individual file errors."""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        # Create mix of valid and invalid files
        (input_dir / "valid.md").write_text("# Valid")
        (input_dir / "invalid.txt").write_text("Not markdown")  # Wrong extension

        # Should process what it can
        results = converter.convert_directory(input_dir, output_dir, preserve_structure=True)

        # At least the valid file should succeed
        successful = [r for r in results if r["success"]]
        assert len(successful) >= 1
```

**Step 8: Run all converter tests**

Run: `uv run pytest tests/test_converter.py -v`
Expected: All 11 tests PASSED

**Step 9: Commit**

```bash
git add tests/test_converter.py
git commit -m "test: add comprehensive tests for converter module

Test coverage:
- Simple markdown conversion
- Tables rendering
- Code blocks with syntax highlighting
- Complex documents with all features
- Empty file handling
- Error handling (nonexistent file, invalid output path)
- PDF validity verification
- Batch conversion (with/without structure preservation)
- Error recovery in batch processing

All 11 tests passing.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Test CLI Module

**Files:**
- Create: `tests/test_cli.py`

**Step 1: Write test for single file CLI conversion**

```python
"""Tests for CLI interface."""

from pathlib import Path

from typer.testing import CliRunner

from md2pdf.cli import main


runner = CliRunner()


class TestCLI:
    """Tests for CLI interface."""

    def test_single_file_conversion(self, tmp_path, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md"""
        input_file = sample_markdown_files["simple"]
        output_file = temp_workspace / "output" / "simple.pdf"

        # Run CLI
        result = runner.invoke(main, [str(input_file), "--output", str(output_file)])

        # Verify success
        assert result.exit_code == 0
        assert output_file.exists()

    def test_create_output_dir_auto(self, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md --create-output-dir auto"""
        input_file = sample_markdown_files["simple"]
        output_base = temp_workspace / "output"

        result = runner.invoke(
            main,
            [
                str(input_file),
                "--output-dir", str(output_base),
                "--create-output-dir", "auto",
            ]
        )

        assert result.exit_code == 0

        # Should create timestamped subdirectory
        subdirs = list(output_base.glob("converted_*"))
        assert len(subdirs) == 1

        # PDF should be in timestamped directory
        pdf_files = list(subdirs[0].glob("*.pdf"))
        assert len(pdf_files) == 1
```

**Step 2: Run tests**

Run: `uv run pytest tests/test_cli.py::TestCLI -v`
Expected: Both tests PASSED

**Step 3: Add more CLI flag tests**

```python
    def test_create_output_dir_named(self, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md --create-output-dir mypdfs"""
        input_file = sample_markdown_files["simple"]
        output_base = temp_workspace / "output"

        result = runner.invoke(
            main,
            [
                str(input_file),
                "--output-dir", str(output_base),
                "--create-output-dir", "mypdfs",
            ]
        )

        assert result.exit_code == 0

        # Should create named subdirectory
        named_dir = output_base / "mypdfs"
        assert named_dir.exists()

        # PDF should be there
        pdf_files = list(named_dir.glob("*.pdf"))
        assert len(pdf_files) == 1

    def test_directory_conversion(self, temp_workspace, sample_markdown_files):
        """Test: md2pdf docs/"""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        result = runner.invoke(
            main,
            [str(input_dir), "--output-dir", str(output_dir)]
        )

        assert result.exit_code == 0

        # Multiple PDFs should be created
        pdf_files = list(output_dir.rglob("*.pdf"))
        assert len(pdf_files) >= 3  # At least simple, tables, code_blocks

    def test_preserve_structure(self, temp_workspace):
        """Test: md2pdf docs/ --preserve-structure"""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        # Verify nested subdoc file exists
        nested_file = input_dir / "nested" / "subdoc.md"
        assert nested_file.exists()

        result = runner.invoke(
            main,
            [str(input_dir), "--output-dir", str(output_dir), "--preserve-structure"]
        )

        assert result.exit_code == 0

        # Nested structure should be preserved
        nested_pdf = output_dir / "nested" / "subdoc.pdf"
        assert nested_pdf.exists()

    def test_no_preserve_structure(self, temp_workspace):
        """Test: md2pdf docs/ --no-preserve-structure"""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        result = runner.invoke(
            main,
            [str(input_dir), "--output-dir", str(output_dir), "--no-preserve-structure"]
        )

        assert result.exit_code == 0

        # All PDFs should be in root output directory
        pdf_files = list(output_dir.glob("*.pdf"))
        assert len(pdf_files) >= 3

        # No nested directories
        nested_pdfs = list(output_dir.rglob("*/*.pdf"))
        assert len(nested_pdfs) == 0
```

**Step 4: Run tests**

Run: `uv run pytest tests/test_cli.py::TestCLI -v`
Expected: All 6 tests PASSED

**Step 5: Add error handling tests**

```python
    def test_custom_output_path(self, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md --output custom.pdf"""
        input_file = sample_markdown_files["simple"]
        custom_output = temp_workspace / "custom_name.pdf"

        result = runner.invoke(
            main,
            [str(input_file), "--output", str(custom_output)]
        )

        assert result.exit_code == 0
        assert custom_output.exists()

    def test_nonexistent_input_file(self, temp_workspace):
        """Test error handling for missing input."""
        nonexistent = temp_workspace / "nonexistent.md"

        result = runner.invoke(main, [str(nonexistent)])

        # Should exit with error
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_invalid_input_directory(self, temp_workspace):
        """Test non-existent directory input."""
        nonexistent_dir = temp_workspace / "nonexistent_dir"

        result = runner.invoke(main, [str(nonexistent_dir)])

        assert result.exit_code != 0

    def test_help_command(self):
        """Test: md2pdf --help"""
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Usage" in result.stdout or "Options" in result.stdout
        assert "--output" in result.stdout
        assert "--create-output-dir" in result.stdout
```

**Step 6: Run all CLI tests**

Run: `uv run pytest tests/test_cli.py -v`
Expected: All 10 tests PASSED

**Step 7: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: add comprehensive tests for CLI module

Test coverage:
- Single file conversion
- --create-output-dir auto (timestamped)
- --create-output-dir named
- Directory conversion
- --preserve-structure flag
- --no-preserve-structure flag
- Custom output path
- Error handling (nonexistent files/directories)
- Help command

All 10 tests passing using typer.testing.CliRunner.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Test Integration Workflows

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write end-to-end workflow test**

```python
"""Integration tests for complete workflows."""

from pathlib import Path

from md2pdf.config import Config
from md2pdf.converter import MarkdownConverter


class TestIntegrationWorkflows:
    """End-to-end integration tests."""

    def test_complete_single_file_workflow(self, tmp_path):
        """End-to-end: Create .md → convert → verify PDF."""
        # Create markdown file
        md_file = tmp_path / "test.md"
        md_file.write_text("""
# Test Document

This is a **complete** workflow test.

- Item 1
- Item 2

```python
print("hello")
```
""")

        # Convert
        config = Config.load()
        converter = MarkdownConverter(config)
        pdf_file = tmp_path / "test.pdf"
        converter.convert_file(md_file, pdf_file)

        # Verify
        assert pdf_file.exists()
        assert pdf_file.stat().st_size > 0

        # Verify PDF header
        with open(pdf_file, "rb") as f:
            assert f.read(4) == b"%PDF"

    def test_complete_directory_workflow(self, tmp_path):
        """End-to-end: Multiple files with subdirs."""
        # Create directory structure
        input_dir = tmp_path / "docs"
        input_dir.mkdir()
        (input_dir / "doc1.md").write_text("# Doc 1")
        (input_dir / "doc2.md").write_text("# Doc 2")

        subdir = input_dir / "subdir"
        subdir.mkdir()
        (subdir / "doc3.md").write_text("# Doc 3")

        # Convert
        config = Config.load()
        converter = MarkdownConverter(config)
        output_dir = tmp_path / "output"

        results = converter.convert_directory(input_dir, output_dir, preserve_structure=True)

        # Verify all succeeded
        assert all(r["success"] for r in results)
        assert len(results) == 3

        # Verify structure preserved
        assert (output_dir / "doc1.pdf").exists()
        assert (output_dir / "doc2.pdf").exists()
        assert (output_dir / "subdir" / "doc3.pdf").exists()
```

**Step 2: Run tests**

Run: `uv run pytest tests/test_integration.py::TestIntegrationWorkflows -v`
Expected: Both tests PASSED

**Step 3: Add more integration tests**

```python
    def test_real_world_scenario_with_auto_dir(self, tmp_path):
        """Simulate real user workflow with --create-output-dir auto."""
        from datetime import datetime

        # User creates markdown
        md_file = tmp_path / "report.md"
        md_file.write_text("# Monthly Report\n\n**Status:** Complete")

        # User converts with auto directory
        config = Config.load()
        converter = MarkdownConverter(config)

        base_output = tmp_path / "output"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        auto_dir = base_output / f"converted_{timestamp}"
        auto_dir.mkdir(parents=True)

        pdf_file = auto_dir / "report.pdf"
        converter.convert_file(md_file, pdf_file)

        # Verify organized output
        assert pdf_file.exists()
        assert "converted_" in str(pdf_file.parent)

    def test_config_file_integration(self, tmp_path):
        """Test .env file affects conversion output."""
        # Create custom .env
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_PAGE_SIZE=Letter\nPDF_FONT_SIZE=14pt")

        # Load config and convert
        config = Config.load(env_file)
        assert config.page_size == "Letter"
        assert config.font_size == "14pt"

        converter = MarkdownConverter(config)
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")
        pdf_file = tmp_path / "test.pdf"

        converter.convert_file(md_file, pdf_file)

        # PDF should be created with custom config
        assert pdf_file.exists()

    def test_error_recovery_in_batch(self, tmp_path):
        """Test batch continues after individual file errors."""
        input_dir = tmp_path / "mixed"
        input_dir.mkdir()

        # Valid file
        (input_dir / "valid.md").write_text("# Valid Document")

        # Empty file (edge case)
        (input_dir / "empty.md").write_text("")

        # Another valid file
        (input_dir / "also_valid.md").write_text("# Also Valid")

        # Convert all
        config = Config.load()
        converter = MarkdownConverter(config)
        output_dir = tmp_path / "output"

        results = converter.convert_directory(input_dir, output_dir, preserve_structure=True)

        # At least the valid files should succeed
        successful = [r for r in results if r["success"]]
        assert len(successful) >= 2

    def test_nested_directory_structure(self, tmp_path):
        """Test complex directory hierarchies."""
        # Create deep nesting
        deep = tmp_path / "docs" / "project" / "src" / "components"
        deep.mkdir(parents=True)
        (deep / "button.md").write_text("# Button Component")

        # Convert
        config = Config.load()
        converter = MarkdownConverter(config)
        input_dir = tmp_path / "docs"
        output_dir = tmp_path / "output"

        results = converter.convert_directory(input_dir, output_dir, preserve_structure=True)

        # Structure should be fully preserved
        expected = output_dir / "project" / "src" / "components" / "button.pdf"
        assert expected.exists()

    def test_all_markdown_features(self, tmp_path):
        """Test document with all supported features."""
        md_file = tmp_path / "comprehensive.md"
        md_file.write_text("""
# Comprehensive Test

## Headers Work

### Including H3

Text with **bold**, *italic*, and ***both***.

## Lists

- Unordered
  - Nested
- Items

1. Ordered
2. List

## Code

```python
def example():
    return True
```

Inline `code` too.

## Tables

| Header | Header |
|--------|--------|
| Cell   | Cell   |

## Blockquotes

> Quote text here
> Multiple lines

---

End of document.
""")

        # Convert
        config = Config.load()
        converter = MarkdownConverter(config)
        pdf_file = tmp_path / "comprehensive.pdf"

        converter.convert_file(md_file, pdf_file)

        # Should produce substantial PDF
        assert pdf_file.exists()
        assert pdf_file.stat().st_size > 2000
```

**Step 4: Run all integration tests**

Run: `uv run pytest tests/test_integration.py -v`
Expected: All 7 tests PASSED

**Step 5: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add comprehensive integration tests

Test coverage:
- Complete single file workflow (create → convert → verify)
- Complete directory workflow with subdirs
- Real-world scenario with auto directory
- Config file integration (.env affects output)
- Error recovery in batch processing
- Complex nested directory structures
- All markdown features combined

All 7 tests passing.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Run Full Test Suite and Check Coverage

**Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass (should be 50+ tests total)

**Step 2: Run with coverage report**

Run: `uv run pytest --cov=src/md2pdf --cov-report=term-missing`
Expected: Coverage report showing 80%+ coverage

**Step 3: Identify any gaps**

Review coverage report output. Look for:
- Uncovered lines in each module
- Branches not tested
- Error handling paths missed

**Step 4: Add missing tests if coverage < 80%**

If coverage is below 80%, identify the gaps and add targeted tests.
Focus on:
- Error handling in cli.py
- Edge cases in converter.py
- Validation paths in config.py

**Step 5: Re-run coverage**

Run: `uv run pytest --cov=src/md2pdf --cov-report=term-missing --cov-report=html`
Expected: 80%+ coverage, HTML report generated in htmlcov/

**Step 6: Verify test performance**

Run: `time uv run pytest`
Expected: All tests complete in <30 seconds

**Step 7: Commit coverage results**

```bash
git add -A
git commit -m "test: achieve 80%+ code coverage

Final test suite statistics:
- Total tests: [NUMBER]
- All tests passing
- Coverage: [PERCENTAGE]%
- Test execution time: [TIME]s

Coverage by module:
- converter.py: [X]%
- config.py: [X]%
- cli.py: [X]%
- styles.py: [X]%
- utils.py: [X]%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Update Documentation

**Files:**
- Modify: `README.md`
- Create: `docs/TESTING.md`

**Step 1: Create TESTING.md**

```markdown
# Testing Guide for md2pdf

## Overview

The md2pdf project uses pytest for comprehensive testing with 80%+ code coverage.

## Running Tests

### All Tests

```bash
uv run pytest
```

### With Coverage

```bash
uv run pytest --cov=src/md2pdf --cov-report=term-missing
```

### Specific Test File

```bash
uv run pytest tests/test_converter.py
```

### Specific Test

```bash
uv run pytest tests/test_cli.py::TestCLI::test_single_file_conversion
```

### Verbose Output

```bash
uv run pytest -v
```

### Show Print Statements

```bash
uv run pytest -s
```

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── fixtures/             # Test markdown files
├── test_cli.py          # CLI interface tests
├── test_converter.py    # Conversion logic tests
├── test_config.py       # Configuration tests
├── test_styles.py       # CSS generation tests
├── test_utils.py        # Utility function tests
└── test_integration.py  # End-to-end tests
```

## Writing New Tests

### Using Fixtures

```python
def test_my_feature(converter, sample_markdown_files, temp_workspace):
    """Test description."""
    # Use fixtures
    input_file = sample_markdown_files["simple"]
    output_file = temp_workspace / "output" / "test.pdf"

    # Test code
    converter.convert_file(input_file, output_file)

    # Assertions
    assert output_file.exists()
```

### Testing CLI

```python
from typer.testing import CliRunner
from md2pdf.cli import main

runner = CliRunner()

def test_cli_feature():
    """Test CLI functionality."""
    result = runner.invoke(main, ["input.md", "--output", "output.pdf"])
    assert result.exit_code == 0
```

## Test Coverage Goals

- **Overall:** 80%+ coverage
- **converter.py:** 85-90%
- **config.py:** 90-95%
- **cli.py:** 80-85%
- **styles.py:** 85-90%
- **utils.py:** 90-95%

## CI/CD Integration

Tests run automatically on:
- Every commit (future: GitHub Actions)
- Every pull request (future: GitHub Actions)

## Troubleshooting

### Tests Fail Locally

1. Ensure dependencies installed: `uv sync --extra dev`
2. Check Python version: `python --version` (need 3.11+)
3. Clear pytest cache: `rm -rf .pytest_cache`

### Coverage Not Showing

1. Install coverage: `uv sync --extra dev`
2. Run with coverage flag: `uv run pytest --cov=src/md2pdf`

### Slow Tests

Current test suite should run in <30 seconds. If slower:
1. Check for network calls (should be none)
2. Check for large file generation
3. Use `pytest -v` to identify slow tests
```

**Step 2: Update README.md**

Add testing section after "Configuration" section:

```markdown
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
```

**Step 3: Verify documentation**

Run: `cat docs/TESTING.md | head -20`
Expected: Documentation displays correctly

**Step 4: Commit documentation**

```bash
git add README.md docs/TESTING.md
git commit -m "docs: add comprehensive testing documentation

Add TESTING.md with:
- How to run tests
- Test structure overview
- Writing new tests guide
- Coverage goals
- CI/CD integration notes
- Troubleshooting tips

Update README.md with testing section.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Final Verification and Cleanup

**Step 1: Run complete test suite one final time**

Run: `uv run pytest -v --cov=src/md2pdf --cov-report=term-missing`
Expected: All tests pass, 80%+ coverage

**Step 2: Verify all test files exist**

Run: `ls -la tests/`
Expected: All test files present

**Step 3: Check git status**

Run: `git status`
Expected: Clean working directory, all changes committed

**Step 4: View commit history**

Run: `git log --oneline -15`
Expected: Series of focused commits for each task

**Step 5: Create final summary commit**

```bash
git commit --allow-empty -m "test: pytest test suite implementation complete

Summary:
- 50+ tests across 6 test modules
- 80%+ code coverage achieved
- Integration-focused testing with real dependencies
- Comprehensive fixtures and shared test utilities
- Full CLI, converter, config, styles, utils coverage
- End-to-end integration tests
- Complete testing documentation

All tests passing, ready for merge.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Step 6: Success!**

The pytest test suite implementation is complete. Next steps:
1. Review the implementation
2. Run `git log` to see all commits
3. Consider using finishing-a-development-branch skill to merge back to main

---

## Success Criteria

- [x] pytest infrastructure set up
- [x] Dev dependencies added and installed
- [x] All test fixtures created (7 markdown files)
- [x] Shared fixtures in conftest.py
- [x] test_utils.py complete (9 tests)
- [x] test_config.py complete (10 tests)
- [x] test_styles.py complete (11 tests)
- [x] test_converter.py complete (11 tests)
- [x] test_cli.py complete (10 tests)
- [x] test_integration.py complete (7 tests)
- [x] 80%+ code coverage achieved
- [x] All tests passing
- [x] Tests run in <30 seconds
- [x] Documentation updated (TESTING.md, README.md)
- [x] All changes committed with clear messages

## Commands Reference

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/md2pdf --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_converter.py

# Run specific test
uv run pytest tests/test_cli.py::TestCLI::test_single_file_conversion

# Run with verbose output
uv run pytest -v

# Install dependencies
uv sync --extra dev

# Check working directory
pwd

# View git log
git log --oneline

# Check git status
git status
```
