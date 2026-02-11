# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-02-10

### Added

#### Core Conversion (Phase 1)
- Markdown to PDF conversion pipeline (Markdown → HTML → Styled HTML + CSS → PDF)
- Single file and directory conversion
- Output directory organization with `--create-output-dir` (auto-timestamped or named)
- Directory structure preservation
- Configuration via `.env` file (page size, margins, fonts)
- Rich terminal output with progress indicators

#### Image Support (Phase 2)
- Embedded image support for PNG, JPEG, SVG, and GIF
- Images resolved relative to markdown file location
- Fully embedded in PDF for portable output
- Clear error messages for missing images

#### Custom Styling (Phase 3)
- 5 built-in themes: github (default), minimal, academic, dark, modern
- `--theme` flag for built-in theme selection
- `--css` flag for custom stylesheet support
- Clean separation of page setup (.env) and styling (themes/CSS)
- Deprecated legacy font settings in `.env` with deprecation warnings

#### Advanced Features (Phase 4)
- Page numbers with configurable position (left/center/right) and format
- Table of Contents generation from H1/H2 headers with clickable links
- PDF metadata support (title, author, subject, keywords) via CLI and `.env`
- TOC styled per-theme across all 5 built-in themes
- HTML escaping for security in TOC headers and PDF titles

#### Testing & Quality (Phase 5)
- 165 tests with 97% code coverage
- Comprehensive test suite covering all modules
- Unit, integration, and edge case tests
