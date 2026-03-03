"""Tests for verse_slides.config module."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import yaml

from verse_slides.config import Config, create_default_config, load_config, DEFAULT_CONFIG


def test_config_initialization_with_defaults():
    """Test Config class initialization with empty data."""
    config = Config({})
    assert config.api_endpoint == "https://api.esv.org/v3/passage/text/"
    assert config.api_key == ""
    assert config.output_directory == "."
    assert config.output_type == "pdf"
    assert config.font == "Helvetica"
    assert config.font_size == 64
    assert config.auto_open is False
    assert config.include_section_headings is True
    assert config.combine_passages is True


def test_config_initialization_with_values():
    """Test Config class initialization with provided values."""
    data = {
        "api_endpoint": "https://custom-api.example.com/v1/text/",
        "api_key": "test-key-123",
        "output_directory": "/custom/output",
        "output_type": "pdf",
        "font": "Times-Roman",
        "font_size": 72,
        "auto_open": True,
        "include_section_headings": False,
        "combine_passages": False,
    }
    config = Config(data)
    assert config.api_endpoint == "https://custom-api.example.com/v1/text/"
    assert config.api_key == "test-key-123"
    assert config.output_directory == "/custom/output"
    assert config.font == "Times-Roman"
    assert config.font_size == 72
    assert config.auto_open is True
    assert config.include_section_headings is False
    assert config.combine_passages is False


def test_create_default_config_creates_directory(tmp_path, monkeypatch):
    """Test that create_default_config creates config directory."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"

    # Mock the utility functions
    monkeypatch.setattr("verse_slides.config.get_config_dir", lambda: config_dir)
    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    result = create_default_config()

    assert result is True
    assert config_dir.exists()
    assert config_file.exists()


def test_create_default_config_writes_default_content(tmp_path, monkeypatch):
    """Test that create_default_config writes correct default content."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"

    monkeypatch.setattr("verse_slides.config.get_config_dir", lambda: config_dir)
    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    create_default_config()

    content = config_file.read_text()
    assert "api_key: \"your-esv-api-key-here\"" in content
    assert "output_directory: \".\"" in content
    assert "font: \"Helvetica\"" in content
    assert "font_size: 64" in content


def test_create_default_config_returns_false_if_exists(tmp_path, monkeypatch):
    """Test that create_default_config returns False if config already exists."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"
    config_dir.mkdir()
    config_file.write_text("existing config")

    monkeypatch.setattr("verse_slides.config.get_config_dir", lambda: config_dir)
    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    result = create_default_config()
    assert result is False


def test_load_config_creates_default_on_first_run(tmp_path, monkeypatch):
    """Test that load_config creates default config on first run."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"

    monkeypatch.setattr("verse_slides.config.get_config_dir", lambda: config_dir)
    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    with pytest.raises(SystemExit) as exc_info:
        load_config()

    assert exc_info.value.code == 1
    assert config_file.exists()


def test_load_config_exits_if_api_key_not_set(tmp_path, monkeypatch):
    """Test that load_config exits if API key is not configured."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"
    config_dir.mkdir()

    # Write config with default API key
    config_file.write_text(DEFAULT_CONFIG)

    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    with pytest.raises(SystemExit) as exc_info:
        load_config()

    assert exc_info.value.code == 1


def test_load_config_loads_valid_config(tmp_path, monkeypatch):
    """Test that load_config successfully loads valid configuration."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"
    config_dir.mkdir()

    # Write valid config
    valid_config = {
        "api_key": "valid-test-key-12345",
        "output_directory": "./test-output",
        "font": "Times-Roman",
        "font_size": 72,
    }
    config_file.write_text(yaml.dump(valid_config))

    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    config = load_config()

    assert isinstance(config, Config)
    assert config.api_key == "valid-test-key-12345"
    assert config.output_directory == "./test-output"
    assert config.font == "Times-Roman"
    assert config.font_size == 72


def test_load_config_handles_invalid_yaml(tmp_path, monkeypatch):
    """Test that load_config handles invalid YAML syntax."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"
    config_dir.mkdir()

    # Write invalid YAML
    config_file.write_text("invalid: yaml: syntax:")

    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    with pytest.raises(SystemExit) as exc_info:
        load_config()

    assert exc_info.value.code == 1


def test_load_config_handles_empty_file(tmp_path, monkeypatch):
    """Test that load_config handles empty config file."""
    config_dir = tmp_path / ".verse-slides"
    config_file = config_dir / "config.yaml"
    config_dir.mkdir()

    # Write empty config (will result in None from yaml.safe_load)
    config_file.write_text("")

    monkeypatch.setattr("verse_slides.config.get_config_file", lambda: config_file)

    # Should exit because API key won't be set
    with pytest.raises(SystemExit) as exc_info:
        load_config()

    assert exc_info.value.code == 1
