"""Tests for verse_slides.cli module."""

import pytest
import sys
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from verse_slides.cli import parse_args, get_references


def test_parse_args_single_reference():
    """Test parse_args with single reference."""
    with patch("sys.argv", ["verse-slides", "John 3:16"]):
        args = parse_args()
        assert args.references == ["John 3:16"]


def test_parse_args_multiple_references():
    """Test parse_args with multiple references."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "Romans 8:28"]):
        args = parse_args()
        assert args.references == ["John 3:16", "Romans 8:28"]


def test_parse_args_input_file():
    """Test parse_args with input file flag."""
    with patch("sys.argv", ["verse-slides", "-f", "refs.txt"]):
        args = parse_args()
        assert args.file == "refs.txt"


def test_parse_args_input_file_long_form():
    """Test parse_args with --input-file flag."""
    with patch("sys.argv", ["verse-slides", "--input-file", "refs.txt"]):
        args = parse_args()
        assert args.file == "refs.txt"


def test_parse_args_output_file():
    """Test parse_args with output file flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "-o", "custom.pdf"]):
        args = parse_args()
        assert args.output == "custom.pdf"


def test_parse_args_output_file_long_form():
    """Test parse_args with --output-file flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--output-file", "custom.pdf"]):
        args = parse_args()
        assert args.output == "custom.pdf"


def test_parse_args_output_dir():
    """Test parse_args with output directory flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "-d", "~/output"]):
        args = parse_args()
        assert args.output_dir == "~/output"


def test_parse_args_output_dir_long_form():
    """Test parse_args with --output-dir flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--output-dir", "~/output"]):
        args = parse_args()
        assert args.output_dir == "~/output"


def test_parse_args_separate_flag():
    """Test parse_args with --separate flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "-s"]):
        args = parse_args()
        assert args.separate is True


def test_parse_args_separate_long_form():
    """Test parse_args with --separate flag (long form)."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--separate"]):
        args = parse_args()
        assert args.separate is True


def test_parse_args_no_headings_flag():
    """Test parse_args with --no-headings flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--no-headings"]):
        args = parse_args()
        assert args.no_headings is True


def test_parse_args_font_flag():
    """Test parse_args with --font flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--font", "Times-Roman"]):
        args = parse_args()
        assert args.font == "Times-Roman"


def test_parse_args_font_size_flag():
    """Test parse_args with --font-size flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--font-size", "72"]):
        args = parse_args()
        assert args.font_size == 72


def test_parse_args_open_flag():
    """Test parse_args with --open flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--open"]):
        args = parse_args()
        assert args.open is True


def test_parse_args_footnotes_flag():
    """Test parse_args with --footnotes flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--footnotes"]):
        args = parse_args()
        assert args.footnotes is True


