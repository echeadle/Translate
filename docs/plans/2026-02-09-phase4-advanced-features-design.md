# Phase 4: Advanced Features - Design Document

**Date:** 2026-02-09
**Status:** Design Complete - Ready for Implementation
**Phase:** 4 of 5

## Overview

Phase 4 adds professional document features to md2pdf while maintaining its "simple and reliable" philosophy. All features are opt-in and backward compatible.

### Scope

**In Scope:**
1. **Headers/Footers** - Page numbers with configurable position (left/center/right)
2. **Table of Contents** - Auto-generated TOC from H1 and H2 headers (opt-in via `--toc` flag)
3. **PDF Metadata** - Title, Author, Subject, Keywords (configurable via .env/CLI)

**Out of Scope (Deferred):**
- Watch mode (auto-regenerate on file changes) - Deferred to Phase 5
- Watermarks - Not prioritized
- Custom header/footer templates - Starting with simple page numbers only
- TOC depth configuration - Fixed at H1/H2 for simplicity

### Goals

- Maintain backward compatibility (existing conversions unchanged)
- Keep features opt-in and simple
- Leverage WeasyPrint's native capabilities
- No new major dependencies
- Maintain 89%+ test coverage

## Architecture

### Overall Design

**Core Approach:** Enhance the existing rendering pipeline with optional TOC generation and CSS-based headers/footers, maintaining the clean separation between page setup (.env) and styling (themes).

### Rendering Flow

**Without TOC (default):**
```
Markdown → HTML → CSS (page setup + theme + headers/footers) → PDF
```

**With --toc flag:**
```
Pass 1: Markdown → HTML → CSS → PDF (get page numbers for headers)
        ↓
   Extract header locations from rendered PDF
        ↓
Pass 2: Generate TOC HTML + Original HTML → CSS → Final PDF
```

### Key Design Principles

1. **Opt-in complexity** - Headers/footers are configured but lightweight; TOC only runs when `--toc` is used
2. **CSS-native implementation** - Use WeasyPrint's `@page` rules for headers/footers (no custom rendering)
3. **Theme compatibility** - Headers/footers respect theme styling; TOC styling can be themed
4. **Configuration hierarchy** - .env for defaults, CLI flags for overrides (e.g., `--author "Jane Doe"`)
5. **Backward compatible** - Existing conversions work exactly the same; new features are additive

### Dependencies

**New Dependencies:** None

WeasyPrint already supports:
- `@page` margin boxes for headers/footers
- `counter(page)` and `counter(pages)` for page numbers
- `document.make_bookmark_tree()` for extracting header locations
- `pdf_metadata` parameter for PDF metadata

## Feature 1: Headers/Footers (Page Numbers)

### Configuration

**.env Settings:**
```bash
# Headers/Footers
ENABLE_PAGE_NUMBERS=true
PAGE_NUMBER_POSITION=center  # Options: left, center, right
PAGE_NUMBER_FORMAT=Page {page} of {pages}  # Template string
```

**Defaults:**
- `ENABLE_PAGE_NUMBERS=false` (opt-in)
- `PAGE_NUMBER_POSITION=center`
- `PAGE_NUMBER_FORMAT=Page {page} of {pages}`

### CLI Flags

```bash
--page-numbers / --no-page-numbers  # Override .env setting
```

### Implementation

**CSS Generation (styles.py):**

Modify `get_page_css()` to include `@page` margin boxes when page numbers are enabled:

```css
@page {
    size: A4;
    margin: 2cm;

    /* Footer with page numbers */
    @bottom-center {  /* or @bottom-left / @bottom-right */
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
        font-family: Arial, sans-serif;
    }
}
```

**Position Mapping:**
- `center` → `@bottom-center`
- `left` → `@bottom-left`
- `right` → `@bottom-right`

**Format String Processing:**
- Replace `{page}` with `counter(page)`
- Replace `{pages}` with `counter(pages)`
- Validate only these two placeholders are used

### Styling

- Font size: 9pt (smaller than body text)
- Color: #666 (gray, unobtrusive)
- Font family: Inherits from body but can be overridden
- Position: Bottom of page (footers only for now)

