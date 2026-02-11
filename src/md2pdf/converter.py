"""Core markdown to PDF conversion logic."""

import html
import re
from datetime import datetime
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
        metadata: Optional[Dict[str, Optional[str]]] = None,
        title_page_enabled: bool = False,
    ) -> None:
        """Convert a single markdown file to PDF.

        Args:
            input_path: Path to the input markdown file.
            output_path: Path where the PDF should be saved.
            toc_enabled: Whether to generate a table of contents from H1/H2 headers.
            metadata: Optional PDF metadata dict (title, author, subject, keywords).
            title_page_enabled: Whether to add a title page before content.

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

            # Generate TOC if enabled (single-pass: CSS target-counter resolves page numbers)
            if toc_enabled:
                headers = self.extract_headers(html_body)

                if not headers:
                    console.print("[yellow]Warning:[/yellow] No H1/H2 headers found for TOC")
                else:
                    toc_html = self.generate_toc_html(headers)
                    html_body = toc_html + html_body

            # Prepend title page (before TOC and content)
            if title_page_enabled:
                title_page_html = self.generate_title_page_html(pdf_metadata)
                html_body = title_page_html + html_body

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

    def convert_merge(
        self,
        input_paths: list[Path],
        output_path: Path,
        toc_enabled: bool = False,
        metadata: Optional[Dict[str, Optional[str]]] = None,
        title_page_enabled: bool = False,
    ) -> None:
        """Merge multiple markdown files into a single PDF.

        Args:
            input_paths: Ordered list of markdown file paths.
            output_path: Path where the merged PDF should be saved.
            toc_enabled: Whether to generate a unified table of contents.
            metadata: Optional PDF metadata dict (title, author, subject, keywords).
            title_page_enabled: Whether to add a title page before content.

        Raises:
            InvalidMarkdownError: If any markdown file cannot be read or parsed.
            ConversionError: If PDF generation fails.
        """
        if not input_paths:
            raise InvalidMarkdownError("No markdown files provided for merging")

        try:
            from md2pdf.image_extension import ImagePathExtension

            html_bodies: list[str] = []

            for path in input_paths:
                try:
                    content = path.read_text(encoding="utf-8")
                except FileNotFoundError:
                    raise InvalidMarkdownError(f"File not found: {path}")
                except Exception as e:
                    raise InvalidMarkdownError(f"Error reading {path}: {e}")

                image_ext = ImagePathExtension(source_file=path)
                extensions = self.base_extensions.copy()
                extensions.append(image_ext)

                md = markdown.Markdown(extensions=extensions, extension_configs={})
                html_bodies.append(md.convert(content))
                md.reset()

            # Join with page breaks between files
            combined_html = '<div style="page-break-before: always;"></div>'.join(
                html_bodies
            )

            # Build PDF metadata
            pdf_metadata: Dict[str, str] = {}
            if metadata:
                pdf_metadata["title"] = metadata.get("title") or output_path.stem
                pdf_metadata["author"] = metadata.get("author") or ""
                pdf_metadata["subject"] = metadata.get("subject") or ""
                pdf_metadata["keywords"] = metadata.get("keywords") or ""
            else:
                pdf_metadata["title"] = output_path.stem
                pdf_metadata["author"] = ""
                pdf_metadata["subject"] = ""
                pdf_metadata["keywords"] = ""

            # Generate unified TOC across all files
            if toc_enabled:
                headers = self.extract_headers(combined_html)
                if not headers:
                    console.print(
                        "[yellow]Warning:[/yellow] No H1/H2 headers found for TOC"
                    )
                else:
                    toc_html = self.generate_toc_html(headers)
                    combined_html = toc_html + combined_html

            # Prepend title page (before TOC and content)
            if title_page_enabled:
                title_page_html = self.generate_title_page_html(pdf_metadata)
                combined_html = title_page_html + combined_html

            # Build complete HTML document
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
    {combined_html}
</body>
</html>
"""

            # Use common parent directory as base_url for image resolution
            base_dir = input_paths[0].parent
            for p in input_paths[1:]:
                # Find the common ancestor directory
                try:
                    base_dir.relative_to(p.parent)
                except ValueError:
                    try:
                        p.parent.relative_to(base_dir)
                    except ValueError:
                        # Walk up to common parent
                        parts_a = base_dir.parts
                        parts_b = p.parent.parts
                        common = []
                        for a, b in zip(parts_a, parts_b):
                            if a == b:
                                common.append(a)
                            else:
                                break
                        base_dir = Path(*common) if common else base_dir

            ensure_directory(output_path.parent)
            document = HTML(
                string=html_doc, base_url=str(base_dir)
            ).render()

            # Set PDF metadata
            document.metadata.title = pdf_metadata["title"]
            if pdf_metadata.get("author"):
                document.metadata.authors = [pdf_metadata["author"]]
            if pdf_metadata.get("subject"):
                document.metadata.description = pdf_metadata["subject"]
            if pdf_metadata.get("keywords"):
                document.metadata.keywords = [
                    kw.strip() for kw in pdf_metadata["keywords"].split(",")
                ]

            document.write_pdf(output_path)

        except InvalidMarkdownError:
            raise
        except Exception as e:
            raise ConversionError(f"Error merging files to PDF: {e}")

    def convert_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        preserve_structure: bool,
        toc_enabled: bool = False,
        metadata: Optional[Dict[str, Optional[str]]] = None,
        title_page_enabled: bool = False,
    ) -> list[dict]:
        """Convert all markdown files in a directory to PDF.

        Args:
            input_dir: Directory containing markdown files.
            output_dir: Directory where PDFs should be saved.
            preserve_structure: Whether to preserve directory structure.
            toc_enabled: Whether to generate a table of contents from H1/H2 headers.
            metadata: Optional PDF metadata dict (title, author, subject, keywords).
            title_page_enabled: Whether to add a title page before content.

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
                self.convert_file(
                    md_file, output_path,
                    toc_enabled=toc_enabled,
                    metadata=metadata,
                    title_page_enabled=title_page_enabled,
                )
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

    def extract_headers(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract H1 and H2 headers from HTML in document order.

        Page numbers are resolved at render time via CSS target-counter,
        so this method only extracts text, level, and anchor IDs.

        Args:
            html_content: HTML content to parse.

        Returns:
            List of dicts with keys: text, level, anchor_id
        """
        headers = []
        seen_ids: Set[str] = set()

        # Combined pattern to find H1 and H2 tags in document order
        pattern = r'<(h[12])\b([^>]*)>(.*?)</\1>'
        id_pattern = r'\bid="([^"]*)"'

        for match in re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL):
            tag = match.group(1).lower()
            attrs = match.group(2)
            content = match.group(3)

            level = int(tag[1])

            # Extract id attribute if present
            id_match = re.search(id_pattern, attrs)
            anchor_id = id_match.group(1).strip() if id_match else ''

            # Get header text (strip nested HTML tags, unescape HTML entities)
            text = html.unescape(re.sub(r'<[^>]+>', '', content).strip())

            if not text:
                continue

            # Validate ID format or generate a new one
            if anchor_id and re.match(r'^[a-zA-Z][\w\-]*$', anchor_id):
                seen_ids.add(anchor_id)
            else:
                anchor_id = self.generate_anchor_id(text, seen_ids)

            headers.append({
                'text': text,
                'level': level,
                'anchor_id': anchor_id,
            })

        return headers

    def generate_toc_html(self, headers: List[Dict[str, Any]]) -> str:
        """Generate HTML for table of contents.

        Page numbers are rendered via CSS target-counter(attr(href url), page)
        so no page number spans are emitted here.

        Args:
            headers: List of header dicts from extract_headers().
                Each dict has keys: text, level, anchor_id

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
            toc_html += '        </li>\n'

        toc_html += '    </ul>\n'
        toc_html += '</div>\n'

        return toc_html

    def generate_title_page_html(self, metadata: Dict[str, Optional[str]]) -> str:
        """Generate HTML for a title page.

        Args:
            metadata: Dict with keys title, author (both optional).

        Returns:
            HTML string for the title page with page break after.
        """
        title = metadata.get('title') or 'Untitled'
        author = metadata.get('author') or ''
        date_str = datetime.now().strftime("%B %d, %Y")

        title_html = '<div class="title-page">\n'
        title_html += f'    <h1>{html.escape(title)}</h1>\n'
        if author:
            title_html += f'    <p class="author">{html.escape(author)}</p>\n'
        title_html += f'    <p class="date">{html.escape(date_str)}</p>\n'
        title_html += '</div>\n'

        return title_html
