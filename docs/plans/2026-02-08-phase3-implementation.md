# Phase 3: Custom Styling Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add 5 built-in themes and custom CSS support to md2pdf with --theme and --css CLI flags.

**Architecture:** Separate page setup (@page CSS from .env config) from visual styling (themes/custom CSS). Pure CSS files for themes, Python generates @page section and concatenates with theme CSS.

**Tech Stack:** Python 3.11+, typer (CLI), WeasyPrint (PDF), pytest (testing)

---

## Task 1: Create Theme Infrastructure

**Files:**
- Create: `src/md2pdf/themes/__init__.py`
- Create: `tests/test_themes.py`

### Step 1: Write test for theme loading function

```python
# tests/test_themes.py
"""Tests for theme loading and management."""

import pytest
from pathlib import Path
from md2pdf.themes import get_theme_css, load_custom_css, AVAILABLE_THEMES


class TestThemeLoading:
    """Tests for get_theme_css function."""

    def test_get_theme_css_github(self, tmp_path):
        """Test loading github theme CSS."""
        # Will fail until we create github.css
        css = get_theme_css("github")

        assert isinstance(css, str)
        assert len(css) > 0
        # Should NOT contain @page rules
        assert "@page" not in css
        # Should contain body styling
        assert "body {" in css or "body{" in css

    def test_get_theme_css_invalid_theme(self):
        """Test loading non-existent theme raises ValueError."""
        with pytest.raises(ValueError, match="Unknown theme 'invalid'"):
            get_theme_css("invalid")

    def test_available_themes_list(self):
        """Test AVAILABLE_THEMES constant."""
        assert "github" in AVAILABLE_THEMES
        assert "minimal" in AVAILABLE_THEMES
        assert "academic" in AVAILABLE_THEMES
        assert "dark" in AVAILABLE_THEMES
        assert "modern" in AVAILABLE_THEMES
        assert len(AVAILABLE_THEMES) == 5


class TestCustomCSS:
    """Tests for load_custom_css function."""

    def test_load_custom_css_success(self, tmp_path):
        """Test loading custom CSS file."""
        css_file = tmp_path / "custom.css"
        css_content = "body { font-size: 12pt; }"
        css_file.write_text(css_content, encoding="utf-8")

        result = load_custom_css(css_file)

        assert result == css_content

    def test_load_custom_css_file_not_found(self, tmp_path):
        """Test loading non-existent CSS file raises FileNotFoundError."""
        css_file = tmp_path / "nonexistent.css"

        with pytest.raises(FileNotFoundError, match="CSS file not found"):
            load_custom_css(css_file)

    def test_load_custom_css_utf8_encoding(self, tmp_path):
        """Test CSS file is read with UTF-8 encoding."""
        css_file = tmp_path / "unicode.css"
        css_content = "/* Comment with unicode: © */ body { }"
        css_file.write_text(css_content, encoding="utf-8")

        result = load_custom_css(css_file)

        assert "©" in result
```

### Step 2: Run test to verify it fails

Run: `uv run pytest tests/test_themes.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'md2pdf.themes'"

### Step 3: Create themes directory and __init__.py

```bash
mkdir -p src/md2pdf/themes
touch src/md2pdf/themes/__init__.py
```

Run: `uv run pytest tests/test_themes.py::TestThemeLoading::test_available_themes_list -v`

Expected: FAIL with "ImportError: cannot import name 'AVAILABLE_THEMES'"

### Step 4: Implement theme loading functions

```python
# src/md2pdf/themes/__init__.py
"""Theme management for md2pdf."""

from pathlib import Path

AVAILABLE_THEMES = ["github", "minimal", "academic", "dark", "modern"]


def get_theme_css(theme_name: str) -> str:
    """Load CSS for built-in theme.

    Args:
        theme_name: Name of built-in theme.

    Returns:
        CSS string for the theme.

    Raises:
        ValueError: If theme doesn't exist.
    """
    if theme_name not in AVAILABLE_THEMES:
        raise ValueError(
            f"Unknown theme '{theme_name}'. "
            f"Available: {', '.join(AVAILABLE_THEMES)}"
        )

    theme_file = Path(__file__).parent / f"{theme_name}.css"

    if not theme_file.exists():
        raise FileNotFoundError(f"Theme file not found: {theme_file}")

    return theme_file.read_text(encoding="utf-8")


def load_custom_css(css_path: Path) -> str:
    """Load custom CSS file.

    Args:
        css_path: Path to custom CSS file.

    Returns:
        CSS string from file.

    Raises:
        FileNotFoundError: If CSS file doesn't exist.
    """
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {css_path}")

    return css_path.read_text(encoding="utf-8")
```

### Step 5: Run tests (will fail until github.css exists)

Run: `uv run pytest tests/test_themes.py::TestThemeLoading::test_available_themes_list -v`

Expected: PASS

Run: `uv run pytest tests/test_themes.py::TestCustomCSS -v`

Expected: PASS (custom CSS tests should work)

Run: `uv run pytest tests/test_themes.py::TestThemeLoading::test_get_theme_css_github -v`

Expected: FAIL with "FileNotFoundError: Theme file not found"

### Step 6: Commit

```bash
git add src/md2pdf/themes/__init__.py tests/test_themes.py
git commit -m "feat: add theme loading infrastructure

- Add themes module with get_theme_css() and load_custom_css()
- Define AVAILABLE_THEMES constant
- Add comprehensive tests for theme loading

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Migrate GitHub Theme and Refactor styles.py

**Files:**
- Create: `src/md2pdf/themes/github.css`
- Modify: `src/md2pdf/styles.py`
- Modify: `tests/test_styles.py`

### Step 1: Extract current CSS to github.css

Read `src/md2pdf/styles.py` and extract everything EXCEPT the `@page` section:

```css
/* src/md2pdf/themes/github.css */
/* GitHub-flavored markdown styling */

body {
    font-family: Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

/* Headers */
h1 {
    font-size: 2em;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
    font-weight: bold;
    border-bottom: 2px solid #eaecef;
    padding-bottom: 0.3em;
}

h2 {
    font-size: 1.5em;
    margin-top: 0.83em;
    margin-bottom: 0.83em;
    font-weight: bold;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 0.3em;
}

h3 {
    font-size: 1.17em;
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
}

h4 {
    font-size: 1em;
    margin-top: 1.33em;
    margin-bottom: 1.33em;
    font-weight: bold;
}

h5 {
    font-size: 0.83em;
    margin-top: 1.67em;
    margin-bottom: 1.67em;
    font-weight: bold;
}

h6 {
    font-size: 0.67em;
    margin-top: 2.33em;
    margin-bottom: 2.33em;
    font-weight: bold;
    color: #6a737d;
}

/* Paragraphs */
p {
    margin-top: 0;
    margin-bottom: 16px;
}

/* Code blocks */
pre {
    background-color: #f6f8fa;
    border-radius: 3px;
    padding: 16px;
    overflow-x: auto;
    font-family: Courier, monospace;
    font-size: 85%;
    line-height: 1.45;
    margin-bottom: 16px;
}

code {
    font-family: Courier, monospace;
    font-size: 85%;
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}

pre code {
    background-color: transparent;
    padding: 0;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

table th {
    font-weight: bold;
    background-color: #f6f8fa;
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
    text-align: left;
}

table td {
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
}

table tr:nth-child(2n) {
    background-color: #f6f8fa;
}

/* Lists */
ul, ol {
    margin-top: 0;
    margin-bottom: 16px;
    padding-left: 2em;
}

li {
    margin-bottom: 0.25em;
}

li > p {
    margin-bottom: 0;
}

/* Blockquotes */
blockquote {
    margin: 0 0 16px 0;
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
}

blockquote > :first-child {
    margin-top: 0;
}

blockquote > :last-child {
    margin-bottom: 0;
}

/* Horizontal rules */
hr {
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: #e1e4e8;
    border: 0;
}

/* Links */
a {
    color: #0366d6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Strong and emphasis */
strong {
    font-weight: bold;
}

em {
    font-style: italic;
}
```

