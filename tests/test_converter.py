"""Tests for markdown to PDF conversion."""

from pathlib import Path

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

    def test_metadata_html_escaping(self, mock_config, tmp_path):
        """Test metadata HTML special characters are escaped."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")
        output_file = tmp_path / "output.pdf"

        # Test HTML injection attempt
        metadata = {
            'title': 'Test </title><script>alert("XSS")</script>',
            'author': 'O\'Brien & <Company>',
            'subject': 'Test "Subject" with quotes',
            'keywords': 'test, <tag>, "quotes"',
        }

        # Should not raise error and should generate valid PDF
        converter.convert_file(md_file, output_file, metadata=metadata)
        assert output_file.exists()
        assert output_file.stat().st_size > 0


class TestMergeConversion:
    """Tests for merge conversion (multiple markdown files → one PDF)."""

    def test_convert_merge_basic(self, converter, tmp_path):
        """Test merging three markdown files into one PDF."""
        files = []
        for i, title in enumerate(["Alpha", "Beta", "Gamma"]):
            md = tmp_path / f"file{i}.md"
            md.write_text(f"# {title}\n\nContent for {title}.")
            files.append(md)

        output = tmp_path / "merged.pdf"
        converter.convert_merge(files, output)

        assert output.exists()
        assert output.stat().st_size > 0
        # Valid PDF header
        assert output.read_bytes()[:4] == b"%PDF"

    def test_convert_merge_empty_list(self, converter, tmp_path):
        """Test that merging an empty list raises an error."""
        output = tmp_path / "merged.pdf"

        with pytest.raises(InvalidMarkdownError, match="No markdown files"):
            converter.convert_merge([], output)

    def test_convert_merge_single_file(self, converter, tmp_path):
        """Test merging a single file works fine."""
        md = tmp_path / "only.md"
        md.write_text("# Solo\n\nJust one file.")

        output = tmp_path / "merged.pdf"
        converter.convert_merge([md], output)

        assert output.exists()
        assert output.stat().st_size > 0

    def test_convert_merge_with_toc(self, converter, tmp_path):
        """Test merged PDF has unified TOC from all files."""
        file_a = tmp_path / "a.md"
        file_a.write_text("# Chapter One\n\n## Section 1.1\n\nText.")

        file_b = tmp_path / "b.md"
        file_b.write_text("# Chapter Two\n\n## Section 2.1\n\nMore text.")

        output = tmp_path / "merged.pdf"
        converter.convert_merge([file_a, file_b], output, toc_enabled=True)

        assert output.exists()
        assert output.stat().st_size > 0

    def test_convert_merge_with_metadata(self, converter, tmp_path):
        """Test merged PDF respects metadata."""
        md = tmp_path / "test.md"
        md.write_text("# Test\n\nContent.")

        output = tmp_path / "merged.pdf"
        metadata = {
            "title": "Merged Document",
            "author": "Test Author",
            "subject": None,
            "keywords": None,
        }
        converter.convert_merge([md], output, metadata=metadata)

        assert output.exists()

    def test_convert_merge_missing_file(self, converter, tmp_path):
        """Test merging with a missing file raises error."""
        valid = tmp_path / "valid.md"
        valid.write_text("# Valid")

        missing = tmp_path / "missing.md"

        output = tmp_path / "merged.pdf"

        with pytest.raises(InvalidMarkdownError, match="File not found"):
            converter.convert_merge([valid, missing], output)
