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

        # Load with defaults
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