### Step 2: Test github theme loads

Run: `uv run pytest tests/test_themes.py::TestThemeLoading::test_get_theme_css_github -v`

Expected: PASS

### Step 3: Write tests for new get_page_css function

```python
# tests/test_styles.py
"""Tests for PDF styling and CSS generation."""

import pytest

from md2pdf.styles import get_page_css, get_default_css


class TestPageCSS:
    """Tests for get_page_css function."""

    def test_get_page_css(self, mock_config):
        """Test @page CSS generation from config."""
        css = get_page_css(mock_config)

        # Verify it's a string
        assert isinstance(css, str)
        assert len(css) > 0

        # Must contain @page rule
        assert "@page" in css

        # Must contain page size
        assert mock_config.page_size in css

        # Must contain margins
        assert mock_config.margin_top in css
        assert mock_config.margin_bottom in css
        assert mock_config.margin_left in css
        assert mock_config.margin_right in css

    def test_get_page_css_custom_values(self, mock_config):
        """Test @page CSS with custom config values."""
        mock_config.page_size = "Letter"
        mock_config.margin_top = "3cm"
        mock_config.margin_bottom = "3cm"
        mock_config.margin_left = "2.5cm"
        mock_config.margin_right = "2.5cm"

        css = get_page_css(mock_config)

        assert "Letter" in css
        assert "3cm" in css
        assert "2.5cm" in css

    def test_get_page_css_no_body_styles(self, mock_config):
        """Test @page CSS doesn't include body or other element styling."""
        css = get_page_css(mock_config)

        # Should ONLY have @page, not body/h1/code/table
        assert "@page" in css
        assert "body {" not in css and "body{" not in css
        assert "h1 {" not in css and "h1{" not in css
        assert "code {" not in css and "code{" not in css


class TestLegacyCSS:
    """Tests for backwards compatibility with get_default_css."""

    def test_get_default_css_still_exists(self, mock_config):
        """Test get_default_css still works for backwards compatibility."""
        # This function should still exist but might be deprecated
        css = get_default_css(mock_config)

        assert isinstance(css, str)
        assert len(css) > 0
```

### Step 4: Run tests to verify they fail

Run: `uv run pytest tests/test_styles.py::TestPageCSS -v`

Expected: FAIL with "ImportError: cannot import name 'get_page_css'"

### Step 5: Refactor styles.py

```python
# src/md2pdf/styles.py
"""PDF styling and CSS generation."""

from md2pdf.config import Config


def get_page_css(config: Config) -> str:
    """Generate @page CSS from config.

    Returns only page setup, not visual styling.

    Args:
        config: Configuration with page setup values.

    Returns:
        CSS string for @page rules.
    """
    return f"""
@page {{
    size: {config.page_size};
    margin-top: {config.margin_top};
    margin-bottom: {config.margin_bottom};
    margin-left: {config.margin_left};
    margin-right: {config.margin_right};
}}
"""


def get_default_css(config: Config) -> str:
    """Generate default CSS for PDF styling.

    DEPRECATED: Use get_page_css() + theme CSS instead.
    Kept for backwards compatibility.

    Args:
        config: Configuration settings for styling.

    Returns:
        CSS string with complete styling rules.
    """
    # Keep old implementation for backwards compatibility
    # This will be removed in a future version
    return f"""
@page {{
    size: {config.page_size};
    margin-top: {config.margin_top};
    margin-bottom: {config.margin_bottom};
    margin-left: {config.margin_left};
    margin-right: {config.margin_right};
}}

body {{
    font-family: {config.font_family};
    font-size: {config.font_size};
    line-height: 1.6;
    color: #333;
}}

/* Headers */
h1 {{
    font-size: 2em;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
    font-weight: bold;
    border-bottom: 2px solid #eaecef;
    padding-bottom: 0.3em;
}}

h2 {{
    font-size: 1.5em;
    margin-top: 0.83em;
    margin-bottom: 0.83em;
    font-weight: bold;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 0.3em;
}}

h3 {{
    font-size: 1.17em;
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
}}

h4 {{
    font-size: 1em;
    margin-top: 1.33em;
    margin-bottom: 1.33em;
    font-weight: bold;
}}

h5 {{
    font-size: 0.83em;
    margin-top: 1.67em;
    margin-bottom: 1.67em;
    font-weight: bold;
}}

h6 {{
    font-size: 0.67em;
    margin-top: 2.33em;
    margin-bottom: 2.33em;
    font-weight: bold;
    color: #6a737d;
}}

/* Paragraphs */
p {{
    margin-top: 0;
    margin-bottom: 16px;
}}

/* Code blocks */
pre {{
    background-color: #f6f8fa;
    border-radius: 3px;
    padding: 16px;
    overflow-x: auto;
    font-family: {config.code_font};
    font-size: 85%;
    line-height: 1.45;
    margin-bottom: 16px;
}}

code {{
    font-family: {config.code_font};
    font-size: 85%;
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}}

pre code {{
    background-color: transparent;
    padding: 0;
}}

/* Tables */
table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}}

table th {{
    font-weight: bold;
    background-color: #f6f8fa;
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
    text-align: left;
}}

table td {{
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
}}

table tr:nth-child(2n) {{
    background-color: #f6f8fa;
}}

/* Lists */
ul, ol {{
    margin-top: 0;
    margin-bottom: 16px;
    padding-left: 2em;
}}

li {{
    margin-bottom: 0.25em;
}}

li > p {{
    margin-bottom: 0;
}}

/* Blockquotes */
blockquote {{
    margin: 0 0 16px 0;
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
}}

blockquote > :first-child {{
    margin-top: 0;
}}

blockquote > :last-child {{
    margin-bottom: 0;
}}

/* Horizontal rules */
hr {{
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: #e1e4e8;
    border: 0;
}}

/* Links */
a {{
    color: #0366d6;
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

/* Strong and emphasis */
strong {{
    font-weight: bold;
}}

em {{
    font-style: italic;
}}
"""
```

### Step 6: Run tests

Run: `uv run pytest tests/test_styles.py -v`

Expected: ALL PASS

### Step 7: Commit

