"""Tests for file marker utilities."""

import pytest
import tempfile
import shutil
from pathlib import Path

from openspec.utils.file_markers import (
    update_file_with_markers,
    has_openspec_markers,
    extract_content_between_markers,
    _replace_content_between_markers
)
from openspec.utils.file_system import read_file, write_file
from openspec.core.config import OPENSPEC_MARKERS


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_create_new_file_with_markers(temp_dir):
    """Test creating a new file with markers."""
    file_path = temp_dir / "test.md"
    content = "Test content here"
    
    await update_file_with_markers(
        str(file_path),
        content,
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    assert file_path.exists()
    file_content = read_file(str(file_path))
    assert OPENSPEC_MARKERS["start"] in file_content
    assert OPENSPEC_MARKERS["end"] in file_content
    assert content in file_content


@pytest.mark.asyncio
async def test_update_existing_file_with_markers(temp_dir):
    """Test updating existing file with markers."""
    file_path = temp_dir / "test.md"
    
    # Create initial file
    initial_content = f"""# Header

Some content before.

{OPENSPEC_MARKERS["start"]}
Old managed content
{OPENSPEC_MARKERS["end"]}

Some content after.
"""
    write_file(str(file_path), initial_content)
    
    # Update with new content
    new_content = "New managed content"
    await update_file_with_markers(
        str(file_path),
        new_content,
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    # Check result
    updated_content = read_file(str(file_path))
    assert "# Header" in updated_content
    assert "Some content before." in updated_content
    assert "Some content after." in updated_content
    assert new_content in updated_content
    assert "Old managed content" not in updated_content


@pytest.mark.asyncio
async def test_update_file_without_markers(temp_dir):
    """Test updating file that doesn't have markers."""
    file_path = temp_dir / "test.md"
    
    # Create file without markers
    initial_content = "# Header\n\nSome existing content.\n"
    write_file(str(file_path), initial_content)
    
    # Update with markers
    new_content = "Managed content"
    await update_file_with_markers(
        str(file_path),
        new_content,
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    # Check result
    updated_content = read_file(str(file_path))
    assert "# Header" in updated_content
    assert "Some existing content." in updated_content
    assert new_content in updated_content
    assert OPENSPEC_MARKERS["start"] in updated_content
    assert OPENSPEC_MARKERS["end"] in updated_content


def test_has_openspec_markers(temp_dir):
    """Test checking for OpenSpec markers."""
    file_path = temp_dir / "test.md"
    
    # File without markers
    write_file(str(file_path), "Just some content")
    assert not has_openspec_markers(
        str(file_path),
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    # File with markers
    content_with_markers = f"""Content before
{OPENSPEC_MARKERS["start"]}
Managed content
{OPENSPEC_MARKERS["end"]}
Content after"""
    write_file(str(file_path), content_with_markers)
    assert has_openspec_markers(
        str(file_path),
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    # Non-existent file
    assert not has_openspec_markers(
        str(temp_dir / "nonexistent.md"),
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )


def test_extract_content_between_markers(temp_dir):
    """Test extracting content between markers."""
    file_path = temp_dir / "test.md"
    
    managed_content = "This is managed content\nWith multiple lines"
    content_with_markers = f"""Content before
{OPENSPEC_MARKERS["start"]}
{managed_content}
{OPENSPEC_MARKERS["end"]}
Content after"""
    
    write_file(str(file_path), content_with_markers)
    
    extracted = extract_content_between_markers(
        str(file_path),
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    assert extracted == managed_content
    
    # Test file without markers
    write_file(str(file_path), "Just some content")
    extracted = extract_content_between_markers(
        str(file_path),
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    assert extracted is None


def test_replace_content_between_markers():
    """Test internal marker replacement function."""
    existing = f"""# Header

Before content

{OPENSPEC_MARKERS["start"]}
Old content here
{OPENSPEC_MARKERS["end"]}

After content
"""
    
    new_content = "New content here"
    result = _replace_content_between_markers(
        existing,
        new_content,
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    assert "# Header" in result
    assert "Before content" in result
    assert "After content" in result
    assert new_content in result
    assert "Old content here" not in result
    
    # Test content without markers
    no_markers = "Just some content"
    result = _replace_content_between_markers(
        no_markers,
        new_content,
        OPENSPEC_MARKERS["start"],
        OPENSPEC_MARKERS["end"]
    )
    
    assert "Just some content" in result
    assert new_content in result
    assert OPENSPEC_MARKERS["start"] in result
    assert OPENSPEC_MARKERS["end"] in result