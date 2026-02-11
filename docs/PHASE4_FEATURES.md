# Phase 4 Features Guide

Comprehensive guide to Phase 4 advanced features: page numbers, table of contents, title page, and PDF metadata.

## Overview

Phase 4 adds four professional document features while maintaining md2pdf's simplicity:

1. **Page Numbers** - Configurable footer page numbers
2. **Table of Contents** - Auto-generated from document headers
3. **Title Page** - Professional cover page with title, author, and date
4. **PDF Metadata** - Document properties (title, author, etc.)

All features are:
- **Opt-in** - Enable only what you need
- **Configurable** - Via .env or CLI flags
- **Theme-compatible** - Work with all 5 themes
- **Backward compatible** - Existing workflows unchanged

## Page Numbers

### Quick Start

```bash
# Enable page numbers
uv run md2pdf document.md --page-numbers
```

### Configuration

**Position:**
- `left` - Bottom left corner
- `center` - Bottom center (default)
- `right` - Bottom right corner

**Format:**
- Use `{page}` for current page number
- Use `{pages}` for total pages
- Default: `Page {page} of {pages}`

**.env Configuration:**

```bash
ENABLE_PAGE_NUMBERS=true
PAGE_NUMBER_POSITION=center
PAGE_NUMBER_FORMAT=Page {page} of {pages}
```

**CLI Flags:**

```bash
# Enable
uv run md2pdf document.md --page-numbers

# Disable (override .env)
uv run md2pdf document.md --no-page-numbers
```

### Examples

```bash
# Center position (default)
uv run md2pdf report.md --page-numbers

# Custom format via .env
echo 'PAGE_NUMBER_FORMAT={page}/{pages}' >> .env
uv run md2pdf report.md --page-numbers

# Left position
echo 'PAGE_NUMBER_POSITION=left' >> .env
uv run md2pdf report.md --page-numbers
```

### Styling

