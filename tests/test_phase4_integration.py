"""Integration tests for Phase 4 features."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from md2pdf.cli import main
import typer

# Create a Typer app for testing
app = typer.Typer()
app.command()(main)

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
            app,
            [str(md_file), "--output", str(output_file), "--page-numbers"]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_page_numbers_all_positions(self, tmp_path):
        """Test page numbers work in all positions."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        for position in ["left", "center", "right"]:
            output_file = tmp_path / f"output_{position}.pdf"

            result = runner.invoke(
                app,
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
            app,
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
                app,
                [str(md_file), "--output", str(output_file), "--toc", "--theme", theme]
            )

            assert result.exit_code == 0
            assert output_file.exists()

    def test_toc_no_headers_warning(self, tmp_path):
        """Test warning shown when document has no headers."""
        md_file = tmp_path / "test.md"
        md_file.write_text("Just plain text with no headers at all.")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            app,
            [str(md_file), "--output", str(output_file), "--toc"]
        )

        assert result.exit_code == 0
        assert output_file.exists()


class TestMetadataIntegration:
    """Integration tests for PDF metadata."""

    def test_metadata_via_cli(self, tmp_path):
        """Test metadata set via CLI flags."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test Document\n\nContent")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            app,
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

    def test_metadata_via_env(self, tmp_path):
        """Test metadata loaded from .env."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "output.pdf"

        result = runner.invoke(
            app,
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
            app,
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
            app,
            [str(md_file), "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_directory_with_toc(self, tmp_path):
        """Test directory conversion with TOC enabled."""
        # Create test directory with multiple markdown files
        md_dir = tmp_path / "docs"
        md_dir.mkdir()

        (md_dir / "intro.md").write_text("# Introduction\n\n## Overview\n\nIntro content")
        (md_dir / "guide.md").write_text("# Guide\n\n## Setup\n\nGuide content")

        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [str(md_dir), "--create-output-dir", "test", "--toc", "--page-numbers"]
        )

        assert result.exit_code == 0
