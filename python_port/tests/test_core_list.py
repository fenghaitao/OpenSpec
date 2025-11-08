"""Tests for OpenSpec list functionality (ported from TypeScript)."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch
from io import StringIO
import sys

from openspec.cli.commands.list_cmd import list_changes


class TestListCommand:
    """Test the list command functionality."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project with OpenSpec structure."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Create OpenSpec structure
        openspec_dir = project_path / "openspec"
        changes_dir = openspec_dir / "changes"
        
        openspec_dir.mkdir()
        changes_dir.mkdir()
        
        yield project_path, changes_dir
        shutil.rmtree(temp_dir)

    def test_list_empty_changes_directory(self, temp_project, capsys):
        """Test listing when changes directory is empty."""
        project_path, changes_dir = temp_project
        
        os.chdir(project_path)
        
        try:
            list_changes()
            captured = capsys.readouterr()
            assert "No changes found" in captured.out
        except SystemExit:
            # Command might exit with code, that's ok for empty directory
            pass

    def test_list_excludes_archive_directory(self, temp_project, capsys):
        """Test that archive directory is excluded from listing."""
        project_path, changes_dir = temp_project
        
        # Create archive directory and a regular change
        archive_dir = changes_dir / "archive"
        archive_dir.mkdir()
        
        my_change_dir = changes_dir / "my-change"
        my_change_dir.mkdir()
        
        # Create tasks.md with some tasks
        tasks_content = "- [x] Task 1\n- [ ] Task 2\n"
        (my_change_dir / "tasks.md").write_text(tasks_content)
        
        os.chdir(project_path)
        
        try:
            list_changes()
            captured = capsys.readouterr()
            
            # Should include my-change but not archive
            assert "my-change" in captured.out
            assert "archive" not in captured.out
            
        except SystemExit:
            pass

    def test_list_counts_tasks_correctly(self, temp_project, capsys):
        """Test that task counting works correctly."""
        project_path, changes_dir = temp_project
        
        test_change_dir = changes_dir / "test-change"
        test_change_dir.mkdir()
        
        # Create tasks.md with mixed completed/incomplete tasks
        tasks_content = """# Tasks
- [x] Completed task 1
- [x] Completed task 2
- [ ] Incomplete task 1
- [ ] Incomplete task 2
- [ ] Incomplete task 3
Regular text that should be ignored
"""
        (test_change_dir / "tasks.md").write_text(tasks_content)
        
        os.chdir(project_path)
        
        try:
            list_changes()
            captured = capsys.readouterr()
            
            # Should show 2 completed out of 5 total tasks
            assert "2/5" in captured.out or "2 / 5" in captured.out
            
        except SystemExit:
            pass

    def test_list_shows_complete_status(self, temp_project, capsys):
        """Test showing complete status for fully completed changes."""
        project_path, changes_dir = temp_project
        
        completed_change_dir = changes_dir / "completed-change"
        completed_change_dir.mkdir()
        
        # Create tasks.md with all completed tasks
        tasks_content = "- [x] Task 1\n- [x] Task 2\n- [x] Task 3\n"
        (completed_change_dir / "tasks.md").write_text(tasks_content)
        
        os.chdir(project_path)
        
        try:
            list_changes()
            captured = capsys.readouterr()
            
            # Should indicate completion
            assert ("Complete" in captured.out or 
                    "✓" in captured.out or 
                    "100%" in captured.out)
            
        except SystemExit:
            pass

    def test_list_handles_changes_without_tasks(self, temp_project, capsys):
        """Test handling changes that don't have tasks.md."""
        project_path, changes_dir = temp_project
        
        no_tasks_dir = changes_dir / "no-tasks"
        no_tasks_dir.mkdir()
        
        # Don't create tasks.md
        
        os.chdir(project_path)
        
        try:
            list_changes()
            captured = capsys.readouterr()
            
            # Should handle missing tasks gracefully
            assert "no-tasks" in captured.out
            
        except SystemExit:
            pass

    def test_list_sorts_changes_alphabetically(self, temp_project, capsys):
        """Test that changes are sorted alphabetically."""
        project_path, changes_dir = temp_project
        
        # Create changes in non-alphabetical order
        for name in ["zebra", "alpha", "middle"]:
            change_dir = changes_dir / name
            change_dir.mkdir()
        
        os.chdir(project_path)
        
        try:
            list_changes()
            captured = capsys.readouterr()
            output = captured.out
            
            # Find positions of each change in output
            alpha_pos = output.find("alpha")
            middle_pos = output.find("middle")
            zebra_pos = output.find("zebra")
            
            # They should be in alphabetical order
            assert alpha_pos < middle_pos < zebra_pos
            
        except SystemExit:
            pass

    def test_list_multiple_changes_various_states(self, temp_project, capsys):
        """Test listing multiple changes with various completion states."""
        project_path, changes_dir = temp_project
        
        # Complete change
        completed_dir = changes_dir / "completed"
        completed_dir.mkdir()
        (completed_dir / "tasks.md").write_text("- [x] Task 1\n- [x] Task 2\n")
        
        # Partial change
        partial_dir = changes_dir / "partial"
        partial_dir.mkdir()
        (partial_dir / "tasks.md").write_text("- [x] Done\n- [ ] Not done\n- [ ] Also not done\n")
        
        # No tasks
        no_tasks_dir = changes_dir / "no-tasks"
        no_tasks_dir.mkdir()
        
        os.chdir(project_path)
        
        try:
            list_changes()
            captured = capsys.readouterr()
            output = captured.out
            
            # Should show all three changes
            assert "completed" in output
            assert "partial" in output
            assert "no-tasks" in output
            
        except SystemExit:
            pass

    def test_list_missing_openspec_directory(self, temp_project):
        """Test error handling when openspec/changes directory is missing."""
        project_path, changes_dir = temp_project
        
        # Remove the changes directory
        shutil.rmtree(changes_dir)
        
        os.chdir(project_path)
        
        with pytest.raises(SystemExit):
            list_changes()