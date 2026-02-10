# tests/test_phase4_config.py
"""Tests for Phase 4 configuration (page numbers and metadata)."""

import os
import pytest
from pathlib import Path
from md2pdf.config import Config


class TestPageNumbersConfig:
    """Tests for page numbers configuration loading."""

    def test_default_page_numbers_disabled(self, clean_env, tmp_path):
        """Test page numbers disabled by default."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.enable_page_numbers is False

    def test_enable_page_numbers_true(self, clean_env, tmp_path):
        """Test enabling page numbers via .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("ENABLE_PAGE_NUMBERS=true\n")

        config = Config.load(env_file)

        assert config.enable_page_numbers is True

    def test_enable_page_numbers_false(self, clean_env, tmp_path):
        """Test explicitly disabling page numbers."""
        env_file = tmp_path / ".env"
        env_file.write_text("ENABLE_PAGE_NUMBERS=false\n")

        config = Config.load(env_file)

        assert config.enable_page_numbers is False

    def test_page_number_position_default(self, clean_env, tmp_path):
        """Test default page number position is center."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.page_number_position == "center"

    def test_page_number_position_left(self, clean_env, tmp_path):
        """Test setting position to left."""
        env_file = tmp_path / ".env"
        env_file.write_text("PAGE_NUMBER_POSITION=left\n")

        config = Config.load(env_file)

        assert config.page_number_position == "left"

    def test_page_number_position_right(self, clean_env, tmp_path):
        """Test setting position to right."""
        env_file = tmp_path / ".env"
        env_file.write_text("PAGE_NUMBER_POSITION=right\n")

        config = Config.load(env_file)

        assert config.page_number_position == "right"

    def test_page_number_position_invalid(self, clean_env, tmp_path):
        """Test invalid position raises error."""
        env_file = tmp_path / ".env"
        env_file.write_text("PAGE_NUMBER_POSITION=invalid\n")

        with pytest.raises(ValueError, match="PAGE_NUMBER_POSITION must be one of"):
            Config.load(env_file)

    def test_page_number_format_default(self, clean_env, tmp_path):
        """Test default page number format."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.page_number_format == "Page {page} of {pages}"

    def test_page_number_format_custom(self, clean_env, tmp_path):
        """Test custom page number format."""
        env_file = tmp_path / ".env"
        env_file.write_text('PAGE_NUMBER_FORMAT={page}/{pages}\n')

        config = Config.load(env_file)

        assert config.page_number_format == "{page}/{pages}"

    def test_page_number_format_truncated(self, clean_env, tmp_path):
        """Test long format string is truncated."""
        env_file = tmp_path / ".env"
        long_format = "x" * 150
        env_file.write_text(f'PAGE_NUMBER_FORMAT={long_format}\n')

        config = Config.load(env_file)

        assert len(config.page_number_format) == 100


class TestMetadataConfig:
    """Tests for PDF metadata configuration."""

    def test_metadata_defaults_empty(self, clean_env, tmp_path):
        """Test metadata fields default to None/empty."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        config = Config.load(env_file)

        assert config.pdf_title is None
        assert config.pdf_author is None
        assert config.pdf_subject is None
        assert config.pdf_keywords is None

    def test_metadata_title_loaded(self, clean_env, tmp_path):
        """Test loading title from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_TITLE=My Document\n")

        config = Config.load(env_file)

        assert config.pdf_title == "My Document"

    def test_metadata_author_loaded(self, clean_env, tmp_path):
        """Test loading author from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_AUTHOR=Jane Doe\n")

        config = Config.load(env_file)

        assert config.pdf_author == "Jane Doe"

    def test_metadata_subject_loaded(self, clean_env, tmp_path):
        """Test loading subject from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_SUBJECT=Technical Documentation\n")

        config = Config.load(env_file)

        assert config.pdf_subject == "Technical Documentation"

    def test_metadata_keywords_loaded(self, clean_env, tmp_path):
        """Test loading keywords from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("PDF_KEYWORDS=markdown, pdf, documentation\n")

        config = Config.load(env_file)

        assert config.pdf_keywords == "markdown, pdf, documentation"

    def test_metadata_all_fields(self, clean_env, tmp_path):
        """Test loading all metadata fields together."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
PDF_TITLE=User Guide
PDF_AUTHOR=Jane Doe
PDF_SUBJECT=Product Documentation
PDF_KEYWORDS=guide, manual, help
""")

        config = Config.load(env_file)

        assert config.pdf_title == "User Guide"
        assert config.pdf_author == "Jane Doe"
        assert config.pdf_subject == "Product Documentation"
        assert config.pdf_keywords == "guide, manual, help"
