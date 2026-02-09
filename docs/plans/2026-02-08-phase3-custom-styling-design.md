# Phase 3: Custom Styling - Design Document

**Date:** 2026-02-08
**Status:** Approved
**Phase:** 3 of 5

## Overview

Add flexible styling system to md2pdf while keeping it simple for beginners and powerful for advanced users.

## Goals

1. **Custom CSS file support** - `--css` flag to load external CSS files
2. **Multiple built-in themes** - 5 pre-designed themes users can choose from
3. **CSS overrides via .env** - Page setup remains in .env, applies to all themes

## Design Principles

- **Clean separation** - Users choose either `--theme` OR `--css`, never both
- **Start simple, grow later** - Clear error messages, intuitive interface
- **Backwards compatible** - Existing .env files continue working with deprecation warnings
- **YAGNI** - No complex override systems, no theme inheritance, keep it simple

## Three Ways to Style PDFs

1. **Built-in themes** (easiest) - `--theme academic`
2. **Custom CSS files** (advanced) - `--css mystyle.css`
3. **Default behavior** (no flags) - Uses `github` theme automatically

## Architecture

### Styling Model

```
Page Setup (from .env)     +    Visual Style (from theme/CSS)
├─ Page size (A4, Letter)       ├─ Fonts and colors
├─ Margins (all sides)           ├─ Headers and spacing
└─ Applied to ALL outputs        ├─ Code block styling
                                 └─ Tables and lists
```

**Mental Model:** `.env` configures the paper, themes/CSS design what goes on it.

### Theme System

**Five Built-in Themes:**

1. **`github`** (default) - Current style, clean and professional
2. **`minimal`** - Maximum whitespace, simple typography, very clean
3. **`academic`** - Serif fonts, formal appearance, traditional papers
4. **`dark`** - Dark background with light text, modern aesthetic
5. **`modern`** - Bold headers, contemporary design, colorful accents

**File Organization:**

```
src/md2pdf/themes/
├── __init__.py              # Theme loading logic
├── github.css               # Pure CSS files (no placeholders)
├── minimal.css
├── academic.css
├── dark.css
└── modern.css
```

**Theme Loading Process:**

1. Python generates `@page { ... }` section from `.env` config
2. Python loads requested theme CSS file (pure CSS, no @page rules)
3. Concatenates: `page_css + theme_css`
4. Passes complete CSS to WeasyPrint

**Why @page in Python?** Keeps CSS files pure and valid. Page setup is config-dependent, visual styling is theme-dependent. Clean separation.

## CLI Interface

### New Flags

```python
theme: Optional[str] = typer.Option(
    None,
    "--theme",
    help="Built-in theme: github, minimal, academic, dark, modern"
)

css: Optional[Path] = typer.Option(
    None,
    "--css",
    help="Path to custom CSS file"
)
```

### Usage Examples

```bash
# Use built-in theme
uv run md2pdf file.md --theme academic

# Use custom CSS
uv run md2pdf file.md --css my-styles.css

# No flags = github theme (default)
uv run md2pdf file.md

# Error: can't use both
uv run md2pdf file.md --theme minimal --css custom.css
# → Error: Cannot use --theme and --css together
```

### CLI Logic Flow

1. **Validate flags** - If both `--theme` and `--css` provided → error and exit
2. **Determine style source:**
   - If `--css` provided → load custom CSS file
   - If `--theme` provided → load that theme
   - If neither → use `github` theme (default)
3. **Generate final CSS** - Combine `@page` config + style source
4. **Convert** - Pass to existing converter

### Error Messages

- Both flags: `"Cannot use --theme and --css together. Choose one."`
- Invalid theme: `"Unknown theme 'foo'. Available: github, minimal, academic, dark, modern"`
- CSS file not found: `"CSS file not found: path/to/file.css"`

## Configuration & Migration

### .env Changes

**Keep (page setup):**
- `PDF_PAGE_SIZE=A4`
- `PDF_MARGIN_TOP=2cm`
- `PDF_MARGIN_BOTTOM=2cm`
- `PDF_MARGIN_LEFT=2cm`
- `PDF_MARGIN_RIGHT=2cm`

**Deprecate (fonts - now in themes):**
- `PDF_FONT_FAMILY` - Show warning, still works temporarily
- `PDF_CODE_FONT` - Show warning, still works temporarily
- `PDF_FONT_SIZE` - Show warning, still works temporarily

### Backwards Compatibility

