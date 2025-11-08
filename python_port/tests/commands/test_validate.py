"""Tests for validate command - ported from test/commands/validate.test.ts"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main


class TestValidateCommand:
    """Test cases for validate command."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project with OpenSpec structure."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Create OpenSpec structure
        changes_dir = project_path / "openspec" / "changes"
        specs_dir = project_path / "openspec" / "specs"
        changes_dir.mkdir(parents=True)
        specs_dir.mkdir(parents=True)
        
        yield project_path
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def setup_valid_spec(self, specs_dir: Path):
        """Create a valid spec for testing."""
        spec_content = """## Purpose
This spec ensures the validation harness exercises a deterministic alpha module for automated tests.

## Requirements

### Requirement: Alpha module SHALL produce deterministic output
The alpha module SHALL produce a deterministic response for validation.

#### Scenario: Deterministic alpha run
- **GIVEN** a configured alpha module
- **WHEN** the module runs the default flow
- **THEN** the output matches the expected fixture result"""
        
        alpha_dir = specs_dir / "alpha"
        alpha_dir.mkdir(parents=True)
        (alpha_dir / "spec.md").write_text(spec_content)
    
    def setup_valid_change(self, changes_dir: Path):
        """Create a valid change for testing."""
        change_content = """# Test Change

## Why
Because reasons that are sufficiently long for validation.

## What Changes
- **alpha:** Add something"""
        
        c1_dir = changes_dir / "c1"
        c1_dir.mkdir(parents=True)
        (c1_dir / "proposal.md").write_text(change_content)
        
        # Create delta content
        delta_content = """## ADDED Requirements
### Requirement: Validator SHALL support alpha change deltas
The validator SHALL accept deltas provided by the test harness.

#### Scenario: Apply alpha delta
- **GIVEN** the test change delta
- **WHEN** openspec validate runs
- **THEN** the validator reports the change as valid"""
        
        delta_dir = c1_dir / "specs" / "alpha"
        delta_dir.mkdir(parents=True)
        (delta_dir / "spec.md").write_text(delta_content)
    
    def setup_duplicate_names(self, changes_dir: Path, specs_dir: Path):
        """Set up duplicate names for ambiguity testing."""
        # Create duplicate change
        dup_change_dir = changes_dir / "dup"
        dup_change_dir.mkdir(parents=True)
        change_content = """# Test Change

## Why
Because reasons that are sufficiently long for validation.

## What Changes
- **alpha:** Add something"""
        (dup_change_dir / "proposal.md").write_text(change_content)
        
        # Create duplicate change delta
        delta_content = """## ADDED Requirements
### Requirement: Validator SHALL support alpha change deltas
The validator SHALL accept deltas provided by the test harness.

#### Scenario: Apply alpha delta
- **GIVEN** the test change delta
- **WHEN** openspec validate runs
- **THEN** the validator reports the change as valid"""
        
        dup_delta_dir = dup_change_dir / "specs" / "dup"
        dup_delta_dir.mkdir(parents=True)
        (dup_delta_dir / "spec.md").write_text(delta_content)
        
        # Create duplicate spec
        spec_content = """## Purpose
This spec ensures the validation harness exercises a deterministic alpha module for automated tests.

## Requirements

### Requirement: Alpha module SHALL produce deterministic output
The alpha module SHALL produce a deterministic response for validation."""
        
        dup_spec_dir = specs_dir / "dup"
        dup_spec_dir.mkdir(parents=True)
        (dup_spec_dir / "spec.md").write_text(spec_content)
    
    def test_prints_helpful_hint_when_no_args_in_non_interactive_mode(self, temp_project, runner):
        """Test that validate prints a helpful hint when no arguments in non-interactive mode."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_valid_spec(specs_dir)
        self.setup_valid_change(changes_dir)
        
        with runner.isolated_filesystem():
            # Copy test project structure
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["validate"])
            assert result.exit_code == 1
            assert "Nothing to validate. Try one of:" in result.output
    
    def test_validates_all_with_all_flag_and_outputs_json_summary(self, temp_project, runner):
        """Test validate --all --json outputs JSON summary."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_valid_spec(specs_dir)
        self.setup_valid_change(changes_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["validate", "--all", "--json"])
            assert result.exit_code == 0
            
            output = result.output.strip()
            assert output != ""
            
            # Parse JSON output
            json_data = json.loads(output)
            assert isinstance(json_data.get("items"), list)
            assert "summary" in json_data
            assert "totals" in json_data["summary"]
            assert json_data.get("version") == "1.0"
    
    def test_validates_only_specs_with_specs_flag_and_respects_concurrency(self, temp_project, runner):
        """Test validate --specs --json --concurrency."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_valid_spec(specs_dir)
        self.setup_valid_change(changes_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["validate", "--specs", "--json", "--concurrency", "1"])
            assert result.exit_code == 0
            
            output = result.output.strip()
            assert output != ""
            
            # Parse JSON output
            json_data = json.loads(output)
            assert all(item.get("type") == "spec" for item in json_data.get("items", []))
    
    def test_errors_on_ambiguous_item_names_and_suggests_type_override(self, temp_project, runner):
        """Test error handling for ambiguous item names."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_valid_spec(specs_dir)
        self.setup_valid_change(changes_dir)
        self.setup_duplicate_names(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["validate", "dup"])
            assert result.exit_code == 1
            assert "Ambiguous item" in result.output
    
    def test_accepts_change_proposals_saved_with_crlf_line_endings(self, temp_project, runner):
        """Test that CRLF line endings are handled properly."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        change_id = "crlf-change"
        
        self.setup_valid_spec(specs_dir)
        
        # Convert content to CRLF
        def to_crlf(content: str) -> str:
            return content.replace('\n', '\r\n')
        
        crlf_content = to_crlf("""# CRLF Proposal

## Why
This change verifies validation works with Windows line endings.

## What Changes
- **alpha:** Ensure validation passes on CRLF files""")
        
        crlf_change_dir = changes_dir / change_id
        crlf_change_dir.mkdir(parents=True)
        (crlf_change_dir / "proposal.md").write_text(crlf_content)
        
        delta_content = to_crlf("""## ADDED Requirements
### Requirement: Parser SHALL accept CRLF change proposals
The parser SHALL accept CRLF change proposals without manual edits.

#### Scenario: Validate CRLF change
- **GIVEN** a change proposal saved with CRLF line endings
- **WHEN** a developer runs openspec validate on the proposal
- **THEN** validation succeeds without section errors""")
        
        delta_dir = crlf_change_dir / "specs" / "alpha"
        delta_dir.mkdir(parents=True)
        (delta_dir / "spec.md").write_text(delta_content)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["validate", change_id])
            assert result.exit_code == 0