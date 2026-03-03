# esv-slides Design Specification

A command-line tool that fetches scripture from the ESV API and generates presentation-ready PDFs for group scripture reading.

---

## Overview

**Purpose:** Automate the process of fetching scripture passages and formatting them for projection on a TV/screen in group settings (e.g., youth group, Bible study).

**Core workflow:**
1. User provides one or more scripture references
2. Tool fetches text from ESV.org API
3. Tool generates a paginated PDF with slides formatted for 16:9 display
4. User opens PDF on laptop/iPad and projects via HDMI or AirPlay

---

## Technical Stack

- **Language:** Python 3.x
- **PDF Generation:** ReportLab
- **HTTP Requests:** requests library
- **Config Parsing:** PyYAML
- **Font:** Open Sans (bundled or system-installed)

---

## Command-Line Interface

### Command Name
```
esv-slides
```

### Basic Usage
```bash
# Single passage
esv-slides "John 3:16-21"

# Multiple passages (space-separated arguments)
esv-slides "John 3:16-21" "Romans 8:28-30"

# Multiple passages (comma-separated)
esv-slides "John 3:16-21, Romans 8:28-30"

# From a text file (one reference per line)
esv-slides --file references.txt
```

### Command-Line Flags

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--file` | `-f` | Path to text file with references (one per line) | None |
| `--output` | `-o` | Custom output filename | Timestamp-based |
| `--output-dir` | `-d` | Output directory | Current working directory |
| `--separate` | `-s` | Generate separate PDFs for each passage | Combined PDF |
| `--no-headings` | | Exclude section headings | Include headings |
| `--font` | | Font family name | Open Sans |
| `--font-size` | | Font size in points | (See PDF Layout section) |
| `--open` | | Auto-open PDF after generation | No auto-open |
| `--help` | `-h` | Show help message | |
| `--version` | `-v` | Show version number | |

---

## Configuration

### Config File Location
```
~/.esv-slides/config.yaml
```

### Config File Structure
```yaml
# ESV API credentials
api_key: "your-esv-api-key-here"

# Output settings
output_directory: "."  # Current directory, or absolute path like ~/Documents/esv-slides/
output_type: "pdf"     # Future option: "google-slides"

# PDF appearance
font: "Open Sans"
font_size: 48          # Points (adjust based on testing)

# Behavior
auto_open: false
include_section_headings: true
combine_passages: true
```

### First Run Behavior
If config file does not exist:
1. Create `~/.esv-slides/` directory
2. Generate default `config.yaml` with placeholder API key
3. Print message instructing user to add their API key
4. Exit with instructions

---

## PDF Layout Specification

### Slide Dimensions
- **Aspect ratio:** 16:9 (widescreen)
- **Page size:** 1920 x 1080 points (or proportional for print quality)

### Color Scheme
- **Background:** Black (#000000)
- **Text:** White (#FFFFFF)

### Slide Types

#### 1. Title Slide (first slide of each passage)
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                                                     │
│                                                     │
│                   John 3:16-21                      │  <- Passage reference (centered)
│                                                     │
│                 Jesus and Nicodemus                 │  <- Section heading if applicable (centered, smaller)
│                                                     │
│                                                     │
│                                                     │
│  ESV                                                │  <- Attribution footer (bottom left, small)
└─────────────────────────────────────────────────────┘
```