### Edge Cases

1. **Invalid position** - Validation in `Config.load()`: raise error with valid options
2. **Invalid format string** - Validate placeholders, show warning for invalid format
3. **Long format strings** - Truncate at 100 chars to prevent layout issues
4. **Theme conflicts** - Use fixed styling to avoid theme interference

## Feature 2: Table of Contents

### CLI Flag

```bash
--toc / --no-toc  # Generate table of contents (default: false)
```

### Two-Pass Rendering Process

**Pass 1 - Extract Header Information:**

1. Convert markdown to HTML (existing pipeline)
2. Render to PDF with WeasyPrint
3. Extract headers and their page numbers from PDF structure
4. WeasyPrint exposes this via `document.make_bookmark_tree()` which includes:
   - Header text
   - Page number
   - Heading level

**Pass 2 - Render with TOC:**

1. Generate TOC HTML from extracted headers
2. Prepend TOC HTML to original document HTML
3. Re-render complete document to final PDF

### TOC HTML Structure

```html
<div class="toc">
    <h1>Table of Contents</h1>
    <ul>
        <li class="toc-h1">
            <a href="#heading-1">Introduction</a>
            <span class="toc-page">1</span>
        </li>
        <li class="toc-h2">
            <a href="#heading-2">Getting Started</a>
            <span class="toc-page">3</span>
        </li>
        <li class="toc-h1">
            <a href="#heading-3">Advanced Topics</a>
            <span class="toc-page">5</span>
        </li>
    </ul>
</div>
```

### TOC Styling (CSS)

Added to all 5 theme files:

```css
/* Table of Contents */
.toc {
    page-break-after: always;  /* TOC on separate pages */
    margin-bottom: 2em;
}

.toc h1 {
    font-size: 1.5em;
    margin-bottom: 1em;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 0.5em;
    display: flex;
    justify-content: space-between;
}

.toc-h1 {
    font-weight: 600;
}

.toc-h2 {
    padding-left: 1.5em;
    font-weight: 400;
}

.toc a {
    flex-grow: 1;
}

.toc-page {
    margin-left: 1em;
    font-weight: 400;
    color: #666;
}
```

**Theme Variations:**
- Each theme can customize TOC styling to match its aesthetic
- GitHub: Simple, clean
- Minimal: Extra spacing
- Academic: Serif fonts
- Dark: Light text on dark background
- Modern: Colorful accents

### Header Extraction

**Algorithm:**
1. Use `document.make_bookmark_tree()` to get PDF structure
2. Filter for H1 and H2 only (ignore H3-H6)
3. Extract: heading text, page number, level
4. Generate unique anchor IDs for each heading

**Anchor ID Generation:**
```python
def generate_anchor_id(text: str, seen_ids: Set[str]) -> str:
    """Generate unique anchor ID from heading text."""
    # Convert to lowercase, replace spaces with hyphens
    base_id = text.lower().replace(" ", "-")
    # Remove special characters
    base_id = re.sub(r'[^a-z0-9-]', '', base_id)

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
```

### Edge Cases

1. **No headers found** - Skip TOC generation, show warning: "No H1/H2 headers found for TOC"
2. **Duplicate header text** - Append counter to anchor: `#introduction`, `#introduction-2`
3. **Special characters in headers** - Sanitize for anchor IDs
4. **Very long TOC** - No pagination limit (TOC can span multiple pages naturally)
5. **Two-pass rendering fails** - If first pass fails, report error; don't attempt second pass

### Performance Considerations

- Two-pass rendering adds overhead (~2x rendering time)
- Acceptable for documents where TOC is needed
- Most documents don't need TOC (opt-in via flag)
- Cache first-pass results to avoid re-parsing markdown

## Feature 3: PDF Metadata

### Configuration

**.env Settings:**
```bash
# PDF Metadata
PDF_TITLE=
PDF_AUTHOR=
PDF_SUBJECT=
PDF_KEYWORDS=
```

**Defaults:**
- All empty (optional)
- Title falls back to filename if not set

