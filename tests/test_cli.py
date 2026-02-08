"""Tests for CLI interface."""

from pathlib import Path

import typer
from typer.testing import CliRunner

from md2pdf.cli import main


# Create a Typer app for testing
app = typer.Typer()
app.command()(main)

runner = CliRunner()


class TestCLI:
    """Tests for CLI interface."""

    def test_single_file_conversion(self, tmp_path, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md"""
        input_file = sample_markdown_files["simple"]
        output_file = temp_workspace / "output" / "simple.pdf"

        # Run CLI
        result = runner.invoke(app, [str(input_file), "--output", str(output_file)])

        # Verify success
        assert result.exit_code == 0
        assert output_file.exists()

    def test_create_output_dir_auto(self, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md --create-output-dir auto"""
        input_file = sample_markdown_files["simple"]
        output_base = temp_workspace / "output"

        result = runner.invoke(
            app,
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

    def test_create_output_dir_named(self, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md --create-output-dir mypdfs"""
        input_file = sample_markdown_files["simple"]
        output_base = temp_workspace / "output"

        result = runner.invoke(
            app,
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
            app,
            [str(input_dir), "--output-dir", str(output_dir)]
        )

        assert result.exit_code == 0

        # Multiple PDFs should be created
        pdf_files = list(output_dir.rglob("*.pdf"))
        assert len(pdf_files) >= 3  # At least simple, tables, code_blocks

    def test_preserve_structure(self, temp_workspace, sample_markdown_files):
        """Test: md2pdf docs/ --preserve-structure"""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        # Verify nested subdoc file exists
        nested_file = input_dir / "nested" / "subdoc.md"
        assert nested_file.exists()

        result = runner.invoke(
            app,
            [str(input_dir), "--output-dir", str(output_dir), "--preserve-structure"]
        )

        assert result.exit_code == 0

        # Nested structure should be preserved
        nested_pdf = output_dir / "nested" / "subdoc.pdf"
        assert nested_pdf.exists()

    def test_no_preserve_structure(self, temp_workspace, sample_markdown_files):
        """Test: md2pdf docs/ --no-preserve-structure"""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        result = runner.invoke(
            app,
            [str(input_dir), "--output-dir", str(output_dir), "--no-preserve-structure"]
        )

        assert result.exit_code == 0

        # All PDFs should be in root output directory
        pdf_files = list(output_dir.glob("*.pdf"))
        assert len(pdf_files) >= 3

        # No nested directories
        nested_pdfs = list(output_dir.rglob("*/*.pdf"))
        assert len(nested_pdfs) == 0

    def test_custom_output_path(self, sample_markdown_files, temp_workspace):
        """Test: md2pdf file.md --output custom.pdf"""
        input_file = sample_markdown_files["simple"]
        custom_output = temp_workspace / "custom_name.pdf"

        result = runner.invoke(
            app,
            [str(input_file), "--output", str(custom_output)]
        )

        assert result.exit_code == 0
        assert custom_output.exists()

    def test_nonexistent_input_file(self, temp_workspace):
        """Test error handling for missing input."""
        nonexistent = temp_workspace / "nonexistent.md"

        result = runner.invoke(app, [str(nonexistent)])

        # Should exit with error
        assert result.exit_code != 0
        # Typer's exists=True outputs to stderr or has error message
        output = (result.stdout + result.stderr).lower()
        assert "not found" in output or "error" in output or "does not exist" in output

    def test_invalid_input_directory(self, temp_workspace):
        """Test non-existent directory input."""
        nonexistent_dir = temp_workspace / "nonexistent_dir"

        result = runner.invoke(app, [str(nonexistent_dir)])

        assert result.exit_code != 0

    def test_help_command(self):
        """Test: md2pdf --help"""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Usage" in result.stdout or "Options" in result.stdout
        assert "--output" in result.stdout
        assert "--create-output-dir" in result.stdout
