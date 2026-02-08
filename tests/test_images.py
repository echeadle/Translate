"""Tests for image path resolution in markdown."""

from pathlib import Path
from shutil import copy
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
        # Minimum size check: PDF with embedded PNG should be >1KB
        assert output_file.stat().st_size > 1000

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
        # Minimum size check: PDF with two embedded images should be >2KB
        assert output_file.stat().st_size > 2000

    def test_absolute_path_image(self, converter, temp_workspace):
        """Test that absolute paths work."""
        input_dir = temp_workspace / "input"

        # Create image at absolute path
        fixtures_dir = Path(__file__).parent / "fixtures"
        abs_image = temp_workspace / "absolute_image.png"
        copy(fixtures_dir / "images" / "sample.png", abs_image)

        md_file = input_dir / "test.md"
        md_file.write_text(f"# Test\n\n![Absolute]({abs_image})")

        output_file = temp_workspace / "output" / "test.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()

    def test_convert_with_fixture_file(self, converter, temp_workspace):
        """Test converting the with_images.md fixture."""
        # Copy fixture and images
        fixtures_dir = Path(__file__).parent / "fixtures"
        input_dir = temp_workspace / "input"
        images_dir = input_dir / "images"
        images_dir.mkdir()

        copy(fixtures_dir / "with_images.md", input_dir / "with_images.md")
        copy(fixtures_dir / "images" / "sample.png", images_dir / "sample.png")
        copy(fixtures_dir / "images" / "diagram.jpg", images_dir / "diagram.jpg")

        md_file = input_dir / "with_images.md"
        output_file = temp_workspace / "output" / "with_images.pdf"

        converter.convert_file(md_file, output_file)

        assert output_file.exists()

    def test_image_path_with_spaces(self, converter, temp_workspace):
        """Test images with spaces in filename."""
        input_dir = temp_workspace / "input"
        images_dir = input_dir / "images"
        images_dir.mkdir()

        fixtures_dir = Path(__file__).parent / "fixtures"
        img_with_space = images_dir / "image with spaces.png"
        copy(fixtures_dir / "images" / "sample.png", img_with_space)

        md_file = input_dir / "test.md"
        md_file.write_text("# Test\n\n![Image](images/image with spaces.png)")

        output_file = temp_workspace / "output" / "test.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()

    def test_nested_image_path(self, converter, temp_workspace):
        """Test images in nested directories."""
        input_dir = temp_workspace / "input"
        images_dir = input_dir / "assets" / "images"
        images_dir.mkdir(parents=True)

        fixtures_dir = Path(__file__).parent / "fixtures"
        copy(fixtures_dir / "images" / "sample.png", images_dir / "sample.png")

        md_file = input_dir / "test.md"
        md_file.write_text("# Test\n\n![Image](assets/images/sample.png)")

        output_file = temp_workspace / "output" / "test.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()

    def test_missing_image_error_message(self, converter, temp_workspace):
        """Test that error message includes helpful context."""
        input_dir = temp_workspace / "input"
        md_file = input_dir / "document.md"
        md_file.write_text("# Test\n\n![Missing](missing.png)")

        output_file = temp_workspace / "output" / "test.pdf"

        with pytest.raises(InvalidMarkdownError) as exc_info:
            converter.convert_file(md_file, output_file)

        error_msg = str(exc_info.value)
        assert "missing.png" in error_msg
        assert "document.md" in error_msg
