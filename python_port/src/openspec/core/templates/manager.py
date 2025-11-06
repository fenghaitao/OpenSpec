"""Template manager for generating AI tool configurations."""

from typing import Dict, Any, Callable


class TemplateManager:
    """Manager for AI tool templates and content generation."""
    
    @staticmethod
    def get_claude_template() -> str:
        """Get the Claude configuration template."""
        from .claude_template import claude_template
        return claude_template
    
    @staticmethod
    def get_cline_template() -> str:
        """Get the Cline configuration template."""
        from .cline_template import cline_template
        return cline_template
    
    @staticmethod
    def get_agents_standard_template() -> str:
        """Get the standard AGENTS.md template."""
        from .agents_root_stub import agents_root_stub_template
        return agents_root_stub_template
    
    @staticmethod
    def get_slash_command_body(command_id: str) -> str:
        """Get the body content for a slash command."""
        from .slash_commands import get_slash_command_body
        return get_slash_command_body(command_id)
    
    @staticmethod
    def get_project_template(context: Dict[str, Any] = None) -> str:
        """Get the project template with context."""
        from .project_template import create_project_template
        return create_project_template(context or {})