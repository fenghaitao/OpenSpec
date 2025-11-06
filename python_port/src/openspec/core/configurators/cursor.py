"""Cursor AI tool configurator."""

from .base import ToolConfigurator


class CursorConfigurator:
    """Configurator for Cursor AI tool (slash commands only)."""
    
    name = "Cursor"
    tool_id = "cursor"
    config_file_name = ""  # Cursor uses slash commands only
    is_available = True
    
    async def configure(self, project_path: str, openspec_dir: str) -> None:
        """Configure Cursor for the project (no config file needed)."""
        # Cursor only uses slash commands, no config file needed
        pass