"""Tests for file system utilities - ported from test/utils/file-system.test.ts"""

import pytest
import tempfile
import shutil
from pathlib import Path

from openspec.utils.file_system import (
    ensure_directory,
    write_file,
    read_file,
    file_exists,
    directory_exists,
    list_files,
    list_directories,
    copy_file,
    move_file,
    delete_file,
    delete_directory
)


class TestFileSystem:
    """Test cases for file system utilities."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_ensure_directory_creates_new_directory(self, temp_dir):
        """Test creating a new directory."""
        new_dir = temp_dir / "new_directory"
        
        ensure_directory(str(new_dir))
        
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_ensure_directory_creates_nested_directories(self, temp_dir):
        """Test creating nested directories."""
        nested_dir = temp_dir / "parent" / "child" / "grandchild"
        
        ensure_directory(str(nested_dir))
        
        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert (temp_dir / "parent").exists()
        assert (temp_dir / "parent" / "child").exists()
    
    def test_ensure_directory_does_not_fail_if_exists(self, temp_dir):
        """Test that ensuring an existing directory doesn't fail."""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()
        
        # Should not raise an exception
        ensure_directory(str(existing_dir))
        
        assert existing_dir.exists()
    
    def test_write_file_creates_new_file(self, temp_dir):
        """Test writing to a new file."""
        file_path = temp_dir / "test.txt"
        content = "Hello, World!"
        
        write_file(str(file_path), content)
        
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_write_file_overwrites_existing_file(self, temp_dir):
        """Test overwriting an existing file."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("Old content")
        
        new_content = "New content"
        write_file(str(file_path), new_content)
        
        assert file_path.read_text() == new_content
    
    def test_write_file_creates_parent_directories(self, temp_dir):
        """Test that writing a file creates parent directories."""
        file_path = temp_dir / "nested" / "dir" / "test.txt"
        content = "Test content"
        
        write_file(str(file_path), content)
        
        assert file_path.exists()
        assert file_path.read_text() == content
        assert (temp_dir / "nested" / "dir").is_dir()
    
    def test_read_file_returns_content(self, temp_dir):
        """Test reading file content."""
        file_path = temp_dir / "test.txt"
        content = "Test content\nMultiple lines"
        file_path.write_text(content)
        
        result = read_file(str(file_path))
        
        assert result == content
    
    def test_read_file_raises_error_if_not_exists(self, temp_dir):
        """Test that reading non-existent file raises error."""
        file_path = temp_dir / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            read_file(str(file_path))
    
    def test_file_exists_returns_true_for_existing_file(self, temp_dir):
        """Test file_exists returns True for existing file."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")
        
        assert file_exists(str(file_path)) is True
    
    def test_file_exists_returns_false_for_nonexistent_file(self, temp_dir):
        """Test file_exists returns False for non-existent file."""
        file_path = temp_dir / "nonexistent.txt"
        
        assert file_exists(str(file_path)) is False
    
    def test_file_exists_returns_false_for_directory(self, temp_dir):
        """Test file_exists returns False for directories."""
        dir_path = temp_dir / "testdir"
        dir_path.mkdir()
        
        assert file_exists(str(dir_path)) is False
    
    def test_directory_exists_returns_true_for_existing_directory(self, temp_dir):
        """Test directory_exists returns True for existing directory."""
        dir_path = temp_dir / "testdir"
        dir_path.mkdir()
        
        assert directory_exists(str(dir_path)) is True
    
    def test_directory_exists_returns_false_for_nonexistent_directory(self, temp_dir):
        """Test directory_exists returns False for non-existent directory."""
        dir_path = temp_dir / "nonexistent"
        
        assert directory_exists(str(dir_path)) is False
    
    def test_directory_exists_returns_false_for_file(self, temp_dir):
        """Test directory_exists returns False for files."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")
        
        assert directory_exists(str(file_path)) is False
    
    def test_list_files_returns_files_in_directory(self, temp_dir):
        """Test listing files in directory."""
        # Create test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.md").write_text("content2")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.txt").write_text("content3")
        
        files = list_files(str(temp_dir))
        
        assert len(files) == 2
        file_names = [Path(f).name for f in files]
        assert "file1.txt" in file_names
        assert "file2.md" in file_names
    
    def test_list_files_with_pattern(self, temp_dir):
        """Test listing files with specific pattern."""
        # Create test files
        (temp_dir / "test1.txt").write_text("content1")
        (temp_dir / "test2.md").write_text("content2")
        (temp_dir / "readme.txt").write_text("content3")
        
        txt_files = list_files(str(temp_dir), "*.txt")
        
        assert len(txt_files) == 2
        file_names = [Path(f).name for f in txt_files]
        assert "test1.txt" in file_names
        assert "readme.txt" in file_names
        assert "test2.md" not in file_names
    
    def test_list_directories_returns_subdirectories(self, temp_dir):
        """Test listing subdirectories."""
        # Create test structure
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir2").mkdir()
        (temp_dir / "file1.txt").write_text("content")
        
        dirs = list_directories(str(temp_dir))
        
        assert len(dirs) == 2
        dir_names = [Path(d).name for d in dirs]
        assert "dir1" in dir_names
        assert "dir2" in dir_names
    
    def test_copy_file_copies_content(self, temp_dir):
        """Test copying file content."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        content = "Test content for copying"
        source.write_text(content)
        
        copy_file(str(source), str(dest))
        
        assert dest.exists()
        assert dest.read_text() == content
        assert source.exists()  # Original should still exist
    
    def test_copy_file_creates_destination_directory(self, temp_dir):
        """Test that copying file creates destination directory."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "nested" / "dest.txt"
        content = "Test content"
        source.write_text(content)
        
        copy_file(str(source), str(dest))
        
        assert dest.exists()
        assert dest.read_text() == content
        assert (temp_dir / "nested").is_dir()
    
    def test_move_file_moves_content(self, temp_dir):
        """Test moving file content."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        content = "Test content for moving"
        source.write_text(content)
        
        move_file(str(source), str(dest))
        
        assert dest.exists()
        assert dest.read_text() == content
        assert not source.exists()  # Original should be moved
    
    def test_move_file_creates_destination_directory(self, temp_dir):
        """Test that moving file creates destination directory."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "nested" / "dest.txt"
        content = "Test content"
        source.write_text(content)
        
        move_file(str(source), str(dest))
        
        assert dest.exists()
        assert dest.read_text() == content
        assert not source.exists()
        assert (temp_dir / "nested").is_dir()
    
    def test_delete_file_removes_file(self, temp_dir):
        """Test deleting a file."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")
        
        delete_file(str(file_path))
        
        assert not file_path.exists()
    
    def test_delete_file_does_not_fail_if_not_exists(self, temp_dir):
        """Test that deleting non-existent file doesn't fail."""
        file_path = temp_dir / "nonexistent.txt"
        
        # Should not raise an exception
        delete_file(str(file_path))
        
        assert not file_path.exists()
    
    def test_delete_directory_removes_directory(self, temp_dir):
        """Test deleting a directory."""
        dir_path = temp_dir / "testdir"
        dir_path.mkdir()
        (dir_path / "file.txt").write_text("content")
        
        delete_directory(str(dir_path))
        
        assert not dir_path.exists()
    
    def test_delete_directory_does_not_fail_if_not_exists(self, temp_dir):
        """Test that deleting non-existent directory doesn't fail."""
        dir_path = temp_dir / "nonexistent"
        
        # Should not raise an exception
        delete_directory(str(dir_path))
        
        assert not dir_path.exists()
    
    def test_read_write_unicode_content(self, temp_dir):
        """Test reading and writing Unicode content."""
        file_path = temp_dir / "unicode.txt"
        unicode_content = "Hello 世界! 🌍 Ñiño café"
        
        write_file(str(file_path), unicode_content)
        result = read_file(str(file_path))
        
        assert result == unicode_content
    
    def test_work_with_pathlib_objects(self, temp_dir):
        """Test that functions work with pathlib.Path objects."""
        file_path = temp_dir / "pathlib_test.txt"
        content = "Testing pathlib support"
        
        # Functions should accept Path objects
        write_file(file_path, content)
        result = read_file(file_path)
        exists = file_exists(file_path)
        
        assert result == content
        assert exists is True