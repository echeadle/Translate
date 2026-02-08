"""Markdown extension for image path resolution."""

from pathlib import Path
from typing import TYPE_CHECKING
import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

if TYPE_CHECKING:
    from markdown import Markdown


class ImagePathProcessor(Treeprocessor):
    """Process image tags to resolve relative paths."""

    def __init__(self, md: "Markdown", source_file: Path):
        """Initialize the image path processor.

        Args:
            md: Markdown instance.
            source_file: Path to the source markdown file.
        """
        super().__init__(md)
        self.source_file = source_file
        self.source_dir = source_file.parent

    def run(self, root: etree.Element) -> etree.Element | None:
        """Process all img tags in the HTML tree.

        Args:
            root: Root element of the HTML tree.

        Returns:
            Modified root element, or None.
        """
        for img in root.iter("img"):
            src = img.get("src")
            if src:
                resolved_path = self._resolve_image_path(src)
                img.set("src", str(resolved_path))
        return root

    def _resolve_image_path(self, path: str) -> Path:
        """Resolve image path relative to markdown file.

        Args:
            path: Image path from markdown (relative or absolute).

        Returns:
            Resolved absolute path to image.

        Raises:
            InvalidMarkdownError: If image file does not exist.
        """
        # Import here to avoid circular dependency
        from md2pdf.converter import InvalidMarkdownError

        # If absolute path, use as-is
        if Path(path).is_absolute():
            img_path = Path(path)
        else:
            # Resolve relative to markdown file location
            img_path = (self.source_dir / path).resolve()

        # Validate image exists
        if not img_path.exists():
            raise InvalidMarkdownError(
                f"Image not found: {path} "
                f"(referenced in {self.source_file})"
            )

        return img_path


class ImagePathExtension(Extension):
    """Markdown extension for resolving image paths."""

    def __init__(self, source_file: Path, **kwargs):
        """Initialize the extension.

        Args:
            source_file: Path to the source markdown file.
            **kwargs: Additional keyword arguments.
        """
        self.source_file = source_file
        super().__init__(**kwargs)

    def extendMarkdown(self, md: "Markdown") -> None:
        """Register the image path processor.

        Args:
            md: Markdown instance to extend.
        """
        processor = ImagePathProcessor(md, self.source_file)
        md.treeprocessors.register(processor, "image_path", 15)