#### 2. Scripture Slide (body slides)
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   ¹⁶For God so loved the world, that he gave his   │  <- Scripture text with superscript verse numbers
│   only Son, that whoever believes in him should    │
│   not perish but have eternal life. ¹⁷For God did  │
│   not send his Son into the world to condemn the   │
│   world, but in order that the world might be      │
│   saved through him.                               │
│                                                     │
│                                                     │
│  John 3:16-21 | ESV                                │  <- Footer: reference + attribution (bottom, small)
└─────────────────────────────────────────────────────┘
```

### Typography

#### Font
- **Family:** Open Sans
- **Body text:** Regular weight
- **Verse numbers:** Superscript (smaller size, raised baseline)
- **Title/reference:** Bold or Semi-Bold

#### Font Sizes (starting point—adjust based on testing)
- **Title slide reference:** 72pt
- **Title slide section heading:** 48pt
- **Body scripture text:** 48pt
- **Verse numbers:** 32pt (superscript)
- **Footer:** 24pt

#### Margins
- **Left/Right:** 100px (proportional)
- **Top:** 80px
- **Bottom:** 120px (accommodate footer)

### Text Flow Rules

1. **Fixed font size:** Font size remains constant; number of slides adjusts to fit content
2. **Verse breaks preferred:** When possible, break between verses, not mid-verse
3. **Mid-verse breaks allowed:** If a single verse exceeds slide capacity, break at a natural point (end of sentence or clause)
4. **Poetry formatting preserved:** Maintain line breaks and indentation for poetic passages (Psalms, Proverbs, prophets)

### Attribution Text
```
Scripture quotations are from the ESV® Bible (The Holy Bible, English Standard Version®), © 2001 by Crossway.
```
- Abbreviated on slides as "ESV" in footer
- Full attribution can be on final slide if needed (optional enhancement)

---

## ESV API Integration

### Endpoint
```
https://api.esv.org/v3/passage/text/
```

### Request Parameters
```python
params = {
    "q": "John 3:16-21",           # Passage reference
    "include-passage-references": False,  # We'll handle this ourselves
    "include-verse-numbers": True,
    "include-first-verse-numbers": True,
    "include-footnotes": False,
    "include-headings": True,      # Section headings (configurable)
    "include-short-copyright": False,  # We'll add our own attribution
    "indent-poetry": True,
    "indent-poetry-lines": 2,
    "line-length": 0               # No line wrapping from API
}
```

### Request Headers
```python
headers = {
    "Authorization": f"Token {api_key}"
}
```

### Response Handling
- Parse JSON response
- Extract `passages` array (typically one element)
- Extract `passage_meta` for canonical reference formatting
- Handle section headings if present

---

## Input Parsing

### Supported Input Formats

#### Direct Arguments
```bash
esv-slides "John 3:16-21"
esv-slides "John 3:16-21" "Romans 8:28-30" "Psalm 23"
```

#### Comma-Separated
```bash
esv-slides "John 3:16-21, Romans 8:28-30, Psalm 23"
```

#### File Input
```bash
esv-slides --file passages.txt
```

File format (one reference per line):
```
John 3:16-21
Romans 8:28-30
Psalm 23
```

### Reference Validation
- Validate format before API call if possible (basic regex)
- Rely on ESV API for authoritative validation
- Handle API error response for invalid references

---

## Output Handling

### Filename Generation

#### Combined PDF (default)
```
scripture_2024-01-15_1430.pdf
```
Format: `scripture_YYYY-MM-DD_HHMM.pdf`

#### Separate PDFs (with --separate flag)
```
John_3_16-21.pdf
Romans_8_28-30.pdf
```
Format: Sanitized passage reference (spaces → underscores, colons → underscores)

#### Custom Filename (with --output flag)
```bash
esv-slides "John 3:16-21" --output youth-group-week-3.pdf
```

### Output Location Priority
1. `--output-dir` flag if provided
2. `output_directory` from config if set
3. Current working directory

---

## Error Handling

All errors should:
1. Print a clear, user-friendly message to stderr
2. Log detailed error info to `~/.esv-slides/esv-slides.log`
3. Exit with non-zero exit code

### Error Categories and Responses

#### Config/Setup Errors

| Error | Message | Exit Code |
|-------|---------|-----------|
| Config file missing (first run) | "Config file created at ~/.esv-slides/config.yaml. Please add your ESV API key and run again." | 1 |
| Malformed YAML | "Config file has invalid YAML syntax at line X: [details]. Please fix and retry." | 1 |
| API key missing | "ESV API key not found in config. Add your key to ~/.esv-slides/config.yaml" | 1 |
| API key invalid (401) | "ESV API key is invalid. Please check your key at ~/.esv-slides/config.yaml" | 1 |

#### File System Errors

| Error | Message | Exit Code |
|-------|---------|-----------|
| Output directory doesn't exist | "Output directory '[path]' does not exist. Create it or specify a different path." | 1 |
| No write permission | "Cannot write to '[path]'. Check permissions or specify a different output directory." | 1 |
| Input file not found | "Input file '[path]' not found." | 1 |
| Input file empty | "Input file '[path]' is empty. Add scripture references (one per line)." | 1 |

#### Input Errors

| Error | Message | Exit Code |
|-------|---------|-----------|
| No reference provided | "No scripture reference provided. Usage: esv-slides \"John 3:16-21\"" | 1 |
| Invalid reference format | "Invalid reference '[ref]'. Use format like 'John 3:16-21' or 'Psalm 23'." | 1 |

#### API Errors

| Error | Message | Exit Code |
|-------|---------|-----------|
| API unreachable | "Cannot connect to ESV API. Check your internet connection and try again." | 1 |
| Rate limited (429) | "ESV API rate limit reached. Please wait a few minutes and try again." | 1 |
| Passage not found | "Passage '[ref]' not found. Check the reference and try again." | 1 |
| Empty response | "ESV API returned no text for '[ref]'. This may be an invalid reference." | 1 |
| Unexpected API error | "ESV API error: [status code]. See log for details." | 1 |

#### Font Errors

| Error | Message | Exit Code |
|-------|---------|-----------|
| Font not found | "Font '[name]' not found. Install it or specify a different font in config." | 1 |

### Log File Format
```
~/.esv-slides/esv-slides.log
```

Log entry format:
```
2024-01-15 14:30:22 [ERROR] API request failed: 401 Unauthorized
  URL: https://api.esv.org/v3/passage/text/
  Reference: John 3:16-21
  Response: {"detail": "Invalid token"}
