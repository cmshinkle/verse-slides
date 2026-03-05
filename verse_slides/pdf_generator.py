"""PDF generation for verse-slides."""

import os
from datetime import datetime
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from .utils import sanitize_filename, setup_logging

logger = setup_logging()

# Slide dimensions (16:9 aspect ratio)
SLIDE_WIDTH = 1920
SLIDE_HEIGHT = 1080

# Layout constants
MARGIN_LEFT = 150  # Increased from 100
MARGIN_RIGHT = 150  # Increased from 100
MARGIN_TOP = 150
MARGIN_BOTTOM = 120

# Font sizes (defaults - can be overridden in PDFGenerator)
TITLE_FONT_SIZE = 72
SECTION_HEADING_FONT_SIZE = 48
BODY_FONT_SIZE = 64  # Increased from 54
VERSE_NUMBER_FONT_SIZE = 42  # Increased proportionally
FOOTER_FONT_SIZE = 24

# Colors
BG_COLOR = colors.HexColor("#000000")  # Black
TEXT_COLOR = colors.HexColor("#FFFFFF")  # White
VERSE_NUMBER_COLOR = colors.HexColor("#FFFFFF")  # White for verse numbers


class PDFGenerator:
    """Generator for creating presentation PDF slides."""

    def __init__(self, output_path, font="Helvetica", font_size=64):
        """Initialize the PDF generator.

        Args:
            output_path: Path to save the PDF
            font: Font family to use (default: Helvetica)
            font_size: Body text font size in points (default: 64)
        """
        self.output_path = output_path
        self.font = font
        self.c = None

        # Font sizes - scale proportionally based on body font size
        # Default body font was 64pt, so calculate relative to that
        scale_factor = font_size / 64.0
        self.body_font_size = font_size
        self.verse_number_font_size = int(42 * scale_factor)  # Was 42pt
        self.title_font_size = int(72 * scale_factor)  # Was 72pt
        self.footer_font_size = int(24 * scale_factor)  # Was 24pt

        # Map base fonts to their bold variants
        self.font_bold_map = {
            "Helvetica": "Helvetica-Bold",
            "Times-Roman": "Times-Bold",
            "Courier": "Courier-Bold",
        }

    def _get_bold_font(self):
        """Get the bold variant of the current font.

        Returns:
            str: Bold font name
        """
        return self.font_bold_map.get(self.font, self.font + "-Bold")

    def create_pdf(self, passages, add_blank_end_page=False):
        """Create a PDF with slides for the given passages.

        Args:
            passages: List of passage dictionaries with 'text' and 'reference' keys
            add_blank_end_page: Whether to add a blank black page at the end
        """
        logger.info(f"Creating PDF at {self.output_path}")

        # Create canvas
        self.c = canvas.Canvas(
            self.output_path,
            pagesize=(SLIDE_WIDTH, SLIDE_HEIGHT)
        )

        for passage in passages:
            self._create_title_slide(passage)
            self._create_body_slides(passage)  # Changed to plural - creates multiple slides

        if add_blank_end_page:
            self._create_blank_slide()

        # Save PDF
        self.c.save()
        logger.info(f"PDF saved successfully: {self.output_path}")

    def _create_blank_slide(self):
        """Create a blank black slide."""
        self.c.setFillColor(BG_COLOR)
        self.c.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=True, stroke=False)
        self.c.showPage()

    def _create_title_slide(self, passage):
        """Create a title slide for a passage.

        Args:
            passage: Dictionary with 'text' and 'reference' keys
        """
        # Black background
        self.c.setFillColor(BG_COLOR)
        self.c.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=True, stroke=False)

        # White text
        self.c.setFillColor(TEXT_COLOR)

        # Draw passage reference (centered, large)
        self.c.setFont(self._get_bold_font(), self.title_font_size)
        reference = passage["reference"]
        ref_width = self.c.stringWidth(reference, self._get_bold_font(), self.title_font_size)
        ref_x = (SLIDE_WIDTH - ref_width) / 2
        ref_y = SLIDE_HEIGHT / 2
        self.c.drawString(ref_x, ref_y, reference)

        # Draw footer
        self._draw_footer("ESV® Bible © 2001 Crossway")

        # New page
        self.c.showPage()

    def _wrap_text(self, text, max_width, font_name, font_size):
        """Wrap text to fit within max_width.

        Args:
            text: Text to wrap
            max_width: Maximum width in points
            font_name: Font name
            font_size: Font size

        Returns:
            list: List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Try adding this word to current line
            test_line = ' '.join(current_line + [word])
            width = self.c.stringWidth(test_line, font_name, font_size)

            if width <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _is_section_heading(self, line):
        """Check if a line is a section heading.

        Args:
            line: Text line to check

        Returns:
            bool: True if line is a heading
        """
        import re
        # Headings don't have verse numbers, aren't empty, and aren't indented
        stripped = line.strip()
        # Check if line starts with leading spaces (poetry/indentation)
        has_leading_spaces = line and line[0] == ' '
        return bool(stripped and not re.search(r'\[\d+\]', stripped) and not has_leading_spaces)

    def _is_poetry(self, text):
        """Check if text contains poetry formatting (indented lines).

        Args:
            text: Text to check

        Returns:
            bool: True if text appears to be poetry
        """
        # Poetry has lines with leading spaces (indentation)
        lines = text.split('\n')
        for line in lines:
            # Check if line starts with spaces and has content
            if line and line[0] == ' ' and line.strip():
                return True
        return False

    def _parse_passage_elements(self, text):
        """Parse passage text into structured elements (headings, body text, and poetry lines).

        Args:
            text: Passage text

        Returns:
            list: List of tuples (element_type, content) where element_type is 'heading', 'body', or 'poetry'
        """
        lines = text.split("\n")
        elements = []
        current_body = []
        is_poetry_passage = self._is_poetry(text)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if self._is_section_heading(line):
                # Save any accumulated body text
                if current_body:
                    if is_poetry_passage:
                        # For poetry, each line is separate
                        for body_line in current_body:
                            elements.append(('poetry', body_line))
                    else:
                        # For prose, join into one body element
                        elements.append(('body', ' '.join(current_body)))
                    current_body = []
                # Add heading
                elements.append(('heading', stripped))
            else:
                # Accumulate body text (preserve original line with indentation for poetry)
                if is_poetry_passage:
                    current_body.append(line)  # Keep original indentation
                else:
                    current_body.append(stripped)

        # Add remaining body text
        if current_body:
            if is_poetry_passage:
                for body_line in current_body:
                    elements.append(('poetry', body_line))
            else:
                elements.append(('body', ' '.join(current_body)))

        return elements

    def _create_body_slides(self, passage):
        """Create body slides with scripture text, paginating as needed.

        Args:
            passage: Dictionary with 'text' and 'reference' keys
        """
        text = passage["text"]

        # Parse text into structured elements
        elements = self._parse_passage_elements(text)

        # Calculate available width
        available_width = SLIDE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

        # Process each element and create wrapped lines with type information
        formatted_lines = []
        for elem_type, content in elements:
            if elem_type == 'heading':
                # Headings are single lines, centered
                formatted_lines.append(('heading', content))
            elif elem_type == 'poetry':
                # Poetry lines need wrapping individually, preserving indentation
                stripped_text = content.lstrip(' ')
                leading_spaces = len(content) - len(stripped_text)

                # Wrap the poetry line (accounting for indentation reducing available width)
                indent_offset = leading_spaces * (self.body_font_size * 0.3)
                poetry_available_width = available_width - indent_offset

                wrapped = self._wrap_text(stripped_text, poetry_available_width, self.font, self.body_font_size)
                # Add back the indentation info to each wrapped line
                for i, line in enumerate(wrapped):
                    # Only first line gets the full indentation
                    if i == 0:
                        formatted_lines.append(('poetry', (leading_spaces, line)))
                    else:
                        # Continuation lines get no extra indent (or could add hanging indent)
                        formatted_lines.append(('poetry', (leading_spaces, line)))
            else:
                # Body text gets wrapped
                wrapped = self._wrap_text(content, available_width, self.font, self.body_font_size)
                for line in wrapped:
                    formatted_lines.append(('body', line))

        # Calculate spacing
        line_height = self.body_font_size * 1.5  # Line spacing
        available_height = SLIDE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

        logger.debug(f"Total formatted lines: {len(formatted_lines)}")

        # Smart pagination: build slides avoiding orphaned headings
        line_index = 0
        slide_num = 0
        while line_index < len(formatted_lines):
            current_slide = []
            lines_on_slide = 0

            while line_index < len(formatted_lines):
                line_item = formatted_lines[line_index]
                line_type = line_item[0]
                text = line_item[1]

                if line_type == 'heading':
                    # Heading takes 2 line heights: space before (if not first) + space after
                    # The heading itself is rendered at current y, then y moves down by line_height
                    lines_needed = 2 if len(current_slide) > 0 else 1  # No space before if first item

                    # Check if there's a body line after this heading
                    has_body_after = (line_index + 1 < len(formatted_lines) and
                                     formatted_lines[line_index + 1][0] == 'body')

                    if has_body_after:
                        # Need room for heading + at least one body line
                        total_needed = lines_needed + 1
                    else:
                        # Just need room for heading
                        total_needed = lines_needed

                    # Calculate available lines on slide
                    max_lines = int(available_height / line_height)

                    # If not enough room, start new slide (unless this is the first item on slide)
                    if lines_on_slide + total_needed > max_lines and len(current_slide) > 0:
                        logger.debug(f"Slide {slide_num}: Breaking before heading. Lines used: {lines_on_slide}/{max_lines}, needed: {total_needed}")
                        break

                    current_slide.append(line_item)  # Preserve original tuple
                    lines_on_slide += lines_needed

                else:  # body text or poetry
                    # Check if this line fits
                    max_lines = int(available_height / line_height)
                    if lines_on_slide + 1 > max_lines:
                        logger.debug(f"Slide {slide_num}: Breaking before {line_type}. Lines used: {lines_on_slide}/{max_lines}")
                        break

                    current_slide.append(line_item)  # Preserve original tuple
                    lines_on_slide += 1

                line_index += 1

            # Create slide with accumulated lines
            if current_slide:
                logger.debug(f"Slide {slide_num}: Creating slide with {len(current_slide)} items, {lines_on_slide} lines")
                self._create_single_body_slide_with_headings(current_slide, passage["reference"], line_height)
                slide_num += 1

    def _render_line_with_colored_verse_numbers(self, x, y, line):
        """Render a line with verse numbers in grey superscript and text in white.

        Args:
            x: X position
            y: Y position
            line: Text line to render

        Returns:
            float: Width of the rendered line
        """
        import re

        # Pattern to match verse numbers in brackets
        pattern = r'\[(\d+)\]'

        # Split line into segments
        segments = []
        last_end = 0

        for match in re.finditer(pattern, line):
            # Add text before verse number
            if match.start() > last_end:
                segments.append(('text', line[last_end:match.start()]))

            # Add verse number (without brackets)
            segments.append(('verse', match.group(1)))  # Just the number, not brackets
            last_end = match.end()

        # Add remaining text
        if last_end < len(line):
            segments.append(('text', line[last_end:]))

        # Render each segment with appropriate color and size
        current_x = x
        for seg_type, seg_text in segments:
            if seg_type == 'verse':
                # Verse numbers: grey, smaller, raised (superscript)
                self.c.setFillColor(VERSE_NUMBER_COLOR)
                self.c.setFont(self.font, self.verse_number_font_size)
                # Raise the baseline for superscript effect
                superscript_y = y + (self.body_font_size * 0.4)
                self.c.drawString(current_x, superscript_y, seg_text)
                current_x += self.c.stringWidth(seg_text, self.font, self.verse_number_font_size)
                # Reset font for next segment
                self.c.setFont(self.font, self.body_font_size)
            else:
                # Regular text: white, normal size
                self.c.setFillColor(TEXT_COLOR)
                self.c.drawString(current_x, y, seg_text)
                current_x += self.c.stringWidth(seg_text, self.font, self.body_font_size)

        return current_x - x

    def _create_single_body_slide_with_headings(self, formatted_lines, reference, line_height):
        """Create a single body slide with the given formatted lines.

        Args:
            formatted_lines: List of tuples (line_type, text) where line_type is 'heading' or 'body'
            reference: Scripture reference for footer
            line_height: Height of each line in points
        """
        # Black background
        self.c.setFillColor(BG_COLOR)
        self.c.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=True, stroke=False)

        # Render lines
        y = SLIDE_HEIGHT - MARGIN_TOP
        for i, line_item in enumerate(formatted_lines):
            line_type = line_item[0]

            if line_type == 'heading':
                text = line_item[1]
                # Add space before heading (unless it's the first line)
                if i > 0:
                    y -= line_height

                # Render heading centered and bold, same size as body text
                self.c.setFillColor(TEXT_COLOR)
                self.c.setFont(self._get_bold_font(), self.body_font_size)
                text_width = self.c.stringWidth(text, self._get_bold_font(), self.body_font_size)
                x = (SLIDE_WIDTH - text_width) / 2
                self.c.drawString(x, y, text)
                # Space after heading (same as before)
                y -= line_height
            elif line_type == 'poetry':
                # Render poetry line with preserved indentation
                # line_item[1] is a tuple: (leading_spaces, text)
                leading_spaces, poetry_text = line_item[1]
                # Each space is roughly 1/3 of the font size in width
                indent_offset = leading_spaces * (self.body_font_size * 0.3)

                self.c.setFont(self.font, self.body_font_size)
                self._render_line_with_colored_verse_numbers(MARGIN_LEFT + indent_offset, y, poetry_text)
                y -= line_height
            else:
                # Render body text left-aligned with colored verse numbers
                text = line_item[1]
                self.c.setFont(self.font, self.body_font_size)
                self._render_line_with_colored_verse_numbers(MARGIN_LEFT, y, text)
                y -= line_height

        # Draw footer
        self._draw_footer(f"{reference} | ESV® Bible © 2001 Crossway")

        # New page
        self.c.showPage()

    def _draw_footer(self, text):
        """Draw footer text at the bottom of the slide.

        Args:
            text: Footer text to display
        """
        self.c.setFont(self.font, self.footer_font_size)
        self.c.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 60, text)


def generate_pdf(passages, output_dir=".", output_filename=None, font="Helvetica", font_size=64,
                 blank_end_page=False):
    """Generate a PDF with slides for the given passages.

    Args:
        passages: List of passage dictionaries
        output_dir: Directory to save the PDF
        output_filename: Custom filename (optional)
        font: Font family to use
        font_size: Body text font size in points
        blank_end_page: Whether to add a blank black page at the end

    Returns:
        str: Path to the generated PDF
    """
    # Generate filename if not provided
    if output_filename:
        filename = output_filename if output_filename.endswith(".pdf") else output_filename + ".pdf"
    else:
        # Use timestamp-based filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"scripture_{timestamp}.pdf"

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, filename)

    # Create PDF
    generator = PDFGenerator(output_path, font=font, font_size=font_size)
    generator.create_pdf(passages, add_blank_end_page=blank_end_page)

    return output_path
