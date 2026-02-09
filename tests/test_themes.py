# tests/test_themes.py
"""Tests for theme loading and management."""

import pytest
from pathlib import Path
from md2pdf.themes import get_theme_css, load_custom_css, AVAILABLE_THEMES


class TestThemeLoading:
    """Tests for get_theme_css function."""

    def test_get_theme_css_success(self, tmp_path):
        """Test successfully loading a theme CSS file."""
        # Create a mock theme CSS file
        themes_dir = Path(__file__).parent.parent / "src" / "md2pdf" / "themes"
        test_css_file = themes_dir / "test_theme.css"
        test_css_content = "body { font-size: 12pt; color: #333; }"

        try:
            # Write test CSS file
            test_css_file.write_text(test_css_content, encoding="utf-8")

            # Temporarily add to AVAILABLE_THEMES
            import md2pdf.themes as themes_module
            themes_module.AVAILABLE_THEMES.append("test_theme")

            # Test loading
            css = get_theme_css("test_theme")

            assert isinstance(css, str)
            assert css == test_css_content
            assert "body" in css

        finally:
            # Cleanup - remove test_theme if it's in the list
            import md2pdf.themes as themes_module
            if "test_theme" in themes_module.AVAILABLE_THEMES:
                themes_module.AVAILABLE_THEMES.remove("test_theme")
            if test_css_file.exists():
                test_css_file.unlink()

    def test_get_theme_css_file_not_found(self):
        """Test that missing CSS file raises FileNotFoundError."""
        # Temporarily add non-existent theme to AVAILABLE_THEMES
        import md2pdf.themes as themes_module
        themes_module.AVAILABLE_THEMES.append("nonexistent")

        try:
            with pytest.raises(FileNotFoundError, match="Theme file not found"):
                get_theme_css("nonexistent")
        finally:
            if "nonexistent" in themes_module.AVAILABLE_THEMES:
                themes_module.AVAILABLE_THEMES.remove("nonexistent")

    def test_get_theme_css_invalid_theme(self):
        """Test loading non-existent theme raises ValueError."""
        with pytest.raises(ValueError, match="Unknown theme 'invalid'"):
            get_theme_css("invalid")

    def test_available_themes_list(self):
        """Test AVAILABLE_THEMES constant."""
        assert "github" in AVAILABLE_THEMES
        assert "minimal" in AVAILABLE_THEMES
        assert "academic" in AVAILABLE_THEMES
        assert "dark" in AVAILABLE_THEMES
        assert "modern" in AVAILABLE_THEMES
        assert len(AVAILABLE_THEMES) == 5


class TestCustomCSS:
    """Tests for load_custom_css function."""

    def test_load_custom_css_success(self, tmp_path):
        """Test loading custom CSS file."""
        css_file = tmp_path / "custom.css"
        css_content = "body { font-size: 12pt; }"
        css_file.write_text(css_content, encoding="utf-8")

        result = load_custom_css(css_file)

        assert result == css_content

    def test_load_custom_css_file_not_found(self, tmp_path):
        """Test loading non-existent CSS file raises FileNotFoundError."""
        css_file = tmp_path / "nonexistent.css"

        with pytest.raises(FileNotFoundError, match="CSS file not found"):
            load_custom_css(css_file)

    def test_load_custom_css_utf8_encoding(self, tmp_path):
        """Test CSS file is read with UTF-8 encoding."""
        css_file = tmp_path / "unicode.css"
        css_content = "/* Comment with unicode: © */ body { }"
        css_file.write_text(css_content, encoding="utf-8")

        result = load_custom_css(css_file)

        assert "©" in result