```

---

## Project Structure

```
esv-slides/
├── esv_slides/
│   ├── __init__.py
│   ├── cli.py              # Argument parsing, main entry point
│   ├── config.py           # Config file loading/creation
│   ├── esv_api.py          # ESV API client
│   ├── pdf_generator.py    # ReportLab PDF creation
│   ├── text_processor.py   # Verse parsing, slide text splitting
│   └── utils.py            # Filename sanitization, logging setup
├── fonts/
│   └── OpenSans-Regular.ttf    # Bundled font (if not relying on system)
│   └── OpenSans-Bold.ttf
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_esv_api.py
│   ├── test_pdf_generator.py
│   └── test_text_processor.py
├── pyproject.toml          # Project metadata, dependencies
├── README.md
└── LICENSE
```

---

## Dependencies

```toml
[project]
dependencies = [
    "requests>=2.28.0",
    "reportlab>=4.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
```

---

## Future Enhancements (Out of Scope for MVP)

1. **Google Slides output** - Add `--format google-slides` option
2. **Additional translations** - Support other Bible APIs
3. **Caching** - Store previously fetched passages locally
4. **Preview mode** - Show how slides will break before generating
5. **Custom themes** - Allow different color schemes
6. **Verse range per slide control** - Let user specify max verses per slide

---

## Testing Considerations

### Key Test Cases

1. **Single verse:** `esv-slides "John 3:16"`
2. **Verse range:** `esv-slides "John 3:16-21"`
3. **Full chapter:** `esv-slides "Psalm 23"`
4. **Poetry passage:** `esv-slides "Psalm 1"`
5. **Long passage:** `esv-slides "Romans 8"` (verify multi-slide pagination)
6. **Multiple passages:** `esv-slides "John 3:16" "Romans 8:28"`
7. **Invalid reference:** `esv-slides "NotABook 99:99"`
8. **File input:** `esv-slides --file test-references.txt`

### Manual Verification
- Open generated PDFs on iPad
- Project to TV via AirPlay
- Verify readability from back of room
- Test annotation capability in PDF viewer

---

## Success Criteria

The tool is complete when:

1. ✅ Running `esv-slides "John 3:16-21"` produces a valid PDF
2. ✅ PDF has black background, white text, 16:9 aspect ratio
3. ✅ Title slide shows passage reference and section heading
4. ✅ Body slides have superscript verse numbers
5. ✅ Footer shows reference and ESV attribution on all slides
6. ✅ Poetry passages preserve formatting
7. ✅ Multiple passages combine into one PDF by default
8. ✅ `--separate` flag generates individual PDFs
9. ✅ Config file stores API key and preferences
10. ✅ All error cases produce clear messages and log entries
