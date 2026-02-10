# tests/test_page_numbers.py
"""Tests for page number configuration."""

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
