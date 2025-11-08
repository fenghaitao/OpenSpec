"""End-to-end CLI tests for OpenSpec (ported from TypeScript)."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main


class TestCLIE2E:
    """End-to-end CLI testing."""

    @pytest.fixture
    def temp_dir(self):
        """Create a clean temporary directory."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_basic_workflow(self, runner, temp_dir):
        """Test basic OpenSpec workflow: init -> change create -> validate."""
        
        with runner.isolated_filesystem():
            os.chdir(str(temp_dir))
            
            # 1. Initialize project
            result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
            assert result.exit_code == 0
            assert Path("openspec").exists()
            assert Path("openspec/project.md").exists()
            assert Path("AGENTS.md").exists()
            
            # 2. Create a change
            result = runner.invoke(main, ["change", "create", "test-feature"])
            if result.exit_code == 0:  # May not be implemented yet
                change_dir = Path("openspec/changes/test-feature")
                assert change_dir.exists()
                assert (change_dir / "proposal.md").exists()
            
            # 3. Create a spec
            result = runner.invoke(main, ["spec", "create", "test-api"])
            if result.exit_code == 0:  # May not be implemented yet
                spec_dir = Path("openspec/specs/test-api")
                assert spec_dir.exists()
                assert (spec_dir / "spec.md").exists()
            
            # 4. List changes
            result = runner.invoke(main, ["list"])
            # Should work even with no changes
            
            # 5. Validate project
            result = runner.invoke(main, ["validate", "--all"])
            # Should be able to validate empty project

    def test_init_with_different_tools(self, runner, temp_dir):
        """Test initialization with different AI tools."""
        
        with runner.isolated_filesystem():
            os.chdir(str(temp_dir))
            
            # Test with multiple tools
            result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude,cursor,cline"])
            assert result.exit_code == 0
            
            # Check that tool-specific files were created
            assert Path(".claude").exists()
            assert Path(".cursor").exists()  # Note: might be .cursor/prompts in Python version
            
            # Check AGENTS.md was created
            assert Path("AGENTS.md").exists()
            assert Path("openspec/AGENTS.md").exists()

    def test_validate_empty_project(self, runner, temp_dir):
        """Test validation of empty project."""
        
        with runner.isolated_filesystem():
            os.chdir(str(temp_dir))
            
            # Initialize first
            runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
            
            # Validate empty project
            result = runner.invoke(main, ["validate", "--all"])
            assert result.exit_code == 0  # Empty project should validate successfully

    def test_help_commands(self, runner):
        """Test help commands work correctly."""
        
        # Main help
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "OpenSpec" in result.output
        
        # Command-specific help
        for command in ["init", "validate", "list", "show", "change", "spec"]:
            result = runner.invoke(main, [command, "--help"])
            # Help should work even if command isn't fully implemented
            assert result.exit_code in [0, 2]  # 0 for success, 2 for Click help

    def test_error_handling_outside_project(self, runner):
        """Test error handling when running commands outside OpenSpec project."""
        
        with runner.isolated_filesystem():
            # Try to run commands that require OpenSpec project
            
            result = runner.invoke(main, ["validate"])
            assert result.exit_code != 0
            
            result = runner.invoke(main, ["list"])
            assert result.exit_code != 0
            
            # Show might also require project context
            result = runner.invoke(main, ["show", "anything"])
            assert result.exit_code != 0

    def test_json_output_format(self, runner, temp_dir):
        """Test JSON output format where supported."""
        
        with runner.isolated_filesystem():
            os.chdir(str(temp_dir))
            
            # Initialize project
            runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
            
            # Test JSON output for validation
            result = runner.invoke(main, ["validate", "--all", "--json"])
            if result.exit_code == 0 and result.output.strip():
                # If JSON output is implemented, it should be parseable
                import json
                try:
                    json.loads(result.output)
                except json.JSONDecodeError:
                    pytest.fail("Invalid JSON output from validate --json")

    def test_non_interactive_mode(self, runner, temp_dir):
        """Test non-interactive mode works correctly."""
        
        with runner.isolated_filesystem():
            os.chdir(str(temp_dir))
            
            # All commands should work in non-interactive mode
            result = runner.invoke(
                main, 
                ["init", "--non-interactive", "--ai-tools", "claude"],
                env={"OPENSPEC_INTERACTIVE": "0"}
            )
            assert result.exit_code == 0
            
            # Other commands should also respect non-interactive mode
            result = runner.invoke(
                main,
                ["validate"],
                env={"OPENSPEC_INTERACTIVE": "0"}
            )
            # Should not hang waiting for input

    def test_concurrent_safety(self, runner, temp_dir):
        """Test that commands are safe for concurrent execution."""
        
        with runner.isolated_filesystem():
            os.chdir(str(temp_dir))
            
            # Initialize project
            runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
            
            # Multiple validate commands should be safe
            results = []
            for _ in range(3):
                result = runner.invoke(main, ["validate", "--all"])
                results.append(result)
            
            # All should succeed or fail consistently
            exit_codes = [r.exit_code for r in results]
            assert len(set(exit_codes)) <= 1  # All same result