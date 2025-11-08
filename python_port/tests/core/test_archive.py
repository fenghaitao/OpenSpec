"""Tests for ArchiveCommand - ported from test/core/archive.test.ts"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import date

from openspec.cli.commands.archive import ArchiveCommand


class TestArchiveCommand:
    """Test cases for ArchiveCommand."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        
        # Change to temp directory
        os.chdir(temp_dir)
        
        # Create OpenSpec structure
        openspec_dir = Path(temp_dir) / "openspec"
        (openspec_dir / "changes").mkdir(parents=True)
        (openspec_dir / "specs").mkdir(parents=True)
        (openspec_dir / "changes" / "archive").mkdir(parents=True)
        
        yield Path(temp_dir)
        
        # Restore original working directory and cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def archive_command(self):
        """Create an ArchiveCommand instance."""
        return ArchiveCommand()
    
    def test_should_archive_change_successfully(self, temp_dir, archive_command):
        """Test successful archiving of a change."""
        # Create a test change
        change_name = "test-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_dir.mkdir(parents=True)
        
        # Create tasks.md with completed tasks
        tasks_content = "- [x] Task 1\n- [x] Task 2"
        (change_dir / "tasks.md").write_text(tasks_content)
        
        # Execute archive with --yes flag
        archive_command.execute(change_name, yes=True)
        
        # Check that change was moved to archive
        archive_dir = temp_dir / "openspec" / "changes" / "archive"
        archives = list(archive_dir.iterdir())
        
        assert len(archives) == 1
        expected_pattern = f"{date.today().isoformat()}-{change_name}"
        assert expected_pattern in str(archives[0].name)
        
        # Verify original change directory no longer exists
        assert not change_dir.exists()
    
    def test_should_warn_about_incomplete_tasks(self, temp_dir, archive_command, capsys):
        """Test warning about incomplete tasks."""
        change_name = "incomplete-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_dir.mkdir(parents=True)
        
        # Create tasks.md with incomplete tasks
        tasks_content = "- [x] Task 1\n- [ ] Task 2\n- [ ] Task 3"
        (change_dir / "tasks.md").write_text(tasks_content)
        
        # Execute archive with --yes flag
        archive_command.execute(change_name, yes=True)
        
        # Verify warning was logged
        captured = capsys.readouterr()
        assert "Warning: 2 incomplete task(s) found" in captured.out
    
    def test_should_update_specs_when_archiving_delta_based_added(self, temp_dir, archive_command):
        """Test updating specs when archiving (delta-based ADDED) and include change name in skeleton."""
        change_name = "spec-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_spec_dir = change_dir / "specs" / "test-capability"
        change_spec_dir.mkdir(parents=True)
        
        # Create delta-based change spec (ADDED requirement)
        spec_content = """# Test Capability Spec - Changes

## ADDED Requirements

### Requirement: The system SHALL provide test capability

#### Scenario: Basic test
Given a test condition
When an action occurs
Then expected result happens"""
        (change_spec_dir / "spec.md").write_text(spec_content)
        
        # Execute archive with --yes flag and skip validation for speed
        archive_command.execute(change_name, yes=True, no_validate=True)
        
        # Verify spec was created from skeleton and ADDED requirement applied
        main_spec_path = temp_dir / "openspec" / "specs" / "test-capability" / "spec.md"
        updated_content = main_spec_path.read_text()
        
        assert "# test-capability Specification" in updated_content
        assert "## Purpose" in updated_content
        assert f"created by archiving change {change_name}" in updated_content
        assert "## Requirements" in updated_content
        assert "### Requirement: The system SHALL provide test capability" in updated_content
        assert "#### Scenario: Basic test" in updated_content
    
    def test_should_throw_error_if_change_does_not_exist(self, temp_dir, archive_command):
        """Test error when change does not exist."""
        with pytest.raises(FileNotFoundError, match="Change 'non-existent-change' not found"):
            archive_command.execute("non-existent-change", yes=True)
    
    def test_should_throw_error_if_archive_already_exists(self, temp_dir, archive_command):
        """Test error when archive already exists."""
        change_name = "duplicate-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_dir.mkdir(parents=True)
        
        # Create existing archive with same date
        today = date.today().isoformat()
        archive_path = temp_dir / "openspec" / "changes" / "archive" / f"{today}-{change_name}"
        archive_path.mkdir(parents=True)
        
        # Try to archive
        with pytest.raises(FileExistsError, match=f"Archive '{today}-{change_name}' already exists"):
            archive_command.execute(change_name, yes=True)
    
    def test_should_handle_change_without_tasks_md(self, temp_dir, archive_command):
        """Test handling of change without tasks.md file."""
        change_name = "no-tasks-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_dir.mkdir(parents=True)
        
        # Execute archive without tasks.md
        archive_command.execute(change_name, yes=True)
        
        # Check that change was archived despite no tasks.md
        archive_dir = temp_dir / "openspec" / "changes" / "archive"
        archives = list(archive_dir.iterdir())
        assert len(archives) == 1
    
    def test_should_skip_specs_when_flag_provided(self, temp_dir, archive_command):
        """Test skipping specs when --skip-specs flag is provided."""
        change_name = "skip-specs-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_spec_dir = change_dir / "specs" / "test-spec"
        change_spec_dir.mkdir(parents=True)
        
        # Create a spec delta
        spec_content = """## ADDED Requirements
### Requirement: Test requirement"""
        (change_spec_dir / "spec.md").write_text(spec_content)
        
        # Execute archive with --skip-specs flag
        archive_command.execute(change_name, yes=True, skip_specs=True)
        
        # Verify spec was NOT created
        main_spec_path = temp_dir / "openspec" / "specs" / "test-spec" / "spec.md"
        assert not main_spec_path.exists()
        
        # But change should still be archived
        archive_dir = temp_dir / "openspec" / "changes" / "archive"
        archives = list(archive_dir.iterdir())
        assert len(archives) == 1
    
    def test_should_handle_multiple_spec_deltas(self, temp_dir, archive_command):
        """Test handling multiple spec deltas in a change."""
        change_name = "multi-spec-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_dir.mkdir(parents=True)
        
        # Create multiple spec deltas
        for spec_name in ["spec-a", "spec-b"]:
            spec_dir = change_dir / "specs" / spec_name
            spec_dir.mkdir(parents=True)
            spec_content = f"""## ADDED Requirements
### Requirement: {spec_name} requirement"""
            (spec_dir / "spec.md").write_text(spec_content)
        
        # Execute archive
        archive_command.execute(change_name, yes=True, no_validate=True)
        
        # Verify both specs were created
        for spec_name in ["spec-a", "spec-b"]:
            main_spec_path = temp_dir / "openspec" / "specs" / spec_name / "spec.md"
            assert main_spec_path.exists()
            content = main_spec_path.read_text()
            assert f"### Requirement: {spec_name} requirement" in content
    
    def test_should_preserve_existing_specs_when_updating(self, temp_dir, archive_command):
        """Test preservation of existing specs when updating."""
        change_name = "update-existing-spec"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_spec_dir = change_dir / "specs" / "existing-spec"
        change_spec_dir.mkdir(parents=True)
        
        # Create existing spec
        main_spec_dir = temp_dir / "openspec" / "specs" / "existing-spec"
        main_spec_dir.mkdir(parents=True)
        existing_content = """# existing-spec Specification

## Purpose
Existing purpose

## Requirements

### Requirement: Existing requirement
Existing description"""
        (main_spec_dir / "spec.md").write_text(existing_content)
        
        # Create change spec with ADDED requirement
        change_content = """## ADDED Requirements

### Requirement: New added requirement
New description"""
        (change_spec_dir / "spec.md").write_text(change_content)
        
        # Execute archive
        archive_command.execute(change_name, yes=True, no_validate=True)
        
        # Verify existing content is preserved and new content added
        updated_content = (main_spec_dir / "spec.md").read_text()
        assert "### Requirement: Existing requirement" in updated_content
        assert "### Requirement: New added requirement" in updated_content
        assert "Existing purpose" in updated_content
    
    @patch('openspec.cli.commands.archive.prompt_for_confirmation')
    def test_should_prompt_for_confirmation_when_yes_flag_not_provided(self, mock_prompt, temp_dir, archive_command):
        """Test prompting for confirmation when --yes flag is not provided."""
        mock_prompt.return_value = True
        
        change_name = "confirm-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_dir.mkdir(parents=True)
        
        # Execute archive without --yes flag
        archive_command.execute(change_name, yes=False)
        
        # Verify confirmation was prompted
        mock_prompt.assert_called_once()
        
        # Verify change was archived after confirmation
        archive_dir = temp_dir / "openspec" / "changes" / "archive"
        archives = list(archive_dir.iterdir())
        assert len(archives) == 1
    
    @patch('openspec.cli.commands.archive.prompt_for_confirmation')
    def test_should_not_archive_when_confirmation_denied(self, mock_prompt, temp_dir, archive_command):
        """Test not archiving when confirmation is denied."""
        mock_prompt.return_value = False
        
        change_name = "denied-feature"
        change_dir = temp_dir / "openspec" / "changes" / change_name
        change_dir.mkdir(parents=True)
        
        # Execute archive without --yes flag
        result = archive_command.execute(change_name, yes=False)
        
        # Verify confirmation was prompted
        mock_prompt.assert_called_once()
        
        # Verify change was NOT archived
        assert change_dir.exists()
        archive_dir = temp_dir / "openspec" / "changes" / "archive"
        archives = list(archive_dir.iterdir())
        assert len(archives) == 0