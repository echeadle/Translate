"""Core markdown to PDF conversion logic."""

import html
from pathlib import Path
from typing import Dict, Optional

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

    def __init__(self, config: Config, css: Optional[str] = None):
        """Initialize the converter.

        Args:
            config: Configuration settings for PDF generation.
            css: Optional complete CSS string (page + styling). If None, uses default.
        """
        self.config = config
        # Store base extensions; create Markdown instance per file
        self.base_extensions = [
            "fenced_code",
            "tables",
            "codehilite",
            "nl2br",
        ]

        # Use provided CSS or generate default
        if css is not None:
            self.css = css
        else:
            # Backwards compatibility: generate default CSS
            self.css = get_default_css(config)

    def convert_file(
        self,
        input_path: Path,
        output_path: Path,
        metadata: Optional[Dict[str, Optional[str]]] = None
    ) -> None:
        """Convert a single markdown file to PDF.

        Args:
            input_path: Path to the input markdown file.
            output_path: Path where the PDF should be saved.
            metadata: Optional PDF metadata dict (title, author, subject, keywords).

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
            # Create markdown instance with image extension
            from md2pdf.image_extension import ImagePathExtension

            image_ext = ImagePathExtension(source_file=input_path)

            # Combine base extensions with the image extension
            all_extensions = self.base_extensions.copy()
            all_extensions.append(image_ext)

            md = markdown.Markdown(
                extensions=all_extensions,
                extension_configs={},
            )

            # Convert markdown to HTML
            html_body = md.convert(markdown_content)
            md.reset()  # Reset parser state

            # Build PDF metadata dict with smart defaults
            pdf_metadata = {}

            if metadata:
                # Use provided metadata or fall back to filename for title
                pdf_metadata['title'] = metadata.get('title') or input_path.stem
                pdf_metadata['author'] = metadata.get('author') or ''
                pdf_metadata['subject'] = metadata.get('subject') or ''
                pdf_metadata['keywords'] = metadata.get('keywords') or ''
            else:
                # Default title to filename
                pdf_metadata['title'] = input_path.stem
                pdf_metadata['author'] = ''
                pdf_metadata['subject'] = ''
                pdf_metadata['keywords'] = ''

            # Create complete HTML document
            html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{html.escape(pdf_metadata['title'], quote=True)}</title>
    <style>
        {self.css}
    </style>
</head>
<body>
    {html_body}
</body>
</html>
"""

            # Generate PDF with metadata using Document API
            ensure_directory(output_path.parent)
            document = HTML(string=html_doc, base_url=str(input_path.parent)).render()

            # Set PDF metadata on document
            document.metadata.title = pdf_metadata['title']
            if pdf_metadata.get('author'):
                document.metadata.authors = [pdf_metadata['author']]
            if pdf_metadata.get('subject'):
                document.metadata.description = pdf_metadata['subject']
            if pdf_metadata.get('keywords'):
                document.metadata.keywords = [kw.strip() for kw in pdf_metadata['keywords'].split(',')]

            document.write_pdf(output_path)

        except InvalidMarkdownError:
            # Re-raise validation errors (including missing images)
            raise
        except Exception as e:
            raise ConversionError(f"Error converting {input_path} to PDF: {e}")

    def convert_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        preserve_structure: bool,
        metadata: Optional[Dict[str, Optional[str]]] = None,
    ) -> list[dict]:
        """Convert all markdown files in a directory to PDF.

        Args:
            input_dir: Directory containing markdown files.
            output_dir: Directory where PDFs should be saved.
            preserve_structure: Whether to preserve directory structure.
            metadata: Optional PDF metadata dict (title, author, subject, keywords).

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
                self.convert_file(md_file, output_path, metadata=metadata)
                result["success"] = True
            except (InvalidMarkdownError, ConversionError) as e:
                result["error"] = str(e)

            results.append(result)

        return results
