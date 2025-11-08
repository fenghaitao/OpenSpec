"""Tests for OpenSpec validate command (ported from TypeScript)."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main


class TestValidateCommand:
    """Test the top-level validate command."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project with OpenSpec structure."""
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

    def setup_basic_fixtures(self, changes_dir, specs_dir):
        """Set up basic test fixtures similar to TypeScript tests."""
        
        # Create a valid spec
        spec_content = [
            '## Purpose',
            'This spec ensures the validation harness exercises a deterministic alpha module for automated tests.',
            '',
            '## Requirements',
            '',
            '### Requirement: Alpha module SHALL produce deterministic output',
            'The alpha module SHALL produce a deterministic response for validation.',
            '',
            '#### Scenario: Deterministic alpha run',
            '- **GIVEN** a configured alpha module',
            '- **WHEN** the module runs the default flow',
            '- **THEN** the output matches the expected fixture result',
        ]
        
        alpha_spec_dir = specs_dir / "alpha"
        alpha_spec_dir.mkdir()
        (alpha_spec_dir / "spec.md").write_text('\n'.join(spec_content))

        # Create a simple change with bullets
        change_content = (
            "# Test Change\n\n"
            "## Why\n"
            "Because reasons that are sufficiently long for validation.\n\n"
            "## What Changes\n"
            "- **alpha:** Add something"
        )
        
        c1_dir = changes_dir / "c1"
        c1_dir.mkdir()
        (c1_dir / "proposal.md").write_text(change_content)
        
        # Create delta spec
        delta_content = [
            '## ADDED Requirements',
            '### Requirement: Validator SHALL support alpha change deltas',
            'The validator SHALL accept deltas provided by the test harness.',
            '',
            '#### Scenario: Apply alpha delta',
            '- **GIVEN** the test change delta',
            '- **WHEN** openspec validate runs',
            '- **THEN** the validator reports the change as valid',
        ]
        
        c1_delta_dir = c1_dir / "specs" / "alpha"
        c1_delta_dir.mkdir(parents=True)
        (c1_delta_dir / "spec.md").write_text('\n'.join(delta_content))

    def test_validate_no_args_non_interactive(self, runner, temp_project):
        """Test validate with no args in non-interactive mode."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_basic_fixtures(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["validate"], env={"OPENSPEC_INTERACTIVE": "0"})
            
            assert result.exit_code == 1
            assert "Nothing to validate" in result.output

    def test_validate_all_with_json(self, runner, temp_project):
        """Test validate --all --json output."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_basic_fixtures(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["validate", "--all", "--json"])
            
            assert result.exit_code == 0
            # Should contain JSON output
            assert result.output.strip()

    def test_validate_specs_only(self, runner, temp_project):
        """Test validate --specs flag."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_basic_fixtures(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["validate", "--specs"])
            
            assert result.exit_code == 0

    def test_validate_changes_only(self, runner, temp_project):
        """Test validate --changes flag."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_basic_fixtures(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["validate", "--changes"])
            
            assert result.exit_code == 0

    def test_validate_specific_item(self, runner, temp_project):
        """Test validating a specific item."""
        project_path, changes_dir, specs_dir = temp_project
        self.setup_basic_fixtures(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["validate", "c1"])
            
            assert result.exit_code == 0

    def test_validate_crlf_line_endings(self, runner, temp_project):
        """Test that validate accepts CRLF line endings (ported from JS)."""
        project_path, changes_dir, specs_dir = temp_project
        
        # Create change with CRLF line endings
        change_id = "crlf-change"
        crlf_content = '\r\n'.join([
            '# CRLF Proposal',
            '',
            '## Why',
            'This change verifies validation works with Windows line endings.',
            '',
            '## What Changes',
            '- **alpha:** Ensure validation passes on CRLF files',
        ])
        
        crlf_change_dir = changes_dir / change_id
        crlf_change_dir.mkdir()
        (crlf_change_dir / "proposal.md").write_text(crlf_content)
        
        # Create delta with CRLF
        delta_content = '\r\n'.join([
            '## ADDED Requirements',
            '### Requirement: Parser SHALL accept CRLF change proposals',
            'The parser SHALL accept CRLF change proposals without manual edits.',
            '',
            '#### Scenario: Validate CRLF change',
            '- **GIVEN** a change proposal saved with CRLF line endings',
            '- **WHEN** a developer runs openspec validate on the proposal',
            '- **THEN** validation succeeds without section errors',
        ])
        
        delta_dir = crlf_change_dir / "specs" / "alpha"
        delta_dir.mkdir(parents=True)
        (delta_dir / "spec.md").write_text(delta_content)
        
        # Create base alpha spec
        alpha_spec_dir = specs_dir / "alpha"
        alpha_spec_dir.mkdir()
        (alpha_spec_dir / "spec.md").write_text("## Purpose\nBase spec\n## Requirements\n")
        
        with runner.isolated_filesystem():
            os.chdir(str(project_path))
            result = runner.invoke(main, ["validate", change_id])
            
            assert result.exit_code == 0

    def test_validate_outside_project(self, runner):
        """Test validate command outside OpenSpec project."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["validate"])
            
            assert result.exit_code == 1
            assert "Not in an OpenSpec project" in result.output