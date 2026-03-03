# Claude Code Prompt: Build esv-slides

## Project Overview

I want to build a Python CLI tool called `esv-slides` that fetches scripture from the ESV.org API and generates presentation-ready PDFs for projecting in group settings like Bible study or youth group.

The attached design spec (`esv-slides-design-spec.md`) contains all the detailed requirements. Please read it thoroughly before starting.

## Build Approach

1. **Start with the happy path first:** Get a working version that can take a single scripture reference and produce a PDF before adding error handling and edge cases.

2. **Build incrementally in this order:**
   - Config file creation and loading
   - ESV API client (fetch a passage, print it to console)
   - Basic PDF generation (single passage, single slide)
   - Multi-slide pagination with proper text flow
   - Title slides and footers
   - Poetry formatting preservation
   - Multiple passage support
   - File input support
   - All CLI flags
   - Comprehensive error handling and logging

3. **Test as you go:** After each major piece, show me how to test it so I can verify it's working before moving on.

## Key Technical Decisions (from the spec)

- **PDF library:** ReportLab
- **Config format:** YAML at `~/.esv-slides/config.yaml`
- **Font:** Open Sans (bundle it with the project if possible)
- **Slide size:** 16:9 aspect ratio (1920x1080 or proportional)
- **Colors:** Black background (#000000), white text (#FFFFFF)

## My Environment

- macOS
- Python 3.x installed
- I have an ESV API key ready

## Questions and Decisions

If you encounter ambiguity in the spec or need to make implementation decisions not covered, ask me before proceeding. I'd rather pause and clarify than have you guess wrong.

## What I'd Like First

Start by:
1. Setting up the project structure
2. Creating the config module (with first-run behavior that creates a template config file)
3. Creating a basic ESV API client that can fetch and print a passage

Once that's working, we'll move on to PDF generation.
