"""Targeted tests to increase coverage from 91% to 95%+.

Covers uncovered lines in cli.py and converter.py.
"""

from unittest.mock import patch

import typer
from typer.testing import CliRunner

from md2pdf.cli import main
from md2pdf.converter import ConversionError, InvalidMarkdownError, MarkdownConverter
from md2pdf.config import Config

# Create a Typer app for testing
app = typer.Typer()
app.command()(main)

runner = CliRunner()


class TestCLIEmptyDirectory:
    """Cover cli.py lines 254-255: empty directory."""

    def test_empty_directory_no_markdown_files(self, tmp_path):
        """Directory with no .md files prints warning and exits 0."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        # Put a non-md file so dir isn't empty but has no markdown
        (empty_dir / "readme.txt").write_text("not markdown")

        output_dir = tmp_path / "out"
        output_dir.mkdir()

        result = runner.invoke(
            app, [str(empty_dir), "--output-dir", str(output_dir)]
        )

        assert result.exit_code == 0
        assert "No markdown files found" in result.stdout


class TestCLISingleFileDefaultOutput:
    """Cover cli.py line 201: default output path (no --output flag)."""

    def test_single_file_default_output(self, tmp_path):
        """Without --output, PDF goes next to input file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Hello\n\nWorld")

        result = runner.invoke(app, [str(md_file)])

        expected_pdf = tmp_path / "test.pdf"
        assert result.exit_code == 0
        assert expected_pdf.exists()


class TestCLIOutputDirWarning:
    """Cover cli.py line 190: --output-dir warning in single file mode."""

    def test_output_dir_warning_single_file(self, tmp_path):
        """--output-dir without --create-output-dir shows warning."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            app,
            [str(md_file), "--output", str(output_file), "--output-dir", str(tmp_path / "ignored")],
        )

        assert result.exit_code == 0
        assert "--output-dir is ignored" in result.stdout


class TestCLIOutputWarningDirectoryMode:
    """Cover cli.py line 224: --output warning in directory mode."""

    def test_output_warning_in_directory_mode(self, tmp_path):
        """--output in directory mode shows warning."""
        input_dir = tmp_path / "docs"
        input_dir.mkdir()
        (input_dir / "test.md").write_text("# Test\n\nContent")

        output_dir = tmp_path / "out"
        output_dir.mkdir()

        result = runner.invoke(
            app,
            [
                str(input_dir),
                "--output", str(tmp_path / "ignored.pdf"),
                "--output-dir", str(output_dir),
            ],
        )

        assert result.exit_code == 0
        assert "--output is ignored" in result.stdout


class TestCLIDefaultOutputDir:
    """Cover cli.py line 230: default output directory from config."""

    def test_default_output_dir_from_config(self, tmp_path, monkeypatch):
        """Without --output-dir, uses config default_output_dir."""
        input_dir = tmp_path / "docs"
        input_dir.mkdir()
        (input_dir / "test.md").write_text("# Test\n\nContent")

        # Change working directory so default output dir is relative to tmp_path
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, [str(input_dir)])

        assert result.exit_code == 0
        # Default output dir is "output" per config
        default_out = tmp_path / "output"
        pdf_files = list(default_out.rglob("*.pdf"))
        assert len(pdf_files) >= 1


class TestCLIConfigValidationError:
    """Cover cli.py lines 123-125: Config.validate() raises ValueError."""

    def test_config_validation_error(self, tmp_path):
        """Config validation error exits with code 2."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        with patch("md2pdf.cli.Config.load") as mock_load:
            bad_config = Config(
                page_size="INVALID",
                margin_top="2cm",
                margin_bottom="2cm",
                margin_left="2cm",
                margin_right="2cm",
                font_family="Arial",
                font_size="11pt",
                code_font="Courier",
                default_output_dir="output",
                preserve_structure=True,
            )
            mock_load.return_value = bad_config

            result = runner.invoke(app, [str(md_file)])

        assert result.exit_code == 2
        assert "Configuration error" in result.stdout


