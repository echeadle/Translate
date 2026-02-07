# Pytest Test Suite Design for md2pdf

**Date:** 2026-02-07
**Goal:** Comprehensive test suite with 80%+ code coverage
**Approach:** Integration-focused testing with real dependencies

## Design Decisions

### 1. Coverage Target
- **80%+ coverage** across all modules
- Comprehensive testing of core functionality, edge cases, and error handling
- Production-ready quality assurance

### 2. Testing Philosophy
- **Real dependencies** - Use actual `markdown` and `weasyprint` libraries (no mocking)
- **Integration-focused** - Tests create actual PDFs and verify real-world behavior
- **Clear structure** - One test file per source module for easy navigation

### 3. Test Organization
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── fixtures/                # Test markdown files and data
│   ├── simple.md           # Basic markdown
│   ├── tables.md           # Table testing
│   ├── code_blocks.md      # Code syntax highlighting
│   ├── complex.md          # All features combined
│   ├── empty.md            # Edge case: empty file
│   ├── invalid.md          # Edge case: malformed content
│   └── nested/
│       └── subdoc.md       # Directory structure testing
├── test_cli.py             # CLI interface tests (~228 lines to cover)
├── test_converter.py       # Core conversion logic tests (~142 lines)
├── test_config.py          # Configuration loading tests (~81 lines)
├── test_styles.py          # CSS generation tests (~192 lines)
├── test_utils.py           # Utility function tests (~53 lines)
└── test_integration.py     # End-to-end workflow tests
```

## Shared Fixtures (conftest.py)

### Core Fixtures

**temp_workspace**
```python
@pytest.fixture
def temp_workspace(tmp_path):
    """Temporary workspace with input/output directories."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "input").mkdir()
    (workspace / "output").mkdir()
    return workspace
```

**sample_markdown_files**
```python
@pytest.fixture
def sample_markdown_files(temp_workspace):
    """Create sample markdown files in temp workspace."""
    # Copy from tests/fixtures/ to temp_workspace/input/
    # Returns dict: {"simple": Path, "tables": Path, ...}
```

**mock_config**
```python
@pytest.fixture
def mock_config():
    """Default Config object for testing."""
    return Config(
        pdf_page_size="A4",
        pdf_margin_top="2cm",
        # ... all default values
    )
```

**converter**
```python
@pytest.fixture
def converter(mock_config):
    """MarkdownConverter instance with test config."""
    return MarkdownConverter(mock_config)
```

**clean_env**
```python
@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment without .env file pollution."""
    # Clear all PDF_* and DEFAULT_* env vars
```

### Fixture Benefits
- `temp_workspace` - Automatic cleanup, isolated tests
- `sample_markdown_files` - Consistent test data across all tests
- `mock_config` - No dependency on .env file
- `converter` - Ready-to-use converter instance
- `clean_env` - Prevents test pollution from user's .env

## Test Coverage by Module

### test_converter.py - Core Conversion Logic

**Class: TestMarkdownConverter**

Tests:
- `test_convert_simple_markdown()` - Basic markdown to PDF conversion
- `test_convert_with_tables()` - Table rendering in PDF
- `test_convert_with_code_blocks()` - Syntax highlighting in code blocks
- `test_convert_complex_document()` - All features combined
- `test_convert_empty_file()` - Handling of empty markdown file
- `test_convert_nonexistent_file()` - Error handling for missing file (should raise InvalidMarkdownError)
- `test_convert_invalid_output_path()` - Error when output path is unwritable (should raise ConversionError)
- `test_batch_conversion()` - Converting multiple files at once
- `test_pdf_file_validity()` - Verify generated PDFs are valid (file size > 0, can be opened)

**Coverage:** Core conversion pipeline, error handling, batch processing

### test_config.py - Configuration Loading

**Class: TestConfig**

Tests:
- `test_load_default_config()` - Config with no .env file
- `test_load_from_env_file()` - Loading custom values from .env
- `test_invalid_margin_values()` - Validation of margin settings
- `test_boolean_parsing()` - PRESERVE_DIRECTORY_STRUCTURE parsing (true/false strings)
- `test_various_page_sizes()` - Different PDF page sizes (parametrized: A4, Letter, A3)
- `test_config_validation()` - Config.validate() method
- `test_missing_env_falls_back_to_defaults()` - Partial .env file handling

**Coverage:** Configuration loading, validation, defaults, error handling

### test_cli.py - CLI Interface

**Class: TestCLI**

Tests:
- `test_single_file_conversion()` - `md2pdf file.md`
- `test_create_output_dir_auto()` - `md2pdf file.md --create-output-dir auto` (verify timestamped directory)
- `test_create_output_dir_named()` - `md2pdf file.md --create-output-dir mypdfs`
- `test_directory_conversion()` - `md2pdf docs/` (multiple files)
- `test_preserve_structure()` - `md2pdf docs/ --preserve-structure` (verify subdirs maintained)
- `test_no_preserve_structure()` - `md2pdf docs/ --no-preserve-structure` (verify flattened output)
- `test_custom_output_path()` - `md2pdf file.md --output custom.pdf`
- `test_custom_output_dir()` - `md2pdf docs/ --output-dir pdfs/`
- `test_nonexistent_input_file()` - Error handling for missing input (should exit with error)
- `test_invalid_input_directory()` - Non-existent directory input
- `test_help_command()` - `md2pdf --help` (verify help text displays)
- `test_version_command()` - `md2pdf --version` (if implemented)
- `test_cli_error_messages()` - Verify user-friendly error messages
- `test_output_already_exists()` - Handling of existing output files

**Testing Strategy:**
- Use `typer.testing.CliRunner` for CLI invocation
- Verify exit codes, stdout/stderr output, file creation
- Test Rich console formatting where applicable

**Coverage:** All CLI flags, error handling, user workflows, output formatting

### test_styles.py - CSS Generation

**Class: TestStyles**

Tests:
- `test_get_default_css()` - CSS generation with default config
- `test_css_with_custom_fonts()` - CSS with custom font settings
- `test_css_with_custom_margins()` - CSS with custom margins (verify @page rules)
- `test_css_with_custom_font_size()` - CSS with custom font size
- `test_css_includes_code_styling()` - Code block styles present (pre/code backgrounds)
- `test_css_includes_table_styling()` - Table styles present (borders, alternating rows)
- `test_css_includes_header_styling()` - Header styles (h1-h6)
- `test_page_size_in_css()` - Different page sizes in CSS (parametrized: A4, Letter, A3)
- `test_css_is_valid()` - Basic CSS syntax validation
- `test_css_configuration_injection()` - Config values properly injected into CSS

**Coverage:** CSS generation, configuration integration, styling rules

### test_utils.py - Utility Functions

**Class: TestUtils**

Tests:
- `test_get_output_path_preserve_structure()` - Path calculation with structure preservation
- `test_get_output_path_flatten()` - Path calculation without structure
- `test_get_output_path_edge_cases()` - Deep nesting, special characters
- `test_ensure_output_dir()` - Directory creation
- `test_ensure_output_dir_already_exists()` - Idempotent directory creation
- `test_get_markdown_files_single()` - Finding markdown files in path
- `test_get_markdown_files_recursive()` - Finding files in subdirectories
- `test_get_markdown_files_empty_directory()` - No markdown files found
- `test_get_markdown_files_mixed_extensions()` - Only .md files returned

**Coverage:** Path utilities, file discovery, directory operations

### test_integration.py - End-to-End Workflows

**Class: TestIntegrationWorkflows**

Tests:
- `test_complete_single_file_workflow()` - End-to-end: Create .md → convert → verify PDF
- `test_complete_directory_workflow()` - Multiple files with subdirs
- `test_real_world_scenario_with_auto_dir()` - Simulate real user workflow with --create-output-dir auto
- `test_config_file_integration()` - .env file affects conversion output
- `test_error_recovery_in_batch()` - Batch continues after individual file errors
- `test_nested_directory_structure()` - Complex directory hierarchies
- `test_all_markdown_features()` - Document with all supported features

**Coverage:** Complete user workflows, real-world scenarios, system integration

## Test Fixtures Content

### tests/fixtures/simple.md
```markdown
# Simple Test
Basic paragraph with **bold** and *italic*.

