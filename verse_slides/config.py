"""Configuration management for verse-slides."""

import sys
from pathlib import Path
import yaml

from .utils import get_config_dir, get_config_file, setup_logging

logger = setup_logging()

DEFAULT_CONFIG = """# Bible API settings
api_endpoint: "https://api.esv.org/v3/passage/text/"  # API endpoint URL
api_key: "your-esv-api-key-here"  # ESV API key from https://api.esv.org

# Output settings
output_directory: "."  # Output directory for PDFs (current directory)
output_type: "pdf"     # Future option: "google-slides"

# PDF appearance
font: "Helvetica"      # Built-in font (can also use "Times-Roman", "Courier")
font_size: 64          # Points (adjust based on testing)

# Behavior
auto_open: false
include_section_headings: true
include_footnotes: false
include_passage_references: false
add_blank_end_page: false
include_title_slide: true
combine_passages: true
"""


class Config:
    """Configuration holder for verse-slides."""

    def __init__(self, data):
        self.api_endpoint = data.get("api_endpoint", "https://api.esv.org/v3/passage/text/")
        self.api_key = data.get("api_key", "")
        self.output_directory = data.get("output_directory", ".")
        self.output_type = data.get("output_type", "pdf")
        self.font = data.get("font", "Helvetica")
        self.font_size = data.get("font_size", 64)
        self.auto_open = data.get("auto_open", False)
        self.include_section_headings = data.get("include_section_headings", True)
        self.include_footnotes = data.get("include_footnotes", False)
        self.include_passage_references = data.get("include_passage_references", False)
        self.add_blank_end_page = data.get("add_blank_end_page", False)
        self.include_title_slide = data.get("include_title_slide", True)
        self.combine_passages = data.get("combine_passages", True)


def create_default_config():
    """Create default config file on first run.

    Returns:
        bool: True if config was created, False if it already existed
    """
    config_dir = get_config_dir()
    config_file = get_config_file()

    if config_file.exists():
        return False

    # Create directory
    config_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created config directory at {config_dir}")

    # Write default config
    config_file.write_text(DEFAULT_CONFIG)
    logger.info(f"Created default config file at {config_file}")

    return True


def load_config():
    """Load configuration from file.

    Returns:
        Config: Configuration object

    Raises:
        SystemExit: If config file doesn't exist or has errors
    """
    config_file = get_config_file()

    # Check if config exists
    if not config_file.exists():
        if create_default_config():
            print(f"Config file created at {config_file}")
            print("Please add your ESV API key and run again.")
            print("\nGet your free API key at: https://api.esv.org")
            logger.info("First run: created config file")
            sys.exit(1)

    # Load config
    try:
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        logger.info("Config file loaded successfully")
    except yaml.YAMLError as e:
        error_msg = f"Config file has invalid YAML syntax: {e}"
        print(f"Error: {error_msg}", file=sys.stderr)
        logger.error(f"YAML parse error: {e}")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Error reading config file: {e}"
        print(f"Error: {error_msg}", file=sys.stderr)
        logger.error(f"Config read error: {e}")
        sys.exit(1)

    if data is None:
        data = {}

    config = Config(data)

    # Validate API key
    if not config.api_key or config.api_key == "your-esv-api-key-here":
        print(f"Error: ESV API key not found in config.", file=sys.stderr)
        print(f"Please add your key to {config_file}", file=sys.stderr)
        print("\nGet your free API key at: https://api.esv.org")
        logger.error("API key missing or not configured")
        sys.exit(1)

    return config
