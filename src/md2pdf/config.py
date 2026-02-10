"""Configuration management for md2pdf."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration settings for PDF conversion."""

    page_size: str
    margin_top: str
    margin_bottom: str
    margin_left: str
    margin_right: str
    font_family: str
    font_size: str
    code_font: str
    default_output_dir: str
    preserve_structure: bool

    # Page Numbers (Phase 4)
    enable_page_numbers: bool = False
    page_number_position: str = "center"  # left, center, right
    page_number_format: str = "Page {page} of {pages}"

    # PDF Metadata (Phase 4)
    pdf_title: Optional[str] = None
    pdf_author: Optional[str] = None
    pdf_subject: Optional[str] = None
    pdf_keywords: Optional[str] = None

    @classmethod
    def load(cls, env_file: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file. If None, looks for .env in current directory.

        Returns:
            Config instance with loaded settings.
        """
        # Load .env file if it exists
        if env_file:
            load_dotenv(env_file, override=True)
        else:
            load_dotenv()

        # Check for deprecated settings
        deprecated_settings = []
        if os.getenv("PDF_FONT_FAMILY"):
            deprecated_settings.append("PDF_FONT_FAMILY")
        if os.getenv("PDF_CODE_FONT"):
            deprecated_settings.append("PDF_CODE_FONT")
        if os.getenv("PDF_FONT_SIZE"):
            deprecated_settings.append("PDF_FONT_SIZE")

        if deprecated_settings:
            # Import here to avoid circular dependency
            from rich.console import Console

            console = Console()
            console.print(
                f"[yellow]⚠️  Deprecated:[/yellow] {', '.join(deprecated_settings)} "
                f"in .env will be ignored. Use --theme or --css instead."
            )

        # Load page number settings
        enable_page_numbers_str = os.getenv("ENABLE_PAGE_NUMBERS", "false").lower()
        enable_page_numbers = enable_page_numbers_str == "true"

        page_number_position = os.getenv("PAGE_NUMBER_POSITION", "center")
        # Validate position
        valid_positions = ["left", "center", "right"]
        if page_number_position not in valid_positions:
            raise ValueError(
                f"PAGE_NUMBER_POSITION must be one of: {', '.join(valid_positions)}. "
                f"Got: {page_number_position}"
            )

        page_number_format = os.getenv("PAGE_NUMBER_FORMAT", "Page {page} of {pages}")
        # Truncate long format strings
        if len(page_number_format) > 100:
            page_number_format = page_number_format[:100]

        # Load PDF metadata
        pdf_title = os.getenv("PDF_TITLE") or None
        pdf_author = os.getenv("PDF_AUTHOR") or None
        pdf_subject = os.getenv("PDF_SUBJECT") or None
        pdf_keywords = os.getenv("PDF_KEYWORDS") or None

        # Load with defaults (still include deprecated settings in dataclass for backwards compat)
        return cls(
            page_size=os.getenv("PDF_PAGE_SIZE", "A4"),
            margin_top=os.getenv("PDF_MARGIN_TOP", "2cm"),
            margin_bottom=os.getenv("PDF_MARGIN_BOTTOM", "2cm"),
            margin_left=os.getenv("PDF_MARGIN_LEFT", "2cm"),
            margin_right=os.getenv("PDF_MARGIN_RIGHT", "2cm"),
            font_family=os.getenv("PDF_FONT_FAMILY", "Arial, sans-serif"),
            font_size=os.getenv("PDF_FONT_SIZE", "11pt"),
            code_font=os.getenv("PDF_CODE_FONT", "Courier, monospace"),
            default_output_dir=os.getenv("DEFAULT_OUTPUT_DIR", "output"),
            preserve_structure=os.getenv("PRESERVE_DIRECTORY_STRUCTURE", "true").lower()
            == "true",
            enable_page_numbers=enable_page_numbers,
            page_number_position=page_number_position,
            page_number_format=page_number_format,
            pdf_title=pdf_title,
            pdf_author=pdf_author,
            pdf_subject=pdf_subject,
            pdf_keywords=pdf_keywords,
        )

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ValueError: If any configuration value is invalid.
        """
        valid_page_sizes = ["A4", "A3", "A5", "Letter", "Legal"]
        if self.page_size not in valid_page_sizes:
            raise ValueError(
                f"Invalid page size: {self.page_size}. "
                f"Must be one of {', '.join(valid_page_sizes)}"
            )

        # Validate margins have units
        for margin_name, margin_value in [
            ("margin_top", self.margin_top),
            ("margin_bottom", self.margin_bottom),
            ("margin_left", self.margin_left),
            ("margin_right", self.margin_right),
        ]:
            if not any(margin_value.endswith(unit) for unit in ["cm", "mm", "in", "pt", "px"]):
                raise ValueError(
                    f"Invalid {margin_name}: {margin_value}. "
                    "Must include unit (cm, mm, in, pt, px)"
                )
