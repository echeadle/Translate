"""PDF styling and CSS generation."""

from md2pdf.config import Config


def _escape_css_string(text: str) -> str:
    """Escape special characters for CSS string literals.

    Args:
        text: Text to escape.

    Returns:
        Escaped text safe for CSS string literals.
    """
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def get_page_number_css(config: Config) -> str:
    """Generate CSS for page numbers in headers/footers.

    Args:
        config: Configuration with page number settings.

    Returns:
        CSS string for @page margin boxes, or empty string if disabled.
    """
    if not config.enable_page_numbers:
        return ""

    # Map position to CSS margin box
    position_map = {
        "left": "@bottom-left",
        "center": "@bottom-center",
        "right": "@bottom-right",
    }

    if config.page_number_position not in position_map:
        raise ValueError(
            f"Invalid page_number_position: {config.page_number_position}. "
            f"Must be one of: {', '.join(position_map.keys())}"
        )
    margin_box = position_map[config.page_number_position]

    # Convert format string to CSS content
    # Split by placeholders and build content string
    content_parts = []
    remaining = config.page_number_format

    while remaining:
        if "{page}" in remaining:
            before, after = remaining.split("{page}", 1)
            if before:
                content_parts.append(f'"{_escape_css_string(before)}"')
            content_parts.append('counter(page)')
            remaining = after
        elif "{pages}" in remaining:
            before, after = remaining.split("{pages}", 1)
            if before:
                content_parts.append(f'"{_escape_css_string(before)}"')
            content_parts.append('counter(pages)')
            remaining = after
        else:
            # No more placeholders
            if remaining:
                content_parts.append(f'"{_escape_css_string(remaining)}"')
            break

    content_value = " ".join(content_parts)

    return f"""
    {margin_box} {{
        content: {content_value};
        font-size: 9pt;
        color: #666;
        font-family: Arial, sans-serif;
    }}
    """


def get_page_css(config: Config) -> str:
    """Generate @page CSS from config.

    Returns only page setup and page numbers.

    Args:
        config: Configuration with page setup values.

    Returns:
        CSS string for @page rules.
    """
    page_number_css = get_page_number_css(config)

    return f"""
@page {{
    size: {config.page_size};
    margin-top: {config.margin_top};
    margin-bottom: {config.margin_bottom};
    margin-left: {config.margin_left};
    margin-right: {config.margin_right};
{page_number_css}
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
