"""Tests for table of contents (TOC) and title page functionality."""

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

    def test_extract_headers_id_attribute_ordering(self, mock_config):
        """Test id attribute works regardless of position in tag."""
        from md2pdf.converter import MarkdownConverter

        converter = MarkdownConverter(mock_config)

        # Test with id attribute NOT first
        html = '<h1 class="big" data-foo="bar" id="test-id">Header</h1>'
        headers = converter.extract_headers(html)

        assert len(headers) == 1
        assert headers[0]['anchor_id'] == 'test-id'
        assert headers[0]['text'] == 'Header'
        assert headers[0]['level'] == 1

    def test_extract_headers_invalid_id_whitespace(self, mock_config):
        """Test IDs with whitespace are regenerated."""
        from md2pdf.converter import MarkdownConverter

        converter = MarkdownConverter(mock_config)

        # Test with invalid ID (contains spaces)
        html = '<h1 id=" bad id ">Header Text</h1>'
        headers = converter.extract_headers(html)

        assert len(headers) == 1
        assert ' ' not in headers[0]['anchor_id']
        assert headers[0]['anchor_id'] == 'header-text'  # Auto-generated
        assert headers[0]['text'] == 'Header Text'

    def test_extract_headers_document_order(self, mock_config):
        """Test headers are returned in document order, not grouped by level."""
        converter = MarkdownConverter(mock_config)

        html = (
            '<h1 id="ch1">Chapter 1</h1>'
            '<h2 id="s1">Section 1</h2>'
            '<h1 id="ch2">Chapter 2</h1>'
            '<h2 id="s2">Section 2</h2>'
        )
        headers = converter.extract_headers(html)

        assert len(headers) == 4
        assert headers[0]['text'] == 'Chapter 1'
        assert headers[0]['level'] == 1
        assert headers[1]['text'] == 'Section 1'
        assert headers[1]['level'] == 2
        assert headers[2]['text'] == 'Chapter 2'
        assert headers[2]['level'] == 1
        assert headers[3]['text'] == 'Section 2'
        assert headers[3]['level'] == 2

    def test_extract_headers_strips_nested_html(self, mock_config):
        """Test that nested HTML tags (bold, etc.) are stripped from header text."""
        converter = MarkdownConverter(mock_config)

        html = '<h1 id="ch1"><strong>Bold Chapter</strong></h1>'
        headers = converter.extract_headers(html)

        assert len(headers) == 1
        assert headers[0]['text'] == 'Bold Chapter'


class TestTOCGeneration:
    """Test TOC HTML generation."""

    def test_generate_toc_html_empty(self, converter):
        """Test empty header list."""
        result = converter.generate_toc_html([])
        assert result == ""

    def test_generate_toc_html_single_h1(self, converter):
        """Test single H1 header."""
        headers = [
            {"text": "Introduction", "level": 1, "anchor_id": "introduction"}
        ]
        result = converter.generate_toc_html(headers)

        assert '<div class="toc">' in result
        assert '<h1>Table of Contents</h1>' in result
        assert '<ul>' in result
        assert '<li class="toc-h1">' in result
        assert '<a href="#introduction">Introduction</a>' in result
        assert '</ul>' in result
        assert '</div>' in result
        # Page numbers are CSS-driven, not in HTML
        assert 'toc-page' not in result

    def test_generate_toc_html_mixed_levels(self, converter):
        """Test mixed H1 and H2 headers."""
        headers = [
            {"text": "Introduction", "level": 1, "anchor_id": "introduction"},
            {"text": "Overview", "level": 2, "anchor_id": "overview"},
            {"text": "Getting Started", "level": 1, "anchor_id": "getting-started"},
        ]
        result = converter.generate_toc_html(headers)

        assert '<li class="toc-h1">' in result
        assert '<li class="toc-h2">' in result
        assert '<a href="#introduction">Introduction</a>' in result
        assert '<a href="#overview">Overview</a>' in result
        assert '<a href="#getting-started">Getting Started</a>' in result

    def test_generate_toc_html_anchor_links(self, converter):
        """Test that TOC entries have correct anchor links for CSS target-counter."""
        headers = [
            {"text": "Chapter 1", "level": 1, "anchor_id": "chapter-1"},
            {"text": "Chapter 2", "level": 1, "anchor_id": "chapter-2"},
            {"text": "Chapter 3", "level": 1, "anchor_id": "chapter-3"},
        ]
        result = converter.generate_toc_html(headers)

        assert '<a href="#chapter-1">Chapter 1</a>' in result
        assert '<a href="#chapter-2">Chapter 2</a>' in result
        assert '<a href="#chapter-3">Chapter 3</a>' in result

    def test_generate_toc_html_escapes_html(self, converter):
        """Test TOC HTML escapes special HTML characters."""
        headers = [
            {"text": "<script>alert('XSS')</script>", "level": 1, "anchor_id": "xss"},
            {"text": "A & B < C > D", "level": 1, "anchor_id": "symbols"}
        ]

        html_output = converter.generate_toc_html(headers)

        # Should have escaped HTML
        assert "&lt;script&gt;" in html_output
        assert "alert('XSS')" not in html_output
        assert "&amp;" in html_output  # Ampersand escaped
        assert "&lt;" in html_output and "&gt;" in html_output


