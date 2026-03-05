"""Tests for verse_slides.pdf_generator module."""

import pytest
import os
from pathlib import Path
from verse_slides.pdf_generator import (
    PDFGenerator,
    generate_pdf,
    SLIDE_WIDTH,
    SLIDE_HEIGHT,
)


@pytest.fixture
def temp_pdf_path(tmp_path):
    """Create a temporary PDF path for testing."""
    return str(tmp_path / "test_output.pdf")


@pytest.fixture
def sample_passage():
    """Create a sample passage for testing."""
    return {
        "reference": "John 3:16",
        "text": "[16] For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life.",
    }


@pytest.fixture
def sample_passage_with_heading():
    """Create a sample passage with section heading."""
    return {
        "reference": "Matthew 5:1-2",
        "text": "The Sermon on the Mount\n[1] Seeing the crowds, he went up on the mountain, and when he sat down, his disciples came to him. [2] And he opened his mouth and taught them, saying:",
    }


@pytest.fixture
def sample_poetry_passage():
    """Create a sample poetry passage (Psalm)."""
    return {
        "reference": "Psalm 23:1-2",
        "text": "[1] The Lord is my shepherd; I shall not want.\n  [2] He makes me lie down in green pastures.\n  He leads me beside still waters.",
    }


def test_pdf_generator_initialization(temp_pdf_path):
    """Test PDFGenerator initialization."""
    generator = PDFGenerator(temp_pdf_path)
    assert generator.output_path == temp_pdf_path
    assert generator.font == "Helvetica"
    assert generator.body_font_size == 64


def test_pdf_generator_custom_font(temp_pdf_path):
    """Test PDFGenerator with custom font."""
    generator = PDFGenerator(temp_pdf_path, font="Times-Roman")
    assert generator.font == "Times-Roman"


def test_pdf_generator_custom_font_size(temp_pdf_path):
    """Test PDFGenerator with custom font size."""
    generator = PDFGenerator(temp_pdf_path, font_size=72)
    assert generator.body_font_size == 72
    # Check that other sizes scale proportionally
    assert generator.verse_number_font_size == int(42 * (72 / 64))
    assert generator.title_font_size == int(72 * (72 / 64))


def test_pdf_generator_font_bold_map(temp_pdf_path):
    """Test that PDFGenerator has correct font bold mappings."""
    generator = PDFGenerator(temp_pdf_path)
    assert generator.font_bold_map["Helvetica"] == "Helvetica-Bold"
    assert generator.font_bold_map["Times-Roman"] == "Times-Bold"
    assert generator.font_bold_map["Courier"] == "Courier-Bold"


def test_get_bold_font_helvetica(temp_pdf_path):
    """Test _get_bold_font for Helvetica."""
    generator = PDFGenerator(temp_pdf_path, font="Helvetica")
    assert generator._get_bold_font() == "Helvetica-Bold"


def test_get_bold_font_times_roman(temp_pdf_path):
    """Test _get_bold_font for Times-Roman."""
    generator = PDFGenerator(temp_pdf_path, font="Times-Roman")
    assert generator._get_bold_font() == "Times-Bold"


def test_create_pdf_generates_file(temp_pdf_path, sample_passage):
    """Test that create_pdf generates a PDF file."""
    generator = PDFGenerator(temp_pdf_path)
    generator.create_pdf([sample_passage])

    assert os.path.exists(temp_pdf_path)
    assert os.path.getsize(temp_pdf_path) > 0


def test_create_pdf_multiple_passages(temp_pdf_path, sample_passage):
    """Test that create_pdf handles multiple passages."""
    passage2 = {
        "reference": "Romans 8:28",
        "text": "[28] And we know that for those who love God all things work together for good.",
    }

    generator = PDFGenerator(temp_pdf_path)
    generator.create_pdf([sample_passage, passage2])

    assert os.path.exists(temp_pdf_path)
    assert os.path.getsize(temp_pdf_path) > 0


def test_is_section_heading_true():
    """Test _is_section_heading with actual heading."""
    generator = PDFGenerator("test.pdf")
    assert generator._is_section_heading("The Sermon on the Mount") is True


def test_is_section_heading_false_with_verse_number():
    """Test _is_section_heading with verse text."""
    generator = PDFGenerator("test.pdf")
    assert generator._is_section_heading("[1] In the beginning") is False


def test_is_section_heading_false_with_indentation():
    """Test _is_section_heading with indented poetry."""
    generator = PDFGenerator("test.pdf")
    assert generator._is_section_heading("  He makes me lie down") is False


def test_is_section_heading_false_with_empty():
    """Test _is_section_heading with empty string."""
    generator = PDFGenerator("test.pdf")
    assert generator._is_section_heading("") is False


def test_is_poetry_true():
    """Test _is_poetry with poetry text."""
    generator = PDFGenerator("test.pdf")
    text = "[1] The Lord is my shepherd\n  [2] He makes me lie down"
    assert generator._is_poetry(text) is True


def test_is_poetry_false():
    """Test _is_poetry with regular prose."""
    generator = PDFGenerator("test.pdf")
    text = "[1] For God so loved the world"
    assert generator._is_poetry(text) is False