class TestConverterFileReadError:
    """Cover converter.py lines 88-89: non-FileNotFoundError read error."""

    def test_file_read_permission_error(self, tmp_path):
        """File with no read permissions raises InvalidMarkdownError."""
        md_file = tmp_path / "noperm.md"
        md_file.write_text("# Test")

        # Remove read permission
        md_file.chmod(0o000)

        config = Config(
            page_size="A4",
            margin_top="2cm",
            margin_bottom="2cm",
            margin_left="2cm",
            margin_right="2cm",
            font_family="Arial",
            font_size="11pt",
            code_font="Courier",
            default_output_dir="output",
            preserve_structure=True,
        )
        converter = MarkdownConverter(config)
        output = tmp_path / "out.pdf"

        try:
            converter.convert_file(md_file, output)
            assert False, "Should have raised InvalidMarkdownError"
        except InvalidMarkdownError as e:
            assert "Error reading" in str(e)
        finally:
            # Restore permissions for cleanup
            md_file.chmod(0o644)


class TestConverterH2InvalidID:
    """Cover converter.py line 356: H2 with invalid/numeric ID."""

    def test_h2_with_numeric_id(self):
        """H2 with numeric-starting ID gets regenerated."""
        config = Config(
            page_size="A4",
            margin_top="2cm",
            margin_bottom="2cm",
            margin_left="2cm",
            margin_right="2cm",
            font_family="Arial",
            font_size="11pt",
            code_font="Courier",
            default_output_dir="output",
            preserve_structure=True,
        )
        converter = MarkdownConverter(config)

        # HTML with H2 that has a numeric-starting ID (invalid per regex)
        html_content = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Test</title>
<style>body { font-size: 11pt; }</style></head>
<body>
<h1 id="valid-h1">Valid H1</h1>
<h2 id="123invalid">Some Section</h2>
</body></html>"""

        headers = converter.extract_headers(html_content, "/tmp")

        # Should have both headers
        assert len(headers) == 2
        # H2 should have regenerated ID (not "123invalid")
        h2 = [h for h in headers if h["level"] == 2][0]
        assert h2["anchor_id"] != "123invalid"
        assert h2["anchor_id"] == "some-section"


class TestCLISingleFileConversionError:
    """Cover cli.py lines 217-219: conversion error in single file mode."""

    def test_single_file_conversion_error(self, tmp_path):
        """Conversion error in single file mode exits with code 1."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent")

        output_file = tmp_path / "test.pdf"

        with patch("md2pdf.cli.MarkdownConverter.convert_file") as mock_convert:
            mock_convert.side_effect = ConversionError("Mock conversion failure")

            result = runner.invoke(
                app, [str(md_file), "--output", str(output_file)]
            )

        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestCLIDirectoryMixedResults:
    """Cover cli.py lines 271-272, 293-298: mixed success/failure."""

    def test_directory_partial_failure(self, tmp_path):
        """Some files fail, some succeed: exit code 1, partial message."""
        input_dir = tmp_path / "docs"
        input_dir.mkdir()
        (input_dir / "good.md").write_text("# Good\n\nThis works fine.")
        (input_dir / "bad.md").write_text("# Bad\n\nThis will fail.")

        output_dir = tmp_path / "out"
        output_dir.mkdir()

        original_convert = MarkdownConverter.convert_file

        def selective_fail(self, input_path, output_path, **kwargs):
            if "bad" in input_path.name:
                raise ConversionError(f"Simulated failure for {input_path}")
            return original_convert(self, input_path, output_path, **kwargs)

        with patch.object(MarkdownConverter, "convert_file", selective_fail):
            result = runner.invoke(
                app, [str(input_dir), "--output-dir", str(output_dir)]
            )

        assert result.exit_code == 1
        assert "Converted" in result.stdout or "failed" in result.stdout


class TestCLIDirectoryAllFail:
    """Cover cli.py lines 290-292: all files fail."""

    def test_directory_all_fail(self, tmp_path):
        """All files fail: exit code 2."""
        input_dir = tmp_path / "docs"
        input_dir.mkdir()
        (input_dir / "a.md").write_text("# A\n\nContent")
        (input_dir / "b.md").write_text("# B\n\nContent")

        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch.object(
            MarkdownConverter,
            "convert_file",
            side_effect=ConversionError("All fail"),
        ):
            result = runner.invoke(
                app, [str(input_dir), "--output-dir", str(output_dir)]
            )

        assert result.exit_code == 2
        assert "Failed to convert all" in result.stdout
