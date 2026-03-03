# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**verse-slides** is a Python CLI tool that fetches scripture from the ESV.org API and generates presentation-ready PDF slides (16:9 aspect ratio) for group scripture reading in youth groups, Bible studies, and church services.

The tool was designed with future extensibility in mind to potentially support additional Bible translations beyond ESV. The short alias `vs` can be used instead of `verse-slides` for convenience.

## Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests reportlab pyyaml

# Install dev dependencies for testing
pip install pytest pytest-cov pytest-mock responses

# Run the tool
python -m verse_slides.cli "John 3:16"
```

## Testing

```bash
# Run all tests (89 tests, 85% coverage)
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=verse_slides --cov-report=term-missing

# Run a single test file
pytest tests/test_pdf_generator.py

# Run a specific test
pytest tests/test_cli.py::test_parse_args_single_reference
```

## Architecture

### Module Structure

- **cli.py**: Command-line interface using argparse. Entry point for the application.
- **config.py**: Configuration management. Creates `~/.verse-slides/config.yaml` on first run.
- **esv_api.py**: ESV API client with comprehensive error handling (401, 429, timeouts, etc.).
- **pdf_generator.py**: PDF generation using ReportLab. Contains the core slide layout logic.
- **utils.py**: Utility functions (logging, path management, filename sanitization, config migration).

### Critical Design Decisions

#### 1. Smart Pagination Algorithm (pdf_generator.py:291-346)

The pagination system ensures section headings never appear orphaned (alone at the bottom of a slide without any verse text). Key logic:

- Headings require 2 line heights (space before + space after)
- When adding a heading, check if there's room for at least one body line after it
- If not enough room, break to new slide before adding the heading
- This prevents awkward heading placement and maintains visual coherence

#### 2. Poetry vs Prose Detection (pdf_generator.py:175-190, 192-239)

The tool automatically detects poetry (Psalms, etc.) by checking for lines with leading spaces (indentation):

- `_is_poetry()`: Returns True if any line starts with spaces
- Poetry lines preserve their original indentation and line breaks
- Each poetry line is wrapped individually while maintaining indent offset
- Prose text is joined into paragraphs and wrapped normally

**Important**: Section headings are identified as lines WITHOUT verse numbers (`[1]`, `[2]`, etc.) and WITHOUT leading spaces. Empty strings must return `False` (not empty string).

#### 3. Font Size Scaling (pdf_generator.py:52-58)

All font sizes scale proportionally based on the body font size:
- Default body: 64pt
- Verse numbers: 42pt (superscript, white)
- Title: 72pt
- Footer: 24pt

Scale factor = `font_size / 64.0`, then multiply all sizes by this factor.

#### 4. Configuration System (config.py)

- User config lives at `~/.verse-slides/config.yaml`
- First run creates default config with template API key
- CLI flags override config file settings
- Config validation happens in `load_config()` (exits with error code 1 if API key missing)
- Auto-migration: `utils.py:migrate_config_dir()` moves `~/.scripture-slides/` to `~/.verse-slides/` on first run

### PDF Slide Layout Constants

```python
SLIDE_WIDTH = 1920      # 16:9 aspect ratio
SLIDE_HEIGHT = 1080
MARGIN_LEFT = 150       # Increased for better readability
MARGIN_RIGHT = 150
MARGIN_TOP = 150
MARGIN_BOTTOM = 120
```

**Color scheme**: Black background (#000000), white text (#FFFFFF), white superscript verse numbers.

### Bible API Integration

**Configurable endpoint**: The API endpoint is configurable via `api_endpoint` in `~/.verse-slides/config.yaml`. This allows support for different Bible translation APIs in the future.

Default endpoint: `https://api.esv.org/v3/passage/text/` (ESV API)

The `ESVAPIClient` class (esv_api.py) accepts an `api_endpoint` parameter:
```python
client = ESVAPIClient(api_key, api_endpoint=custom_url, include_headings=True)
```

Key API parameters:
- `include-verse-numbers: True` - Verse numbers in `[1]` format
- `include-headings: True/False` - Section headings (e.g., "The Sermon on the Mount")
- `indent-poetry: True` - Poetry indentation with 2 spaces per level
- `line-length: 0` - No API-side line wrapping (we handle it)

The API returns canonical references (e.g., "John 3:16–21" with en-dash). Use this for display.

## Common Development Workflows

### Testing Text Rendering

Use Psalm 23 for poetry formatting and Matthew 5:1-12 for headings + pagination:

```bash
python -m verse_slides.cli "Psalm 23" --output-file test-psalm.pdf --open
python -m verse_slides.cli "Matthew 5:1-12" --output-file test-sermon.pdf --open
```

### Testing Multiple Passages

```bash
python -m verse_slides.cli "John 3:16" "Romans 8:28" --separate
```

### Running with Custom Fonts

Supported fonts: `Helvetica` (default), `Times-Roman`, `Courier`

Bold variants are mapped in `pdf_generator.py:61-65`:
```python
self.font_bold_map = {
    "Helvetica": "Helvetica-Bold",
    "Times-Roman": "Times-Bold",
    "Courier": "Courier-Bold",
}
```

## Important Implementation Notes

### Text Wrapping (pdf_generator.py:124-157)

The `_wrap_text()` method splits text by words and measures width using ReportLab's `stringWidth()`. It does NOT split mid-word. For poetry, wrapping accounts for indentation offset.

### Verse Number Rendering (pdf_generator.py:348-400)

Verse numbers in brackets `[16]` are rendered as white superscript:
1. Parse line with regex to find `\[\d+\]`
2. Split into segments (text vs verse numbers)
3. Render verse numbers at `y + (body_font_size * 0.4)` (raised baseline)
4. Render with `verse_number_font_size` (smaller than body text)

### Error Handling Philosophy

All modules use `sys.exit(1)` for fatal errors (invalid API key, connection failures, etc.) with clear user-facing error messages printed to stderr. Logging goes to `~/.verse-slides/verse-slides.log`.

## Git Workflow

```bash
# Stage changes
git add -A

# Commit (always include co-author)
git commit -m "Your commit message

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

## Configuration File Location

User config: `~/.verse-slides/config.yaml`
Log file: `~/.verse-slides/verse-slides.log`

**Note**: The config directory was renamed from `.scripture-slides` to `.verse-slides`. Auto-migration handles this transparently on first run. The `.gitignore` excludes this directory.

## Known Limitations

- Only supports ESV translation (extensible to others in future)
- PDF only (no Google Slides yet, though `output_type` config exists for future)
- Assumes three built-in ReportLab fonts (Helvetica, Times-Roman, Courier)
- Auto-open (`--open` flag) uses macOS `open` command (may need adjustment for Windows/Linux)

## Test Coverage

Current coverage: **85%** (89 tests)

Most uncovered lines are in:
- CLI display/output code (hard to test without capturing stdout)
- Edge cases in pagination (complex slide-building logic)
- Error handling branches that require specific external failures