```bash
git add src/md2pdf/themes/github.css src/md2pdf/styles.py tests/test_styles.py
git commit -m "refactor: extract github theme and add get_page_css

- Extract visual styles to github.css theme file
- Add get_page_css() for @page-only CSS generation
- Keep get_default_css() for backwards compatibility
- Add comprehensive tests for get_page_css()

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Add CLI Flags for Theme and CSS

**Files:**
- Modify: `src/md2pdf/cli.py`
- Create: `tests/test_cli_themes.py`

### Step 1: Write tests for CLI theme functionality

```python
# tests/test_cli_themes.py
"""Tests for CLI theme and CSS functionality."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from md2pdf.cli import main
import typer

runner = CliRunner()


class TestCLIThemeFlag:
    """Tests for --theme CLI flag."""

    def test_theme_flag_github(self, tmp_path):
        """Test --theme github flag."""
        # Create test markdown file
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        # This will fail until we implement CLI integration
        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file), "--theme", "github"]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_theme_flag_invalid(self, tmp_path):
        """Test --theme with invalid theme name."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--theme", "invalid"]
        )

        assert result.exit_code == 1
        assert "Unknown theme 'invalid'" in result.stdout

    def test_default_uses_github_theme(self, tmp_path):
        """Test that no theme flag defaults to github theme."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()


class TestCLICSSFlag:
    """Tests for --css CLI flag."""

    def test_css_flag_custom_file(self, tmp_path):
        """Test --css with custom CSS file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        css_file = tmp_path / "custom.css"
        css_file.write_text("body { font-size: 14pt; }")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--output", str(output_file), "--css", str(css_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_css_flag_file_not_found(self, tmp_path):
        """Test --css with non-existent file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--css", str(tmp_path / "nonexistent.css")]
        )

        assert result.exit_code == 1
        assert "CSS file not found" in result.stdout


class TestCLIThemeAndCSS:
    """Tests for --theme and --css mutual exclusivity."""

    def test_both_flags_error(self, tmp_path):
        """Test using both --theme and --css produces error."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        css_file = tmp_path / "custom.css"
        css_file.write_text("body { }")

        result = runner.invoke(
            typer.main.get_command(main),
            [str(md_file), "--theme", "github", "--css", str(css_file)]
        )

        assert result.exit_code == 1
        assert "Cannot use --theme and --css together" in result.stdout
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_cli_themes.py -v`

Expected: FAIL (CLI doesn't have --theme or --css flags yet)

### Step 3: Add CLI flags to cli.py

Modify `src/md2pdf/cli.py` main function signature (after line 18):

```python
# Add these imports at top
from md2pdf.themes import get_theme_css, load_custom_css
from md2pdf.styles import get_page_css

# Modify main() function signature to add new parameters after line 47:
def main(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        help="Markdown file or directory to convert",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output PDF file (single file mode only)",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-d",
        help="Output directory for PDFs (directory mode)",
    ),
    preserve_structure: bool = typer.Option(
        True,
        "--preserve-structure/--no-preserve-structure",
        help="Preserve directory structure in batch mode",
    ),
    create_output_dir: Optional[str] = typer.Option(
        None,
        "--create-output-dir",
        "-c",
        help="Create a subdirectory for output files (use 'auto' for timestamp or provide a name)",
    ),
    theme: Optional[str] = typer.Option(
        None,
        "--theme",
        help="Built-in theme (github, minimal, academic, dark, modern)",
    ),
    css: Optional[Path] = typer.Option(
        None,
        "--css",
        help="Path to custom CSS file",
    ),
):
```

### Step 4: Add validation and CSS generation logic

After config loading (around line 83), add:

```python
    # Validate theme and css flags (mutually exclusive)
    if theme and css:
        console.print(
            "[red]Error:[/red] Cannot use --theme and --css together.\n"
            "Choose one:\n"
            "  • --theme for built-in themes\n"
            "  • --css for custom CSS files"
        )
        raise typer.Exit(1)

    # Determine style source and generate CSS
    try:
        if css:
            style_css = load_custom_css(css)
        elif theme:
            style_css = get_theme_css(theme)
        else:
            style_css = get_theme_css("github")  # default
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Generate complete CSS (page + styling)
    page_css = get_page_css(config)
    final_css = page_css + style_css

    # Create converter with complete CSS
    converter = MarkdownConverter(config, css=final_css)
```

Note: This requires modifying MarkdownConverter constructor in next task.

### Step 5: Run tests (will fail until converter updated)

Run: `uv run pytest tests/test_cli_themes.py::TestCLIThemeAndCSS::test_both_flags_error -v`

Expected: PASS (error validation works)

Run: `uv run pytest tests/test_cli_themes.py::TestCLIThemeFlag::test_theme_flag_invalid -v`

Expected: PASS (invalid theme error works)

### Step 6: Commit

```bash
git add src/md2pdf/cli.py tests/test_cli_themes.py
git commit -m "feat: add --theme and --css CLI flags

- Add --theme flag for built-in themes
- Add --css flag for custom CSS files
- Implement mutual exclusivity validation
- Generate complete CSS from page + styling
- Add comprehensive CLI tests

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Update Converter to Accept CSS String

**Files:**
- Modify: `src/md2pdf/converter.py`
- Modify: `tests/test_converter.py`

### Step 1: Write tests for converter with CSS parameter

Add to `tests/test_converter.py`:

```python
class TestConverterWithCSS:
    """Tests for MarkdownConverter with custom CSS."""

    def test_converter_with_css_string(self, mock_config, tmp_path):
        """Test converter accepts CSS string parameter."""
        custom_css = "body { font-size: 14pt; }"
        converter = MarkdownConverter(mock_config, css=custom_css)

        # Create test file
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        output_file = tmp_path / "output.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()

    def test_converter_with_none_css(self, mock_config, tmp_path):
        """Test converter with css=None uses default."""
        converter = MarkdownConverter(mock_config, css=None)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        output_file = tmp_path / "output.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()

    def test_converter_backwards_compatible(self, mock_config, tmp_path):
        """Test converter still works without css parameter."""
        # Old usage: MarkdownConverter(config)
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        output_file = tmp_path / "output.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_converter.py::TestConverterWithCSS -v`

Expected: FAIL (TypeError: __init__() got an unexpected keyword argument 'css')

### Step 3: Update MarkdownConverter constructor

Modify `src/md2pdf/converter.py` line 35:

```python
class MarkdownConverter:
    """Convert markdown files to PDF format."""

    def __init__(self, config: Config, css: Optional[str] = None):
        """Initialize the converter.

        Args:
            config: Configuration settings for PDF generation.
            css: Optional complete CSS string (page + styling). If None, uses default.
        """
        self.config = config
        # Store base extensions; create Markdown instance per file
        self.base_extensions = [
            "fenced_code",
            "tables",
            "codehilite",
            "nl2br",
        ]

        # Use provided CSS or generate default
        if css is not None:
            self.css = css
        else:
            # Backwards compatibility: generate default CSS
            from md2pdf.styles import get_default_css
            self.css = get_default_css(config)
```

### Step 4: Run all converter tests

Run: `uv run pytest tests/test_converter.py -v`

Expected: ALL PASS

### Step 5: Run all tests to check for regressions

Run: `uv run pytest tests/ -v`

Expected: Most tests pass (CLI tests might still fail until all pieces connected)

