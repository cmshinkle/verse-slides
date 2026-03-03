# verse-slides

A command-line tool that fetches scripture and generates presentation-ready PDF slides for group scripture reading in youth groups, Bible studies, and church services.

Currently supports ESV (English Standard Version) via the ESV.org API.

**Tip:** You can use `vs` as a short alias for `verse-slides` in all commands below.

## Features

- **16:9 Widescreen Slides** - Perfect for modern displays and projectors
- **Beautiful Typography** - Large, readable text with clean layout
- **Poetry Formatting** - Preserves line breaks and indentation for Psalms and poetic passages
- **Section Headings** - Bold, centered headings for context
- **Smart Pagination** - Automatically splits long passages across multiple slides
- **Multiple Passages** - Combine multiple references into one presentation
- **Flexible Output** - Generate combined or separate PDFs
- **Highly Configurable** - Customize fonts, sizes, and output settings

## Installation

### Homebrew (Recommended for macOS)

```bash
# Add the tap
brew tap cmshinkle/verse-slides

# Install the tool
brew install verse-slides
```

### Install from Source (For Developers)

#### Prerequisites
- Python 3.8 or higher
- ESV API key (free at https://api.esv.org)

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/cmshinkle/verse-slides.git
   cd verse-slides
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install requests reportlab pyyaml
   ```

4. Run the tool:
   ```bash
   verse-slides "John 3:16"
   ```

## Quick Start

1. **First run** - Generate config file:
   ```bash
   verse-slides "John 3:16"
   ```
   This creates `~/.verse-slides/config.yaml`

2. **Add your API key** - Edit the config file:
   ```bash
   open ~/.verse-slides/config.yaml
   ```
   Replace `your-esv-api-key-here` with your actual API key from https://api.esv.org

3. **Generate slides**:
   ```bash
   verse-slides "John 3:16-21"
   ```
   Your PDF will be saved to the current directory

## Usage Examples

### Basic Usage

```bash
# Single verse
verse-slides "John 3:16"

# Verse range
verse-slides "John 3:16-21"

# Whole chapter
verse-slides "Psalm 23"

# Multiple passages (combined into one PDF)
verse-slides "John 3:16-21" "Romans 8:28-30"

# Comma-separated references
verse-slides "John 3:16, Romans 8:28, Psalm 23"
```

### File Input

Create a text file with one reference per line:

**references.txt:**
```
John 3:16-21
Romans 8:28-30
Psalm 23
Matthew 5:1-12
```

Then generate slides:
```bash
verse-slides --input-file references.txt
```

### Custom Output

```bash
# Custom filename
verse-slides "Psalm 23" --output-file sunday-sermon.pdf

# Custom output directory
verse-slides "John 3:16" --output-dir ~/Documents/Slides

# Separate PDFs for each passage
verse-slides "John 3:16" "Romans 8:28" --separate

# Auto-open PDF after generation
verse-slides "Psalm 23" --open
```

### Customization

```bash
# Different font
verse-slides "John 3:16" --font Times-Roman

# Custom font size (default: 64pt)
verse-slides "John 3:16" --font-size 72

# No section headings
verse-slides "Matthew 5:1-12" --no-headings

# Combine multiple options
verse-slides "Psalm 23" --font-size 80 --output-file large-psalm.pdf --open
```

## Command-Line Options

### Input Options

| Flag | Description |
|------|-------------|
| `references` | Scripture reference(s) as positional arguments |
| `-f, --input-file FILE` | Read references from a text file (one per line) |

### Output Options

| Flag | Description |
|------|-------------|
| `-o, --output-file FILE` | Custom output filename (default: `scripture_YYYY-MM-DD_HHMM.pdf`) |
| `-d, --output-dir DIR` | Output directory (default: current directory) |
| `-s, --separate` | Generate separate PDFs for each passage |
| `--open` | Auto-open PDF(s) after generation |

### Content Options

| Flag | Description |
|------|-------------|
| `--no-headings` | Exclude section headings from slides |

### Appearance Options

| Flag | Description |
|------|-------------|
| `--font NAME` | Font family (default: `Helvetica`; also supports `Times-Roman`, `Courier`) |
| `--font-size SIZE` | Body text font size in points (default: `64`) |

### Other Options

| Flag | Description |
|------|-------------|
| `-h, --help` | Show help message and exit |
| `-v, --version` | Show version number and exit |

## Configuration

Settings can be configured in `~/.verse-slides/config.yaml`:

```yaml
# Bible API settings
api_endpoint: "https://api.esv.org/v3/passage/text/"  # API endpoint URL
api_key: "your-esv-api-key-here"  # ESV API key from https://api.esv.org

# Output settings
output_directory: "."
output_type: "pdf"

# PDF appearance
font: "Helvetica"
font_size: 64

# Behavior
auto_open: false
include_section_headings: true
combine_passages: true
```

Command-line flags override config file settings.

## Slide Layout

### Title Slide
- Centered passage reference (e.g., "John 3:16–21")
- Black background, white text
- ESV attribution in footer

### Body Slides
- Large, readable text (64pt default)
- White superscript verse numbers
- Section headings (bold, centered)
- Smart pagination (headings always with at least one verse)
- Poetry formatting preserved (line breaks and indentation)
- Reference and ESV attribution in footer

## Getting an ESV API Key

1. Visit https://api.esv.org
2. Click "Get API Key"
3. Create a free account
4. Copy your API key
5. Add it to `~/.verse-slides/config.yaml`

The API key is free for personal and church use.

## Troubleshooting

### "Config file created" message
- The tool created a config file for you
- Add your ESV API key to `~/.verse-slides/config.yaml`
- Run the command again

### "ESV API key is invalid"
- Check that your API key is correct in the config file
- Ensure there are no extra spaces or quotes
- Get a new key at https://api.esv.org if needed

### PDF not opening automatically
- Use the `--open` flag
- Or set `auto_open: true` in your config file
- PDFs are always saved even if they don't auto-open

### Text is too small/large
- Use `--font-size` to adjust (try values between 48-80)
- Or update `font_size` in your config file

## Examples for Common Use Cases

### Youth Group
```bash
verse-slides "John 3:16-21" "Romans 5:8" --font-size 72 --open
```

### Bible Study Series
```bash
verse-slides --input-file romans-study.txt --separate --output-dir ~/RomansSeries
```

### Sunday Sermon
```bash
verse-slides "Matthew 5:1-20" --output-file sermon-beatitudes.pdf --font-size 64 --open
```

### Worship Service Readings
```bash
verse-slides "Psalm 23" "John 10:11-18" --output-file good-shepherd-readings.pdf
```

## License

MIT License

## Credits

Scripture quotations are from the ESV® Bible (The Holy Bible, English Standard Version®), copyright © 2001 by Crossway, a publishing ministry of Good News Publishers. Used by permission. All rights reserved.
