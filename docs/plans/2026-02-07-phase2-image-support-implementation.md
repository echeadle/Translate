# Phase 2: Image Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add image embedding support to md2pdf using Markdown Extension approach

**Architecture:** Create custom Python-Markdown extension to intercept image tags, resolve paths relative to source markdown file, validate image existence, and update paths for weasyprint to embed in PDF.

**Tech Stack:** Python-Markdown extension system, weasyprint (existing), pytest (existing)

---

## Task 1: Create Test Image Fixtures

**Files:**
- Create: `tests/fixtures/images/sample.png`
- Create: `tests/fixtures/images/diagram.jpg`
- Create: `tests/fixtures/with_images.md`

**Step 1: Create fixtures directory**

```bash
mkdir -p tests/fixtures/images
```

**Step 2: Create sample PNG image (100x100 blue square)**

```python
# Run this Python snippet to create sample.png
from PIL import Image
img = Image.new('RGB', (100, 100), color='blue')
img.save('tests/fixtures/images/sample.png')
```

**Step 3: Create sample JPEG image (100x100 red square)**

```python
# Run this Python snippet to create diagram.jpg
from PIL import Image
img = Image.new('RGB', (100, 100), color='red')
img.save('tests/fixtures/images/diagram.jpg')
```

**Step 4: Create markdown file with images**

Create `tests/fixtures/with_images.md`:

```markdown
# Document with Images

## Local Image

![Sample PNG](images/sample.png)

## Another Image

![Diagram](images/diagram.jpg)

## Multiple Images

![First](images/sample.png)
![Second](images/diagram.jpg)

## Text After Images

This text should appear below the images.
```

**Step 5: Verify fixtures exist**

```bash
ls -la tests/fixtures/images/
cat tests/fixtures/with_images.md
```

Expected: Directory contains sample.png and diagram.jpg, markdown file exists

**Step 6: Commit fixtures**

```bash
git add tests/fixtures/images/ tests/fixtures/with_images.md
git commit -m "test: add image fixtures for Phase 2"
```

---

## Task 2: Create Image Extension Module (TDD - Part 1: Tests)

**Files:**
- Create: `tests/test_images.py`

**Step 1: Write test for basic image path resolution**

Create `tests/test_images.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_images.py::TestImageSupport::test_convert_with_single_image -v
```