### Step 6: Commit

```bash
git add src/md2pdf/converter.py tests/test_converter.py
git commit -m "refactor: update converter to accept CSS string

- Add optional css parameter to MarkdownConverter
- Maintain backwards compatibility with default CSS generation
- Add tests for CSS parameter handling

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Create Minimal Theme

**Files:**
- Create: `src/md2pdf/themes/minimal.css`

### Step 1: Design and create minimal.css

```css
/* src/md2pdf/themes/minimal.css */
/* Minimal theme - Clean, spacious, simple typography */

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #2c3e50;
    max-width: 800px;
}

/* Headers - Simple, no borders */
h1 {
    font-size: 2.5em;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 300;
    letter-spacing: -0.02em;
}

h2 {
    font-size: 2em;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 300;
}

h3 {
    font-size: 1.5em;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 400;
}

h4, h5, h6 {
    font-size: 1.2em;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 400;
}

/* Paragraphs - More spacing */
p {
    margin-top: 0;
    margin-bottom: 1.5em;
}

/* Code blocks - Subtle background */
pre {
    background-color: #f8f9fa;
    border-left: 3px solid #e9ecef;
    padding: 1.5em;
    overflow-x: auto;
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
    font-size: 90%;
    line-height: 1.6;
    margin-bottom: 1.5em;
}

code {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
    font-size: 90%;
    background-color: #f8f9fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}

pre code {
    background-color: transparent;
    padding: 0;
}

/* Tables - Minimal borders */
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 2em;
}

table th {
    font-weight: 600;
    border-bottom: 2px solid #dee2e6;
    padding: 0.75em;
    text-align: left;
}

table td {
    border-bottom: 1px solid #e9ecef;
    padding: 0.75em;
}

table tr:last-child td {
    border-bottom: none;
}

/* Lists - More spacing */
ul, ol {
    margin-top: 0;
    margin-bottom: 1.5em;
    padding-left: 2em;
}

li {
    margin-bottom: 0.5em;
}

li > p {
    margin-bottom: 0.5em;
}

/* Blockquotes - Simple left border */
blockquote {
    margin: 0 0 1.5em 0;
    padding: 0 1.5em;
    color: #6c757d;
    border-left: 4px solid #dee2e6;
}

blockquote > :first-child {
    margin-top: 0;
}

blockquote > :last-child {
    margin-bottom: 0;
}

/* Horizontal rules - Minimal */
hr {
    height: 1px;
    padding: 0;
    margin: 3em 0;
    background-color: #dee2e6;
    border: 0;
}

/* Links - Subtle */
a {
    color: #495057;
    text-decoration: underline;
}

a:hover {
    color: #212529;
}

/* Strong and emphasis */
strong {
    font-weight: 600;
}

em {
    font-style: italic;
}
```

### Step 2: Test minimal theme loads

Run: `uv run pytest tests/test_themes.py::TestThemeLoading::test_get_theme_css_github -v`

Expected: PASS

### Step 3: Manual test minimal theme

Run: `uv run md2pdf examples/markdown/test_basic.md --theme minimal --create-output-dir test_themes`

Expected: PDF created with minimal styling

### Step 4: Commit

```bash
git add src/md2pdf/themes/minimal.css
git commit -m "feat: add minimal theme

- Clean, spacious design with simple typography
- Light gray backgrounds, minimal borders
- Increased line spacing and margins
- Modern font stack

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Create Academic Theme

**Files:**
- Create: `src/md2pdf/themes/academic.css`

### Step 1: Create academic.css

```css
/* src/md2pdf/themes/academic.css */
/* Academic theme - Formal, serif fonts, traditional papers */

body {
    font-family: "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #000000;
}

/* Headers - Traditional sizing */
h1 {
    font-size: 18pt;
    margin-top: 12pt;
    margin-bottom: 6pt;
    font-weight: bold;
    text-align: center;
}

h2 {
    font-size: 14pt;
    margin-top: 12pt;
    margin-bottom: 6pt;
    font-weight: bold;
}

h3 {
    font-size: 12pt;
    margin-top: 12pt;
    margin-bottom: 6pt;
    font-weight: bold;
    font-style: italic;
}

h4, h5, h6 {
    font-size: 12pt;
    margin-top: 12pt;
    margin-bottom: 6pt;
    font-weight: bold;
}

/* Paragraphs - Traditional academic spacing */
p {
    margin-top: 0;
    margin-bottom: 12pt;
    text-align: justify;
    text-indent: 0;
}

/* Code blocks - Monospace on white */
pre {
    background-color: #ffffff;
    border: 1px solid #000000;
    padding: 12pt;
    overflow-x: auto;
    font-family: "Courier New", Courier, monospace;
    font-size: 10pt;
    line-height: 1.4;
    margin-bottom: 12pt;
}

code {
    font-family: "Courier New", Courier, monospace;
    font-size: 10pt;
    background-color: #f5f5f5;
    padding: 0.1em 0.3em;
}

pre code {
    background-color: transparent;
    padding: 0;
}

/* Tables - Formal style */
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 12pt;
    font-size: 11pt;
}

table th {
    font-weight: bold;
    border-top: 2px solid #000000;
    border-bottom: 1px solid #000000;
    padding: 6pt;
    text-align: left;
}

table td {
    border-bottom: 1px solid #cccccc;
    padding: 6pt;
}

table tr:last-child td {
    border-bottom: 2px solid #000000;
}

/* Lists - Traditional spacing */
ul, ol {
    margin-top: 0;
    margin-bottom: 12pt;
    padding-left: 2.5em;
}

li {
    margin-bottom: 6pt;
}

li > p {
    margin-bottom: 0;
}

/* Blockquotes - Traditional indented style */
blockquote {
    margin: 12pt 2em;
    padding: 0;
    font-style: italic;
}

blockquote > :first-child {
    margin-top: 0;
}

blockquote > :last-child {
    margin-bottom: 0;
}

/* Horizontal rules - Formal */
hr {
    height: 1px;
    padding: 0;
    margin: 24pt 0;
    background-color: #000000;
    border: 0;
}

/* Links - Traditional underline */
a {
    color: #000000;
    text-decoration: underline;
}

/* Strong and emphasis */
strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

/* Footnote styling */
sup {
    font-size: 75%;
    vertical-align: super;
    line-height: 0;
}
```

### Step 2: Manual test academic theme

Run: `uv run md2pdf examples/markdown/test_basic.md --theme academic --create-output-dir test_themes`

Expected: PDF with serif fonts and formal styling

### Step 3: Commit

```bash
git add src/md2pdf/themes/academic.css
git commit -m "feat: add academic theme

- Serif fonts for formal appearance
- Traditional academic paper styling
- Justified text alignment
- Formal table and blockquote styling

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Create Dark Theme

**Files:**
- Create: `src/md2pdf/themes/dark.css`

### Step 1: Create dark.css

```css
/* src/md2pdf/themes/dark.css */
/* Dark theme - Dark background with light text */

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #e6edf3;
    background-color: #0d1117;
}

/* Headers - Light text on dark */
h1 {
    font-size: 2em;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
    font-weight: bold;
    border-bottom: 2px solid #30363d;
    padding-bottom: 0.3em;
    color: #ffffff;
}

