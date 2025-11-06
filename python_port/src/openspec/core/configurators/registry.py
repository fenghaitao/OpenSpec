"""Tool registry for managing AI tool configurators."""

from typing import Dict, List, Optional
from .base import ToolConfigurator


class ToolRegistry:
    """Registry for AI tool configurators."""
    
    _tools: Dict[str, ToolConfigurator] = {}
    
    @classmethod
    def register(cls, tool: ToolConfigurator) -> None:
        """Register a tool configurator."""
        # Use the tool's value/id as the key, not the name
        key = getattr(tool, 'tool_id', None) or tool.name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        cls._tools[key] = tool
    
    @classmethod
    def get(cls, tool_id: str) -> Optional[ToolConfigurator]:
        """Get a tool configurator by ID."""
        return cls._tools.get(tool_id)
    
    @classmethod
    def get_all(cls) -> List[ToolConfigurator]:
        """Get all registered tool configurators."""
        return list(cls._tools.values())
    
    @classmethod
    def get_available(cls) -> List[ToolConfigurator]:
        """Get all available tool configurators."""
        return [tool for tool in cls._tools.values() if tool.is_available]


# Auto-register tools when imported
def _register_default_tools():
    """Register default tool configurators."""
    from .claude import ClaudeConfigurator
    from .cline import ClineConfigurator
    from .cursor import CursorConfigurator
    from .agents import AgentsStandardConfigurator
    
    ToolRegistry.register(ClaudeConfigurator())
    ToolRegistry.register(ClineConfigurator())
    ToolRegistry.register(CursorConfigurator())
    ToolRegistry.register(AgentsStandardConfigurator())


# Register tools on module import
_register_default_tools()