Expected: PASS (images will be broken links but conversion won't fail yet)

**Step 3: Write test for missing image error**

Add to `tests/test_images.py`:

```python
    def test_missing_image_fails(self, converter, temp_workspace):
        """Test that missing images cause conversion to fail."""
        input_dir = temp_workspace / "input"
        md_file = input_dir / "test.md"
        md_file.write_text("# Test\n\n![Missing](images/missing.png)")

        output_file = temp_workspace / "output" / "test.pdf"

        with pytest.raises(InvalidMarkdownError, match="Image not found"):
            converter.convert_file(md_file, output_file)
```

**Step 4: Run test to verify it fails**

```bash
uv run pytest tests/test_images.py::TestImageSupport::test_missing_image_fails -v
```

Expected: FAIL (no image validation yet)

**Step 5: Write test for multiple images**

Add to `tests/test_images.py`:

```python
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
```

**Step 6: Write test for absolute path images**

Add to `tests/test_images.py`:

```python
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
```

**Step 7: Run all tests to verify they fail appropriately**

```bash
uv run pytest tests/test_images.py -v
```

Expected: Some pass (basic conversion), test_missing_image_fails should FAIL

**Step 8: Commit test file**

```bash
git add tests/test_images.py
git commit -m "test: add image support test cases"
```

---

## Task 3: Implement Image Extension Module

**Files:**
- Create: `src/md2pdf/image_extension.py`

**Step 1: Create image extension module**

Create `src/md2pdf/image_extension.py`:

```python
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
```

**Step 2: Run tests to verify basic structure**

```bash
uv run pytest tests/test_images.py -v
```

Expected: Still failing (not integrated into converter yet)

**Step 3: Commit image extension module**

```bash
git add src/md2pdf/image_extension.py
git commit -m "feat: add image path extension module"
```

---

## Task 4: Integrate Image Extension into Converter

**Files:**
- Modify: `src/md2pdf/converter.py:35-50` (MarkdownConverter.__init__)
- Modify: `src/md2pdf/converter.py:52-97` (convert_file method)

**Step 1: Refactor MarkdownConverter.__init__ to remove self.md**

In `src/md2pdf/converter.py`, replace lines 35-50:

```python
    def __init__(self, config: Config):
        """Initialize the converter.

        Args:
            config: Configuration settings for PDF generation.
        """
        self.config = config
        # Store base extensions; create Markdown instance per file
        self.base_extensions = [
            "fenced_code",
            "tables",
            "codehilite",
            "nl2br",
        ]
        self.css = get_default_css(config)
```

**Step 2: Update convert_file method to use image extension**

In `src/md2pdf/converter.py`, replace the convert_file method (lines 52-97):

```python
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
            # Create markdown instance with image extension
            from md2pdf.image_extension import ImagePathExtension

            image_ext = ImagePathExtension(source_file=input_path)

            md = markdown.Markdown(
                extensions=self.base_extensions,
                extension_configs={},
            )
            md.registerExtension(image_ext)

            # Convert markdown to HTML
            html_body = md.convert(markdown_content)
            md.reset()  # Reset parser state

            # Create complete HTML document
            html_doc = f"""<!DOCTYPE html>
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

            # Generate PDF (weasyprint embeds images by default)
            ensure_directory(output_path.parent)
            HTML(string=html_doc, base_url=str(input_path.parent)).write_pdf(
                output_path
            )

        except InvalidMarkdownError:
            # Re-raise validation errors (including missing images)
            raise
        except Exception as e:
            raise ConversionError(f"Error converting {input_path} to PDF: {e}")
```

**Step 3: Run tests to verify integration**

```bash
uv run pytest tests/test_images.py -v
```

Expected: All image tests should PASS

**Step 4: Run all existing tests to ensure no regressions**

```bash
uv run pytest tests/test_converter.py -v
```

Expected: All existing tests should still PASS

**Step 5: Commit converter changes**

```bash
git add src/md2pdf/converter.py
git commit -m "feat: integrate image extension into converter"
```

---

## Task 5: Add Integration Tests with Real Fixtures

**Files:**
- Modify: `tests/conftest.py:36-59` (sample_markdown_files fixture)
- Create: `tests/test_integration.py` (add image test if not exists)

**Step 1: Update conftest to include with_images.md fixture**

In `tests/conftest.py`, update the `sample_markdown_files` fixture (around line 42):

```python
    # Copy all non-nested fixtures
    for fixture_file in ["simple.md", "tables.md", "code_blocks.md",
                          "complex.md", "empty.md", "invalid.md", "with_images.md"]:
        src = fixtures_dir / fixture_file
        if src.exists():
            dst = input_dir / fixture_file
            shutil.copy(src, dst)
            files[fixture_file.replace(".md", "")] = dst

    # Copy images directory if with_images.md is present
    images_src = fixtures_dir / "images"
    if images_src.exists():
        images_dst = input_dir / "images"
        shutil.copytree(images_src, images_dst)
```

**Step 2: Add integration test for images**

Check if `tests/test_integration.py` exists. If not, create it:

```python
"""Integration tests for end-to-end workflows."""

from pathlib import Path
import pytest


class TestImageIntegration:
    """Integration tests for image support."""

    def test_full_workflow_with_images(self, converter, sample_markdown_files, temp_workspace):
        """Test complete workflow: markdown with images -> PDF."""
        if "with_images" not in sample_markdown_files:
            pytest.skip("with_images.md fixture not available")

        input_file = sample_markdown_files["with_images"]
        output_file = temp_workspace / "output" / "with_images.pdf"

        # Convert
        converter.convert_file(input_file, output_file)

        # Verify PDF created and is larger (has embedded images)
        assert output_file.exists()

        # PDF with images should be significantly larger than text-only
        simple_output = temp_workspace / "output" / "simple.pdf"
        converter.convert_file(sample_markdown_files["simple"], simple_output)

        # Image PDF should be at least 2x larger
        assert output_file.stat().st_size > simple_output.stat().st_size * 2
```

If `tests/test_integration.py` exists, add the `TestImageIntegration` class to it.

**Step 3: Run integration tests**

```bash
uv run pytest tests/test_integration.py::TestImageIntegration -v
```

Expected: PASS

**Step 4: Run full test suite**

```bash
uv run pytest -v
```

Expected: All tests PASS

**Step 5: Commit integration tests**

```bash
git add tests/conftest.py tests/test_integration.py
git commit -m "test: add image integration tests"
```

---

## Task 6: Add Edge Case Tests

**Files:**
- Modify: `tests/test_images.py` (add more edge cases)

**Step 1: Add test for image with spaces in path**

Add to `tests/test_images.py`:

```python
    def test_image_path_with_spaces(self, converter, temp_workspace):
        """Test images with spaces in filename."""
        input_dir = temp_workspace / "input"
        images_dir = input_dir / "images"
        images_dir.mkdir()

        from shutil import copy
        fixtures_dir = Path(__file__).parent / "fixtures"
        img_with_space = images_dir / "image with spaces.png"
        copy(fixtures_dir / "images" / "sample.png", img_with_space)

        md_file = input_dir / "test.md"
        md_file.write_text("# Test\n\n![Image](images/image with spaces.png)")

        output_file = temp_workspace / "output" / "test.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()
```

**Step 2: Add test for nested image paths**

Add to `tests/test_images.py`:

```python
    def test_nested_image_path(self, converter, temp_workspace):
        """Test images in nested directories."""
        input_dir = temp_workspace / "input"
        images_dir = input_dir / "assets" / "images"
        images_dir.mkdir(parents=True)

        from shutil import copy
        fixtures_dir = Path(__file__).parent / "fixtures"
        copy(fixtures_dir / "images" / "sample.png", images_dir / "sample.png")

        md_file = input_dir / "test.md"
        md_file.write_text("# Test\n\n![Image](assets/images/sample.png)")

        output_file = temp_workspace / "output" / "test.pdf"
        converter.convert_file(md_file, output_file)

        assert output_file.exists()
```

**Step 3: Add test for image error message accuracy**

Add to `tests/test_images.py`:

```python
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
```

**Step 4: Run edge case tests**

```bash
uv run pytest tests/test_images.py::TestImageSupport::test_image_path_with_spaces -v
uv run pytest tests/test_images.py::TestImageSupport::test_nested_image_path -v
uv run pytest tests/test_images.py::TestImageSupport::test_missing_image_error_message -v
```

Expected: All PASS

**Step 5: Commit edge case tests**

```bash
git add tests/test_images.py
git commit -m "test: add edge case tests for images"
```

---

## Task 7: Verify Coverage and Quality

**Files:**
- Review: All modified files

**Step 1: Run full test suite**

```bash
uv run pytest -v
```

Expected: All tests PASS

**Step 2: Check test coverage**

```bash
uv run pytest --cov=src/md2pdf --cov-report=term-missing
```

Expected: Coverage should remain >= 80% (ideally improve)

**Step 3: Run manual test with example**

```bash
# Convert the test fixture manually
uv run md2pdf tests/fixtures/with_images.md --create-output-dir test-images
```

Expected: PDF created in output/test-images/ with embedded images

**Step 4: Verify PDF validity**

```bash
# Check PDF file size
ls -lh output/test-images/with_images.pdf

# Open PDF to visually verify images
# (Use your preferred PDF viewer)
```

Expected: PDF opens correctly, images visible

**Step 5: Review code quality**

```bash
# Check for type hints
grep -n "def " src/md2pdf/image_extension.py

# Verify docstrings
head -n 30 src/md2pdf/image_extension.py
```

Expected: All functions have type hints and docstrings

**Step 6: Commit verification notes**

```bash
git add -A
git commit -m "verify: Phase 2 image support implementation complete"
```

---

## Task 8: Update Documentation

**Files:**
- Modify: `README.md` (add image support to features)
- Modify: `docs/USAGE_GUIDE.md` (add image examples)
- Create: `examples/markdown/with_images_example.md` (user-facing example)
- Modify: `/home/echeadle/.claude/projects/-home-echeadle-Translate/memory/MEMORY.md` (update roadmap)

**Step 1: Update README.md**

Find the "Supported Markdown Features" section in `README.md` and add:

```markdown
- **Images** - Embed images from local files (relative or absolute paths)
```

**Step 2: Create usage documentation**

Add to `docs/USAGE_GUIDE.md` (create if it doesn't exist):

```markdown
## Using Images in Markdown

md2pdf supports embedding images in your PDFs. Images are automatically embedded in the PDF, making the output fully portable.

### Relative Paths

Image paths are resolved relative to the markdown file location:

```markdown
# My Document

![Architecture Diagram](images/architecture.png)
![Screenshot](screenshots/example.jpg)
```

If your markdown is at `/docs/report.md`, the images will be resolved from:
- `/docs/images/architecture.png`
- `/docs/screenshots/example.jpg`

### Absolute Paths

You can also use absolute paths:

```markdown
![Logo](/home/user/assets/logo.png)
```

### Supported Formats

All image formats supported by weasyprint work:
- PNG (recommended for diagrams and screenshots)
- JPEG (good for photos)
- SVG (if supported by your weasyprint installation)
- GIF

### Error Handling

If an image is missing, conversion will fail with a clear error:

```
InvalidMarkdownError: Image not found: images/missing.png (referenced in /path/to/document.md)
```
```

**Step 3: Create example file**

Create `examples/markdown/with_images_example.md`:

```markdown
# Document with Images Example

This example demonstrates image embedding in md2pdf.

## Architecture Diagram

Below is a sample architecture diagram:

![Sample Architecture](../../tests/fixtures/images/sample.png)

## Multiple Images

You can include multiple images in a single document:

![First Image](../../tests/fixtures/images/sample.png)

![Second Image](../../tests/fixtures/images/diagram.jpg)

## Text Flow

Images integrate seamlessly with your text. The content flows naturally around them.
```

**Step 4: Update MEMORY.md**

Update `/home/echeadle/.claude/projects/-home-echeadle-Translate/memory/MEMORY.md`:

Change:
```markdown
## Roadmap Progress
- ✅ Phase 5: Testing & Quality (COMPLETE - 61 tests, 83% coverage)
- 🔜 Next: Phase 2 (Image Support) OR Phase 3 (Custom Styling)
- Future: Phase 4 (Advanced Features)
```

To:
```markdown
## Roadmap Progress
- ✅ Phase 5: Testing & Quality (COMPLETE - 61 tests, 83% coverage)
- ✅ Phase 2: Image Support (COMPLETE - 2026-02-07)
- 🔜 Next: Phase 3 (Custom Styling)
- Future: Phase 4 (Advanced Features)

## Phase 2 Notes (Image Support)
- Markdown extension approach for clean integration
- Images resolved relative to .md file location
- All weasyprint formats supported (PNG, JPEG, SVG)
- Images fully embedded in PDF (portable output)
- Clear error messages for missing images
```

**Step 5: Commit documentation**

```bash
git add README.md docs/USAGE_GUIDE.md examples/markdown/with_images_example.md
git add /home/echeadle/.claude/projects/-home-echeadle-Translate/memory/MEMORY.md
git commit -m "docs: add Phase 2 image support documentation"
```

---

## Task 9: Final Verification and Cleanup

**Files:**
- Review: All changes

**Step 1: Run complete test suite**

```bash
uv run pytest -v --cov=src/md2pdf --cov-report=term-missing
```

Expected: All tests PASS, coverage >= 80%

**Step 2: Test real-world example**

```bash
uv run md2pdf examples/markdown/with_images_example.md --create-output-dir phase2-test
```

Expected: PDF created successfully with images

**Step 3: Review git status**

```bash
git status
git log --oneline -10
```

Expected: Clean working tree, commits show clear progression

**Step 4: Create summary commit (if needed)**

```bash
# Only if there are uncommitted changes
git add -A
git commit -m "feat: Phase 2 image support complete

- Added ImagePathExtension for markdown image processing
- Images resolved relative to source .md file
- Full test coverage with edge cases
- Documentation updated
- Backward compatible (no breaking changes)"
```

**Step 5: Verify memory update**

```bash
cat /home/echeadle/.claude/projects/-home-echeadle-Translate/memory/MEMORY.md | grep -A 5 "Roadmap Progress"
```

Expected: Shows Phase 2 as complete

---

## Success Criteria

- ✅ Images from local files embed correctly in PDFs
- ✅ Relative paths resolve correctly (relative to .md file)
- ✅ Missing images cause clear error messages
- ✅ All weasyprint-supported formats work
- ✅ PDFs are standalone (images fully embedded)
- ✅ Tests cover common cases and edge cases
- ✅ Existing tests continue to pass (no regressions)
- ✅ Documentation updated (README, USAGE_GUIDE, examples)
- ✅ Test coverage maintained >= 80%
- ✅ MEMORY.md updated with Phase 2 complete

## Dependencies

**Required:**
- Pillow (for creating test images) - add to dev dependencies

**Command:**
```bash
uv add --dev Pillow
```

## Testing Commands Summary

```bash
# Run image tests only
uv run pytest tests/test_images.py -v

# Run all tests
uv run pytest -v

# Check coverage
uv run pytest --cov=src/md2pdf --cov-report=term-missing

# Manual test
uv run md2pdf tests/fixtures/with_images.md --create-output-dir test
```

## Notes

- **Backward Compatibility:** 100% - documents without images work exactly as before
- **Performance:** Minimal impact - only path resolution overhead
- **Future Enhancements:** Image optimization, remote URLs (deferred per YAGNI)
- **Test Strategy:** TDD approach ensures correctness before implementation