```python
# Check for deprecated settings
deprecated_settings = []
if os.getenv("PDF_FONT_FAMILY"):
    deprecated_settings.append("PDF_FONT_FAMILY")
if os.getenv("PDF_CODE_FONT"):
    deprecated_settings.append("PDF_CODE_FONT")
if os.getenv("PDF_FONT_SIZE"):
    deprecated_settings.append("PDF_FONT_SIZE")

if deprecated_settings:
    console.print(
        f"[yellow]⚠️  Deprecated:[/yellow] {', '.join(deprecated_settings)} "
        f"in .env will be ignored. Use --theme or --css instead."
    )
```

### Migration Path

1. Existing `.env` files keep working (page setup)
2. Font settings show warning but don't break anything
3. Documentation explains: "Use themes for fonts now"
4. Future version can remove font settings entirely

## Implementation Components

### Component 1: Theme Loading (`themes/__init__.py`)

```python
from pathlib import Path
from typing import Optional

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

### Component 2: Refactored Styles (`styles.py`)

```python
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

# Note: get_default_css() becomes deprecated
```

### Component 3: CLI Changes (`cli.py`)

```python
def main(
    # ... existing parameters ...
    theme: Optional[str] = typer.Option(
        None,
        "--theme",
        help="Built-in theme (github, minimal, academic, dark, modern)"
    ),
    css: Optional[Path] = typer.Option(
        None,
        "--css",
        help="Path to custom CSS file"
    ),
):
    """Convert markdown to PDF with optional styling."""

    # Validation: mutually exclusive
    if theme and css:
        console.print(
            "[red]Error:[/red] Cannot use --theme and --css together.\n"
            "Choose one:\n"
            "  • --theme for built-in themes\n"
            "  • --css for custom CSS files"
        )
        raise typer.Exit(1)

    # Determine style source
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

    # Generate complete CSS
    page_css = get_page_css(config)
    final_css = page_css + style_css

    # Pass to converter
    converter = MarkdownConverter(css=final_css)
    # ... rest of conversion logic ...
```

### Component 4: Converter Changes (`converter.py`)

```python
class MarkdownConverter:
    def __init__(self, css: Optional[str] = None):
        """Initialize converter.

        Args:
            css: Complete CSS string (page + styling). If None, uses default.
        """
        self.css = css
        # ... rest of init ...
```

**Key Change:** Converter receives complete CSS string instead of generating it internally.

### Component 5: Config Changes (`config.py`)

Add deprecation warnings in `Config.load()`:

```python
@classmethod
def load(cls, env_file: Optional[Path] = None) -> "Config":
    """Load configuration from environment variables."""
    # ... existing loading logic ...

    # Check for deprecated settings
    deprecated_settings = []
    if os.getenv("PDF_FONT_FAMILY"):
        deprecated_settings.append("PDF_FONT_FAMILY")
    if os.getenv("PDF_CODE_FONT"):
        deprecated_settings.append("PDF_CODE_FONT")
    if os.getenv("PDF_FONT_SIZE"):
        deprecated_settings.append("PDF_FONT_SIZE")

    if deprecated_settings:
        from rich.console import Console
        console = Console()
        console.print(
            f"[yellow]⚠️  Deprecated:[/yellow] {', '.join(deprecated_settings)} "
            f"in .env will be ignored. Use --theme or --css instead."
        )

    return config
```

## File Organization

### New Files

```
src/md2pdf/themes/
├── __init__.py              # Theme registry and loading
├── github.css               # Migrate current styles here
├── minimal.css              # New: clean, spacious design
├── academic.css             # New: formal, serif fonts
├── dark.css                 # New: dark mode
└── modern.css               # New: contemporary design
```

### Modified Files

```
src/md2pdf/
├── styles.py                # Refactor: only generates @page CSS
├── config.py                # Add deprecation warnings
├── cli.py                   # Add --theme and --css flags
└── converter.py             # Use new theme system
```

## Error Handling

### Error Scenarios

1. **Both flags used:**
   - Error: "Cannot use --theme and --css together"
   - Exit code: 1

2. **Invalid theme name:**
   - Error: "Unknown theme 'foo'. Available: github, minimal, academic, dark, modern"
   - Exit code: 1

3. **CSS file not found:**
   - Error: "CSS file not found: path/to/file.css"
   - Exit code: 1

4. **CSS file read error:**
   - Error: "Cannot read CSS file: [reason]"
   - Exit code: 1

## Testing Strategy

### Unit Tests

- `test_themes.py` - Theme loading, validation, file reading
- `test_styles.py` - Update to test `get_page_css()` only
- `test_config.py` - Deprecation warnings for font settings

### Integration Tests

- `test_cli_themes.py` - CLI with each theme flag
- `test_cli_custom_css.py` - CLI with custom CSS files
- `test_cli_theme_css_conflict.py` - Both flags (should error)

### Manual Testing Checklist

```bash
# Test each theme
uv run md2pdf examples/markdown/test_basic.md --theme github --create-output-dir themes
uv run md2pdf examples/markdown/test_basic.md --theme minimal --create-output-dir themes
uv run md2pdf examples/markdown/test_basic.md --theme academic --create-output-dir themes
uv run md2pdf examples/markdown/test_basic.md --theme dark --create-output-dir themes
uv run md2pdf examples/markdown/test_basic.md --theme modern --create-output-dir themes

