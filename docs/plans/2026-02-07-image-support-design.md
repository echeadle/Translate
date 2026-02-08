# Phase 2: Image Support Design

**Date:** 2026-02-07
**Status:** Design Complete - Ready for Implementation
**Approach:** Markdown Extension (Option 1)

## Goal

Add image support to md2pdf to enable embedding images from local files in generated PDFs.

## Requirements Summary

**From Brainstorming Session:**
- **Primary Use Case:** Documentation with diagrams (technical docs with architecture diagrams, screenshots, charts)
- **Path Resolution:** Relative to markdown file location
- **Format Support:** All formats weasyprint supports (future-proof)
- **Error Handling:** Fail conversion on missing/invalid images (clean failures)
- **Embedding:** Fully embed images in PDF (standalone, portable files)
- **Optimization:** Basic embedding only (YAGNI principle)
- **Testing:** Real image files in test fixtures (integration-focused)

## Design Approach: Markdown Extension (Option 1)

### Architecture

Use Python-Markdown's extension system to intercept and process images during the markdown-to-HTML conversion:

1. **Create Custom Markdown Extension** (`ImagePathExtension`)
   - Intercept `![alt](path)` during HTML generation
   - Resolve relative paths based on source markdown file location
   - Validate image files exist
   - Update image paths in HTML for weasyprint

2. **Path Resolution Logic**
   - Images paths are relative to the markdown file's directory
   - Example: `/docs/report.md` with `![](images/chart.png)` → resolve to `/docs/images/chart.png`
   - Absolute paths pass through unchanged

3. **Error Handling**
   - Fail conversion with `InvalidMarkdownError` if image not found
   - Clear error message: "Image not found: {path} (referenced in {markdown_file})"
   - Consistent with existing error handling philosophy

4. **Embedding**
   - Let weasyprint handle image embedding (it embeds by default)
   - Images become part of PDF (no external dependencies)

### Why Option 1 (Markdown Extension)?

**Selected over:**
- Option 2 (Post-Process HTML): Extra parsing step, might miss edge cases
- Option 3 (Pre-Process Markdown): Duplicate parsing, doesn't leverage pipeline

**Advantages:**
- Clean separation of concerns
- Leverages existing markdown pipeline
- Easy to test (markdown → HTML → PDF flow)
- Extensible for future image features
- Doesn't require HTML parsing

## Implementation Components

### 1. New Module: `src/md2pdf/image_extension.py`

```python
"""Markdown extension for image path resolution."""

from pathlib import Path
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree


class ImagePathProcessor(Treeprocessor):
    """Process image tags to resolve relative paths."""

    def __init__(self, md, source_file: Path):
        super().__init__(md)
        self.source_file = source_file
        self.source_dir = source_file.parent

    def run(self, root: etree.Element) -> etree.Element:
        """Process all img tags in the HTML tree."""
        for img in root.iter('img'):
            src = img.get('src')
            if src:
                resolved_path = self._resolve_image_path(src)
                img.set('src', str(resolved_path))
        return root

    def _resolve_image_path(self, path: str) -> Path:
        """Resolve image path relative to markdown file."""
        # If absolute path, use as-is
        if Path(path).is_absolute():
            img_path = Path(path)
        else:
            # Resolve relative to markdown file location
            img_path = (self.source_dir / path).resolve()

        # Validate image exists
        if not img_path.exists():
            from md2pdf.converter import InvalidMarkdownError
            raise InvalidMarkdownError(
                f"Image not found: {path} "
                f"(referenced in {self.source_file})"
            )

        return img_path


class ImagePathExtension(Extension):
    """Markdown extension for resolving image paths."""

    def __init__(self, source_file: Path, **kwargs):
        self.source_file = source_file
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        """Register the image path processor."""
        processor = ImagePathProcessor(md, self.source_file)
        md.treeprocessors.register(processor, 'image_path', 15)
```

### 2. Update: `src/md2pdf/converter.py`

**Changes to `MarkdownConverter.__init__`:**
```python
def __init__(self, config: Config):
    self.config = config
    # Don't initialize markdown here anymore - need source file path
    self.base_extensions = [
        "fenced_code",
        "tables",
        "codehilite",
        "nl2br",
    ]
    self.css = get_default_css(config)
```

