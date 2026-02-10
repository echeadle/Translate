"""Tests for table of contents (TOC) functionality."""

from md2pdf.converter import MarkdownConverter


class TestHeaderExtraction:
    """Test anchor ID generation from header text."""

    def test_generate_anchor_id_simple(self, converter):
        """Test simple text conversion."""
        seen_ids = set()
        result = converter.generate_anchor_id("Introduction", seen_ids)
        assert result == "introduction"
        assert "introduction" in seen_ids

    def test_generate_anchor_id_with_spaces(self, converter):
        """Test text with spaces."""
        seen_ids = set()
        result = converter.generate_anchor_id("Getting Started", seen_ids)
        assert result == "getting-started"
        assert "getting-started" in seen_ids

    def test_generate_anchor_id_with_special_chars(self, converter):
        """Test text with special characters."""
        seen_ids = set()
        result = converter.generate_anchor_id("FAQ's & Tips!", seen_ids)
        assert result == "faqs-tips"
        assert "faqs-tips" in seen_ids

    def test_generate_anchor_id_duplicate(self, converter):
        """Test duplicate handling."""
        seen_ids = set()

        # First occurrence
        result1 = converter.generate_anchor_id("Introduction", seen_ids)
        assert result1 == "introduction"

        # Second occurrence
        result2 = converter.generate_anchor_id("Introduction", seen_ids)
        assert result2 == "introduction-2"

        # Third occurrence
        result3 = converter.generate_anchor_id("Introduction", seen_ids)
        assert result3 == "introduction-3"

        assert seen_ids == {"introduction", "introduction-2", "introduction-3"}

    def test_generate_anchor_id_numbers_only(self, converter):
        """Test text with only numbers."""
        seen_ids = set()
        result = converter.generate_anchor_id("2024", seen_ids)
        assert result == "2024"
        assert "2024" in seen_ids

    def test_generate_anchor_id_empty_after_sanitize(self, converter):
        """Test text that becomes empty after sanitization."""
        seen_ids = set()
        result = converter.generate_anchor_id("!!!", seen_ids)
        assert result == "heading"
        assert "heading" in seen_ids


class TestTOCGeneration:
    """Test TOC HTML generation."""

    def test_generate_toc_html_empty(self, converter):
        """Test empty header list."""
        result = converter.generate_toc_html([])
        assert result == ""

    def test_generate_toc_html_single_h1(self, converter):
        """Test single H1 header."""
        headers = [
            {"text": "Introduction", "level": 1, "page": 1, "anchor_id": "introduction"}
        ]
        result = converter.generate_toc_html(headers)

        assert '<div class="toc">' in result
        assert '<h1>Table of Contents</h1>' in result
        assert '<ul>' in result
        assert '<li class="toc-h1">' in result
        assert '<a href="#introduction">Introduction</a>' in result
        assert '<span class="toc-page">1</span>' in result
        assert '</ul>' in result
        assert '</div>' in result

    def test_generate_toc_html_mixed_levels(self, converter):
        """Test mixed H1 and H2 headers."""
        headers = [
            {"text": "Introduction", "level": 1, "page": 1, "anchor_id": "introduction"},
            {"text": "Overview", "level": 2, "page": 1, "anchor_id": "overview"},
            {"text": "Getting Started", "level": 1, "page": 2, "anchor_id": "getting-started"},
        ]
        result = converter.generate_toc_html(headers)

        assert '<li class="toc-h1">' in result
        assert '<li class="toc-h2">' in result
        assert '<a href="#introduction">Introduction</a>' in result
        assert '<a href="#overview">Overview</a>' in result
        assert '<a href="#getting-started">Getting Started</a>' in result

    def test_generate_toc_html_page_numbers(self, converter):
        """Test page numbers appear correctly."""
        headers = [
            {"text": "Chapter 1", "level": 1, "page": 1, "anchor_id": "chapter-1"},
            {"text": "Chapter 2", "level": 1, "page": 5, "anchor_id": "chapter-2"},
            {"text": "Chapter 3", "level": 1, "page": 10, "anchor_id": "chapter-3"},
        ]
        result = converter.generate_toc_html(headers)

        assert '<span class="toc-page">1</span>' in result
        assert '<span class="toc-page">5</span>' in result
        assert '<span class="toc-page">10</span>' in result

    def test_generate_toc_html_escapes_html(self, converter):
        """Test TOC HTML escapes special HTML characters."""
        headers = [
            {"text": "<script>alert('XSS')</script>", "level": 1, "page": 1, "anchor_id": "xss"},
            {"text": "A & B < C > D", "level": 1, "page": 2, "anchor_id": "symbols"}
        ]

        html_output = converter.generate_toc_html(headers)

        # Should have escaped HTML
        assert "&lt;script&gt;" in html_output
        assert "alert('XSS')" not in html_output
        assert "&amp;" in html_output  # Ampersand escaped
        assert "&lt;" in html_output and "&gt;" in html_output


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