- Font size: 9pt (smaller than body text)
- Color: Gray (#666) - unobtrusive
- Position: Bottom of page
- Respects theme aesthetic

## Table of Contents

### Quick Start

```bash
# Generate TOC
uv run md2pdf document.md --toc
```

### How It Works

1. **Scans your document** for H1 and H2 headers
2. **Extracts header text and page numbers**
3. **Generates TOC** at the beginning of PDF
4. **Creates clickable links** to each section

### What Gets Included

- **H1 headers** - Top-level sections
- **H2 headers** - Subsections (indented)
- **H3-H6 ignored** - Only two levels for simplicity

### TOC Structure

```
Table of Contents

Introduction ........................ 1
  Background ........................ 2
Getting Started ..................... 3
  Installation ...................... 4
  Configuration ..................... 5
Advanced Topics ..................... 6
```

### Examples

```bash
# Basic TOC
uv run md2pdf documentation.md --toc

# TOC with page numbers
uv run md2pdf documentation.md --toc --page-numbers

# TOC with theme
uv run md2pdf documentation.md --toc --theme academic

# Complete professional document
uv run md2pdf report.md --toc --page-numbers --theme academic
```

### Edge Cases

**No headers found:**
- Warning displayed: "No H1/H2 headers found for TOC"
- PDF still generated without TOC

**Duplicate header text:**
- Anchors numbered automatically: `#introduction`, `#introduction-2`

**Special characters in headers:**
- Sanitized automatically for valid anchor IDs

### Theme Styling

Each theme styles the TOC to match its aesthetic:

- **GitHub**: Clean, familiar look
- **Minimal**: Extra spacing, light typography
- **Academic**: Formal, centered heading
- **Dark**: Light text on dark background
- **Modern**: Colorful accents, gradient background

## Title Page

### Quick Start

```bash
# Add title page
uv run md2pdf document.md --title-page --title "User Guide" --author "Jane Doe"
```

### How It Works

1. **Generates a full-page title** before all other content
2. **Displays three elements:**
   - **Title** - From `--title` or `.env` (falls back to "Untitled")
   - **Author** - From `--author` or `.env` (omitted if empty)
   - **Date** - Auto-generated in "Month DD, YYYY" format
3. **Page break after** - Content starts on the next page

### Rendering Order

When combined with TOC: **Title Page → TOC → Content**

### Examples

```bash
# Basic title page
uv run md2pdf report.md --title-page --title "Annual Report"

# Title page with author
uv run md2pdf report.md --title-page --title "Annual Report" --author "Company Name"

# Complete professional document
uv run md2pdf report.md --title-page --toc --page-numbers --title "Annual Report" --author "Company Name" --theme academic

# Merged document with title page
uv run md2pdf docs/ --merge --title-page --toc --title "User Guide" --author "Team"
```

### Theme Styling

Each theme styles the title page to match its aesthetic:

- **GitHub**: Clean with subtle border below title
- **Minimal**: Light weight fonts, generous spacing
- **Academic**: Formal, serif, centered
- **Dark**: Dark background with light text
- **Modern**: Gradient accent border matching modern style

### Edge Cases

**No title provided:**
- Falls back to "Untitled"

**No author provided:**
- Author line is omitted entirely

**Special characters in title/author:**
- Automatically escaped for security (HTML escaping)

## PDF Metadata

### Quick Start

```bash
# Via CLI
uv run md2pdf document.md --title "User Guide" --author "Jane Doe"
```

### Metadata Fields

**Title** - Document title
- Defaults to filename if not set
- Appears in PDF viewer title bar

**Author** - Document creator
- Optional (empty if not set)

**Subject** - Document description
- Optional (empty if not set)

**Keywords** - Comma-separated tags
- Optional (empty if not set)
- Used for PDF search/indexing

### Configuration

**.env:**

```bash
PDF_TITLE=User Guide
PDF_AUTHOR=Jane Doe
PDF_SUBJECT=Product Documentation
PDF_KEYWORDS=guide, manual, help
```

**CLI Flags:**

```bash
uv run md2pdf document.md \
    --title "User Guide" \
    --author "Jane Doe" \
    --subject "Documentation" \
    --keywords "guide, manual"
```

**CLI overrides .env** - Explicit values take precedence

### Examples

```bash
# Set title and author
uv run md2pdf report.md --title "Annual Report 2024" --author "Company Name"

# Full metadata
uv run md2pdf guide.md \
    --title "User Guide" \
    --author "Documentation Team" \
    --subject "Product Help" \
    --keywords "guide, manual, tutorial, help"

# Configure in .env for all documents
cat >> .env << EOF
PDF_AUTHOR=Your Name
PDF_KEYWORDS=documentation, markdown, pdf
EOF
```

### Viewing Metadata

1. Open PDF in any viewer (Adobe, Preview, etc.)
2. Open Properties dialog (usually in File menu)
3. Metadata appears in Document Properties

## Combining Features

All features work together seamlessly:

```bash
# Professional report with title page
uv run md2pdf annual_report.md \
    --title-page \
    --toc \
    --page-numbers \
    --title "Annual Report 2024" \
    --author "Company Name" \
    --subject "Financial Report" \
    --theme academic

# User documentation
uv run md2pdf user_guide.md \
    --title-page \
    --toc \
    --page-numbers \
    --title "User Guide v2.0" \
    --author "Documentation Team" \
    --keywords "guide, manual, tutorial" \
    --theme github

# Merged technical docs with title page
uv run md2pdf api_docs/ \
    --merge \
    --title-page \
    --toc \
    --page-numbers \
    --title "API Documentation" \
    --subject "Developer Guide" \
    --theme minimal
```

**Rendering order:** Title Page → Table of Contents → Content (with page numbers)

## Best Practices

### When to Use TOC

**Good use cases:**
- Long documents (5+ pages)
- Multi-chapter documents
- Technical documentation
- User guides and manuals

**Not recommended:**
- Short documents (1-2 pages)
- Documents without clear structure
- Documents with few headers

### When to Use Page Numbers

**Good use cases:**
- Any multi-page document
- Documents for printing
- Reports and formal documents
- Reference documentation

**Not recommended:**
- Single-page documents

### When to Use Title Page

**Good use cases:**
- Reports and formal documents
- Books and merged multi-file documents
- Documents for distribution
- Any document with clear title and author

**Not recommended:**
- Quick notes or drafts
- Single-page documents
- Internal working documents

### Metadata Tips

1. **Always set title** - More professional than filename
2. **Set author for shared documents** - Clarifies ownership
3. **Use keywords for searchable PDFs** - Better organization
4. **Keep metadata concise** - Clear and descriptive

## FAQ

**Q: Can I customize TOC depth?**
A: Not yet. Currently fixed at H1 and H2 for simplicity.

**Q: Can I style page numbers differently?**
A: Position and format are configurable. Color/font are fixed to avoid theme conflicts.

**Q: Does TOC affect page numbers?**
A: TOC pages are included in the page count. If TOC is 2 pages, your content starts on page 3.

**Q: Can I put page numbers in the header?**
A: Not yet. Currently only footer position is supported.

**Q: What if my headers have special characters?**
A: They're automatically sanitized for valid HTML anchor IDs.

**Q: Can I disable TOC for certain sections?**
A: No. TOC includes all H1 and H2 headers. Use H3-H6 for sections you want to exclude.

**Q: Can I customize the title page date format?**
A: Not yet. The date uses "Month DD, YYYY" format (e.g., "February 11, 2026").

**Q: Does the title page affect page numbering?**
A: Yes. The title page is page 1, so your content starts on a later page number.

**Q: What happens if I use --title-page without --title?**
A: The title falls back to "Untitled". Set a title with `--title` or `PDF_TITLE` in `.env`.

## Troubleshooting

**TOC links don't work:**
- Ensure using a PDF viewer that supports hyperlinks
- Try a different viewer (Adobe Reader, Preview, etc.)

**Page numbers not appearing:**
- Check `ENABLE_PAGE_NUMBERS=true` in .env
- Or use `--page-numbers` flag
- Verify PDF has multiple pages

**Metadata not visible:**
- Open Document Properties in your PDF viewer
- Some viewers hide empty fields

**TOC styling looks wrong:**
- Ensure using one of the 5 built-in themes
- Custom CSS may need TOC styles added

**Title page shows "Untitled":**
- Set a title with `--title "Your Title"` or `PDF_TITLE` in `.env`

**Title page author is missing:**
- Author is only shown if provided via `--author` or `PDF_AUTHOR` in `.env`

## See Also

- [THEMES.md](THEMES.md) - Theme customization guide
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Complete usage examples
- [README.md](../README.md) - Quick start guide
