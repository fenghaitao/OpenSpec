"""Tests for ListCommand - ported from test/core/list.test.ts"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from openspec.cli.commands.list_cmd import ListCommand


class TestListCommand:
    """Test cases for ListCommand."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def list_command(self):
        """Create a ListCommand instance."""
        return ListCommand()
    
    def test_missing_openspec_changes_directory(self, temp_dir, list_command):
        """Test handling of missing openspec/changes directory."""
        with pytest.raises(FileNotFoundError, match="No OpenSpec changes directory found"):
            list_command.execute(str(temp_dir), 'changes')
    
    def test_empty_changes_directory(self, temp_dir, list_command, capsys):
        """Test handling of empty changes directory."""
        changes_dir = temp_dir / "openspec" / "changes"
        changes_dir.mkdir(parents=True)
        
        list_command.execute(str(temp_dir), 'changes')
        
        captured = capsys.readouterr()
        assert "No active changes found." in captured.out
    
    def test_exclude_archive_directory(self, temp_dir, list_command, capsys):
        """Test that archive directory is excluded from listings."""
        changes_dir = temp_dir / "openspec" / "changes"
        
        # Create archive and regular change directories
        (changes_dir / "archive").mkdir(parents=True)
        my_change_dir = changes_dir / "my-change"
        my_change_dir.mkdir(parents=True)
        
        # Create tasks.md with some tasks
        tasks_content = "- [x] Task 1\n- [ ] Task 2\n"
        (my_change_dir / "tasks.md").write_text(tasks_content)
        
        list_command.execute(str(temp_dir), 'changes')
        
        captured = capsys.readouterr()
        assert "Changes:" in captured.out
        assert "my-change" in captured.out
        assert "archive" not in captured.out
    
    def test_count_tasks_correctly(self, temp_dir, list_command, capsys):
        """Test that tasks are counted correctly."""
        changes_dir = temp_dir / "openspec" / "changes"
        test_change_dir = changes_dir / "test-change"
        test_change_dir.mkdir(parents=True)
        
        tasks_content = """# Tasks
- [x] Completed task 1
- [x] Completed task 2
- [ ] Incomplete task 1
- [ ] Incomplete task 2
- [ ] Incomplete task 3
Regular text that should be ignored
"""
        (test_change_dir / "tasks.md").write_text(tasks_content)
        
        list_command.execute(str(temp_dir), 'changes')
        
        captured = capsys.readouterr()
        assert "2/5 tasks" in captured.out
    
    def test_show_complete_status_for_fully_completed_changes(self, temp_dir, list_command, capsys):
        """Test showing complete status for fully completed changes."""
        changes_dir = temp_dir / "openspec" / "changes"
        completed_change_dir = changes_dir / "completed-change"
        completed_change_dir.mkdir(parents=True)
        
        tasks_content = "- [x] Task 1\n- [x] Task 2\n- [x] Task 3\n"
        (completed_change_dir / "tasks.md").write_text(tasks_content)
        
        list_command.execute(str(temp_dir), 'changes')
        
        captured = capsys.readouterr()
        assert "✓ Complete" in captured.out
    
    def test_handle_changes_without_tasks_md(self, temp_dir, list_command, capsys):
        """Test handling changes without tasks.md file."""
        changes_dir = temp_dir / "openspec" / "changes"
        no_tasks_dir = changes_dir / "no-tasks"
        no_tasks_dir.mkdir(parents=True)
        
        list_command.execute(str(temp_dir), 'changes')
        
        captured = capsys.readouterr()
        output_lines = [line for line in captured.out.split('\n') if 'no-tasks' in line and 'No tasks' in line]
        assert len(output_lines) > 0
    
    def test_sort_changes_alphabetically(self, temp_dir, list_command, capsys):
        """Test that changes are sorted alphabetically."""
        changes_dir = temp_dir / "openspec" / "changes"
        
        # Create changes in non-alphabetical order
        (changes_dir / "zebra").mkdir(parents=True)
        (changes_dir / "alpha").mkdir(parents=True)
        (changes_dir / "middle").mkdir(parents=True)
        
        list_command.execute(str(temp_dir))
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Find positions of each change name in output
        alpha_pos = output.find("alpha")
        middle_pos = output.find("middle")
        zebra_pos = output.find("zebra")
        
        # Verify alphabetical order
        assert alpha_pos < middle_pos < zebra_pos
    
    def test_handle_multiple_changes_with_various_states(self, temp_dir, list_command, capsys):
        """Test handling multiple changes with various completion states."""
        changes_dir = temp_dir / "openspec" / "changes"
        
        # Complete change
        completed_dir = changes_dir / "completed"
        completed_dir.mkdir(parents=True)
        (completed_dir / "tasks.md").write_text("- [x] Task 1\n- [x] Task 2\n")
        
        # Partial change
        partial_dir = changes_dir / "partial"
        partial_dir.mkdir(parents=True)
        (partial_dir / "tasks.md").write_text("- [x] Done\n- [ ] Not done\n- [ ] Also not done\n")
        
        # No tasks
        no_tasks_dir = changes_dir / "no-tasks"
        no_tasks_dir.mkdir(parents=True)
        
        list_command.execute(str(temp_dir))
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "Changes:" in output
        
        # Check for completed change
        completed_lines = [line for line in output.split('\n') if 'completed' in line and '✓ Complete' in line]
        assert len(completed_lines) > 0
        
        # Check for partial change
        partial_lines = [line for line in output.split('\n') if 'partial' in line and '1/3 tasks' in line]
        assert len(partial_lines) > 0
        
        # Check for no-tasks change
        no_tasks_lines = [line for line in output.split('\n') if 'no-tasks' in line and 'No tasks' in line]
        assert len(no_tasks_lines) > 0