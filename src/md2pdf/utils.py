"""Utility functions for file handling."""

from pathlib import Path


def find_markdown_files(directory: Path) -> list[Path]:
    """Recursively find all markdown files in a directory.

    Args:
        directory: Directory to search in.

    Returns:
        List of Path objects for all .md files found.
    """
    return sorted(directory.rglob("*.md"))


def get_output_path(
    input_path: Path,
    input_dir: Path,
    output_dir: Path,
    preserve_structure: bool,
) -> Path:
    """Calculate the output PDF path for an input markdown file.

    Args:
        input_path: Path to the input markdown file.
        input_dir: Root directory of the input (for structure preservation).
        output_dir: Root directory for output PDFs.
        preserve_structure: Whether to preserve directory structure.

    Returns:
        Path where the PDF should be saved.
    """
    # Change extension to .pdf
    pdf_name = input_path.stem + ".pdf"

    if preserve_structure:
        # Preserve relative path structure
        relative_path = input_path.relative_to(input_dir)
        return output_dir / relative_path.parent / pdf_name
    else:
        # Flatten to output directory
        return output_dir / pdf_name


def ensure_directory(path: Path) -> None:
    """Create directory if it doesn't exist.

    Args:
        path: Directory path to create.
    """
    path.mkdir(parents=True, exist_ok=True)
