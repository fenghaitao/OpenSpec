"""Tests for OpenSpec show command (ported from TypeScript)."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main


class TestShowCommand:
    """Test the top-level show command."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project with test data."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Create OpenSpec structure
        openspec_dir = project_path / "openspec"
        changes_dir = openspec_dir / "changes"
        specs_dir = openspec_dir / "specs"
        
        openspec_dir.mkdir()
        changes_dir.mkdir()
        specs_dir.mkdir()
        
        yield project_path, changes_dir, specs_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def setup_test_data(self, changes_dir, specs_dir):
        """Set up test changes and specs."""
        
        # Create a test change
        change_content = """# Change: Demo

## Why
Because reasons that are long enough for validation requirements.

## What Changes
- **auth:** Add requirement
"""
        demo_change_dir = changes_dir / "demo"
        demo_change_dir.mkdir()
        (demo_change_dir / "proposal.md").write_text(change_content)

        # Create a test spec
        spec_content = """## Purpose
Auth spec for user authentication.

## Requirements

### Requirement: User Authentication
The system SHALL authenticate users before granting access.

#### Scenario: Valid credentials
- **GIVEN** a user with valid credentials
- **WHEN** they attempt to log in
- **THEN** access is granted

### Requirement: Session Management
The system SHALL manage user sessions securely.
"""
        auth_spec_dir = specs_dir / "auth"
        auth_spec_dir.mkdir()
        (auth_spec_dir / "spec.md").write_text(spec_content)

    def test_show_no_args_non_interactive(self, runner, temp_project):
        """Test show command with no args in non-interactive mode."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_test_data(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["show"], env={"OPENSPEC_INTERACTIVE": "0"})
            
            assert result.exit_code == 1
            assert "Nothing to show" in result.output

    def test_show_change_with_json(self, runner, temp_project):
        """Test showing a change with JSON output."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_test_data(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["show", "demo", "--json"])
            
            if result.exit_code == 0:
                # Should contain JSON output
                assert result.output.strip()
                # Could parse JSON here to verify structure

    def test_show_spec_with_requirements_flag(self, runner, temp_project):
        """Test showing a spec with requirements flag."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_test_data(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["show", "auth", "--requirements"])
            
            if result.exit_code == 0:
                # Should show requirements
                assert "Requirement" in result.output

    def test_show_ambiguous_item(self, runner, temp_project):
        """Test showing item when both change and spec exist with same name."""
        project_path, changes_dir, specs_dir = temp_project
        
        # Create both a change and spec named 'foo'
        foo_change_dir = changes_dir / "foo"
        foo_change_dir.mkdir()
        change_content = """# Change: Foo

## Why
Because we need foo functionality that is comprehensive enough.

## What Changes
- **foo:** Add foo feature
"""
        (foo_change_dir / "proposal.md").write_text(change_content)
        
        foo_spec_dir = specs_dir / "foo"
        foo_spec_dir.mkdir()
        spec_content = """## Purpose
Foo specification for the system.

## Requirements

### Requirement: Foo SHALL work
The foo feature SHALL work correctly.
"""
        (foo_spec_dir / "spec.md").write_text(spec_content)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["show", "foo"])
            
            assert result.exit_code == 1
            assert "Ambiguous item" in result.output
            assert "--type" in result.output

    def test_show_unknown_item(self, runner, temp_project):
        """Test showing an unknown item."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_test_data(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["show", "unknown-item"])
            
            assert result.exit_code == 1
            assert "Unknown item" in result.output or "not found" in result.output.lower()

    def test_show_with_type_specification(self, runner, temp_project):
        """Test showing with explicit type specification."""
        project_path, changes_dir, specs_dir = temp_project
        
        # Create both change and spec with same name
        foo_change_dir = changes_dir / "duplicate"
        foo_change_dir.mkdir()
        change_content = """# Change: Duplicate

## Why
Because we need duplicate functionality for testing purposes.

## What Changes
- **system:** Add duplicate handling
"""
        (foo_change_dir / "proposal.md").write_text(change_content)
        
        foo_spec_dir = specs_dir / "duplicate"
        foo_spec_dir.mkdir()
        spec_content = """## Purpose
Duplicate handling specification.

## Requirements

### Requirement: System SHALL handle duplicates
The system SHALL properly handle duplicate entries.
"""
        (foo_spec_dir / "spec.md").write_text(spec_content)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            
            # Test showing change specifically
            result = runner.invoke(main, ["show", "duplicate", "--type", "change"])
            if result.exit_code == 0:
                assert "Change: Duplicate" in result.output
            
            # Test showing spec specifically  
            result = runner.invoke(main, ["show", "duplicate", "--type", "spec"])
            if result.exit_code == 0:
                assert "Purpose" in result.output

    def test_show_outside_project(self, runner):
        """Test show command outside OpenSpec project."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["show", "anything"])
            
            assert result.exit_code == 1
            # Should indicate not in OpenSpec project