### CLI Flags

```bash
--title "Document Title"
--author "Author Name"
--subject "Document Subject"
--keywords "keyword1, keyword2, keyword3"
```

**CLI Precedence:** CLI flags override .env settings

### Implementation

**WeasyPrint Integration (converter.py):**

```python
def convert_file(
    self,
    input_path: Path,
    output_path: Path,
    toc_enabled: bool = False,
    metadata: Optional[Dict[str, str]] = None
) -> None:
    """Convert markdown file to PDF.

    Args:
        input_path: Path to input markdown file.
        output_path: Path where PDF will be saved.
        toc_enabled: Whether to generate table of contents.
        metadata: PDF metadata (title, author, subject, keywords).
    """
    # Convert markdown to HTML
    html = self.markdown.convert(markdown_content)
    document = HTML(string=html, base_url=str(input_path.parent))

    # Build metadata with smart defaults
    pdf_metadata = {
        'title': metadata.get('title') or input_path.stem,  # Filename fallback
        'author': metadata.get('author', ''),
        'subject': metadata.get('subject', ''),
        'keywords': metadata.get('keywords', ''),
    }

    # Write PDF with metadata
    document.write_pdf(output_path, pdf_metadata=pdf_metadata)
```

### Metadata Fields

**Standard PDF Metadata Fields:**

1. **Title** - Document title
   - Default: Filename without .md extension
   - Example: "User Guide" or "report.md" → "report"

2. **Author** - Document author/creator
   - Default: Empty
   - Example: "Jane Doe"

3. **Subject** - Document subject/description
   - Default: Empty
   - Example: "Technical Documentation"

4. **Keywords** - Comma-separated keywords
   - Default: Empty
   - Example: "markdown, pdf, documentation"

### Edge Cases

1. **Empty metadata** - Valid; PDFs can have empty metadata fields
2. **Very long values** - PDF spec allows long strings; no truncation needed
3. **Special characters** - WeasyPrint handles UTF-8 encoding automatically
4. **CLI overrides .env** - CLI values take precedence (explicit > implicit)
5. **Missing title** - Falls back to filename

## Component Changes

### Files to Modify

**1. src/md2pdf/config.py**

Add fields to Config dataclass:

```python
@dataclass
class Config:
    # ... existing fields ...

    # Headers/Footers
    enable_page_numbers: bool = False
    page_number_position: str = "center"  # left, center, right
    page_number_format: str = "Page {page} of {pages}"

    # PDF Metadata
    pdf_title: Optional[str] = None
    pdf_author: Optional[str] = None
    pdf_subject: Optional[str] = None
    pdf_keywords: Optional[str] = None
```

Update `Config.load()`:
- Load new fields from environment variables
- Validate `page_number_position` is one of: left, center, right
- Validate `page_number_format` contains only `{page}` and `{pages}` placeholders

**2. src/md2pdf/styles.py**

Add new function:

```python
def get_page_number_css(config: Config) -> str:
    """Generate CSS for page numbers in headers/footers.

    Args:
        config: Configuration with page number settings.

    Returns:
        CSS string for @page margin boxes, or empty string if disabled.
    """
    if not config.enable_page_numbers:
        return ""

    # Map position to CSS margin box
    position_map = {
        "left": "@bottom-left",
        "center": "@bottom-center",
        "right": "@bottom-right",
    }

    margin_box = position_map[config.page_number_position]

    # Convert format string to CSS content
    content = config.page_number_format
    content = content.replace("{page}", '" counter(page) "')
    content = content.replace("{pages}", '" counter(pages) "')

    return f"""
    {margin_box} {{
        content: "{content}";
        font-size: 9pt;
        color: #666;
        font-family: Arial, sans-serif;
    }}
    """
```

Modify `get_page_css()`:
- Add call to `get_page_number_css()` if enabled
- Append page number CSS to @page rule

**3. src/md2pdf/converter.py**

Add methods:

