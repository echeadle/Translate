"""Core markdown to PDF conversion logic."""

from pathlib import Path
from typing import Optional

import markdown
from weasyprint import HTML

from md2pdf.config import Config
from md2pdf.styles import get_default_css
from md2pdf.utils import ensure_directory, find_markdown_files, get_output_path


class MD2PDFError(Exception):
    """Base exception for md2pdf errors."""

    pass


class InvalidMarkdownError(MD2PDFError):
    """Raised when markdown parsing fails."""

    pass


class ConversionError(MD2PDFError):
    """Raised when PDF generation fails."""

    pass


class MarkdownConverter:
    """Convert markdown files to PDF format."""

    def __init__(self, config: Config):
        """Initialize the converter.

        Args:
            config: Configuration settings for PDF generation.
        """
        self.config = config
        self.md = markdown.Markdown(
            extensions=[
                "fenced_code",
                "tables",
                "codehilite",
                "nl2br",
            ]
        )
        self.css = get_default_css(config)

    def convert_file(self, input_path: Path, output_path: Path) -> None:
        """Convert a single markdown file to PDF.

        Args:
            input_path: Path to the input markdown file.
            output_path: Path where the PDF should be saved.

        Raises:
            InvalidMarkdownError: If the markdown file cannot be read or parsed.
            ConversionError: If PDF generation fails.
        """
        try:
            # Read markdown content
            markdown_content = input_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise InvalidMarkdownError(f"File not found: {input_path}")
        except Exception as e:
            raise InvalidMarkdownError(f"Error reading {input_path}: {e}")

        try:
            # Convert markdown to HTML
            html_body = self.md.convert(markdown_content)
            self.md.reset()  # Reset parser state for next conversion

            # Create complete HTML document
            html_doc = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        {self.css}
    </style>
</head>
<body>
    {html_body}
</body>
</html>
"""

            # Generate PDF
            ensure_directory(output_path.parent)
            HTML(string=html_doc).write_pdf(output_path)

        except Exception as e:
            raise ConversionError(f"Error converting {input_path} to PDF: {e}")

    def convert_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        preserve_structure: bool,
    ) -> list[dict]:
        """Convert all markdown files in a directory to PDF.

        Args:
            input_dir: Directory containing markdown files.
            output_dir: Directory where PDFs should be saved.
            preserve_structure: Whether to preserve directory structure.

        Returns:
            List of dictionaries with conversion results:
                [{"input": Path, "output": Path, "success": bool, "error": Optional[str]}]
        """
        markdown_files = find_markdown_files(input_dir)
        results = []

        for md_file in markdown_files:
            output_path = get_output_path(
                md_file,
                input_dir,
                output_dir,
                preserve_structure,
            )

            result = {
                "input": md_file,
                "output": output_path,
                "success": False,
                "error": None,
            }

            try:
                self.convert_file(md_file, output_path)
                result["success"] = True
            except (InvalidMarkdownError, ConversionError) as e:
                result["error"] = str(e)

            results.append(result)

        return results
