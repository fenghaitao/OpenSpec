"""Integration tests for init command with AI configurators."""

import pytest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner

from openspec.cli.main import main
from openspec.utils.file_system import read_file
from openspec.core.config import OPENSPEC_MARKERS


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


def test_init_with_claude(runner, temp_project):
    """Test init command with Claude tool."""
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
        assert result.exit_code == 0
        
        # Check OpenSpec structure
        assert Path("openspec").exists()
        assert Path("openspec/project.md").exists()
        assert Path("AGENTS.md").exists()
        
        # Check Claude configuration
        assert Path("CLAUDE.md").exists()
        claude_content = read_file("CLAUDE.md")
        assert OPENSPEC_MARKERS["start"] in claude_content
        assert "OpenSpec Instructions" in claude_content
        
        # Check Claude slash commands
        assert Path(".claude/commands/openspec/proposal.md").exists()
        assert Path(".claude/commands/openspec/apply.md").exists()
        assert Path(".claude/commands/openspec/archive.md").exists()
        
        proposal_content = read_file(".claude/commands/openspec/proposal.md")
        assert "name: OpenSpec: Proposal" in proposal_content
        assert OPENSPEC_MARKERS["start"] in proposal_content


def test_init_with_multiple_tools(runner, temp_project):
    """Test init command with multiple tools."""
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude,cline,cursor"])
        assert result.exit_code == 0
        
        # Check Claude files
        assert Path("CLAUDE.md").exists()
        assert Path(".claude/commands/openspec/proposal.md").exists()
        
        # Check Cline files
        assert Path("CLINE.md").exists()
        assert Path(".cline/prompts/openspec/proposal.md").exists()
        
        # Check Cursor files (slash commands only)
        assert Path(".cursor/prompts/openspec/proposal.md").exists()
        
        # Universal AGENTS.md should be created
        assert Path("AGENTS.md").exists()


def test_init_extend_mode(runner, temp_project):
    """Test init command in extend mode (updating existing project)."""
    with runner.isolated_filesystem():
        # First initialization
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude"])
        assert result.exit_code == 0
        
        # Modify Claude file to test preservation
        claude_file = Path("CLAUDE.md")
        original_content = claude_file.read_text()
        custom_content = f"# My Custom Header\n\n{original_content}\n\n# My Custom Footer"
        claude_file.write_text(custom_content)
        
        # Second initialization (extend mode)
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "claude,cline"])
        assert result.exit_code == 0
        
        # Check that custom content is preserved
        updated_content = claude_file.read_text()
        assert "My Custom Header" in updated_content
        assert "My Custom Footer" in updated_content
        assert OPENSPEC_MARKERS["start"] in updated_content
        
        # Check that Cline was added
        assert Path("CLINE.md").exists()


def test_init_agents_only(runner, temp_project):
    """Test init with universal AGENTS.md only."""
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "agents"])
        assert result.exit_code == 0
        
        # Check that AGENTS.md is created
        assert Path("AGENTS.md").exists()
        agents_content = read_file("AGENTS.md")
        assert OPENSPEC_MARKERS["start"] in agents_content
        assert "OpenSpec Instructions" in agents_content
        
        # No other tool files should be created
        assert not Path("CLAUDE.md").exists()
        assert not Path("CLINE.md").exists()


def test_init_error_handling(runner, temp_project):
    """Test init command error handling."""
    with runner.isolated_filesystem():
        # Test with invalid tool
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", "invalid-tool"])
        assert result.exit_code == 1
        
        # Test with empty tools
        result = runner.invoke(main, ["init", "--non-interactive", "--ai-tools", ""])
        assert result.exit_code == 1