```python
class MarkdownConverter:
    # ... existing methods ...

    def extract_headers(self, document) -> List[Dict[str, Any]]:
        """Extract H1 and H2 headers with page numbers from PDF.

        Args:
            document: WeasyPrint Document object.

        Returns:
            List of dicts with keys: text, level, page, anchor_id
        """
        headers = []
        seen_ids = set()

        bookmarks = document.make_bookmark_tree()
        for bookmark in bookmarks:
            if bookmark.level in (1, 2):  # H1 and H2 only
                anchor_id = self.generate_anchor_id(bookmark.label, seen_ids)
                headers.append({
                    'text': bookmark.label,
                    'level': bookmark.level,
                    'page': bookmark.destination[0],  # Page number
                    'anchor_id': anchor_id,
                })

        return headers

    def generate_anchor_id(self, text: str, seen_ids: Set[str]) -> str:
        """Generate unique anchor ID from heading text."""
        # Convert to lowercase, replace spaces with hyphens
        base_id = text.lower().replace(" ", "-")
        # Remove special characters
        base_id = re.sub(r'[^a-z0-9-]', '', base_id)

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

    def generate_toc_html(self, headers: List[Dict[str, Any]]) -> str:
        """Generate HTML for table of contents.

        Args:
            headers: List of header dicts from extract_headers().

        Returns:
            HTML string for TOC.
        """
        if not headers:
            return ""

        toc_html = '<div class="toc">\n'
        toc_html += '    <h1>Table of Contents</h1>\n'
        toc_html += '    <ul>\n'

        for header in headers:
            css_class = f"toc-h{header['level']}"
            toc_html += f'        <li class="{css_class}">\n'
            toc_html += f'            <a href="#{header["anchor_id"]}">{header["text"]}</a>\n'
            toc_html += f'            <span class="toc-page">{header["page"]}</span>\n'
            toc_html += '        </li>\n'

        toc_html += '    </ul>\n'
        toc_html += '</div>\n'

        return toc_html

    def convert_file(
        self,
        input_path: Path,
        output_path: Path,
        toc_enabled: bool = False,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Convert markdown file to PDF.

        Args:
            input_path: Path to input markdown file.
            output_path: Path where PDF will be saved.
            toc_enabled: Whether to generate table of contents.
            metadata: PDF metadata dict (title, author, subject, keywords).
        """
        # Read and convert markdown
        markdown_content = input_path.read_text(encoding="utf-8")
        html_content = self.markdown.convert(markdown_content)

        if toc_enabled:
            # Two-pass rendering for TOC
            # Pass 1: Render to extract headers
            temp_doc = HTML(string=html_content, base_url=str(input_path.parent))
            headers = self.extract_headers(temp_doc)

            if not headers:
                console.print("[yellow]Warning:[/yellow] No H1/H2 headers found for TOC")
            else:
                # Pass 2: Render with TOC
                toc_html = self.generate_toc_html(headers)
                html_content = toc_html + html_content

        # Final render
        document = HTML(string=html_content, base_url=str(input_path.parent))

        # Build metadata with smart defaults
        pdf_metadata = {
            'title': (metadata or {}).get('title') or input_path.stem,
            'author': (metadata or {}).get('author', ''),
            'subject': (metadata or {}).get('subject', ''),
            'keywords': (metadata or {}).get('keywords', ''),
        }

        document.write_pdf(output_path, pdf_metadata=pdf_metadata)
```

**4. src/md2pdf/cli.py**

Add CLI flags:

