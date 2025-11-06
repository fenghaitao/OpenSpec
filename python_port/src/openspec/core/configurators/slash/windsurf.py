"""Windsurf slash command configurator."""

from typing import Dict
from ..base import SlashCommandConfigurator


class WindsurfSlashCommandConfigurator(SlashCommandConfigurator):
    """Slash command configurator for Windsurf."""
    
    tool_id = "windsurf"
    is_available = True
    
    # File paths for Windsurf slash commands
    _FILE_PATHS: Dict[str, str] = {
        "proposal": ".windsurf/prompts/openspec/proposal.md",
        "apply": ".windsurf/prompts/openspec/apply.md",
        "archive": ".windsurf/prompts/openspec/archive.md"
    }
    
    # Frontmatter for each command
    _FRONTMATTER: Dict[str, str] = {
        "proposal": """# OpenSpec: Proposal

Scaffold a new OpenSpec change and validate strictly.""",
        "apply": """# OpenSpec: Apply

Implement an approved OpenSpec change and keep tasks in sync.""",
        "archive": """# OpenSpec: Archive

Archive a deployed OpenSpec change and update specs."""
    }
    
    def get_relative_path(self, command_id: str) -> str:
        """Get the relative path for a Windsurf slash command."""
        return self._FILE_PATHS[command_id]
    
    def get_frontmatter(self, command_id: str) -> str:
        """Get the frontmatter for a Windsurf slash command."""
        return self._FRONTMATTER[command_id]