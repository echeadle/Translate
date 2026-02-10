"""Core markdown to PDF conversion logic."""

import html
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import markdown
from weasyprint import HTML
from rich.console import Console

from md2pdf.config import Config
from md2pdf.styles import get_default_css
from md2pdf.utils import ensure_directory, find_markdown_files, get_output_path

console = Console()


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
            "toc",  # Adds IDs to headers for TOC generation
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
        toc_enabled: bool = False,
        metadata: Optional[Dict[str, Optional[str]]] = None
    ) -> None:
        """Convert a single markdown file to PDF.

        Args:
            input_path: Path to the input markdown file.
            output_path: Path where the PDF should be saved.
            toc_enabled: Whether to generate a table of contents from H1/H2 headers.
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

            # Two-pass rendering if TOC enabled
            if toc_enabled:
                # Pass 1: Create initial HTML to extract headers
                html_doc_pass1 = f"""<!DOCTYPE html>
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
                # Extract headers with page numbers
                headers = self.extract_headers(html_doc_pass1, str(input_path.parent))

                if not headers:
                    console.print("[yellow]Warning:[/yellow] No H1/H2 headers found for TOC")
                else:
                    # Pass 2: Generate and prepend TOC
                    toc_html = self.generate_toc_html(headers)
                    html_body = toc_html + html_body

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
        toc_enabled: bool = False,
        metadata: Optional[Dict[str, Optional[str]]] = None,
    ) -> list[dict]:
        """Convert all markdown files in a directory to PDF.

        Args:
            input_dir: Directory containing markdown files.
            output_dir: Directory where PDFs should be saved.
            preserve_structure: Whether to preserve directory structure.
            toc_enabled: Whether to generate a table of contents from H1/H2 headers.
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
                self.convert_file(md_file, output_path, toc_enabled=toc_enabled, metadata=metadata)
                result["success"] = True
            except (InvalidMarkdownError, ConversionError) as e:
                result["error"] = str(e)

            results.append(result)

        return results

    def generate_anchor_id(self, text: str, seen_ids: Set[str]) -> str:
        """Generate unique anchor ID from heading text.

        Args:
            text: Heading text to convert to anchor ID.
            seen_ids: Set of already-used IDs to avoid duplicates.

        Returns:
            Unique anchor ID string.
        """
        # Convert to lowercase
        base_id = text.lower()

        # Replace spaces with hyphens
        base_id = base_id.replace(" ", "-")

        # Remove special characters (keep only alphanumeric and hyphens)
        base_id = re.sub(r'[^a-z0-9-]', '', base_id)

        # Remove consecutive hyphens
        base_id = re.sub(r'-+', '-', base_id)

        # Remove leading/trailing hyphens
        base_id = base_id.strip('-')

        # Handle empty result
        if not base_id:
            base_id = "heading"

        # Handle duplicates
        if base_id not in seen_ids:
            seen_ids.add(base_id)
            return base_id

        # Append counter for duplicates
        counter = 2
        while f"{base_id}-{counter}" in seen_ids:
            counter += 1

        unique_id = f"{base_id}-{counter}"
        seen_ids.add(unique_id)
        return unique_id

    def extract_headers(self, html_content: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract H1 and H2 headers with page numbers from rendered PDF.

        Args:
            html_content: HTML content to render.
            base_url: Base URL for resolving relative paths.

        Returns:
            List of dicts with keys: text, level, page, anchor_id
        """
        from weasyprint import HTML
        import re as regex

        headers = []
        seen_ids = set()

        try:
            # Parse HTML to extract header elements with their IDs using regex
            # Match H1 and H2 tags - capture content regardless of attribute order
            h1_pattern = r'<h1\b[^>]*>(.*?)</h1>'
            h2_pattern = r'<h2\b[^>]*>(.*?)</h2>'
            # Pattern to extract id attribute from any position in tag
            id_pattern = r'\bid="([^"]*)"'

            header_elements = []

            # Find all H1 headers
            for match in regex.finditer(h1_pattern, html_content, regex.IGNORECASE | regex.DOTALL):
                # Extract the full opening tag to find id attribute
                # match.start() points to '<h1', find the end of opening tag '>'
                tag_end = html_content.find('>', match.start())
                opening_tag = html_content[match.start():tag_end+1]

                # Extract id attribute if present
                id_match = regex.search(id_pattern, opening_tag)
                anchor_id = id_match.group(1).strip() if id_match else ''

                # Get header text (remove HTML tags)
                text = regex.sub(r'<[^>]+>', '', match.group(1)).strip()

                if text:
                    # Validate ID format (must start with letter, contain only alphanumeric, underscore, hyphen)
                    if anchor_id and regex.match(r'^[a-zA-Z][\w\-]*$', anchor_id):
                        seen_ids.add(anchor_id)
                    else:
                        # Invalid or missing ID - generate new one
                        anchor_id = self.generate_anchor_id(text, seen_ids)

                    header_elements.append({
                        'text': text,
                        'level': 1,
                        'anchor_id': anchor_id
                    })

            # Find all H2 headers
            for match in regex.finditer(h2_pattern, html_content, regex.IGNORECASE | regex.DOTALL):
                # Extract the full opening tag to find id attribute
                # match.start() points to '<h2', find the end of opening tag '>'
                tag_end = html_content.find('>', match.start())
                opening_tag = html_content[match.start():tag_end+1]

                # Extract id attribute if present
                id_match = regex.search(id_pattern, opening_tag)
                anchor_id = id_match.group(1).strip() if id_match else ''

                # Get header text (remove HTML tags)
                text = regex.sub(r'<[^>]+>', '', match.group(1)).strip()

                if text:
                    # Validate ID format (must start with letter, contain only alphanumeric, underscore, hyphen)
                    if anchor_id and regex.match(r'^[a-zA-Z][\w\-]*$', anchor_id):
                        seen_ids.add(anchor_id)
                    else:
                        # Invalid or missing ID - generate new one
                        anchor_id = self.generate_anchor_id(text, seen_ids)

                    header_elements.append({
                        'text': text,
                        'level': 2,
                        'anchor_id': anchor_id
                    })

            if not header_elements:
                return []

            # Render PDF to get page numbers from bookmarks
            document = HTML(string=html_content, base_url=base_url)
            rendered = document.render()

            # Try to get bookmarks for page numbers
            try:
                bookmarks = rendered.make_bookmark_tree()
                bookmark_pages = {}

                # Build a map of bookmark labels to page numbers
                for bookmark in bookmarks:
                    if bookmark.destination:
                        # destination is (page_number, x, y)
                        page_num = bookmark.destination[0]
                        bookmark_pages[bookmark.label] = page_num

                # Match headers with bookmark pages
                for header_info in header_elements:
                    # Try to find matching bookmark by text
                    page = bookmark_pages.get(header_info['text'], 1)

                    headers.append({
                        'text': header_info['text'],
                        'level': header_info['level'],
                        'page': page,
                        'anchor_id': header_info['anchor_id'],
                    })
            except (AttributeError, ValueError, RuntimeError) as e:
                # Fallback: assign page 1 if bookmarks don't work
                console.print(f"[yellow]Warning:[/yellow] Could not extract bookmarks: {e}")
                for header_info in header_elements:
                    headers.append({
                        'text': header_info['text'],
                        'level': header_info['level'],
                        'page': 1,  # Default to page 1 if we can't determine
                        'anchor_id': header_info['anchor_id'],
                    })

        except (ValueError, AttributeError, RuntimeError) as e:
            # If extraction fails, return empty list
            # (TOC generation will be skipped)
            console.print(f"[yellow]Warning:[/yellow] Could not extract headers: {e}")
            return []

        return headers

    def generate_toc_html(self, headers: List[Dict[str, Any]]) -> str:
        """Generate HTML for table of contents.

        Args:
            headers: List of header dicts from extract_headers().
                Each dict has keys: text, level, page, anchor_id

        Returns:
            HTML string for TOC, or empty string if no headers.
        """
        if not headers:
            return ""

        toc_html = '<div class="toc">\n'
        toc_html += '    <h1>Table of Contents</h1>\n'
        toc_html += '    <ul>\n'

        for header in headers:
            css_class = f"toc-h{header['level']}"
            toc_html += f'        <li class="{css_class}">\n'
            toc_html += f'            <a href="#{header["anchor_id"]}">{html.escape(header["text"])}</a>\n'
            toc_html += f'            <span class="toc-page">{html.escape(str(header["page"]))}</span>\n'
            toc_html += '        </li>\n'

        toc_html += '    </ul>\n'
        toc_html += '</div>\n'

        return toc_html
