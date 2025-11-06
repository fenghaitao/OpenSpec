"""Base configurator interfaces and types."""

from abc import ABC, abstractmethod
from typing import Protocol, List, Dict, Any
from pathlib import Path


class ToolConfigurator(Protocol):
    """Protocol for AI tool configurators."""
    
    name: str
    config_file_name: str
    is_available: bool
    
    async def configure(self, project_path: str, openspec_dir: str) -> None:
        """Configure the AI tool for the project."""
        ...


class SlashCommandTarget:
    """Represents a slash command target file."""
    
    def __init__(self, id: str, path: str, kind: str = "slash"):
        self.id = id
        self.path = path
        self.kind = kind


class SlashCommandConfigurator(ABC):
    """Base class for slash command configurators."""
    
    @property
    @abstractmethod
    def tool_id(self) -> str:
        """Unique identifier for the tool."""
        ...
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Whether this configurator is available."""
        ...
    
    def get_targets(self) -> List[SlashCommandTarget]:
        """Get all slash command targets for this tool."""
        from ..templates.slash_commands import ALL_COMMANDS
        return [
            SlashCommandTarget(id=cmd_id, path=self.get_relative_path(cmd_id))
            for cmd_id in ALL_COMMANDS
        ]
    
    async def generate_all(self, project_path: str, openspec_dir: str) -> List[str]:
        """Generate all slash command files for this tool."""
        from ...utils.file_system import ensure_directory, write_file, read_file
        from ..config import OPENSPEC_MARKERS
        
        created_or_updated = []
        
        for target in self.get_targets():
            body = self.get_body(target.id)
            file_path = Path(project_path) / target.path
            
            # Ensure directory exists
            ensure_directory(str(file_path.parent))
            
            if file_path.exists():
                self._update_body(str(file_path), body)
            else:
                frontmatter = self.get_frontmatter(target.id)
                sections = []
                if frontmatter:
                    sections.append(frontmatter.strip())
                sections.append(f"{OPENSPEC_MARKERS['start']}\n{body}\n{OPENSPEC_MARKERS['end']}")
                content = "\n".join(sections) + "\n"
                write_file(str(file_path), content)
            
            created_or_updated.append(target.path)
        
        return created_or_updated
    
    async def update_existing(self, project_path: str, openspec_dir: str) -> List[str]:
        """Update existing slash command files."""
        updated = []
        
        for target in self.get_targets():
            file_path = Path(project_path) / target.path
            if file_path.exists():
                body = self.get_body(target.id)
                self._update_body(str(file_path), body)
                updated.append(target.path)
        
        return updated
    
    @abstractmethod
    def get_relative_path(self, command_id: str) -> str:
        """Get the relative path for a slash command file."""
        ...
    
    @abstractmethod
    def get_frontmatter(self, command_id: str) -> str:
        """Get the frontmatter for a slash command file."""
        ...
    
    def get_body(self, command_id: str) -> str:
        """Get the body content for a slash command."""
        from ..templates.manager import TemplateManager
        return TemplateManager.get_slash_command_body(command_id).strip()
    
    def resolve_absolute_path(self, project_path: str, command_id: str) -> str:
        """Resolve absolute path for a slash command target."""
        rel_path = self.get_relative_path(command_id)
        return str(Path(project_path) / rel_path)
    
    def _update_body(self, file_path: str, body: str) -> None:
        """Update the body content between OpenSpec markers."""
        from ...utils.file_system import read_file, write_file
        from ..config import OPENSPEC_MARKERS
        
        content = read_file(file_path)
        start_marker = OPENSPEC_MARKERS["start"]
        end_marker = OPENSPEC_MARKERS["end"]
        
        start_index = content.find(start_marker)
        end_index = content.find(end_marker)
        
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            raise ValueError(f"Missing OpenSpec markers in {file_path}")
        
        before = content[:start_index + len(start_marker)]
        after = content[end_index:]
        updated_content = f"{before}\n{body}\n{after}"
        
        write_file(file_path, updated_content)