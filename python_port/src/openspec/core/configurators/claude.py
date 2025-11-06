"""Claude AI tool configurator."""

from pathlib import Path
from .base import ToolConfigurator
from ..templates.manager import TemplateManager
from ..config import OPENSPEC_MARKERS
from ...utils.file_markers import update_file_with_markers


class ClaudeConfigurator:
    """Configurator for Claude Code AI tool."""
    
    name = "Claude Code"
    tool_id = "claude"
    config_file_name = "CLAUDE.md"
    is_available = True
    
    async def configure(self, project_path: str, openspec_dir: str) -> None:
        """Configure Claude for the project."""
        file_path = str(Path(project_path) / self.config_file_name)
        content = TemplateManager.get_claude_template()
        
        await update_file_with_markers(
            file_path,
            content,
            OPENSPEC_MARKERS["start"],
            OPENSPEC_MARKERS["end"]
        )