**Changes to `convert_file` method:**
```python
def convert_file(self, input_path: Path, output_path: Path) -> None:
    """Convert a single markdown file to PDF."""
    try:
        markdown_content = input_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise InvalidMarkdownError(f"File not found: {input_path}")
    except Exception as e:
        raise InvalidMarkdownError(f"Error reading {input_path}: {e}")

    try:
        # Create markdown instance with image extension
        from md2pdf.image_extension import ImagePathExtension

        extensions = self.base_extensions.copy()
        image_ext = ImagePathExtension(source_file=input_path)

        md = markdown.Markdown(
            extensions=extensions,
            extension_configs={}
        )
        md.registerExtension(image_ext)

        # Convert markdown to HTML
        html_body = md.convert(markdown_content)
        md.reset()

        # Create complete HTML document
        html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>{self.css}</style>
</head>
<body>{html_body}</body>
</html>"""

        # Generate PDF (weasyprint will embed images)
        ensure_directory(output_path.parent)
        HTML(string=html_doc, base_url=str(input_path.parent)).write_pdf(output_path)

    except InvalidMarkdownError:
        raise
    except Exception as e:
        raise ConversionError(f"Error converting {input_path} to PDF: {e}")
```

**Key addition:** `base_url=str(input_path.parent)` tells weasyprint where to resolve relative paths from.

## Testing Strategy

### Test Fixtures to Add

**Location:** `tests/fixtures/images/`

Create test image files:
1. `sample.png` - Simple PNG (e.g., 100x100px colored square)
2. `diagram.jpg` - Simple JPEG
3. `chart.svg` - Simple SVG (if weasyprint supports)

**New Markdown Test File:** `tests/fixtures/with_images.md`

```markdown
# Document with Images

## Local Image
![Sample PNG](images/sample.png)

## Relative Path
![Diagram](images/diagram.jpg)

## Text continues after image
This text should appear below the image.
```

### New Test Module: `tests/test_images.py`

**Test Cases:**
1. `test_convert_with_local_image` - Basic image embedding
2. `test_convert_with_relative_path` - Path resolution works
3. `test_convert_with_multiple_images` - Multiple images in one document
4. `test_missing_image_fails` - Proper error on missing image
5. `test_absolute_path_image` - Absolute paths work (if applicable)
6. `test_image_in_pdf_validity` - PDF contains embedded images (check file size > baseline)

### Update Existing Tests

**`tests/test_converter.py`:**
- Existing tests should continue to pass (no images = no change)

**`tests/test_integration.py`:**
- Add integration test with images in real-world workflow

## Future Enhancements (Documented for Reference)

These were considered but deferred (YAGNI principle):

### Image Optimization
- **Resize large images** - Automatically scale down oversized images to max dimensions
- **Compress images** - Re-encode at lower quality for smaller PDFs
- **Format conversion** - Convert all images to optimal format (e.g., WebP, optimized JPEG)
- **Configuration:** Add `--optimize-images` flag or config options

### Advanced Features
- **Remote URL support** - Download images from http/https URLs
- **Image caching** - Cache downloaded/processed images
- **Alt text handling** - Better accessibility with alt text in PDFs
- **Image sizing** - Support markdown image size syntax `![](image.png){width=50%}`

### When to Revisit
- If users report large PDF file sizes
- If image quality issues arise
- If remote images become a common request

## Success Criteria

- [ ] Images from local files embed correctly in PDFs
- [ ] Relative paths resolve correctly (relative to .md file)
- [ ] Missing images cause clear error messages
- [ ] All weasyprint-supported formats work
- [ ] PDFs are standalone (images fully embedded)
- [ ] Tests cover common cases and edge cases
- [ ] Existing tests continue to pass (no regressions)
- [ ] Documentation updated

## Documentation Updates

**After Implementation:**

1. **Update `README.md`** - Add "Images" to Supported Markdown Features section
2. **Update `docs/USAGE_GUIDE.md`** - Add image usage examples
3. **Update `MEMORY.md`** - Mark Phase 2 as complete
4. **Update test fixtures** - Add example with images to `examples/markdown/`

## Implementation Notes

**Dependencies:** No new dependencies needed
- Python-Markdown already supports extensions
- weasyprint already handles image embedding

**Breaking Changes:** None
- Fully backward compatible
- Documents without images work identically

**Performance Impact:** Minimal
- Image validation adds negligible overhead
- Image embedding is handled by weasyprint (same as before)

---

**Design Status:** ✅ Complete and validated
**Ready for:** Implementation planning and execution
