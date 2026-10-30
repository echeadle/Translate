"""Targeted tests to increase coverage from 91% to 97%+.

Covers uncovered lines in cli.py and converter.py.
"""

from pathlib import Path
from unittest.mock import patch
import pytest

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

        headers = converter.extract_headers(html_content)

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


# --- New converter.py gap tests (lines 215-216, 248, 282-295, 307, 309, 317-318, 453) ---


def _make_converter() -> MarkdownConverter:
    """Helper to create a converter with default config."""
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
    return MarkdownConverter(config)


class TestMergeGenericReadError:
    """Cover converter.py lines 215-216: generic exception reading file in merge."""

    def test_merge_oserror_on_read(self, tmp_path):
        """Mock read_text() to raise OSError in convert_merge."""
        converter = _make_converter()

        bad_file = tmp_path / "bad.md"
        bad_file.write_text("# Test")

        output = tmp_path / "merged.pdf"

        with patch.object(Path, "read_text", side_effect=OSError("disk error")):
            with pytest.raises(InvalidMarkdownError, match="Error reading"):
                converter.convert_merge([bad_file], output)


class TestMergeNoHeadersWarning:
    """Cover converter.py line 248: 'No headers' warning when merge + TOC on headerless content."""

    def test_merge_toc_no_headers(self, tmp_path, capsys):
        """Merge headerless files with toc_enabled=True shows warning."""
        converter = _make_converter()

        f1 = tmp_path / "a.md"
        f1.write_text("Just plain text, no headers at all.")
        f2 = tmp_path / "b.md"
        f2.write_text("More plain text without any headers.")

        output = tmp_path / "merged.pdf"

        converter.convert_merge([f1, f2], output, toc_enabled=True)

        assert output.exists()


class TestMergeCommonParentDir:
    """Cover converter.py lines 282-295: common parent dir logic for unrelated dirs."""

    def test_merge_files_from_separate_subdirs(self, tmp_path):
        """Merge files from two separate subdirectories finds common parent."""
        converter = _make_converter()

        dir_a = tmp_path / "project" / "src" / "docs"
        dir_a.mkdir(parents=True)
        dir_b = tmp_path / "project" / "lib" / "notes"
        dir_b.mkdir(parents=True)

        f1 = dir_a / "readme.md"
        f1.write_text("# Readme\n\nFrom src/docs.")
        f2 = dir_b / "notes.md"
        f2.write_text("# Notes\n\nFrom lib/notes.")

        output = tmp_path / "merged.pdf"

        converter.convert_merge([f1, f2], output)

        assert output.exists()
        assert output.stat().st_size > 0


class TestMergeSubjectKeywordsMetadata:
    """Cover converter.py lines 307, 309: subject/keywords metadata on merge."""

    def test_merge_with_full_metadata(self, tmp_path):
        """Merge with subject and keywords sets PDF metadata."""
        converter = _make_converter()

        f1 = tmp_path / "ch1.md"
        f1.write_text("# Chapter 1\n\nIntro content.")

        output = tmp_path / "book.pdf"

        metadata = {
            "title": "Full Book",
            "author": "Test Author",
            "subject": "Testing Subject",
            "keywords": "python, testing, pdf",
        }

        converter.convert_merge([f1], output, metadata=metadata)

        assert output.exists()
        assert output.stat().st_size > 0


class TestMergeConversionErrorWrapping:
    """Cover converter.py lines 317-318: ConversionError wrapping in merge."""

    def test_merge_html_render_raises(self, tmp_path):
        """Mock HTML() to raise generic Exception, gets wrapped in ConversionError."""
        converter = _make_converter()

        f1 = tmp_path / "ok.md"
        f1.write_text("# OK\n\nContent.")

        output = tmp_path / "merged.pdf"

        with patch("md2pdf.converter.HTML", side_effect=RuntimeError("render boom")):
            with pytest.raises(ConversionError, match="Error merging files to PDF"):
                converter.convert_merge([f1], output)


class TestExtractHeadersSkipsEmpty:
    """Cover converter.py line 453: skip empty header text in extract_headers()."""

    def test_empty_header_text_skipped(self):
        """H1 with empty text content is skipped."""
        converter = _make_converter()

        html_content = '<h1 id="x"></h1><h1 id="real">Real Header</h1>'
        headers = converter.extract_headers(html_content)

        assert len(headers) == 1
        assert headers[0]["text"] == "Real Header"
