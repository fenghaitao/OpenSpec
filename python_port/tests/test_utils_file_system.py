"""Tests for OpenSpec file system utilities (ported from TypeScript)."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path

from openspec.utils.file_system import ensure_directory, write_file, read_file, file_exists
from pathlib import Path


class TestFileSystemUtils:
    """Test file system utility functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    def test_ensure_directory_creates_directory(self, temp_dir):
        """Test that ensure_directory creates directories."""
        test_dir = temp_dir / "test_directory"
        
        assert not test_dir.exists()
        ensure_directory(str(test_dir))
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_ensure_directory_creates_nested_directories(self, temp_dir):
        """Test creating nested directory structure."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        
        assert not nested_dir.exists()
        ensure_directory(str(nested_dir))
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_ensure_directory_handles_existing_directory(self, temp_dir):
        """Test that ensure_directory handles existing directories gracefully."""
        test_dir = temp_dir / "existing"
        test_dir.mkdir()
        
        # Should not raise error
        ensure_directory(str(test_dir))
        assert test_dir.exists()

    def test_write_file_creates_file(self, temp_dir):
        """Test that write_file creates files with content."""
        test_file = temp_dir / "test.txt"
        content = "Hello, World!"
        
        write_file(str(test_file), content)
        
        assert test_file.exists()
        assert test_file.read_text() == content

    def test_write_file_overwrites_existing(self, temp_dir):
        """Test that write_file overwrites existing files."""
        test_file = temp_dir / "test.txt"
        
        # Write initial content
        write_file(str(test_file), "Initial content")
        assert test_file.read_text() == "Initial content"
        
        # Overwrite with new content
        write_file(str(test_file), "New content")
        assert test_file.read_text() == "New content"

    def test_write_file_creates_parent_directories(self, temp_dir):
        """Test that write_file creates parent directories if needed."""
        test_file = temp_dir / "nested" / "deep" / "file.txt"
        content = "Deep file content"
        
        write_file(str(test_file), content)
        
        assert test_file.exists()
        assert test_file.read_text() == content

    def test_read_file_reads_content(self, temp_dir):
        """Test that read_file correctly reads file content."""
        test_file = temp_dir / "test.txt"
        content = "Test file content"
        
        test_file.write_text(content)
        
        result = read_file(str(test_file))
        assert result == content

    def test_read_file_handles_missing_file(self, temp_dir):
        """Test that read_file handles missing files gracefully."""
        missing_file = temp_dir / "missing.txt"
        
        with pytest.raises((FileNotFoundError, IOError)):
            read_file(str(missing_file))

    def test_file_exists_detects_existing_files(self, temp_dir):
        """Test file_exists correctly identifies existing files."""
        test_file = temp_dir / "exists.txt"
        test_file.write_text("content")
        
        assert file_exists(str(test_file)) is True
        
        missing_file = temp_dir / "missing.txt"
        assert file_exists(str(missing_file)) is False

    def test_path_exists_with_directories(self, temp_dir):
        """Test that file_exists works with directories too (since Python implementation uses Path.exists())."""
        test_dir = temp_dir / "directory"
        test_dir.mkdir()
        
        # In Python implementation, file_exists uses Path.exists() which returns True for directories
        assert file_exists(str(test_dir)) is True

    def test_unicode_content_handling(self, temp_dir):
        """Test handling of unicode content in files."""
        test_file = temp_dir / "unicode.txt"
        content = "Unicode content: 🚀 ñoño çafé"
        
        write_file(str(test_file), content)
        result = read_file(str(test_file))
        
        assert result == content

    def test_large_file_handling(self, temp_dir):
        """Test handling of larger files."""
        test_file = temp_dir / "large.txt"
        content = "Large content line.\n" * 1000
        
        write_file(str(test_file), content)
        result = read_file(str(test_file))
        
        assert result == content
        assert len(result.splitlines()) == 1000

    def test_empty_file_handling(self, temp_dir):
        """Test handling of empty files."""
        test_file = temp_dir / "empty.txt"
        
        write_file(str(test_file), "")
        result = read_file(str(test_file))
        
        assert result == ""

    def test_path_with_spaces_handling(self, temp_dir):
        """Test handling paths with spaces."""
        test_dir = temp_dir / "directory with spaces"
        test_file = test_dir / "file with spaces.txt"
        content = "Content in file with spaces"
        
        write_file(str(test_file), content)
        
        assert file_exists(str(test_file))
        assert directory_exists(str(test_dir))
        assert read_file(str(test_file)) == content