```python
def main(
    input_path: Path = typer.Argument(...),
    # ... existing arguments ...

    # TOC flag
    toc: bool = typer.Option(
        False,
        "--toc/--no-toc",
        help="Generate table of contents from H1 and H2 headers",
    ),

    # Page numbers flag
    page_numbers: Optional[bool] = typer.Option(
        None,
        "--page-numbers/--no-page-numbers",
        help="Enable/disable page numbers (overrides .env)",
    ),

    # Metadata flags
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="PDF title (overrides .env, defaults to filename)",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        help="PDF author (overrides .env)",
    ),
    subject: Optional[str] = typer.Option(
        None,
        "--subject",
        help="PDF subject (overrides .env)",
    ),
    keywords: Optional[str] = typer.Option(
        None,
        "--keywords",
        help="PDF keywords, comma-separated (overrides .env)",
    ),
):
    """Convert markdown to PDF with optional TOC and metadata."""

    # Load config
    config = Config.load()

    # Apply CLI overrides
    if page_numbers is not None:
        config.enable_page_numbers = page_numbers

    # Build metadata dict
    metadata = {
        'title': title or config.pdf_title,
        'author': author or config.pdf_author,
        'subject': subject or config.pdf_subject,
        'keywords': keywords or config.pdf_keywords,
    }

    # Create converter with updated CSS
    converter = MarkdownConverter(config, css=final_css)

    # Convert with TOC if requested
    converter.convert_file(
        input_path,
        output_path,
        toc_enabled=toc,
        metadata=metadata
    )
```

**5. Theme CSS Files**

Add TOC styling to all 5 theme files:
- `src/md2pdf/themes/github.css`
- `src/md2pdf/themes/minimal.css`
- `src/md2pdf/themes/academic.css`
- `src/md2pdf/themes/dark.css`
- `src/md2pdf/themes/modern.css`

Each theme gets customized TOC styling that matches its aesthetic.

**6. .env.example**

Add new configuration options:

```bash
# Headers/Footers
ENABLE_PAGE_NUMBERS=false
PAGE_NUMBER_POSITION=center  # Options: left, center, right
PAGE_NUMBER_FORMAT=Page {page} of {pages}

# PDF Metadata
PDF_TITLE=
PDF_AUTHOR=
PDF_SUBJECT=
PDF_KEYWORDS=
```

## Testing Strategy

### Unit Tests

**test_config.py:**
- Test loading page number settings from .env
- Test validation of `page_number_position` (valid: left/center/right)
- Test validation of `page_number_format` (only {page} and {pages} allowed)
- Test loading metadata fields
- Test CLI overrides work correctly
- Test empty/missing config values use defaults

**test_styles.py:**
- Test `get_page_number_css()` generates correct CSS for each position
- Test page number format string interpolation
- Test disabled page numbers returns empty string
- Test invalid position raises error
- Test CSS output includes both @page setup and page numbers

**test_converter.py:**
- Test `extract_headers()` finds H1 and H2 tags
- Test `extract_headers()` ignores H3-H6
- Test `generate_anchor_id()` creates valid IDs
- Test `generate_anchor_id()` handles duplicates
- Test `generate_anchor_id()` sanitizes special characters
- Test `generate_toc_html()` creates valid HTML
- Test `generate_toc_html()` with empty headers returns empty string
- Test two-pass rendering produces PDF with TOC
- Test metadata passed to WeasyPrint correctly
- Test title defaults to filename when not set
- Test single-pass rendering (no TOC) still works

### Integration Tests

**test_integration.py:**
- Test convert with `--toc` flag produces PDF with TOC at start
- Test page numbers appear in correct position (test all 3: left/center/right)
- Test page numbers with different formats
- Test metadata fields appear in PDF properties (requires PDF inspection)
- Test combined features: TOC + page numbers + metadata work together
- Test backward compatibility: conversions without new flags unchanged
- Test TOC with all 5 themes (styling consistency)
- Test empty TOC (no headers) shows warning
- Test duplicate headers get unique anchors
- Test very long documents (100+ pages) work correctly

### Manual Testing Checklist

**Page Numbers:**
- [ ] Generate PDF with page numbers in left position
- [ ] Generate PDF with page numbers in center position
- [ ] Generate PDF with page numbers in right position
- [ ] Test custom format string
- [ ] Verify page numbers with all 5 themes
- [ ] Test with single page document (1 of 1)
- [ ] Test with long document (100+ pages)

**Table of Contents:**
- [ ] Generate PDF with `--toc` flag
- [ ] Verify TOC appears at start of document
- [ ] Click TOC links, verify navigation works
- [ ] Test document with no headers (warning shown)
- [ ] Test document with duplicate header text
- [ ] Test document with special characters in headers
- [ ] Verify TOC styling with all 5 themes
- [ ] Test long TOC (50+ headers)

