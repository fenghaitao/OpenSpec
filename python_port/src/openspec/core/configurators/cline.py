"""Cline AI tool configurator."""

from pathlib import Path
from .base import ToolConfigurator
from ..templates.manager import TemplateManager
from ..config import OPENSPEC_MARKERS
from ...utils.file_markers import update_file_with_markers


class ClineConfigurator:
    """Configurator for Cline AI tool."""
    
    name = "Cline"
    tool_id = "cline"
    config_file_name = "CLINE.md"
    is_available = True
    
    async def configure(self, project_path: str, openspec_dir: str) -> None:
        """Configure Cline for the project."""
        file_path = str(Path(project_path) / self.config_file_name)
        content = TemplateManager.get_cline_template()
        
        await update_file_with_markers(
            file_path,
            content,
            OPENSPEC_MARKERS["start"],
            OPENSPEC_MARKERS["end"]
        )