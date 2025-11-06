"""Universal AGENTS.md configurator."""

from pathlib import Path
from .base import ToolConfigurator
from ..templates.manager import TemplateManager
from ..config import OPENSPEC_MARKERS
from ...utils.file_markers import update_file_with_markers


class AgentsStandardConfigurator:
    """Configurator for universal AGENTS.md (works with any AI tool)."""
    
    name = "Universal AGENTS.md"
    tool_id = "agents"
    config_file_name = "AGENTS.md"
    is_available = True
    
    async def configure(self, project_path: str, openspec_dir: str) -> None:
        """Configure universal AGENTS.md for the project."""
        file_path = str(Path(project_path) / self.config_file_name)
        content = TemplateManager.get_agents_standard_template()
        
        await update_file_with_markers(
            file_path,
            content,
            OPENSPEC_MARKERS["start"],
            OPENSPEC_MARKERS["end"]
        )