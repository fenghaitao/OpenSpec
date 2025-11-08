"""Basic CLI E2E tests - ported from test/cli-e2e/basic.test.ts"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main


class TestBasicCLIE2E:
    """Basic end-to-end CLI tests."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project with OpenSpec structure."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        yield project_path
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_init_project_flow(self, temp_project, runner):
        """Test the complete project initialization flow."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project with Claude
            result = runner.invoke(main, [
                "init", 
                "--ai-tools", "claude",
                "--non-interactive"
            ])
            
            assert result.exit_code == 0
            
            # Verify project structure was created
            assert (temp_project / "openspec").is_dir()
            assert (temp_project / "openspec" / "changes").is_dir()
            assert (temp_project / "openspec" / "specs").is_dir()
            assert (temp_project / "openspec" / "changes" / "archive").is_dir()
            
            # Verify configuration files
            assert (temp_project / "openspec" / "project.md").is_file()
            assert (temp_project / "openspec" / "AGENTS.md").is_file()
            assert (temp_project / "AGENTS.md").is_file()
            assert (temp_project / "CLAUDE.md").is_file()
    
    def test_create_and_validate_change_flow(self, temp_project, runner):
        """Test creating and validating a change."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project first
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            
            # Create a change
            result = runner.invoke(main, ["change", "create", "test-feature"])
            assert result.exit_code == 0
            
            # Verify change was created
            change_dir = temp_project / "openspec" / "changes" / "test-feature"
            assert change_dir.is_dir()
            assert (change_dir / "proposal.md").is_file()
            assert (change_dir / "tasks.md").is_file()
            
            # Modify the proposal to have valid content
            proposal_content = """# Test Feature

## Why
This feature is needed to improve the system functionality and provide better user experience for our customers.

## What Changes
- **api:** Add new endpoint for feature management
- **ui:** Update interface to support new feature
- **docs:** Add documentation for the new feature"""
            
            (change_dir / "proposal.md").write_text(proposal_content)
            
            # Validate the change
            result = runner.invoke(main, ["validate", "test-feature"])
            assert result.exit_code == 0
    
    def test_create_and_validate_spec_flow(self, temp_project, runner):
        """Test creating and validating a spec."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project first
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            
            # Create a spec
            result = runner.invoke(main, ["spec", "create", "api-spec"])
            assert result.exit_code == 0
            
            # Verify spec was created
            spec_dir = temp_project / "openspec" / "specs" / "api-spec"
            assert spec_dir.is_dir()
            assert (spec_dir / "spec.md").is_file()
            
            # Modify the spec to have valid content
            spec_content = """# API Specification

## Purpose
This specification defines the REST API endpoints and behavior for the application.

## Requirements

### Requirement: GET /api/users endpoint
The API SHALL provide a GET endpoint at /api/users that returns a list of users.

#### Scenario: Successful user list retrieval
- **GIVEN** the API is running and database is accessible
- **WHEN** a GET request is made to /api/users
- **THEN** the response should contain a JSON array of user objects

### Requirement: POST /api/users endpoint  
The API SHALL provide a POST endpoint at /api/users that creates a new user.

