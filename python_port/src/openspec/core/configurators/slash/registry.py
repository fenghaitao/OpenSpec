"""Registry for slash command configurators."""

from typing import Dict, List, Optional
from ..base import SlashCommandConfigurator


class SlashCommandRegistry:
    """Registry for slash command configurators."""
    
    _configurators: Dict[str, SlashCommandConfigurator] = {}
    
    @classmethod
    def register(cls, configurator: SlashCommandConfigurator) -> None:
        """Register a slash command configurator."""
        cls._configurators[configurator.tool_id] = configurator
    
    @classmethod
    def get(cls, tool_id: str) -> Optional[SlashCommandConfigurator]:
        """Get a slash command configurator by tool ID."""
        return cls._configurators.get(tool_id)
    
    @classmethod
    def get_all(cls) -> List[SlashCommandConfigurator]:
        """Get all registered slash command configurators."""
        return list(cls._configurators.values())


# Auto-register slash command configurators
def _register_default_configurators():
    """Register default slash command configurators."""
    from .claude import ClaudeSlashCommandConfigurator
    from .cline import ClineSlashCommandConfigurator
    from .cursor import CursorSlashCommandConfigurator
    from .github_copilot import GitHubCopilotSlashCommandConfigurator
    from .windsurf import WindsurfSlashCommandConfigurator
    
    SlashCommandRegistry.register(ClaudeSlashCommandConfigurator())
    SlashCommandRegistry.register(ClineSlashCommandConfigurator())
    SlashCommandRegistry.register(CursorSlashCommandConfigurator())
    SlashCommandRegistry.register(GitHubCopilotSlashCommandConfigurator())
    SlashCommandRegistry.register(WindsurfSlashCommandConfigurator())


# Register configurators on module import
_register_default_configurators()