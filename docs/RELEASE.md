# How to Create a Release

This guide walks through manually creating a new release of verse-slides on GitHub.

**Recommended approach:** Just ask Claude Code to "Create a release" - it will handle all steps automatically.

**This document:** Manual process if you need to do it yourself.

## Before You Release

1. **Make sure all changes are committed and pushed**
   ```bash
   git status  # Should show "nothing to commit, working tree clean"
   git push origin main
   ```

2. **Test that everything works**
   ```bash
   source venv/bin/activate
   pytest  # All tests should pass
   verse-slides "John 3:16" --output-file test.pdf
   ```

3. **Update version numbers** (required)
   - Edit `pyproject.toml` and update the version number
     - Example: `version = "0.1.0"` → `version = "0.2.0"`
   - Edit `verse_slides/__init__.py` and update `__version__`
     - Example: `__version__ = "0.1.0"` → `__version__ = "0.2.0"`
   - Commit and push:
     ```bash
     git add pyproject.toml verse_slides/__init__.py
     git commit -m "Bump version to 0.2.0"
     git push origin main
     ```

## Creating a Release on GitHub

### Step 1: Create and Push a Git Tag

Tags mark specific points in your repository's history. Each release needs a tag.

```bash
# Create a tag (use semantic versioning: v0.1.0, v0.2.0, v1.0.0, etc.)
git tag v0.1.0

# Push the tag to GitHub
git push origin v0.1.0
```

**Tag naming convention:**
- `v0.1.0` - First release
- `v0.2.0` - Minor feature additions
- `v1.0.0` - Major milestone
- `v0.1.1` - Bug fix release

### Step 2: Create the Release on GitHub

1. **Go to your repository on GitHub**
   - https://github.com/cmshinkle/verse-slides

2. **Click "Releases"** (on the right sidebar)

3. **Click "Draft a new release"**

4. **Fill in the release form:**

   - **Choose a tag:** Select the tag you just pushed (e.g., `v0.1.0`)

   - **Release title:** Give it a descriptive name
     - Example: `v0.1.0 - Initial Release`
     - Example: `v0.2.0 - NET Bible Support`

   - **Description:** Write release notes describing what's new
     ```markdown
     ## What's New

     - Added support for custom fonts
     - Fixed pagination issue with long passages
     - Improved poetry formatting for Psalms

     ## Installation

     Download `verse-slides` below and follow the instructions in README.md

     ## Requirements

     - macOS 10.15 or later
     - ESV API key (free at https://api.esv.org)
     ```

5. **Click "Publish release"**

### Step 3: Update the Homebrew Formula

Once you publish the release:

1. **Calculate the SHA256 hash** of the release tarball:
   ```bash
   curl -sL https://github.com/cmshinkle/verse-slides/archive/refs/tags/v0.1.0.tar.gz | shasum -a 256
   ```

2. **Update the Homebrew formula** in your tap repository:
   - Repository: `https://github.com/cmshinkle/homebrew-verse-slides`
   - File: `verse-slides.rb`
   - Update the `url` to point to the new tag
   - Update the `sha256` with the hash from step 1

3. **Test the formula locally**:
   ```bash
   brew uninstall verse-slides  # If already installed
   brew install --build-from-source verse-slides
   verse-slides "John 3:16"
   ```

4. **Commit and push the formula update**:
   ```bash
   git add verse-slides.rb
   git commit -m "Update to v0.1.0"
   git push origin main
   ```

5. **Users can now upgrade**:
   ```bash
   brew update
   brew upgrade verse-slides
   ```

## Quick Release Checklist

- [ ] All changes committed and pushed
- [ ] Tests passing (`pytest`)
- [ ] Version numbers updated in `pyproject.toml` and `verse_slides/__init__.py`
- [ ] Git tag created and pushed (`git tag v0.1.0 && git push origin v0.1.0`)
- [ ] Release created on GitHub with descriptive notes
- [ ] SHA256 hash calculated for release tarball
- [ ] Homebrew formula updated in tap repository
- [ ] Formula changes committed and pushed
- [ ] Tested installation: `brew uninstall verse-slides && brew install verse-slides`

## Troubleshooting

### "Tag already exists"
If you need to redo a release:
```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin :refs/tags/v0.1.0

# Create the tag again
git tag v0.1.0
git push origin v0.1.0
```

### "brew install fails"
Common issues:
1. **SHA256 mismatch**: Recalculate the hash and update the formula
   ```bash
   curl -sL https://github.com/cmshinkle/verse-slides/archive/refs/tags/vX.Y.Z.tar.gz | shasum -a 256
   ```
2. **URL not found**: Make sure the git tag exists and the GitHub release is published
3. **Syntax error in formula**: Run `brew audit verse-slides` to check
4. **Missing dependencies**: Ensure Python 3.8+ is available

### "Users aren't getting the update"
Users need to run:
```bash
brew update                      # Update Homebrew and tap info
brew upgrade verse-slides # Upgrade to latest version
```

If still not working, they can reinstall:
```bash
brew uninstall verse-slides
brew install verse-slides
```

## Example Release Notes Template

```markdown
# verse-slides v0.1.0

Initial release of verse-slides - a CLI tool to generate presentation-ready PDF slides from scripture passages.

## Features

- ESV Bible support via ESV.org API
- 16:9 widescreen slides with beautiful typography
- Poetry formatting for Psalms
- Smart pagination with section headings
- Configurable fonts and sizes
- Multiple output options

## Installation

**Homebrew (Recommended):**
```bash
brew tap cmshinkle/verse-slides
brew install verse-slides
```

**Setup:**
1. Get free ESV API key: https://api.esv.org
2. First run creates config at `~/.verse-slides/config.yaml`
3. Add your API key to the config file

**Usage:**
```bash
verse-slides "John 3:16"
verse-slides "Psalm 23" --font-size 72 --open
```

## Requirements

- macOS (or Linux with Homebrew)
- Python 3.8+ (installed automatically by Homebrew)
- ESV API key (free)

## Known Issues

None

## What's Next

See [BACKLOG.md](BACKLOG.md) for planned features.
```

## Semantic Versioning Guide

**MAJOR.MINOR.PATCH** (e.g., 1.2.3)

- **MAJOR** (1.0.0): Breaking changes - Changes that require users to update their workflow
- **MINOR** (0.2.0): New features - Backwards-compatible functionality additions
- **PATCH** (0.1.1): Bug fixes - Backwards-compatible bug fixes

**Examples:**
- `v0.1.0` → `v0.1.1`: Fixed a bug
- `v0.1.0` → `v0.2.0`: Added NET Bible support
- `v0.9.0` → `v1.0.0`: First stable release
- `v1.2.0` → `v2.0.0`: Changed CLI flags (breaking change)

## Deleting a Release

If you need to delete a release:

1. Go to the Releases page
2. Click on the release
3. Click "Delete" (top right)
4. Delete the tag:
   ```bash
   git push origin :refs/tags/v0.1.0
   git tag -d v0.1.0
   ```

## Resources

- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Semantic Versioning](https://semver.org/)
- [Writing Good Release Notes](https://github.com/phauer/blog-related/blob/master/release-notes/release-notes.md)