**PDF Metadata:**
- [ ] Set metadata via .env, verify in PDF properties
- [ ] Set metadata via CLI flags, verify overrides work
- [ ] Verify title defaults to filename when not set
- [ ] Test all 4 fields (title, author, subject, keywords)
- [ ] Test with empty metadata (all fields optional)
- [ ] Verify Unicode in metadata fields

**Combined Features:**
- [ ] Test TOC + page numbers together
- [ ] Test TOC + page numbers + metadata together
- [ ] Test all features with all 5 themes

**Backward Compatibility:**
- [ ] Run existing test suite, verify all pass
- [ ] Convert examples directory without new flags
- [ ] Verify output identical to Phase 3

### Expected Test Coverage

**Current:** 89% (96 tests)
**Target:** 89%+ (111+ tests)
**New Tests:** ~15 tests

**Breakdown:**
- test_config.py: +3 tests (page numbers, metadata)
- test_styles.py: +2 tests (page number CSS)
- test_converter.py: +6 tests (TOC methods, metadata)
- test_integration.py: +4 tests (end-to-end features)

## Implementation Order

### Task 1: Page Numbers Foundation
**Goal:** Basic page number support in CSS

**Files:**
- `src/md2pdf/config.py` - Add page number config fields
- `src/md2pdf/styles.py` - Add `get_page_number_css()`
- `tests/test_config.py` - Test config loading
- `tests/test_styles.py` - Test CSS generation

**Deliverable:** Page numbers appear in PDFs (no CLI flag yet)

**Testing:**
- Unit tests for config and styles
- Manual: Verify page numbers in generated PDFs

---

### Task 2: Page Numbers CLI
**Goal:** Add CLI flags for page numbers

**Files:**
- `src/md2pdf/cli.py` - Add `--page-numbers/--no-page-numbers` flag
- `tests/test_cli.py` - Test flag parsing and override logic

**Deliverable:** Users can enable/disable page numbers via CLI

**Testing:**
- CLI flag tests
- Manual: Test flag overrides .env setting

---

### Task 3: PDF Metadata
**Goal:** Add metadata support

**Files:**
- `src/md2pdf/config.py` - Add metadata config fields
- `src/md2pdf/cli.py` - Add metadata CLI flags
- `src/md2pdf/converter.py` - Pass metadata to WeasyPrint
- `tests/test_config.py` - Test metadata loading
- `tests/test_converter.py` - Test metadata passing

**Deliverable:** PDF metadata can be set via .env or CLI

**Testing:**
- Unit tests for config and converter
- Manual: Verify metadata in PDF properties dialog

---

### Task 4: TOC Infrastructure
**Goal:** Build TOC generation methods

**Files:**
- `src/md2pdf/converter.py` - Add `extract_headers()` and `generate_toc_html()`
- `tests/test_converter.py` - Test header extraction and HTML generation

**Deliverable:** Internal methods for TOC (not exposed via CLI yet)

**Testing:**
- Unit tests for TOC methods
- Test anchor ID generation and sanitization

---

### Task 5: TOC Two-Pass Rendering
**Goal:** Integrate TOC into conversion pipeline

**Files:**
- `src/md2pdf/converter.py` - Implement two-pass logic in `convert_file()`
- `src/md2pdf/cli.py` - Add `--toc` flag
- `tests/test_integration.py` - End-to-end TOC tests

**Deliverable:** `--toc` flag generates TOC in PDF

**Testing:**
- Integration tests for TOC generation
- Manual: Verify TOC appears and links work

---

### Task 6: TOC Styling
**Goal:** Add TOC CSS to all themes

**Files:**
- `src/md2pdf/themes/github.css` - Add TOC styles
- `src/md2pdf/themes/minimal.css` - Add TOC styles
- `src/md2pdf/themes/academic.css` - Add TOC styles
- `src/md2pdf/themes/dark.css` - Add TOC styles
- `src/md2pdf/themes/modern.css` - Add TOC styles
- `tests/test_integration.py` - Test TOC with each theme

