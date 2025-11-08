"""Tests for show command - ported from test/commands/show.test.ts"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main


class TestShowCommand:
    """Test cases for show command."""
    
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
    
    def setup_demo_change(self, changes_dir: Path):
        """Create a demo change for testing."""
        change_content = "# Change: Demo\n\n## Why\nBecause reasons.\n\n## What Changes\n- **auth:** Add requirement\n"
        demo_dir = changes_dir / "demo"
        demo_dir.mkdir(parents=True)
        (demo_dir / "proposal.md").write_text(change_content)
    
    def setup_auth_spec(self, specs_dir: Path):
        """Create an auth spec for testing."""
        spec_content = "## Purpose\nAuth spec.\n\n## Requirements\n\n### Requirement: User Authentication\nText\n"
        auth_dir = specs_dir / "auth"
        auth_dir.mkdir(parents=True)
        (auth_dir / "spec.md").write_text(spec_content)
    
    def setup_ambiguous_foo(self, changes_dir: Path, specs_dir: Path):
        """Create ambiguous 'foo' items for testing."""
        # Create foo change
        foo_change_content = "# Change: Foo\n\n## Why\n\n## What Changes\n"
        foo_change_dir = changes_dir / "foo"
        foo_change_dir.mkdir(parents=True)
        (foo_change_dir / "proposal.md").write_text(foo_change_content)
        
        # Create foo spec
        foo_spec_content = "## Purpose\n\n## Requirements\n\n### Requirement: R\nX"
        foo_spec_dir = specs_dir / "foo"
        foo_spec_dir.mkdir(parents=True)
        (foo_spec_dir / "spec.md").write_text(foo_spec_content)
    
    def test_prints_hint_and_non_zero_exit_when_no_args_and_non_interactive(self, temp_project, runner):
        """Test that show prints hint and exits with non-zero when no args in non-interactive mode."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_demo_change(changes_dir)
        self.setup_auth_spec(specs_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["show"])
            assert result.exit_code != 0
            assert "Nothing to show." in result.output
            assert "openspec show <item>" in result.output
            assert "openspec change show" in result.output
            assert "openspec spec show" in result.output
    
    def test_auto_detects_change_id_and_supports_json(self, temp_project, runner):
        """Test auto-detection of change ID and JSON support."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_demo_change(changes_dir)
        self.setup_auth_spec(specs_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["show", "demo", "--json"])
            assert result.exit_code == 0
            
            # Parse JSON output
            json_data = json.loads(result.output)
            assert json_data.get("id") == "demo"
            assert isinstance(json_data.get("deltas"), list)
    
    def test_auto_detects_spec_id_and_supports_spec_only_flags(self, temp_project, runner):
        """Test auto-detection of spec ID and spec-only flags."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_demo_change(changes_dir)
        self.setup_auth_spec(specs_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["show", "auth", "--json", "--requirements"])
            assert result.exit_code == 0
            
            # Parse JSON output
            json_data = json.loads(result.output)
            assert json_data.get("id") == "auth"
            assert isinstance(json_data.get("requirements"), list)
    
    def test_handles_ambiguity_and_suggests_type(self, temp_project, runner):
        """Test handling of ambiguous item names."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_demo_change(changes_dir)
        self.setup_auth_spec(specs_dir)
        self.setup_ambiguous_foo(changes_dir, specs_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["show", "foo"])
            assert result.exit_code != 0
            assert "Ambiguous item" in result.output
            assert "--type change|spec" in result.output
    
    def test_prints_nearest_matches_when_not_found(self, temp_project, runner):
        """Test printing nearest matches when item is not found."""
        changes_dir = temp_project / "openspec" / "changes"
        specs_dir = temp_project / "openspec" / "specs"
        
        self.setup_demo_change(changes_dir)
        self.setup_auth_spec(specs_dir)
        
        with runner.isolated_filesystem():
            import os
            os.chdir(str(temp_project))
            
            result = runner.invoke(main, ["show", "unknown-item"])
            assert result.exit_code != 0
            assert "Unknown item 'unknown-item'" in result.output
            assert "Did you mean:" in result.output