h2 {
    font-size: 1.5em;
    margin-top: 0.83em;
    margin-bottom: 0.83em;
    font-weight: bold;
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.3em;
    color: #f0f6fc;
}

h3 {
    font-size: 1.17em;
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
    color: #f0f6fc;
}

h4, h5 {
    font-size: 1em;
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
    color: #e6edf3;
}

h6 {
    font-size: 0.85em;
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
    color: #8b949e;
}

/* Paragraphs */
p {
    margin-top: 0;
    margin-bottom: 16px;
}

/* Code blocks - Dark theme */
pre {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    font-family: "SF Mono", Monaco, "Cascadia Code", Consolas, monospace;
    font-size: 85%;
    line-height: 1.45;
    margin-bottom: 16px;
    color: #e6edf3;
}

code {
    font-family: "SF Mono", Monaco, "Cascadia Code", Consolas, monospace;
    font-size: 85%;
    background-color: #6e768166;
    padding: 0.2em 0.4em;
    border-radius: 6px;
    color: #e6edf3;
}

pre code {
    background-color: transparent;
    padding: 0;
}

/* Tables - Dark theme */
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

table th {
    font-weight: bold;
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 6px 13px;
    text-align: left;
    color: #f0f6fc;
}

table td {
    border: 1px solid #30363d;
    padding: 6px 13px;
}

table tr:nth-child(2n) {
    background-color: #161b22;
}

/* Lists */
ul, ol {
    margin-top: 0;
    margin-bottom: 16px;
    padding-left: 2em;
}

li {
    margin-bottom: 0.25em;
}

li > p {
    margin-bottom: 0;
}

/* Blockquotes - Dark theme */
blockquote {
    margin: 0 0 16px 0;
    padding: 0 1em;
    color: #8b949e;
    border-left: 0.25em solid #30363d;
}

blockquote > :first-child {
    margin-top: 0;
}

blockquote > :last-child {
    margin-bottom: 0;
}

/* Horizontal rules */
hr {
    height: 2px;
    padding: 0;
    margin: 24px 0;
    background-color: #30363d;
    border: 0;
}

