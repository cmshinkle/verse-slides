"""Command-line interface for verse-slides."""

import sys
import os
import subprocess
import argparse
from . import __version__
from .config import load_config
from .esv_api import ESVAPIClient
from .pdf_generator import generate_pdf
from .utils import setup_logging, sanitize_filename

logger = setup_logging()


def parse_args():
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate presentation-ready PDF slides from scripture passages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  verse-slides "John 3:16-21"
  verse-slides "John 3:16-21" "Romans 8:28-30"
  verse-slides --input-file references.txt
  verse-slides "Psalm 23" --output-file my-slides.pdf
  verse-slides "Romans 8" --font-size 72 --separate
        """
    )

    parser.add_argument(
        "references",
        nargs="*",
        help="Scripture reference(s) to generate slides for"
    )

    parser.add_argument(
        "-f", "--input-file",
        dest="file",
        metavar="FILE",
        help="Read scripture references from a text file (one reference per line)"
    )

    parser.add_argument(
        "-o", "--output-file",
        dest="output",
        metavar="FILE",
        help="Custom output filename (default: scripture_YYYY-MM-DD_HHMM.pdf)"
    )

    parser.add_argument(
        "-d", "--output-dir",
        metavar="DIR",
        help="Directory where PDFs will be saved (default: ./output/)"
    )

    parser.add_argument(
        "-s", "--separate",
        action="store_true",
        help="Generate a separate PDF file for each passage instead of combining them"
    )

    parser.add_argument(
        "--no-headings",
        action="store_true",
        help="Exclude section headings from slides (e.g., 'The Beatitudes')"
    )

    parser.add_argument(
        "--font",
        metavar="NAME",
        help="Font family to use (default: Helvetica; also supports Times-Roman, Courier)"
    )

    parser.add_argument(
        "--font-size",
        type=int,
        metavar="SIZE",
        help="Body text font size in points (default: 64; other sizes scale proportionally)"
    )

    parser.add_argument(
        "--open",
        action="store_true",
        help="Automatically open the generated PDF(s) after creation"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"verse-slides {__version__}"
    )

    args = parser.parse_args()

    # Validate that we have at least one reference source
    if not args.references and not args.file:
        parser.print_help()
        print("\nError: No scripture reference provided.", file=sys.stderr)
        print('Usage: verse-slides "John 3:16-21"', file=sys.stderr)
        sys.exit(1)

    return args


def get_references(args):
    """Extract references from arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        list: List of scripture references
    """
    references = []

    # Get references from command-line arguments
    if args.references:
        for ref in args.references:
            # Handle comma-separated references
            if "," in ref:
                references.extend([r.strip() for r in ref.split(",")])
            else:
                references.append(ref)

    # Get references from file
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_refs = [line.strip() for line in f if line.strip()]
                if not file_refs:
                    print(f"Error: Input file '{args.file}' is empty.", file=sys.stderr)
                    print("Add scripture references (one per line).", file=sys.stderr)
                    logger.error(f"Empty input file: {args.file}")
                    sys.exit(1)
                references.extend(file_refs)
        except FileNotFoundError:
            print(f"Error: Input file '{args.file}' not found.", file=sys.stderr)
            logger.error(f"Input file not found: {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            logger.error(f"Error reading input file: {e}")
            sys.exit(1)

    return references


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    config = load_config()

    # Get references to process
    references = get_references(args)
    logger.info(f"Processing {len(references)} reference(s)")

    # Override config with command-line arguments if provided
    include_headings = not args.no_headings if args.no_headings else config.include_section_headings
    output_dir = args.output_dir if args.output_dir else config.output_directory
    font = args.font if args.font else config.font
    font_size = args.font_size if args.font_size else config.font_size
    auto_open = args.open if args.open else config.auto_open

    # Create API client
    client = ESVAPIClient(config.api_key, api_endpoint=config.api_endpoint, include_headings=include_headings)

    # Fetch all passages
    print(f"Fetching {len(references)} passage(s)...")
    passages = []
    for ref in references:
        logger.info(f"Fetching: {ref}")
        result = client.fetch_passage(ref)
        passages.append(result)
        print(f"  ✓ {result['reference']}")

    # Generate PDF(s)
    print(f"\nGenerating PDF(s)...")

    if args.separate:
        # Generate separate PDFs for each passage
        generated_files = []
        for passage in passages:
            # Create filename from reference
            filename = sanitize_filename(passage['reference']) + ".pdf"
            output_path = generate_pdf([passage], output_dir, filename, font, font_size)
            generated_files.append(output_path)
            print(f"  ✓ {output_path}")

        print(f"\nSuccessfully generated {len(generated_files)} PDF(s)!")

        # Auto-open first PDF if requested
        if auto_open and generated_files:
            subprocess.run(["open", generated_files[0]])

    else:
        # Generate combined PDF
        filename = args.output if args.output else None
        output_path = generate_pdf(passages, output_dir, filename, font, font_size)
        print(f"  ✓ {output_path}")

        print(f"\nSuccessfully generated PDF: {output_path}")

        # Auto-open if requested
        if auto_open:
            subprocess.run(["open", output_path])


if __name__ == "__main__":
    main()
