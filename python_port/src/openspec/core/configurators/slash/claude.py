"""Claude slash command configurator."""

from typing import Dict
from ..base import SlashCommandConfigurator


class ClaudeSlashCommandConfigurator(SlashCommandConfigurator):
    """Slash command configurator for Claude Code."""
    
    tool_id = "claude"
    is_available = True
    
    # File paths for Claude slash commands
    _FILE_PATHS: Dict[str, str] = {
        "proposal": ".claude/commands/openspec/proposal.md",
        "apply": ".claude/commands/openspec/apply.md", 
        "archive": ".claude/commands/openspec/archive.md"
    }
    
    # YAML frontmatter for each command
    _FRONTMATTER: Dict[str, str] = {
        "proposal": """---
name: OpenSpec: Proposal
description: Scaffold a new OpenSpec change and validate strictly.
category: OpenSpec
tags: [openspec, change]
---""",
        "apply": """---
name: OpenSpec: Apply
description: Implement an approved OpenSpec change and keep tasks in sync.
category: OpenSpec
tags: [openspec, apply]
---""",
        "archive": """---
name: OpenSpec: Archive
description: Archive a deployed OpenSpec change and update specs.
category: OpenSpec
tags: [openspec, archive]
---"""
    }
    
    def get_relative_path(self, command_id: str) -> str:
        """Get the relative path for a Claude slash command."""
        return self._FILE_PATHS[command_id]
    
    def get_frontmatter(self, command_id: str) -> str:
        """Get the frontmatter for a Claude slash command."""
        return self._FRONTMATTER[command_id]