- List item 1
- List item 2

1. Numbered item
2. Another item
```

### tests/fixtures/tables.md
```markdown
# Table Test

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Data A   | Data B   | Data C   |
| Row 3    | More     | Data     |
```

### tests/fixtures/code_blocks.md
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

### tests/fixtures/complex.md
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

### tests/fixtures/empty.md
(Empty file - 0 bytes)

### tests/fixtures/invalid.md
```markdown
# Test
[Broken link](
Unclosed **bold
```

### tests/fixtures/nested/subdoc.md
```markdown
# Nested Document
Testing directory structure preservation.
```

**Total Test Data Size:** ~7-8 small markdown files, <5KB total

## Dependencies to Add

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
]
```

## Running Tests

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

# Run and show print statements
uv run pytest -s
```

## Expected Coverage Results

**Target:** 80%+ overall coverage

**Per Module Estimates:**
- `converter.py` - 85-90% (core logic well tested)
- `config.py` - 90-95% (straightforward to test)
- `cli.py` - 80-85% (many branches, complex)
- `styles.py` - 85-90% (CSS generation)
- `utils.py` - 90-95% (pure functions)

**Uncovered Code:** Likely in error handling paths that are hard to trigger, edge cases in CLI formatting

## Testing Strategy Summary

1. **Use real dependencies** - No mocking of markdown/weasyprint
2. **Verify actual PDFs** - Check files exist, have content, are valid
3. **Test user workflows** - Focus on real-world usage patterns
4. **Parametrize common patterns** - Use `@pytest.mark.parametrize` for multiple scenarios
5. **Clear test names** - Descriptive names that explain what's being tested
6. **Isolated tests** - Each test is independent, uses temp directories
7. **Fast enough** - Integration tests are slower but still reasonable (<1s per test typically)

## Implementation Order

1. **Setup** - Add dependencies, create tests/ directory structure
2. **Fixtures** - Create conftest.py and tests/fixtures/ content
3. **Core tests** - test_converter.py, test_config.py (most critical)
4. **Utility tests** - test_utils.py (simplest)
5. **Style tests** - test_styles.py
6. **CLI tests** - test_cli.py (most complex)
7. **Integration tests** - test_integration.py (ties everything together)
8. **Coverage analysis** - Run coverage, identify gaps, add tests

## Success Criteria

- [ ] All tests pass
- [ ] 80%+ code coverage achieved
- [ ] All modules have corresponding test files
- [ ] Integration tests verify end-to-end workflows
- [ ] Tests run in <30 seconds total
- [ ] Clear test failure messages
- [ ] Documentation updated with testing instructions
