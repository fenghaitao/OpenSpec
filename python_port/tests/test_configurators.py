"""Tests for AI tool configurators."""

import pytest
import tempfile
import shutil
from pathlib import Path

from openspec.core.configurators.claude import ClaudeConfigurator
from openspec.core.configurators.cline import ClineConfigurator
from openspec.core.configurators.slash.claude import ClaudeSlashCommandConfigurator
from openspec.core.configurators.registry import ToolRegistry
from openspec.core.configurators.slash.registry import SlashCommandRegistry
from openspec.core.config import OPENSPEC_MARKERS
from openspec.utils.file_system import read_file


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_claude_configurator(temp_project):
    """Test Claude configurator creates correct file."""
    configurator = ClaudeConfigurator()
    
    await configurator.configure(str(temp_project), "openspec")
    
    claude_file = temp_project / "CLAUDE.md"
    assert claude_file.exists()
    
    content = read_file(str(claude_file))
    assert OPENSPEC_MARKERS["start"] in content
    assert OPENSPEC_MARKERS["end"] in content
    assert "OpenSpec Instructions" in content


@pytest.mark.asyncio
async def test_cline_configurator(temp_project):
    """Test Cline configurator creates correct file."""
    configurator = ClineConfigurator()
    
    await configurator.configure(str(temp_project), "openspec")
    
    cline_file = temp_project / "CLINE.md"
    assert cline_file.exists()
    
    content = read_file(str(cline_file))
    assert OPENSPEC_MARKERS["start"] in content
    assert OPENSPEC_MARKERS["end"] in content
    assert "OpenSpec Instructions" in content


@pytest.mark.asyncio
async def test_claude_slash_commands(temp_project):
    """Test Claude slash command configurator."""
    configurator = ClaudeSlashCommandConfigurator()
    
    created_files = await configurator.generate_all(str(temp_project), "openspec")
    
    assert len(created_files) == 3
    assert ".claude/commands/openspec/proposal.md" in created_files
    assert ".claude/commands/openspec/apply.md" in created_files
    assert ".claude/commands/openspec/archive.md" in created_files
    
    # Check proposal file content
    proposal_file = temp_project / ".claude/commands/openspec/proposal.md"
    assert proposal_file.exists()
    
    content = read_file(str(proposal_file))
    assert "name: OpenSpec: Proposal" in content
    assert "Scaffold a new OpenSpec change" in content
    assert OPENSPEC_MARKERS["start"] in content
    assert OPENSPEC_MARKERS["end"] in content


def test_tool_registry():
    """Test tool registry functionality."""
    claude_configurator = ToolRegistry.get("claude")
    assert claude_configurator is not None
    assert claude_configurator.name == "Claude Code"
    assert claude_configurator.config_file_name == "CLAUDE.md"
    
    cline_configurator = ToolRegistry.get("cline")
    assert cline_configurator is not None
    assert cline_configurator.name == "Cline"


def test_slash_command_registry():
    """Test slash command registry functionality."""
    claude_slash = SlashCommandRegistry.get("claude")
    assert claude_slash is not None
    assert claude_slash.tool_id == "claude"
    
    cline_slash = SlashCommandRegistry.get("cline")
    assert cline_slash is not None
    assert cline_slash.tool_id == "cline"


@pytest.mark.asyncio
async def test_file_update_preserves_custom_content(temp_project):
    """Test that updating files preserves custom content outside markers."""
    configurator = ClaudeConfigurator()
    
    # Create initial file with custom content
    claude_file = temp_project / "CLAUDE.md"
    initial_content = f"""# My Custom Claude Setup

Some custom instructions here.

{OPENSPEC_MARKERS["start"]}
Old OpenSpec content
{OPENSPEC_MARKERS["end"]}

More custom content below.
"""
    
    claude_file.write_text(initial_content)
    
    # Update the file
    await configurator.configure(str(temp_project), "openspec")
    
    # Check that custom content is preserved
    updated_content = read_file(str(claude_file))
    assert "My Custom Claude Setup" in updated_content
    assert "Some custom instructions here." in updated_content
    assert "More custom content below." in updated_content
    assert "OpenSpec Instructions" in updated_content  # New content
    assert "Old OpenSpec content" not in updated_content  # Old content replaced


@pytest.mark.asyncio
async def test_targets_and_paths():
    """Test slash command targets and path resolution."""
    configurator = ClaudeSlashCommandConfigurator()
    
    targets = configurator.get_targets()
    assert len(targets) == 3
    
    proposal_target = next(t for t in targets if t.id == "proposal")
    assert proposal_target.path == ".claude/commands/openspec/proposal.md"
    
    # Test path resolution
    abs_path = configurator.resolve_absolute_path("/test/project", "proposal")
    assert abs_path == "/test/project/.claude/commands/openspec/proposal.md"