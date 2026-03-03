# verse-slides Backlog

This file tracks future features, enhancements, and ideas for the verse-slides project.

## Priority Legend

- 🔥 **High Priority** - Would add significant value
- 🔨 **Medium Priority** - Nice to have, moderate effort
- 💡 **Low Priority / Ideas** - Exploratory, long-term

---

## 🔥 High Priority

### NET Bible Translation Support

**Status:** Researched, Ready for Implementation

**Description:**
Add support for the NET (New English Translation) Bible as an alternative to ESV, with a CLI flag to select translation.

**Implementation Details:**

**NET Bible API:**
- Endpoint: `https://labs.bible.org/api/?passage=John+3:16&type=json`
- Response format: JSON array with one object per verse
  ```json
  [
    {
      "bookname": "John",
      "chapter": "3",
      "verse": "16",
      "text": "For this is the way God loved the world..."
    }
  ]
  ```

**Key Differences from ESV:**
- Returns JSON arrays (one object per verse)
- No verse numbers embedded in text (need to add `[16]` formatting)
- No section headings support
- Different copyright requirements

**NET Copyright Requirements:**
- Attribution: `"Scripture quoted by permission. Quotations designated (NET) are from the NET Bible® copyright ©1996, 2019 by Biblical Studies Press, L.L.C."`
- For apps with internet: NET must hyperlink to https://netbible.org
- Include sentence: "To see the NET Bible® study tool go to https://netbible.org"
- Non-commercial use allowed with attribution
- Text cannot be modified, altered, or changed

**Proposed Changes:**

1. **CLI Flag:**
   ```bash
   python -m verse_slides.cli "John 3:16" --translation net
   # or --version net
   ```

2. **Config Setting:**
   ```yaml
   bible_version: "esv"  # Options: esv, net
   ```

3. **Architecture:**
   - Create `BibleAPIFactory` to select the right API client
   - Create `NETAPIClient` alongside `ESVAPIClient`
   - Format NET verses with `[16]` style verse numbers for consistency
   - Adjust copyright attribution in PDF footers based on version
   - Update config.py to include `bible_version` setting

4. **Limitations for NET:**
   - No section headings (NET API doesn't provide them)
   - Poetry formatting may need adjustment (test with Psalms)

**Effort Estimate:** ~200-300 lines of code, ~20 new tests

**Resources:**
- [NET Bible Web Service (API)](https://labs.bible.org/api_web_service)
- [NET Bible Copyright](https://netbible.com/copyright/)
- [Bible.org Permissions](https://bible.org/permissions)

---

## 🔨 Medium Priority

### NIV (New International Version) Support

**Description:**
Add support for NIV translation. Requires research into NIV API availability and licensing.

**Notes:**
- NIV has more restrictive copyright than ESV/NET
- May require commercial license for digital distribution
- API availability unclear - need to research Biblica or Zondervan APIs
- Very popular translation, would be valuable for many users

**Next Steps:**
1. Research NIV API availability (API.Bible, Biblica)
2. Review NIV copyright requirements
3. Determine if licensing is feasible for open-source project

---

### Google Slides Export

**Description:**
Add support for exporting to Google Slides format instead of just PDF.

**Implementation Notes:**
- Config already has `output_type: "pdf"` placeholder for future formats
- Would use Google Slides API
- Requires OAuth authentication for user's Google account
- More complex than PDF generation

**Benefits:**
- Users can edit slides after generation
- Easy sharing and collaboration
- Cloud-based (no local files needed)

**Challenges:**
- Authentication complexity
- API rate limits
- Requires Google account

**Effort Estimate:** Significant (500+ lines), requires Google API integration

---

### CLI Flag: `--no-title-slide`

**Description:**
Add option to skip the title slide and start directly with body slides.

**Use Case:**
- When combining multiple passages, user may not want individual title slides
- Quick reference slides where title is unnecessary

**Implementation:**
```bash
python -m verse_slides.cli "John 3:16" --no-title-slide
```

**Effort Estimate:** Small (~20 lines)

---

### Slide Templates / Themes

**Description:**
Add support for different visual themes beyond the default black background.

**Potential Themes:**
- Dark (current): Black background, white text
- Light: White background, dark text
- Blue: Navy background, white text
- Custom: User-defined colors

**Implementation:**
```bash
python -m verse_slides.cli "John 3:16" --theme light
```

**Config:**
```yaml
theme: "dark"  # Options: dark, light, blue, custom
custom_background_color: "#000000"
custom_text_color: "#FFFFFF"
```

**Effort Estimate:** Medium (~100-150 lines)

---

## 💡 Low Priority / Ideas

### Verse-by-Verse Animation Support

**Description:**
Generate slides where each verse appears one at a time (good for presentations).

**Implementation:**
- Each verse gets its own slide
- Or progressive reveal within same slide (PDF doesn't support this, would need Google Slides)

---

### Multiple Language Support

**Description:**
Support for non-English Bible translations (Spanish, French, Chinese, etc.).

**Notes:**
- Would need to find APIs for various languages
- Each translation has its own copyright requirements
- UI/error messages could remain in English

---

### PowerPoint Export

**Description:**
Export to PowerPoint (.pptx) format using python-pptx library.

**Benefits:**
- Similar to Google Slides but offline
- Widely used in churches
- Editable after generation

---

### Background Images

**Description:**
Allow users to add background images to slides (subtle patterns, landscapes, etc.).

**Challenges:**
- Text readability over images
- Image licensing/copyright
- File size increases

---

### Verse Highlighting

**Description:**
Allow specific verses within a passage to be highlighted (different color, bold, etc.).

**Example:**
```bash
python -m verse_slides.cli "John 3:16-21" --highlight "16,17"
```

---

### Scripture Memory Mode

**Description:**
Generate slides with words progressively removed to aid memorization.

**Example:**
- Slide 1: Full verse
- Slide 2: Some words replaced with ___
- Slide 3: More words removed
- Slide 4: Just reference

---

### Batch Processing

**Description:**
Process multiple scripture lists from a directory of files at once.

**Example:**
```bash
python -m verse_slides.cli --batch-dir ./weekly-readings/ --output-dir ./output/
```

---

### CLI Completions

**Description:**
Add shell completion support for bash/zsh/fish.

**Implementation:**
- Use argcomplete or similar library
- Makes CLI more user-friendly

---

## Contributing Ideas

Have an idea for a feature? Add it to this backlog with:
- **Description:** What the feature does
- **Use Case:** Why it would be valuable
- **Implementation Notes:** (Optional) Technical thoughts

Then submit a pull request or open a GitHub issue!

---

## Completed Features

When items are implemented, move them here with the completion date.

### ✅ Configurable API Endpoint (2026-01-20)
Added `api_endpoint` config setting to support different Bible APIs in the future.

### ✅ Comprehensive Test Suite (2026-01-20)
88 tests with 85% coverage across all modules.

### ✅ Poetry Formatting (2026-01-20)
Automatic detection and preservation of poetry indentation and line breaks.

### ✅ Smart Pagination (2026-01-20)
Headings always appear with at least one verse (no orphaned headings).