class TestTOCRendering:
    """Tests for TOC rendering in PDF conversion."""

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


class TestTitlePageGeneration:
    """Test title page HTML generation."""

    def test_generate_title_page_basic(self, converter):
        """Test full metadata produces expected HTML."""
        metadata = {'title': 'My Document', 'author': 'John Doe'}
        result = converter.generate_title_page_html(metadata)

        assert '<div class="title-page">' in result
        assert '<h1>My Document</h1>' in result
        assert '<p class="author">John Doe</p>' in result
        assert '<p class="date">' in result
        assert '</div>' in result

    def test_generate_title_page_no_author(self, converter):
        """Test author line omitted when empty."""
        metadata = {'title': 'Solo Doc', 'author': ''}
        result = converter.generate_title_page_html(metadata)

        assert '<h1>Solo Doc</h1>' in result
        assert 'class="author"' not in result
        assert '<p class="date">' in result

    def test_generate_title_page_html_escaping(self, converter):
        """Test XSS prevention via HTML escaping."""
        metadata = {
            'title': '<script>alert("XSS")</script>',
            'author': 'A & B < C',
        }
        result = converter.generate_title_page_html(metadata)

        assert '&lt;script&gt;' in result
        assert '<script>' not in result
        assert '&amp;' in result
        assert '&lt; C' in result

    def test_generate_title_page_no_title_fallback(self, converter):
        """Test falls back to 'Untitled' when title is empty."""
        metadata = {'title': '', 'author': ''}
        result = converter.generate_title_page_html(metadata)

        assert '<h1>Untitled</h1>' in result

    def test_generate_title_page_none_title_fallback(self, converter):
        """Test falls back to 'Untitled' when title is None."""
        metadata = {'title': None, 'author': None}
        result = converter.generate_title_page_html(metadata)

        assert '<h1>Untitled</h1>' in result

    def test_generate_title_page_date_format(self, converter):
        """Test date uses expected strftime format (Month DD, YYYY)."""
        import re

        metadata = {'title': 'Test', 'author': ''}
        result = converter.generate_title_page_html(metadata)

        # Date should match pattern like "February 11, 2026"
        assert re.search(r'[A-Z][a-z]+ \d{2}, \d{4}', result)


class TestTitlePageRendering:
    """Tests for title page rendering in PDF conversion."""

    def test_convert_with_title_page(self, mock_config, tmp_path):
        """Test single file produces valid PDF with title page."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Hello\n\nSome content.")

        output_file = tmp_path / "output.pdf"
        metadata = {'title': 'Test Title', 'author': 'Test Author'}

        converter.convert_file(
            md_file, output_file,
            title_page_enabled=True,
            metadata=metadata,
        )

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_title_page_with_toc(self, mock_config, tmp_path):
        """Test title page + TOC both present."""
        converter = MarkdownConverter(mock_config)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Chapter 1\n\nContent.\n\n# Chapter 2\n\nMore content.")

        output_file = tmp_path / "output.pdf"
        metadata = {'title': 'My Book', 'author': 'Author'}

        converter.convert_file(
            md_file, output_file,
            toc_enabled=True,
            title_page_enabled=True,
            metadata=metadata,
        )

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_merge_with_title_page(self, mock_config, tmp_path):
        """Test merged PDF with title page."""
        converter = MarkdownConverter(mock_config)

        file1 = tmp_path / "a.md"
        file1.write_text("# Part 1\n\nFirst part.")
        file2 = tmp_path / "b.md"
        file2.write_text("# Part 2\n\nSecond part.")

        output_file = tmp_path / "merged.pdf"
        metadata = {'title': 'Merged Doc', 'author': 'Merger'}

        converter.convert_merge(
            [file1, file2],
            output_file,
            title_page_enabled=True,
            metadata=metadata,
        )

        assert output_file.exists()
        assert output_file.stat().st_size > 0