def test_parse_args_refs_flag():
    """Test parse_args with --refs flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--refs"]):
        args = parse_args()
        assert args.refs is True


def test_parse_args_blank_end_page_flag():
    """Test parse_args with --blank-end-page flag."""
    with patch("sys.argv", ["verse-slides", "John 3:16", "--blank-end-page"]):
        args = parse_args()
        assert args.blank_end_page is True


def test_parse_args_no_references_exits():
    """Test parse_args exits when no references provided."""
    with patch("sys.argv", ["verse-slides"]):
        with pytest.raises(SystemExit):
            parse_args()


def test_parse_args_multiple_flags_combined():
    """Test parse_args with multiple flags combined."""
    with patch("sys.argv", [
        "verse-slides",
        "John 3:16",
        "-o", "custom.pdf",
        "--font-size", "80",
        "--open",
        "--no-headings"
    ]):
        args = parse_args()
        assert args.references == ["John 3:16"]
        assert args.output == "custom.pdf"
        assert args.font_size == 80
        assert args.open is True
        assert args.no_headings is True


def test_get_references_single_arg():
    """Test get_references with single reference argument."""
    args = MagicMock()
    args.references = ["John 3:16"]
    args.file = None

    refs = get_references(args)
    assert refs == ["John 3:16"]


def test_get_references_multiple_comma_separated():
    """Test get_references with multiple comma-separated references."""
    args = MagicMock()
    args.references = ["John 3:16,", "Romans 8:28"]
    args.file = None

    refs = get_references(args)
    assert refs == ["John 3:16", "Romans 8:28"]


def test_get_references_comma_separated():
    """Test get_references with comma-separated references."""
    args = MagicMock()
    args.references = ["John 3:16, Romans 8:28, Psalm 23"]
    args.file = None

    refs = get_references(args)
    assert refs == ["John 3:16", "Romans 8:28", "Psalm 23"]


def test_get_references_unquoted_single():
    """Test get_references with unquoted single reference (split by shell)."""
    args = MagicMock()
    args.references = ["John", "3:16"]
    args.file = None

    refs = get_references(args)
    assert refs == ["John 3:16"]


def test_get_references_unquoted_multiple_comma_separated():
    """Test get_references with unquoted comma-separated references."""
    args = MagicMock()
    args.references = ["John", "3:16,", "Romans", "8:28"]
    args.file = None

    refs = get_references(args)
    assert refs == ["John 3:16", "Romans 8:28"]


def test_get_references_unquoted_numbered_book():
    """Test get_references with unquoted numbered book like 1 John."""
    args = MagicMock()
    args.references = ["1", "John", "3:16"]
    args.file = None

    refs = get_references(args)
    assert refs == ["1 John 3:16"]


def test_get_references_from_file(tmp_path):
    """Test get_references reading from file."""
    # Create test file
    ref_file = tmp_path / "refs.txt"
    ref_file.write_text("John 3:16\nRomans 8:28\nPsalm 23\n")

    args = MagicMock()
    args.references = []
    args.file = str(ref_file)

    refs = get_references(args)
    assert refs == ["John 3:16", "Romans 8:28", "Psalm 23"]


def test_get_references_from_file_with_empty_lines(tmp_path):
    """Test get_references from file with empty lines."""
    ref_file = tmp_path / "refs.txt"
    ref_file.write_text("John 3:16\n\nRomans 8:28\n\n\nPsalm 23\n")

    args = MagicMock()
    args.references = []
    args.file = str(ref_file)

    refs = get_references(args)
    assert refs == ["John 3:16", "Romans 8:28", "Psalm 23"]


def test_get_references_from_file_not_found():
    """Test get_references exits when file not found."""
    args = MagicMock()
    args.references = []
    args.file = "nonexistent.txt"

    with pytest.raises(SystemExit) as exc_info:
        get_references(args)

    assert exc_info.value.code == 1


def test_get_references_from_empty_file(tmp_path):
    """Test get_references exits when file is empty."""
    ref_file = tmp_path / "refs.txt"
    ref_file.write_text("")

    args = MagicMock()
    args.references = []
    args.file = str(ref_file)

    with pytest.raises(SystemExit) as exc_info:
        get_references(args)

    assert exc_info.value.code == 1


def test_get_references_combined_args_and_file(tmp_path):
    """Test get_references with both args and file."""
    ref_file = tmp_path / "refs.txt"
    ref_file.write_text("Psalm 23\n")

    args = MagicMock()
    args.references = ["John 3:16,", "Romans 8:28"]
    args.file = str(ref_file)

    refs = get_references(args)
    # Should include both args and file references
    assert "John 3:16" in refs
    assert "Romans 8:28" in refs
    assert "Psalm 23" in refs
    assert len(refs) == 3


def test_get_references_strips_whitespace(tmp_path):
    """Test get_references strips whitespace from file lines."""
    ref_file = tmp_path / "refs.txt"
    ref_file.write_text("  John 3:16  \n  Romans 8:28\n")

    args = MagicMock()
    args.references = []
    args.file = str(ref_file)

    refs = get_references(args)
    assert refs == ["John 3:16", "Romans 8:28"]


@patch("verse_slides.cli.load_config")
@patch("verse_slides.cli.ESVAPIClient")
@patch("verse_slides.cli.generate_pdf")
def test_main_basic_flow(mock_generate_pdf, mock_api_client, mock_load_config):
    """Test main function basic flow."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.api_key = "test-key"
    mock_config.include_section_headings = True
    mock_config.output_directory = "./output"
    mock_config.font = "Helvetica"
    mock_config.font_size = 64
    mock_config.auto_open = False
    mock_load_config.return_value = mock_config

    mock_client = MagicMock()
    mock_client.fetch_passage.return_value = {
        "reference": "John 3:16",
        "text": "[16] For God so loved the world...",
    }
    mock_api_client.return_value = mock_client

    mock_generate_pdf.return_value = "./output/test.pdf"

    # Import main here to avoid premature execution
    from verse_slides.cli import main

    with patch("sys.argv", ["verse-slides", "John 3:16"]):
        main()

    # Verify API client was called
    mock_client.fetch_passage.assert_called_once_with("John 3:16")

    # Verify PDF generation was called
    assert mock_generate_pdf.called
