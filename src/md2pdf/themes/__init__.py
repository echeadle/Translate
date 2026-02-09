# src/md2pdf/themes/__init__.py
"""Theme management for md2pdf."""

from pathlib import Path

AVAILABLE_THEMES = ["github", "minimal", "academic", "dark", "modern"]


def get_theme_css(theme_name: str) -> str:
    """Load CSS for built-in theme.

    Args:
        theme_name: Name of built-in theme.

    Returns:
        CSS string for the theme.

    Raises:
        ValueError: If theme doesn't exist.
    """
    if theme_name not in AVAILABLE_THEMES:
        raise ValueError(
            f"Unknown theme '{theme_name}'. "
            f"Available: {', '.join(AVAILABLE_THEMES)}"
        )

    theme_file = Path(__file__).parent / f"{theme_name}.css"

    if not theme_file.exists():
        raise FileNotFoundError(f"Theme file not found: {theme_file}")

    return theme_file.read_text(encoding="utf-8")


def load_custom_css(css_path: Path) -> str:
    """Load custom CSS file.

    Args:
        css_path: Path to custom CSS file.

    Returns:
        CSS string from file.

    Raises:
        FileNotFoundError: If CSS file doesn't exist.
    """
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {css_path}")

    return css_path.read_text(encoding="utf-8")
