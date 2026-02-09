"""PDF styling and CSS generation."""

from md2pdf.config import Config


def get_page_css(config: Config) -> str:
    """Generate @page CSS from config.

    Returns only page setup, not visual styling.

    Args:
        config: Configuration with page setup values.

    Returns:
        CSS string for @page rules.
    """
    return f"""
@page {{
    size: {config.page_size};
    margin-top: {config.margin_top};
    margin-bottom: {config.margin_bottom};
    margin-left: {config.margin_left};
    margin-right: {config.margin_right};
}}
"""


def get_default_css(config: Config) -> str:
    """Generate default CSS for PDF styling.

    DEPRECATED: Use get_page_css() + theme CSS instead.
    Kept for backwards compatibility.

    Args:
        config: Configuration settings for styling.

    Returns:
        CSS string with complete styling rules.
    """
    from md2pdf.themes import get_theme_css

    # Combine page setup with github theme for backwards compatibility
    page_css = get_page_css(config)
    theme_css = get_theme_css('github')

    # Replace hardcoded fonts in theme with config values for backwards compatibility
    theme_css = theme_css.replace(
        'font-family: Arial, sans-serif;',
        f'font-family: {config.font_family};'
    )
    theme_css = theme_css.replace(
        'font-size: 11pt;',
        f'font-size: {config.font_size};'
    )
    theme_css = theme_css.replace(
        'font-family: Courier, monospace;',
        f'font-family: {config.code_font};'
    )

    return page_css + "\n" + theme_css
