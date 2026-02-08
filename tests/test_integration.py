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
