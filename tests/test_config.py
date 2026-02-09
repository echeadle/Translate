"""Tests for configuration management."""

import os
from pathlib import Path

import pytest

from md2pdf.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_load_default_config(self, clean_env):
        """Test config loading with no .env file."""
        config = Config.load()

        # Verify defaults
        assert config.page_size == "A4"
        assert config.margin_top == "2cm"
        assert config.margin_bottom == "2cm"
        assert config.margin_left == "2cm"
        assert config.margin_right == "2cm"
        assert config.font_family == "Arial, sans-serif"
        assert config.font_size == "11pt"
        assert config.code_font == "Courier, monospace"
        assert config.default_output_dir == "output"
        assert config.preserve_structure is True

    def test_load_from_env_file(self, tmp_path, clean_env):
        """Test loading custom values from .env file."""
        # Create custom .env
        env_file = tmp_path / ".env"
        env_file.write_text("""
PDF_PAGE_SIZE=Letter
PDF_MARGIN_TOP=1in
PDF_FONT_FAMILY=Times, serif
PDF_FONT_SIZE=12pt
PRESERVE_DIRECTORY_STRUCTURE=false
""")

        # Load config
        config = Config.load(env_file)

        # Verify custom values
        assert config.page_size == "Letter"
        assert config.margin_top == "1in"
        assert config.font_family == "Times, serif"
        assert config.font_size == "12pt"
        assert config.preserve_structure is False

    def test_config_validation(self, mock_config):
        """Test config validation passes for valid config."""
        # Should not raise
        mock_config.validate()

    def test_invalid_page_size(self, mock_config):
        """Test validation catches invalid page size."""
        mock_config.page_size = "INVALID"

        with pytest.raises(ValueError, match="Invalid page size"):
            mock_config.validate()

    def test_invalid_margin_no_unit(self, mock_config):
        """Test validation catches margin without unit."""
        mock_config.margin_top = "2"  # Missing unit

        with pytest.raises(ValueError, match="Invalid margin_top"):
            mock_config.validate()

    @pytest.mark.parametrize("page_size", ["A4", "Letter", "A3", "A5", "Legal"])
    def test_various_page_sizes(self, page_size, mock_config):
        """Test different valid PDF page sizes."""
        mock_config.page_size = page_size
        mock_config.validate()  # Should not raise

    def test_boolean_parsing_true(self, tmp_path, clean_env):
        """Test PRESERVE_DIRECTORY_STRUCTURE parsing for true values."""
        env_file = tmp_path / ".env"
        env_file.write_text("PRESERVE_DIRECTORY_STRUCTURE=true")

        config = Config.load(env_file)
        assert config.preserve_structure is True

    def test_boolean_parsing_false(self, tmp_path, clean_env):
        """Test PRESERVE_DIRECTORY_STRUCTURE parsing for false values."""
        env_file = tmp_path / ".env"
        env_file.write_text("PRESERVE_DIRECTORY_STRUCTURE=false")

        config = Config.load(env_file)
        assert config.preserve_structure is False

    def test_missing_env_falls_back_to_defaults(self, tmp_path, clean_env):
        """Test partial .env file uses defaults for missing values."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_PAGE_SIZE=Letter")  # Only one value

        config = Config.load(env_file)

        # Custom value
        assert config.page_size == "Letter"
        # Defaults for rest
        assert config.margin_top == "2cm"
        assert config.font_family == "Arial, sans-serif"


class TestDeprecationWarnings:
    """Tests for deprecated .env settings."""

    def test_font_family_deprecation_warning(self, tmp_path, clean_env, capsys):
        """Test warning shown for PDF_FONT_FAMILY."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_FONT_FAMILY=Georgia, serif")

        Config.load(env_file)

        captured = capsys.readouterr()
        assert "Deprecated" in captured.out or "deprecated" in captured.out.lower()
        assert "PDF_FONT_FAMILY" in captured.out

    def test_code_font_deprecation_warning(self, tmp_path, clean_env, capsys):
        """Test warning shown for PDF_CODE_FONT."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_CODE_FONT=Monaco, monospace")

        Config.load(env_file)

        captured = capsys.readouterr()
        assert "PDF_CODE_FONT" in captured.out

    def test_font_size_deprecation_warning(self, tmp_path, clean_env, capsys):
        """Test warning shown for PDF_FONT_SIZE."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_FONT_SIZE=14pt")

        Config.load(env_file)

        captured = capsys.readouterr()
        assert "PDF_FONT_SIZE" in captured.out

    def test_multiple_deprecation_warnings(self, tmp_path, clean_env, capsys):
        """Test warning shows all deprecated settings."""
        env_file = tmp_path / ".env"
        env_file.write_text("""PDF_FONT_FAMILY=Georgia
PDF_CODE_FONT=Monaco
PDF_FONT_SIZE=14pt""")

        Config.load(env_file)

        captured = capsys.readouterr()
        assert "PDF_FONT_FAMILY" in captured.out
        assert "PDF_CODE_FONT" in captured.out
        assert "PDF_FONT_SIZE" in captured.out

    def test_no_warning_for_valid_settings(self, tmp_path, clean_env, capsys):
        """Test no warning for non-deprecated settings."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_PAGE_SIZE=A4")

        Config.load(env_file)

        captured = capsys.readouterr()
        # Should not contain deprecation warning
        assert "Deprecated" not in captured.out or captured.out == ""