#### Scenario: Successful user creation
- **GIVEN** valid user data is provided in the request body
- **WHEN** a POST request is made to /api/users
- **THEN** a new user should be created and returned in the response"""
            
            (spec_dir / "spec.md").write_text(spec_content)
            
            # Validate the spec
            result = runner.invoke(main, ["validate", "api-spec"])
            assert result.exit_code == 0
    
    def test_list_changes_and_specs(self, temp_project, runner):
        """Test listing changes and specs."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project and create some items
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            runner.invoke(main, ["change", "create", "change-1"])
            runner.invoke(main, ["change", "create", "change-2"])
            runner.invoke(main, ["spec", "create", "spec-1"])
            runner.invoke(main, ["spec", "create", "spec-2"])
            
            # List changes
            result = runner.invoke(main, ["list"])
            assert result.exit_code == 0
            assert "change-1" in result.output
            assert "change-2" in result.output
            assert "Changes:" in result.output
    
    def test_show_change_and_spec(self, temp_project, runner):
        """Test showing change and spec details."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project and create items
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            runner.invoke(main, ["change", "create", "show-test"])
            runner.invoke(main, ["spec", "create", "show-spec"])
            
            # Show change
            result = runner.invoke(main, ["show", "show-test"])
            assert result.exit_code == 0
            
            # Show spec  
            result = runner.invoke(main, ["show", "show-spec"])
            assert result.exit_code == 0
    
    def test_validate_all_with_json_output(self, temp_project, runner):
        """Test validating all items with JSON output."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project and create items
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            runner.invoke(main, ["change", "create", "json-test"])
            runner.invoke(main, ["spec", "create", "json-spec"])
            
            # Create valid content
            change_dir = temp_project / "openspec" / "changes" / "json-test"
            proposal_content = """# JSON Test Feature

## Why
This feature is needed for comprehensive testing of the JSON validation output functionality.

## What Changes
- **core:** Add JSON validation support
- **api:** Update endpoints to return JSON responses"""
            
            (change_dir / "proposal.md").write_text(proposal_content)
            
            spec_dir = temp_project / "openspec" / "specs" / "json-spec"
            spec_content = """# JSON Specification

## Purpose
This specification defines JSON response formats and validation requirements.

## Requirements

### Requirement: JSON Response Format
All API responses SHALL be in valid JSON format.

#### Scenario: Valid JSON response
- **GIVEN** an API endpoint is called
- **WHEN** the response is generated
- **THEN** it should be valid JSON"""
            
            (spec_dir / "spec.md").write_text(spec_content)
            
            # Validate all with JSON output
            result = runner.invoke(main, ["validate", "--all", "--json"])
            assert result.exit_code == 0
            
            # Parse JSON output
            json_data = json.loads(result.output)
            assert "items" in json_data
            assert "summary" in json_data
            assert "version" in json_data
            assert isinstance(json_data["items"], list)
    
    def test_view_dashboard(self, temp_project, runner):
        """Test viewing the project dashboard."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            
            # View dashboard
            result = runner.invoke(main, ["view"])
            assert result.exit_code == 0
            assert "Project Dashboard" in result.output
    
    def test_update_agent_files(self, temp_project, runner):
        """Test updating agent instruction files."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            
            # Update agent files
            result = runner.invoke(main, ["update"])
            assert result.exit_code == 0
    
    def test_error_handling_outside_project(self, runner):
        """Test error handling when running commands outside an OpenSpec project."""
        with runner.isolated_filesystem():
            # Try to validate without being in a project
            result = runner.invoke(main, ["validate", "--all"])
            assert result.exit_code == 1
            assert "Not in an OpenSpec project" in result.output
    
    def test_help_commands(self, runner):
        """Test help commands."""
        # Main help
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "OpenSpec" in result.output
        
        # Subcommand help
        result = runner.invoke(main, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize" in result.output
        
        result = runner.invoke(main, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate" in result.output
    
    def test_complete_workflow_with_archive(self, temp_project, runner):
        """Test complete workflow including archiving."""
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            # Initialize project
            runner.invoke(main, ["init", "--ai-tools", "claude", "--non-interactive"])
            
            # Create and set up a change
            runner.invoke(main, ["change", "create", "workflow-test"])
            
            change_dir = temp_project / "openspec" / "changes" / "workflow-test"
            proposal_content = """# Workflow Test Feature

## Why
This feature demonstrates the complete OpenSpec workflow from creation to archive.

## What Changes
- **core:** Add workflow testing capabilities
- **docs:** Document the complete workflow process"""
            
            (change_dir / "proposal.md").write_text(proposal_content)
            
            # Add some completed tasks
            tasks_content = """# Tasks for workflow-test

- [x] Create initial proposal
- [x] Define requirements
- [x] Implement core functionality
- [x] Add documentation
- [x] Test implementation"""
            
            (change_dir / "tasks.md").write_text(tasks_content)
            
            # Validate the change
            result = runner.invoke(main, ["validate", "workflow-test"])
            assert result.exit_code == 0
            
            # Archive the change
            result = runner.invoke(main, ["archive", "workflow-test", "--yes"])
            assert result.exit_code == 0
            
            # Verify change was archived
            assert not change_dir.exists()
            archive_dir = temp_project / "openspec" / "changes" / "archive"
            archived_items = list(archive_dir.iterdir())
            assert len(archived_items) == 1
            assert "workflow-test" in str(archived_items[0].name)