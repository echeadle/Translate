"""Shared pytest fixtures for md2pdf tests."""

import shutil
from pathlib import Path

import pytest

from md2pdf.config import Config
from md2pdf.converter import MarkdownConverter


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with input/output directories.

    Returns:
        Path: Workspace directory containing input/ and output/ subdirs.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "input").mkdir()
    (workspace / "output").mkdir()
    return workspace


@pytest.fixture
def sample_markdown_files(temp_workspace):
    """Copy sample markdown files to temp workspace.

    Args:
        temp_workspace: Temporary workspace directory.

    Returns:
        dict: Mapping of fixture names to Path objects.
    """
    fixtures_dir = Path(__file__).parent / "fixtures"
    input_dir = temp_workspace / "input"

    files = {}

    # Copy all non-nested fixtures
    for fixture_file in ["simple.md", "tables.md", "code_blocks.md",
                          "complex.md", "empty.md", "invalid.md", "with_images.md"]:
        src = fixtures_dir / fixture_file
        if src.exists():
            dst = input_dir / fixture_file
            shutil.copy(src, dst)
            files[fixture_file.replace(".md", "")] = dst

    # Copy images directory if with_images.md is present
    images_src = fixtures_dir / "images"
    if images_src.exists():
        images_dst = input_dir / "images"
        shutil.copytree(images_src, images_dst)

    # Copy nested fixture
    nested_src = fixtures_dir / "nested" / "subdoc.md"
    if nested_src.exists():
        nested_dir = input_dir / "nested"
        nested_dir.mkdir()
        nested_dst = nested_dir / "subdoc.md"
        shutil.copy(nested_src, nested_dst)
        files["nested_subdoc"] = nested_dst

    return files


@pytest.fixture
def mock_config():
    """Create Config object with default test values.

    Returns:
        Config: Test configuration.
    """
    return Config(
        page_size="A4",
        margin_top="2cm",
        margin_bottom="2cm",
        margin_left="2cm",
        margin_right="2cm",
        font_family="Arial, sans-serif",
        font_size="11pt",
        code_font="Courier, monospace",
        default_output_dir="output",
        preserve_structure=True,
    )


@pytest.fixture
def converter(mock_config):
    """Create MarkdownConverter instance with test config.

    Args:
        mock_config: Test configuration.

    Returns:
        MarkdownConverter: Ready-to-use converter instance.
    """
    return MarkdownConverter(mock_config)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables to prevent .env pollution.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Clear all PDF_* and DEFAULT_* environment variables
    env_vars = [
        "PDF_PAGE_SIZE",
        "PDF_MARGIN_TOP",
        "PDF_MARGIN_BOTTOM",
        "PDF_MARGIN_LEFT",
        "PDF_MARGIN_RIGHT",
        "PDF_FONT_FAMILY",
        "PDF_FONT_SIZE",
        "PDF_CODE_FONT",
        "DEFAULT_OUTPUT_DIR",
        "PRESERVE_DIRECTORY_STRUCTURE",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
