"""Tests for PDF styling and CSS generation."""

import pytest

from md2pdf.styles import get_default_css


class TestStyles:
    """Tests for get_default_css function."""

    def test_get_default_css(self, mock_config):
        """Test CSS generation with default config."""
        css = get_default_css(mock_config)

        # Verify CSS is generated
        assert isinstance(css, str)
        assert len(css) > 0

        # Check for key CSS components
        assert "@page" in css
        assert "body" in css
        assert "code" in css
        assert "table" in css

    def test_css_with_custom_fonts(self, mock_config):
        """Test CSS generation with custom font settings."""
        mock_config.font_family = "Georgia, serif"
        mock_config.code_font = "Monaco, monospace"

        css = get_default_css(mock_config)

        # Verify custom fonts in CSS
        assert "Georgia, serif" in css
        assert "Monaco, monospace" in css

    def test_css_with_custom_margins(self, mock_config):
        """Test CSS generation with custom margins."""
        mock_config.margin_top = "3cm"
        mock_config.margin_bottom = "3cm"
        mock_config.margin_left = "2.5cm"
        mock_config.margin_right = "2.5cm"

        css = get_default_css(mock_config)

        # Verify margins in @page rule
        assert "margin-top: 3cm" in css or "margin: 3cm" in css

    def test_css_with_custom_font_size(self, mock_config):
        """Test CSS generation with custom font size."""
        mock_config.font_size = "14pt"

        css = get_default_css(mock_config)

        assert "14pt" in css

    def test_css_includes_code_styling(self, mock_config):
        """Test code block styles present."""
        css = get_default_css(mock_config)

        # Code blocks should have background
        assert "pre" in css or "code" in css
        assert "#f6f8fa" in css or "background" in css

    def test_css_includes_table_styling(self, mock_config):
        """Test table styles present."""
        css = get_default_css(mock_config)

        # Tables should have styling
        assert "table" in css
        assert "border" in css

    def test_css_includes_header_styling(self, mock_config):
        """Test header styles present for h1-h6."""
        css = get_default_css(mock_config)

        # Headers should be styled
        assert "h1" in css
        assert "h2" in css

    @pytest.mark.parametrize("size,expected", [
        ("A4", "A4"),
        ("Letter", "Letter"),
        ("A3", "A3"),
    ])
    def test_page_size_in_css(self, size, expected, mock_config):
        """Test different page sizes appear in CSS."""
        mock_config.page_size = size

        css = get_default_css(mock_config)

        # Page size should appear in @page rule
        assert expected in css
        assert "@page" in css

    def test_css_configuration_injection(self, mock_config):
        """Test all config values properly injected into CSS."""
        # Set all custom values
        mock_config.page_size = "Letter"
        mock_config.margin_top = "1in"
        mock_config.font_family = "Helvetica, sans-serif"
        mock_config.font_size = "10pt"
        mock_config.code_font = "Consolas, monospace"

        css = get_default_css(mock_config)

        # All values should appear
        assert "Letter" in css
        assert "1in" in css
        assert "Helvetica, sans-serif" in css
        assert "10pt" in css
        assert "Consolas, monospace" in css
