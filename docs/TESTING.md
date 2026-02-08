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