**Deliverable:** TOC styled consistently across all themes

**Testing:**
- Visual inspection of TOC with each theme
- Verify theme aesthetic is maintained

---

### Task 7: Documentation
**Goal:** Document new features

**Files:**
- `README.md` - Add new flags to usage section
- `docs/USAGE_GUIDE.md` - Add examples for each feature
- `docs/PHASE4_FEATURES.md` - Create comprehensive feature guide
- `.env.example` - Add new configuration options

**Deliverable:** Complete documentation for Phase 4 features

**Testing:**
- Verify examples in documentation work
- Check for typos and clarity

---

### Task 8: Integration Testing
**Goal:** Comprehensive end-to-end verification

**No new files** - Run full test suite and manual tests

**Deliverable:** All features working together, no regressions

**Testing:**
- Run full test suite (111+ tests)
- Complete manual testing checklist
- Test backward compatibility

---

## Implementation Rationale

**Order justification:**

1. **Page numbers first** - Simplest feature, builds confidence
2. **Metadata second** - Independent of other features, straightforward
3. **TOC third** - Most complex, benefits from having other features working
4. **Documentation last** - Can document all features together once complete

**Why two-pass for TOC?**
- WeasyPrint doesn't expose page numbers until PDF is rendered
- Alternative (PyPDF post-processing) adds dependency and complexity
- Two-pass is simpler and leverages existing WeasyPrint features

**Why page numbers only (no custom headers)?**
- YAGNI - Start simple, add complexity if users request it
- Page numbers cover 90% of use cases
- Can add custom headers in future phase if needed

## Success Criteria

- [ ] Page numbers appear at configured position (left/center/right)
- [ ] Page numbers respect format string template
- [ ] `--toc` flag generates table of contents with H1 and H2 headers
- [ ] TOC links navigate to correct sections in PDF
- [ ] TOC styled consistently across all 5 themes
- [ ] PDF metadata (title, author, subject, keywords) appears in PDF properties
- [ ] Metadata defaults to filename for title when not set
- [ ] CLI flags override .env settings correctly
- [ ] All features work together (TOC + page numbers + metadata)
- [ ] Backward compatible - existing conversions unchanged
- [ ] 111+ tests passing with 89%+ coverage
- [ ] Documentation complete and accurate
- [ ] No new dependencies added

## Open Questions

**Resolved:**
- ~~Should TOC be at start or end of document?~~ → Start (standard convention)
- ~~Should page numbers be in header or footer?~~ → Footer (less intrusive)
- ~~Should we support custom TOC depth?~~ → No, fixed at H1/H2 (YAGNI)
- ~~Should we support watch mode?~~ → No, deferred to Phase 5

**None remaining**

## Future Enhancements (Beyond Phase 4)

Potential features for Phase 5 or later:

1. **Watch Mode** - Auto-regenerate on file changes (deferred from Phase 4)
2. **Custom Headers** - Not just page numbers, but custom text/templates
3. **TOC Depth Configuration** - `--toc-depth` flag for user control
4. **Watermarks** - Background text/image on each page
5. **Header/Footer Per-Theme** - Themes define their own header/footer styling
6. **First Page Different** - Special header/footer for page 1 (title page)
7. **Odd/Even Page Headers** - Different headers for left/right pages
8. **Custom TOC Styling** - User-provided TOC CSS
9. **TOC Position** - Allow TOC at end instead of start
10. **PDF Bookmarks** - Generate PDF outline/bookmarks from headers

**Evaluation criteria for future additions:**
- Does it align with "simple and reliable" philosophy?
- Is there user demand?
- Does it maintain backward compatibility?
- Can it be implemented without major architectural changes?

## References

- [WeasyPrint Documentation - Paged Media](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html)
- [CSS Paged Media Specification](https://www.w3.org/TR/css-page-3/)
- [PDF Metadata Standards](https://wwwimages2.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf)
- [Markdown Extensions](https://python-markdown.github.io/extensions/)

## Version History

- **2026-02-09** - Initial design document created
- Status: Ready for implementation planning
