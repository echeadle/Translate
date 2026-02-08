"""Tests for image path resolution in markdown."""

from pathlib import Path
import pytest
from md2pdf.converter import MarkdownConverter, InvalidMarkdownError


class TestImageSupport:
    """Tests for image embedding in PDFs."""

    def test_convert_with_single_image(self, converter, temp_workspace):
        """Test converting markdown with one image."""
        # Setup: Create markdown with image
        input_dir = temp_workspace / "input"
        images_dir = input_dir / "images"
        images_dir.mkdir()

        # Copy test image
        from shutil import copy
        fixtures_dir = Path(__file__).parent / "fixtures"
        copy(fixtures_dir / "images" / "sample.png", images_dir / "sample.png")

        # Create markdown
        md_file = input_dir / "test.md"
        md_file.write_text("# Test\n\n![Image](images/sample.png)")

        output_file = temp_workspace / "output" / "test.pdf"

        # Execute
        converter.convert_file(md_file, output_file)

        # Verify
        assert output_file.exists()
        assert output_file.stat().st_size > 1000  # Should be larger with image

    def test_missing_image_fails(self, converter, temp_workspace):
        """Test that missing images cause conversion to fail."""
        input_dir = temp_workspace / "input"
        md_file = input_dir / "test.md"
        md_file.write_text("# Test\n\n![Missing](images/missing.png)")

        output_file = temp_workspace / "output" / "test.pdf"

        with pytest.raises(InvalidMarkdownError, match="Image not found"):
            converter.convert_file(md_file, output_file)

    def test_convert_with_multiple_images(self, converter, temp_workspace):
        """Test converting markdown with multiple images."""
        input_dir = temp_workspace / "input"
        images_dir = input_dir / "images"
        images_dir.mkdir()

        from shutil import copy
        fixtures_dir = Path(__file__).parent / "fixtures"
        copy(fixtures_dir / "images" / "sample.png", images_dir / "sample.png")
        copy(fixtures_dir / "images" / "diagram.jpg", images_dir / "diagram.jpg")

        md_file = input_dir / "test.md"
        md_file.write_text(
            "# Test\n\n"
            "![First](images/sample.png)\n\n"
            "![Second](images/diagram.jpg)"
        )

        output_file = temp_workspace / "output" / "test.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 2000  # Larger with two images

    def test_absolute_path_image(self, converter, temp_workspace):
        """Test that absolute paths work."""
        input_dir = temp_workspace / "input"

        # Create image at absolute path
        from shutil import copy
        fixtures_dir = Path(__file__).parent / "fixtures"
        abs_image = temp_workspace / "absolute_image.png"
        copy(fixtures_dir / "images" / "sample.png", abs_image)

        md_file = input_dir / "test.md"
        md_file.write_text(f"# Test\n\n![Absolute]({abs_image})")

        output_file = temp_workspace / "output" / "test.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()