# Test custom CSS
uv run md2pdf examples/markdown/test_basic.md --css examples/custom.css --create-output-dir themes

# Test default (no flags)
uv run md2pdf examples/markdown/test_basic.md --create-output-dir themes

# Test errors
uv run md2pdf file.md --theme invalid
uv run md2pdf file.md --css nonexistent.css
uv run md2pdf file.md --theme github --css custom.css
```

### Coverage Goals

- Maintain 86%+ overall coverage
- 100% coverage on new `themes/__init__.py` module
- Update existing tests to use new architecture

## Implementation Order

1. **Create theme infrastructure**
   - Create `themes/` directory
   - Implement `themes/__init__.py` with loading functions
   - Add tests for theme loading

2. **Migrate github theme**
   - Extract current CSS to `github.css`
   - Refactor `styles.py` to only generate `@page` CSS
   - Update tests

3. **Add CLI flags**
   - Add `--theme` and `--css` parameters
   - Implement validation logic
   - Add error handling

4. **Update converter**
   - Modify to accept CSS string
   - Update converter tests

5. **Create remaining themes**
   - Design and implement: minimal, academic, dark, modern
   - Test each theme with example files

6. **Add deprecation warnings**
   - Update `config.py` with warnings
   - Update `.env.example`
   - Test deprecation messages

7. **Documentation**
   - Update README.md with theme examples
   - Update USAGE_GUIDE.md
   - Create theme showcase examples

8. **Integration testing**
   - Test all themes end-to-end
   - Test custom CSS files
   - Test error scenarios
   - Verify backwards compatibility

## Success Criteria

- [ ] All 5 themes implemented and working
- [ ] `--theme` flag accepts all theme names
- [ ] `--css` flag loads custom CSS files
- [ ] Using both flags produces clear error
- [ ] Default behavior uses `github` theme
- [ ] Deprecation warnings shown for font settings
- [ ] All tests passing (70+ tests)
- [ ] Coverage maintained at 86%+
- [ ] Documentation updated
- [ ] Manual testing checklist completed

## Future Enhancements (Not in Phase 3)

- Theme + CSS override system (use theme as base, CSS for tweaks)
- More themes based on user feedback
- Theme preview command (`--preview-theme`)
- Custom theme directory support
- CSS validation before conversion

## Design Decisions & Rationale

### Why mutually exclusive flags?

**Simplicity for beginners.** Clear mental model: pick a theme OR bring your own CSS. Avoids confusion about precedence and cascading. Can add override system later if needed.

### Why @page in Python instead of CSS?

**Clean separation.** Page setup is configuration (comes from .env), styling is visual design (comes from themes). Keeps CSS files pure and valid. Easy to test themes in browser.

### Why deprecate font settings instead of removing?

**Smooth migration.** Existing users see warnings but nothing breaks. Gives time to update workflows. Can remove in future major version.

### Why 5 themes?

**Balance.** Enough variety for most use cases (professional, minimal, formal, modern, dark). Not so many that it's overwhelming. Easy to add more based on feedback.

### Why no theme inheritance/extension?

**YAGNI.** Complex systems can come later if needed. Start simple, add power when users request it. Most users will pick a theme or bring CSS, not both.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing workflows | High | Deprecation warnings, backwards compatibility |
| Theme CSS quality | Medium | Test with multiple markdown files, iterate on design |
| Performance with large CSS | Low | CSS is small text files, negligible impact |
| Users want theme + overrides | Medium | Clear error message, document custom CSS approach |

## Approval

- [x] Architecture approved
- [x] CLI interface approved
- [x] Migration strategy approved
- [x] Testing approach approved
- [x] Ready for implementation

**Approved by:** User
**Date:** 2026-02-08
