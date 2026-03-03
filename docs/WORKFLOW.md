# Development and Release Workflow

This document describes the workflow for developing and releasing verse-slides.

## Day-to-Day Development

Make changes, test, and commit as often as you like. No need to create releases for every change.

```bash
# 1. Make changes to code in your editor

# 2. Test locally with your virtual environment
cd ~/Documents/Projects/Personal/ESV\ Slides
source venv/bin/activate
python -m verse_slides.cli "John 3:16" --output-file test.pdf

# 3. Run tests (optional but recommended)
pytest

# 4. Commit changes
git add .
git commit -m "Description of your changes

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 5. Push to GitHub
git push origin main
```

**Important**: Changes pushed to `main` are NOT immediately available to Homebrew users. They only get updates when you create a release.

## Creating a Release

When you're ready to share your changes with users, tell Claude Code:

> "Create a release"

or

> "Create version 0.3.0"

Claude will automatically:

1. ✅ Update version numbers in `pyproject.toml` and `verse_slides/__init__.py`
2. ✅ Commit and push the version bump
3. ✅ Create and push a git tag (e.g., `v0.3.0`)
4. ✅ Create a GitHub release with release notes
5. ✅ Calculate the SHA256 hash of the release tarball
6. ✅ Update the Homebrew formula with new version and hash in the tap repository
7. ✅ Commit and push the formula update to the tap

## After Release

Users can now get your updates:

```bash
# New users
brew tap cmshinkle/verse-slides
brew install verse-slides

# Existing users
brew update
brew upgrade verse-slides
```

## Semantic Versioning Guide

Use semantic versioning for your releases: `MAJOR.MINOR.PATCH`

### Version Number Guidelines

- **PATCH** (0.2.1): Bug fixes only
  - Fixed a bug
  - Small documentation updates
  - No new features or breaking changes

- **MINOR** (0.3.0): New features (backwards-compatible)
  - Added new command-line flag
  - Added new Bible translation support
  - Added new output format
  - Enhanced existing functionality

- **MAJOR** (1.0.0): Breaking changes
  - Changed command-line interface
  - Removed or renamed flags
  - Changed config file format
  - Any change that requires users to modify their workflow

### Examples

- `v0.2.0` → `v0.2.1`: Fixed pagination bug
- `v0.2.1` → `v0.3.0`: Added NET Bible support
- `v0.9.0` → `v1.0.0`: First stable release
- `v1.2.0` → `v2.0.0`: Changed CLI flags (breaking change)

## When to Release?

Release whenever you feel the changes are worth sharing:

- **After bug fixes**: Users will appreciate getting fixes quickly
- **After new features**: Share new functionality when it's ready
- **When it makes sense**: No pressure to release immediately
- **Batch changes**: You can accumulate multiple changes before releasing

## Release Checklist

Before asking Claude to create a release:

- [ ] All changes committed and pushed to main
- [ ] Tests passing (`pytest`)
- [ ] Tested locally with `python -m verse_slides.cli`
- [ ] Ready to share changes with users

Then just say: **"Create a release"**

## Repository Structure

### Main Repository
**Location**: `cmshinkle/verse-slides`
- Contains the Python source code
- Git tags trigger releases when you create them

### Homebrew Tap Repository
**Location**: `cmshinkle/homebrew-verse-slides`
- Contains the Homebrew formula (`verse-slides.rb`)
- Automatically updated when you create a release
- Users install via `brew tap cmshinkle/verse-slides`

## Distribution

### Homebrew Installation
```bash
brew tap cmshinkle/verse-slides
brew install verse-slides
```

**Updates**: Users run `brew update && brew upgrade verse-slides`

## Troubleshooting

### "Version still shows old number"
Make sure both version strings are updated:
- `pyproject.toml`: `version = "0.3.0"`
- `verse_slides/__init__.py`: `__version__ = "0.3.0"`

### "Homebrew users aren't getting updates"
Check that:
1. Git tag was created and pushed
2. GitHub release was created
3. Homebrew formula points to the correct tag
4. SHA256 hash matches the release tarball
5. Users ran `brew update` before `brew upgrade`

## Additional Resources

- [RELEASE.md](RELEASE.md): Manual release process (if needed)
- [BACKLOG.md](BACKLOG.md): Planned features and enhancements
- [README.md](README.md): User-facing documentation
- [CLAUDE.md](CLAUDE.md): Technical documentation for Claude Code sessions