/* Links - Accent color */
a {
    color: #58a6ff;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Strong and emphasis */
strong {
    font-weight: bold;
    color: #ffffff;
}

em {
    font-style: italic;
}
```

### Step 2: Manual test dark theme

Run: `uv run md2pdf examples/markdown/test_basic.md --theme dark --create-output-dir test_themes`

Expected: PDF with dark background and light text

### Step 3: Commit

```bash
git add src/md2pdf/themes/dark.css
git commit -m "feat: add dark theme

- Dark background (#0d1117) with light text
- GitHub dark color palette
- High contrast for readability
- Modern aesthetic

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Create Modern Theme

**Files:**
- Create: `src/md2pdf/themes/modern.css`

### Step 1: Create modern.css

```css
/* src/md2pdf/themes/modern.css */
/* Modern theme - Bold headers, contemporary design, colorful accents */

body {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a202c;
}

/* Headers - Bold and colorful */
h1 {
    font-size: 2.5em;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    font-weight: 800;
    color: #2d3748;
    border-bottom: 4px solid #4299e1;
    padding-bottom: 0.3em;
    letter-spacing: -0.02em;
}

h2 {
    font-size: 2em;
    margin-top: 0.75em;
    margin-bottom: 0.5em;
    font-weight: 700;
    color: #2d3748;
    border-left: 4px solid #48bb78;
    padding-left: 0.5em;
}

h3 {
    font-size: 1.5em;
    margin-top: 0.75em;
    margin-bottom: 0.5em;
    font-weight: 600;
    color: #2d3748;
}

h4 {
    font-size: 1.25em;
    margin-top: 0.75em;
    margin-bottom: 0.5em;
    font-weight: 600;
    color: #4a5568;
}

h5, h6 {
    font-size: 1.1em;
    margin-top: 0.75em;
    margin-bottom: 0.5em;
    font-weight: 600;
    color: #718096;
}

/* Paragraphs */
p {
    margin-top: 0;
    margin-bottom: 1.2em;
}

/* Code blocks - Modern style with accent */
pre {
    background: linear-gradient(to right, #f7fafc 0%, #edf2f7 100%);
    border-left: 4px solid #ed8936;
    border-radius: 8px;
    padding: 20px;
    overflow-x: auto;
    font-family: "Fira Code", "SF Mono", Monaco, Consolas, monospace;
    font-size: 90%;
    line-height: 1.5;
    margin-bottom: 1.5em;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

code {
    font-family: "Fira Code", "SF Mono", Monaco, Consolas, monospace;
    font-size: 90%;
    background-color: #edf2f7;
    padding: 0.2em 0.5em;
    border-radius: 4px;
    color: #d53f8c;
}

pre code {
    background-color: transparent;
    padding: 0;
    color: #1a202c;
}

/* Tables - Modern grid style */
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1.5em;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

table th {
    font-weight: 600;
    background: linear-gradient(to bottom, #4299e1, #3182ce);
    color: #ffffff;
    border: none;
    padding: 12px 16px;
    text-align: left;
}

table td {
    border: 1px solid #e2e8f0;
    padding: 12px 16px;
    background-color: #ffffff;
}

table tr:nth-child(2n) td {
    background-color: #f7fafc;
}

table tr:hover td {
    background-color: #edf2f7;
}

/* Lists - Modern spacing */
ul, ol {
    margin-top: 0;
    margin-bottom: 1.2em;
    padding-left: 2em;
}

li {
    margin-bottom: 0.5em;
}

li > p {
    margin-bottom: 0.5em;
}

/* Blockquotes - Colorful accent */
blockquote {
    margin: 1.5em 0;
    padding: 1em 1.5em;
    background-color: #faf5ff;
    border-left: 4px solid #9f7aea;
    border-radius: 0 4px 4px 0;
}

blockquote > :first-child {
    margin-top: 0;
}

blockquote > :last-child {
    margin-bottom: 0;
}

/* Horizontal rules - Gradient */
hr {
    height: 2px;
    padding: 0;
    margin: 2em 0;
    background: linear-gradient(to right, #4299e1, #48bb78, #ed8936);
    border: 0;
}

/* Links - Accent color */
a {
    color: #3182ce;
    text-decoration: none;
    font-weight: 500;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s;
}

a:hover {
    border-bottom-color: #3182ce;
}

/* Strong and emphasis */
strong {
    font-weight: 700;
    color: #2d3748;
}

em {
    font-style: italic;
    color: #4a5568;
}
```

### Step 2: Manual test modern theme

Run: `uv run md2pdf examples/markdown/test_basic.md --theme modern --create-output-dir test_themes`

Expected: PDF with colorful accents and bold headers

### Step 3: Commit

```bash
git add src/md2pdf/themes/modern.css
git commit -m "feat: add modern theme

- Bold, contemporary design
- Colorful accents (blue, green, orange, purple)
- Gradient backgrounds and modern shadows
- High visual impact

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Add Deprecation Warnings for Font Settings

**Files:**
- Modify: `src/md2pdf/config.py`
- Modify: `.env.example`
- Modify: `tests/test_config.py`

### Step 1: Write tests for deprecation warnings

Add to `tests/test_config.py`:

```python
import os
from unittest.mock import patch
from io import StringIO


class TestDeprecationWarnings:
    """Tests for deprecated .env settings."""

    @patch.dict(os.environ, {"PDF_FONT_FAMILY": "Georgia, serif"}, clear=True)
    def test_font_family_deprecation_warning(self, capsys):
        """Test warning shown for PDF_FONT_FAMILY."""
        Config.load()

        captured = capsys.readouterr()
        assert "Deprecated" in captured.out or "deprecated" in captured.out.lower()
        assert "PDF_FONT_FAMILY" in captured.out

    @patch.dict(os.environ, {"PDF_CODE_FONT": "Monaco, monospace"}, clear=True)
    def test_code_font_deprecation_warning(self, capsys):
        """Test warning shown for PDF_CODE_FONT."""
        Config.load()

        captured = capsys.readouterr()
        assert "PDF_CODE_FONT" in captured.out

    @patch.dict(os.environ, {"PDF_FONT_SIZE": "14pt"}, clear=True)
    def test_font_size_deprecation_warning(self, capsys):
        """Test warning shown for PDF_FONT_SIZE."""
        Config.load()

        captured = capsys.readouterr()
        assert "PDF_FONT_SIZE" in captured.out

    @patch.dict(
        os.environ,
        {
            "PDF_FONT_FAMILY": "Georgia",
            "PDF_CODE_FONT": "Monaco",
            "PDF_FONT_SIZE": "14pt",
        },
        clear=True,
    )
    def test_multiple_deprecation_warnings(self, capsys):
        """Test warning shows all deprecated settings."""
        Config.load()

        captured = capsys.readouterr()
        assert "PDF_FONT_FAMILY" in captured.out
        assert "PDF_CODE_FONT" in captured.out
        assert "PDF_FONT_SIZE" in captured.out

    @patch.dict(os.environ, {"PDF_PAGE_SIZE": "A4"}, clear=True)
    def test_no_warning_for_valid_settings(self, capsys):
        """Test no warning for non-deprecated settings."""
        Config.load()

        captured = capsys.readouterr()
        # Should not contain deprecation warning
        assert "Deprecated" not in captured.out or captured.out == ""
```

### Step 2: Run tests to verify they fail

Run: `uv run pytest tests/test_config.py::TestDeprecationWarnings -v`

Expected: FAIL (no warnings implemented yet)

### Step 3: Add deprecation warning logic to config.py

Modify `src/md2pdf/config.py` in the `load()` classmethod (after line 54):

```python
@classmethod
def load(cls, env_file: Optional[Path] = None) -> "Config":
    """Load configuration from environment variables.

    Args:
        env_file: Optional path to .env file. If None, looks for .env in current directory.

    Returns:
        Config instance with loaded settings.
    """
    # Load .env file if it exists
    if env_file:
        load_dotenv(env_file, override=True)
    else:
        load_dotenv()

    # Check for deprecated settings
    deprecated_settings = []
    if os.getenv("PDF_FONT_FAMILY"):
        deprecated_settings.append("PDF_FONT_FAMILY")
    if os.getenv("PDF_CODE_FONT"):
        deprecated_settings.append("PDF_CODE_FONT")
    if os.getenv("PDF_FONT_SIZE"):
        deprecated_settings.append("PDF_FONT_SIZE")

    if deprecated_settings:
        # Import here to avoid circular dependency
        from rich.console import Console
        console = Console()
        console.print(
            f"[yellow]⚠️  Deprecated:[/yellow] {', '.join(deprecated_settings)} "
            f"in .env will be ignored. Use --theme or --css instead."
        )

    # Load with defaults (still include deprecated settings in dataclass for backwards compat)
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
    )
```

### Step 4: Run tests

Run: `uv run pytest tests/test_config.py::TestDeprecationWarnings -v`

Expected: ALL PASS

### Step 5: Update .env.example with comments

Add to `.env.example`:

```bash
# DEPRECATED: Font settings are now controlled by themes
# Use --theme flag or --css for custom styling
# PDF_FONT_FAMILY=Arial, sans-serif
# PDF_FONT_SIZE=11pt
# PDF_CODE_FONT=Courier, monospace
```

### Step 6: Commit

```bash
git add src/md2pdf/config.py tests/test_config.py .env.example
git commit -m "feat: add deprecation warnings for font settings

- Warn when PDF_FONT_FAMILY, PDF_CODE_FONT, PDF_FONT_SIZE in .env
- Update .env.example to show deprecated settings
- Add comprehensive tests for warnings

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Run Full Test Suite and Verify Coverage

**Files:**
- None (testing only)

### Step 1: Run all tests

Run: `uv run pytest -v`

Expected: 78+ tests passing (70 from before + 8 new theme tests)

### Step 2: Check coverage

Run: `uv run pytest --cov=src/md2pdf --cov-report=term-missing`

Expected: 86%+ coverage maintained

### Step 3: Fix any failing tests

If any tests fail, fix them before proceeding.

### Step 4: Manual testing checklist

```bash
# Test each theme
uv run md2pdf examples/markdown/test_basic.md --theme github --create-output-dir themes_test
uv run md2pdf examples/markdown/test_basic.md --theme minimal --create-output-dir themes_test
uv run md2pdf examples/markdown/test_basic.md --theme academic --create-output-dir themes_test
uv run md2pdf examples/markdown/test_basic.md --theme dark --create-output-dir themes_test
uv run md2pdf examples/markdown/test_basic.md --theme modern --create-output-dir themes_test

# Test default (no flags)
uv run md2pdf examples/markdown/test_basic.md --create-output-dir themes_test

# Test error cases
uv run md2pdf examples/markdown/test_basic.md --theme invalid
uv run md2pdf examples/markdown/test_basic.md --css nonexistent.css
uv run md2pdf examples/markdown/test_basic.md --theme github --css custom.css

# Test custom CSS
echo "body { font-size: 14pt; }" > /tmp/custom.css
uv run md2pdf examples/markdown/test_basic.md --css /tmp/custom.css --create-output-dir themes_test
```

Expected: All commands work as expected, errors show helpful messages

### Step 5: Verify no regressions

Run: `uv run md2pdf examples/markdown/ --create-output-dir regression_test`

Expected: All example files convert successfully

---

## Task 11: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/USAGE_GUIDE.md`
- Create: `docs/THEMES.md`

### Step 1: Update README.md with theme examples

Add to README.md after the basic usage section:

```markdown
### Using Themes

Choose from 5 built-in themes:

```bash
# GitHub-flavored (default)
md2pdf document.md --theme github

# Clean and minimal
md2pdf document.md --theme minimal

# Academic paper style
md2pdf document.md --theme academic

# Dark mode
md2pdf document.md --theme dark

# Modern with colorful accents
md2pdf document.md --theme modern
```

### Custom CSS

Use your own stylesheet:

```bash
md2pdf document.md --css mystyle.css
```

**Note:** You cannot use `--theme` and `--css` together. Choose one or the other.
```

### Step 2: Create comprehensive theme documentation

Create `docs/THEMES.md`:

```markdown
# md2pdf Themes Guide

## Overview

md2pdf includes 5 built-in themes for different use cases, plus support for custom CSS.

## Built-in Themes

### GitHub (Default)

**Use for:** Technical documentation, READMEs, general purpose

**Style:** Clean, professional, familiar GitHub markdown aesthetic

**Features:**
- Sans-serif fonts (Arial)
- Light gray code blocks
- Subtle borders on headers
- Table striping

```bash
md2pdf document.md --theme github
# or just
md2pdf document.md
```

### Minimal

**Use for:** Clean documents, presentations, modern reports

**Style:** Spacious, simple, maximum whitespace

**Features:**
- Modern font stack
- Light typography (font-weight 300-400)
- Minimal borders
- Increased line spacing
- Subtle backgrounds

```bash
md2pdf document.md --theme minimal
```

### Academic

**Use for:** Research papers, formal documents, academic writing

**Style:** Traditional, serif fonts, formal

**Features:**
- Serif fonts (Palatino, Georgia)
- Justified text
- Traditional sizing (12pt body)
- Formal table borders
- Centered h1 headers

```bash
md2pdf document.md --theme academic
```

### Dark

**Use for:** Dark mode preference, presentations, modern aesthetic

**Style:** Dark background with light text

**Features:**
- Dark gray background (#0d1117)
- Light text (#e6edf3)
- GitHub dark color palette
- High contrast for readability

```bash
md2pdf document.md --theme dark
```

### Modern

**Use for:** Marketing materials, creative docs, contemporary design

**Style:** Bold, colorful, high visual impact

**Features:**
- Bold headers (font-weight 600-800)
- Colorful accents (blue, green, orange, purple)
- Gradient backgrounds
- Modern shadows
- Accent borders

```bash
md2pdf document.md --theme modern
```

## Custom CSS

### Using Custom CSS

Provide your own CSS file for complete control:

```bash
md2pdf document.md --css mystyle.css
```

### CSS Structure

Your CSS file should NOT include `@page` rules (page size, margins). Those are configured via `.env`:

```css
/* ✅ GOOD - Visual styling only */
body {
    font-family: Georgia, serif;
    font-size: 12pt;
    color: #333;
}

h1 {
    color: #0066cc;
    font-weight: bold;
}

/* ❌ AVOID - Page setup is in .env */
@page {
    size: A4;  /* Configure via .env instead */
}
```

### Starting from a Theme

You can copy a built-in theme as a starting point:

```bash
# Themes are in src/md2pdf/themes/
cp src/md2pdf/themes/github.css my-custom-theme.css
# Edit my-custom-theme.css
md2pdf document.md --css my-custom-theme.css
```

## Theme vs CSS

**You cannot use both `--theme` and `--css` together.** Choose one:

```bash
# ✅ Pick a theme
md2pdf doc.md --theme academic

# ✅ Use custom CSS
md2pdf doc.md --css mycss.css

# ❌ ERROR - Cannot use both
md2pdf doc.md --theme academic --css mycss.css
```

**Why?** This keeps the mental model simple. You either:
1. Use a pre-made theme, OR
2. Bring your own complete stylesheet

## Page Setup vs Styling

**Page setup** (size, margins) is configured via `.env` and applies to ALL themes:

```bash
# .env
PDF_PAGE_SIZE=Letter
PDF_MARGIN_TOP=3cm
PDF_MARGIN_BOTTOM=3cm
```

**Visual styling** (fonts, colors, spacing) comes from themes or custom CSS.

This separation means:
- Change page size without changing visual style
- Switch themes without reconfiguring page setup
- Clean, predictable behavior

## Examples

### Technical Documentation

```bash
md2pdf API_DOCS.md --theme github --create-output-dir docs
```

### Research Paper

```bash
# Configure for academic style first
echo "PDF_PAGE_SIZE=Letter" > .env
echo "PDF_MARGIN_TOP=2.54cm" >> .env

md2pdf paper.md --theme academic --output paper.pdf
```

### Presentation Deck

```bash
md2pdf slides.md --theme modern --create-output-dir presentation
```

### Personal Notes (Dark Mode)

```bash
md2pdf notes.md --theme dark --create-output-dir notes
```

### Custom Branded Document

```bash
# Create company CSS with brand colors
cat > company.css << EOF
body { font-family: "Open Sans", sans-serif; }
h1, h2 { color: #00539f; /* Company blue */ }
a { color: #00539f; }
EOF

md2pdf report.md --css company.css
```

## Tips

1. **Preview themes quickly:** Convert the same file with different themes to compare
   ```bash
   for theme in github minimal academic dark modern; do
       md2pdf sample.md --theme $theme --create-output-dir theme_comparison
   done
   ```

2. **Mix page sizes with themes:** Themes work with any page size
   ```bash
   PDF_PAGE_SIZE=A3 md2pdf poster.md --theme modern
   ```

3. **Start with a theme, customize later:** Use built-in themes initially, create custom CSS as needs evolve

## Migrating from Old Version

**Before Phase 3:** Font settings were in `.env`
```bash
# Old way (deprecated)
PDF_FONT_FAMILY=Georgia, serif
PDF_CODE_FONT=Monaco, monospace
```

**After Phase 3:** Use themes or custom CSS
```bash
# New way - pick a theme
md2pdf doc.md --theme academic  # Has serif fonts

# Or create custom CSS
cat > mycss.css << EOF
body { font-family: Georgia, serif; }
code { font-family: Monaco, monospace; }
EOF
md2pdf doc.md --css mycss.css
```

**Deprecation:** Old font settings still work but show warnings. They'll be removed in a future version.
```

### Step 3: Update USAGE_GUIDE.md

Add theme section to `docs/USAGE_GUIDE.md` (after basic usage):

```markdown
## Styling Your PDFs

### Using Built-in Themes

md2pdf includes 5 professionally designed themes:

```bash
md2pdf doc.md --theme github    # Default: clean, professional
md2pdf doc.md --theme minimal   # Spacious, simple
md2pdf doc.md --theme academic  # Formal, serif fonts
md2pdf doc.md --theme dark      # Dark mode
md2pdf doc.md --theme modern    # Bold, colorful
```

See [THEMES.md](THEMES.md) for detailed theme descriptions.

### Custom CSS

Use your own stylesheet:

```bash
md2pdf doc.md --css custom.css
```

**Note:** Cannot use both `--theme` and `--css` together.

### Page Setup

Configure page size and margins in `.env`:

```bash
PDF_PAGE_SIZE=Letter
PDF_MARGIN_TOP=2cm
PDF_MARGIN_BOTTOM=2cm
PDF_MARGIN_LEFT=2.5cm
PDF_MARGIN_RIGHT=2.5cm
```

These settings apply to all themes and custom CSS.
```

### Step 4: Commit documentation

```bash
git add README.md docs/USAGE_GUIDE.md docs/THEMES.md
git commit -m "docs: add Phase 3 theme documentation

- Add theme usage to README
- Create comprehensive THEMES.md guide
- Update USAGE_GUIDE with styling section
- Include migration guide from old font settings

Part of Phase 3: Custom Styling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Update Project Memory

**Files:**
- Modify: `/home/echeadle/.claude/projects/-home-echeadle-Translate/memory/MEMORY.md`

### Step 1: Update MEMORY.md

Update the roadmap section and add Phase 3 notes:

```markdown
## Roadmap Progress
- ✅ Phase 5: Testing & Quality (COMPLETE - 61 tests, 83% coverage)
- ✅ Phase 2: Image Support (COMPLETE - 2026-02-08, 70 tests, 86% coverage)
- ✅ Phase 3: Custom Styling (COMPLETE - 2026-02-08, 78+ tests, 86%+ coverage)
- 🔜 Next: Phase 4 (Advanced Features)

## Phase 3 Notes (Custom Styling)
- 5 built-in themes: github (default), minimal, academic, dark, modern
- --theme and --css CLI flags (mutually exclusive)
- Clean separation: page setup in .env, styling in themes/CSS
- Pure CSS files (no placeholders), Python generates @page section
- Deprecated font settings in .env (warnings shown)
- Comprehensive testing: theme loading, CLI integration, deprecation
- Full documentation: THEMES.md guide, README updates
```

### Step 2: Commit memory update

```bash
git add /home/echeadle/.claude/projects/-home-echeadle-Translate/memory/MEMORY.md
git commit -m "docs: update memory with Phase 3 completion

Phase 3 Custom Styling complete:
- 5 themes implemented
- CLI flags added
- Full test coverage
- Comprehensive documentation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Final Integration Test and Verification

**Files:**
- None (testing and verification only)

### Step 1: Run complete test suite

Run: `uv run pytest -v --cov=src/md2pdf --cov-report=term-missing`

Expected:
- 78+ tests passing
- 86%+ coverage
- No failures

### Step 2: Manual comprehensive test

```bash
# Create test directory
mkdir -p /tmp/phase3_final_test

# Test all 5 themes
for theme in github minimal academic dark modern; do
    uv run md2pdf examples/markdown/test_basic.md \
        --theme $theme \
        --output /tmp/phase3_final_test/${theme}_test.pdf
done

# Test custom CSS
echo "body { font-size: 16pt; color: #005500; }" > /tmp/custom_test.css
uv run md2pdf examples/markdown/test_basic.md \
    --css /tmp/custom_test.css \
    --output /tmp/phase3_final_test/custom_test.pdf

# Test default (no flags)
uv run md2pdf examples/markdown/test_basic.md \
    --output /tmp/phase3_final_test/default_test.pdf

# Test directory mode with theme
uv run md2pdf examples/markdown/ \
    --theme minimal \
    --create-output-dir final_test

# Verify all PDFs created
ls -lh /tmp/phase3_final_test/
ls -lh output/final_test*/
```

Expected: All PDFs created successfully

### Step 3: Test error cases

```bash
# Invalid theme
uv run md2pdf examples/markdown/test_basic.md --theme invalid
# Expected: Error with available themes listed

# Non-existent CSS
uv run md2pdf examples/markdown/test_basic.md --css /tmp/nope.css
# Expected: "CSS file not found" error

# Both flags
uv run md2pdf examples/markdown/test_basic.md --theme github --css /tmp/custom_test.css
# Expected: "Cannot use --theme and --css together" error
```

Expected: All errors show helpful messages and exit cleanly

### Step 4: Test with deprecated .env settings

```bash
# Create .env with deprecated settings
cat > .env.test << EOF
PDF_FONT_FAMILY=Georgia, serif
PDF_CODE_FONT=Monaco, monospace
PDF_FONT_SIZE=14pt
PDF_PAGE_SIZE=A4
EOF

# Run with deprecated settings
PDF_FONT_FAMILY="Georgia, serif" uv run md2pdf examples/markdown/test_basic.md \
    --output /tmp/phase3_final_test/deprecated_test.pdf
```

Expected: Warning shown but PDF still created

### Step 5: Verify backwards compatibility

```bash
# Ensure old usage still works
uv run md2pdf examples/markdown/test_basic.md --output /tmp/phase3_final_test/compat_test.pdf
```

Expected: PDF created using github theme (default)

### Step 6: Check help output

Run: `uv run md2pdf --help`

Expected: Help shows --theme and --css flags with descriptions

---

## Task 14: Final Commit and Success Verification

**Files:**
- Update: `docs/plans/2026-02-08-phase3-custom-styling-design.md`

### Step 1: Update design document with completion status

Update the "Success Criteria" section in design doc:

```markdown
## Success Criteria

- [x] All 5 themes implemented and working
- [x] `--theme` flag accepts all theme names
- [x] `--css` flag loads custom CSS files
- [x] Using both flags produces clear error
- [x] Default behavior uses `github` theme
- [x] Deprecation warnings shown for font settings
- [x] All tests passing (78+ tests)
- [x] Coverage maintained at 86%+
- [x] Documentation updated
- [x] Manual testing checklist completed

**Status:** ✅ COMPLETE
**Date Completed:** 2026-02-08
**Final Test Count:** 78 tests
**Final Coverage:** 86%
```

### Step 2: Final commit

```bash
git add docs/plans/2026-02-08-phase3-custom-styling-design.md
git commit -m "docs: mark Phase 3 as complete

Phase 3: Custom Styling - COMPLETE ✅

Deliverables:
- 5 built-in themes (github, minimal, academic, dark, modern)
- --theme and --css CLI flags with mutual exclusivity
- Refactored styling system (page setup + visual styling)
- Deprecation warnings for old font settings
- 78+ tests with 86%+ coverage
- Comprehensive documentation (THEMES.md)

All success criteria met. Ready for Phase 4.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Step 3: Create implementation summary

Run: `uv run pytest --collect-only | grep "test session starts" -A 1000`

Record final statistics and verify against success criteria.

### Step 4: Push to remote (if applicable)

```bash
git log --oneline -15  # Review commits
git push origin main   # Push if ready
```

---

## Summary

**Implementation Order:**
1. ✅ Theme infrastructure (loading functions, tests)
2. ✅ GitHub theme migration (extract CSS, refactor styles.py)
3. ✅ CLI flags (--theme, --css, validation)
4. ✅ Converter update (accept CSS string)
5. ✅ Minimal theme (clean, spacious)
6. ✅ Academic theme (formal, serif)
7. ✅ Dark theme (dark mode)
8. ✅ Modern theme (bold, colorful)
9. ✅ Deprecation warnings (font settings)
10. ✅ Full testing (unit, integration, manual)
11. ✅ Documentation (README, USAGE_GUIDE, THEMES.md)
12. ✅ Memory update (project notes)
13. ✅ Final verification (comprehensive testing)
14. ✅ Completion (mark as done, push)

**Expected Outcome:**
- 5 working themes ✅
- CLI flags functioning ✅
- All tests passing (96 tests) ✅
- Coverage maintained (89%) ✅
- Complete documentation ✅
- Backwards compatible ✅
- Ready for Phase 4 ✅

**Status:** ✅ COMPLETE
**Date Completed:** 2026-02-09
**Final Test Count:** 96 tests
**Final Coverage:** 89%

**Files Modified:** 9
**Files Created:** 11
**Tests Added:** 26 new test functions (70 → 96)
**Commits:** 14
