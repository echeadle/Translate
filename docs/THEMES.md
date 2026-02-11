# md2pdf Themes Guide

## Overview

md2pdf includes 5 built-in themes for different use cases, plus support for custom CSS.

## Built-in Themes

### GitHub (Default)

**Use for:** Technical documentation, READMEs, general purpose

**Style:** Clean, professional, familiar GitHub markdown aesthetic

**Features:**
- Sans-serif fonts (Arial)
- Light gray code blocks
- Subtle borders on headers
- Table striping

```bash
uv run md2pdf document.md --theme github
# or just
uv run md2pdf document.md
```

### Minimal

**Use for:** Clean documents, presentations, modern reports

**Style:** Spacious, simple, maximum whitespace

**Features:**
- Modern font stack
- Light typography (font-weight 300-400)
- Minimal borders
- Increased line spacing
- Subtle backgrounds

```bash
uv run md2pdf document.md --theme minimal
```

### Academic

**Use for:** Research papers, formal documents, academic writing

**Style:** Traditional, serif fonts, formal

**Features:**
- Serif fonts (Palatino, Georgia)
- Justified text
- Traditional sizing (12pt body)
- Formal table borders
- Centered h1 headers

```bash
uv run md2pdf document.md --theme academic
```

### Dark

**Use for:** Dark mode preference, presentations, modern aesthetic

**Style:** Dark background with light text

**Features:**
- Dark gray background (#0d1117)
- Light text (#e6edf3)
- GitHub dark color palette
- High contrast for readability

```bash
uv run md2pdf document.md --theme dark
```

### Modern

**Use for:** Marketing materials, creative docs, contemporary design

**Style:** Bold, colorful, high visual impact

**Features:**
- Bold headers (font-weight 600-800)
- Colorful accents (blue, green, orange, purple)
- Gradient backgrounds
- Modern shadows
- Accent borders

```bash
uv run md2pdf document.md --theme modern
```

## Title Page & TOC Styling

All 5 built-in themes include matching styles for both title pages and table of contents. When you use `--title-page` or `--toc`, the output automatically matches your chosen theme.

If you use custom CSS (`--css`), you'll need to add `.title-page` and `.toc` styles yourself. Copy them from any built-in theme as a starting point:

```bash
# View the CSS for a theme
cat src/md2pdf/themes/github.css
```

## Custom CSS

### Using Custom CSS

Provide your own CSS file for complete control:

```bash
uv run md2pdf document.md --css mystyle.css
```

### CSS Structure

Your CSS file should NOT include `@page` rules (page size, margins). Those are configured via `.env`:

```css
/* ✅ GOOD - Visual styling only */
body {
    font-family: Georgia, serif;
    font-size: 12pt;
    color: #333;
}

h1 {
    color: #0066cc;
    font-weight: bold;
}

/* ❌ AVOID - Page setup is in .env */
@page {
    size: A4;  /* Configure via .env instead */
}
```

### Starting from a Theme

You can copy a built-in theme as a starting point:

```bash
# Themes are in src/md2pdf/themes/
cp src/md2pdf/themes/github.css my-custom-theme.css
# Edit my-custom-theme.css
uv run md2pdf document.md --css my-custom-theme.css
```

## Theme vs CSS

**You cannot use both `--theme` and `--css` together.** Choose one:

```bash
# ✅ Pick a theme
uv run md2pdf doc.md --theme academic

# ✅ Use custom CSS
uv run md2pdf doc.md --css mycss.css

# ❌ ERROR - Cannot use both
uv run md2pdf doc.md --theme academic --css mycss.css
```

**Why?** This keeps the mental model simple. You either:
1. Use a pre-made theme, OR
2. Bring your own complete stylesheet

## Page Setup vs Styling

**Page setup** (size, margins) is configured via `.env` and applies to ALL themes:

```bash
# .env
PDF_PAGE_SIZE=Letter
PDF_MARGIN_TOP=3cm
PDF_MARGIN_BOTTOM=3cm
```

**Visual styling** (fonts, colors, spacing) comes from themes or custom CSS.

This separation means:
- Change page size without changing visual style
- Switch themes without reconfiguring page setup
- Clean, predictable behavior

## Examples

### Technical Documentation

```bash
uv run md2pdf API_DOCS.md --theme github --create-output-dir docs
```

### Research Paper

```bash
# Configure for academic style first
echo "PDF_PAGE_SIZE=Letter" > .env
echo "PDF_MARGIN_TOP=2.54cm" >> .env

uv run md2pdf paper.md --theme academic --output paper.pdf
```

### Presentation Deck

```bash
uv run md2pdf slides.md --theme modern --create-output-dir presentation
```

### Personal Notes (Dark Mode)

```bash
uv run md2pdf notes.md --theme dark --create-output-dir notes
```

### Custom Branded Document

```bash
# Create company CSS with brand colors
cat > company.css << EOF
body { font-family: "Open Sans", sans-serif; }
h1, h2 { color: #00539f; /* Company blue */ }
a { color: #00539f; }
EOF

uv run md2pdf report.md --css company.css
```

## Tips

1. **Preview themes quickly:** Convert the same file with different themes to compare
   ```bash
   for theme in github minimal academic dark modern; do
       uv run md2pdf sample.md --theme $theme --create-output-dir theme_comparison
   done
   ```

2. **Mix page sizes with themes:** Themes work with any page size
   ```bash
   PDF_PAGE_SIZE=A3 uv run md2pdf poster.md --theme modern
   ```

3. **Start with a theme, customize later:** Use built-in themes initially, create custom CSS as needs evolve

## Migrating from Old Version

**Before Phase 3:** Font settings were in `.env`
```bash
# Old way (deprecated)
PDF_FONT_FAMILY=Georgia, serif
PDF_CODE_FONT=Monaco, monospace
```

**After Phase 3:** Use themes or custom CSS
```bash
# New way - pick a theme
uv run md2pdf doc.md --theme academic  # Has serif fonts

# Or create custom CSS
cat > mycss.css << EOF
body { font-family: Georgia, serif; }
code { font-family: Monaco, monospace; }
EOF
uv run md2pdf doc.md --css mycss.css
```

**Deprecation:** Old font settings still work but show warnings. They'll be removed in a future version.