def test_parse_passage_elements_with_heading(sample_passage_with_heading):
    """Test _parse_passage_elements correctly identifies headings."""
    generator = PDFGenerator("test.pdf")
    elements = generator._parse_passage_elements(sample_passage_with_heading["text"])

    # Should have a heading element
    headings = [e for e in elements if e[0] == "heading"]
    assert len(headings) == 1
    assert headings[0][1] == "The Sermon on the Mount"


def test_parse_passage_elements_with_body_text(sample_passage):
    """Test _parse_passage_elements with body text."""
    generator = PDFGenerator("test.pdf")
    elements = generator._parse_passage_elements(sample_passage["text"])

    # Should have body elements
    body_elements = [e for e in elements if e[0] == "body"]
    assert len(body_elements) > 0


def test_parse_passage_elements_with_poetry(sample_poetry_passage):
    """Test _parse_passage_elements correctly identifies poetry."""
    generator = PDFGenerator("test.pdf")
    elements = generator._parse_passage_elements(sample_poetry_passage["text"])

    # Should have poetry elements
    poetry_elements = [e for e in elements if e[0] == "poetry"]
    assert len(poetry_elements) > 0


def test_generate_pdf_creates_file(tmp_path, sample_passage):
    """Test generate_pdf function creates PDF file."""
    output_dir = str(tmp_path)
    output_path = generate_pdf([sample_passage], output_dir=output_dir, output_filename="test.pdf")

    assert os.path.exists(output_path)
    assert output_path.endswith("test.pdf")


def test_generate_pdf_creates_directory(tmp_path, sample_passage):
    """Test generate_pdf creates output directory if it doesn't exist."""
    output_dir = str(tmp_path / "new_dir")
    assert not os.path.exists(output_dir)

    generate_pdf([sample_passage], output_dir=output_dir, output_filename="test.pdf")

    assert os.path.exists(output_dir)


def test_generate_pdf_with_custom_font(tmp_path, sample_passage):
    """Test generate_pdf with custom font."""
    output_dir = str(tmp_path)
    output_path = generate_pdf(
        [sample_passage],
        output_dir=output_dir,
        output_filename="test.pdf",
        font="Times-Roman"
    )

    assert os.path.exists(output_path)


def test_generate_pdf_with_custom_font_size(tmp_path, sample_passage):
    """Test generate_pdf with custom font size."""
    output_dir = str(tmp_path)
    output_path = generate_pdf(
        [sample_passage],
        output_dir=output_dir,
        output_filename="test.pdf",
        font_size=72
    )

    assert os.path.exists(output_path)


def test_generate_pdf_adds_pdf_extension(tmp_path, sample_passage):
    """Test generate_pdf adds .pdf extension if missing."""
    output_dir = str(tmp_path)
    output_path = generate_pdf(
        [sample_passage],
        output_dir=output_dir,
        output_filename="test"  # No extension
    )

    assert output_path.endswith(".pdf")


def test_generate_pdf_timestamp_filename(tmp_path, sample_passage):
    """Test generate_pdf generates timestamp-based filename when not provided."""
    output_dir = str(tmp_path)
    output_path = generate_pdf([sample_passage], output_dir=output_dir)

    assert "scripture_" in os.path.basename(output_path)
    assert output_path.endswith(".pdf")


def test_create_pdf_with_blank_end_page(temp_pdf_path, sample_passage):
    """Test that create_pdf with blank end page generates a valid PDF."""
    generator = PDFGenerator(temp_pdf_path)
    generator.create_pdf([sample_passage], add_blank_end_page=True)

    assert os.path.exists(temp_pdf_path)
    assert os.path.getsize(temp_pdf_path) > 0


def test_generate_pdf_with_blank_end_page(tmp_path, sample_passage):
    """Test generate_pdf with blank_end_page flag."""
    output_dir = str(tmp_path)
    output_path = generate_pdf(
        [sample_passage],
        output_dir=output_dir,
        output_filename="test.pdf",
        blank_end_page=True,
    )

    assert os.path.exists(output_path)


def test_wrap_text_single_line(temp_pdf_path):
    """Test _wrap_text with text that fits on one line."""
    generator = PDFGenerator(temp_pdf_path)
    generator.c = generator.c or type('obj', (object,), {
        'stringWidth': lambda self, text, font, size: len(text) * 10
    })()

    text = "Short text"
    wrapped = generator._wrap_text(text, 1000, "Helvetica", 64)

    assert len(wrapped) == 1
    assert wrapped[0] == "Short text"


def test_wrap_text_multiple_lines(temp_pdf_path):
    """Test _wrap_text wraps long text across multiple lines."""
    generator = PDFGenerator(temp_pdf_path)
    # Mock stringWidth to simulate width calculation
    class MockCanvas:
        def stringWidth(self, text, font, size):
            return len(text) * 10

    generator.c = MockCanvas()

    text = "This is a very long line of text that should be wrapped"
    wrapped = generator._wrap_text(text, 200, "Helvetica", 64)

    # Should be wrapped into multiple lines
    assert len(wrapped) > 1
