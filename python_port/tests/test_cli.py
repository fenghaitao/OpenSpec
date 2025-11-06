"""Tests for OpenSpec CLI."""

import pytest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "OpenSpec" in result.output


def test_init_command(runner, temp_project):
    """Test init command."""
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
        assert result.exit_code == 0
        
        # Check created files
        assert Path("openspec").exists()
        assert Path("openspec/project.md").exists()
        assert Path("AGENTS.md").exists()


def test_validate_no_project(runner, temp_project):
    """Test validate command outside project."""
    result = runner.invoke(main, ["validate"])
    assert result.exit_code == 1
    assert "Not in an OpenSpec project" in result.output


def test_change_create(runner, temp_project):
    """Test change creation."""
    with runner.isolated_filesystem():
        # First init project
        runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
        
        # Create change
        result = runner.invoke(main, ["change", "create", "test-change"])
        assert result.exit_code == 0
        
        # Check created files
        change_dir = Path("openspec/changes/test-change")
        assert change_dir.exists()
        assert (change_dir / "proposal.md").exists()
        assert (change_dir / "tasks.md").exists()


def test_spec_create(runner, temp_project):
    """Test spec creation."""
    with runner.isolated_filesystem():
        # First init project
        runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
        
        # Create spec
        result = runner.invoke(main, ["spec", "create", "test-spec"])
        assert result.exit_code == 0
        
        # Check created files
        spec_dir = Path("openspec/specs/test-spec")
        assert spec_dir.exists()
        assert (spec_dir / "spec.md").exists()


def test_list_empty_project(runner, temp_project):
    """Test list command in empty project."""
    with runner.isolated_filesystem():
        # First init project
        runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
        
        # List changes
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "No changes found" in result.output


def test_view_empty_project(runner, temp_project):
    """Test view command in empty project."""
    with runner.isolated_filesystem():
        # First init project
        runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
        
        # View dashboard
        result = runner.invoke(main, ["view"])
        assert result.exit_code == 0
        assert "Project Dashboard" in result.output