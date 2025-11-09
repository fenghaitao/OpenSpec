"""Template manager for generating AI tool configurations."""

from typing import Dict, Any, List, NamedTuple


class Template(NamedTuple):
    """Template definition."""
    path: str
    content: str


class TemplateManager:
    """Manager for AI tool templates and content generation."""
    
    @staticmethod
    def _read_ts_template(filename: str, export_name: str) -> str:
        """Read a template from TypeScript file."""
        try:
            from pathlib import Path
            import re
            
            # Path to TypeScript templates
            current_file = Path(__file__)
            python_port_root = current_file.parent.parent.parent.parent.parent  # Go up to python_port root
            openspec_root = python_port_root.parent  # Go up one more to main OpenSpec directory
            ts_template_path = openspec_root / "src" / "core" / "templates" / filename
            
            # Read and extract the TypeScript template
            ts_content = ts_template_path.read_text()
            
            # Extract the template content
            pattern = rf'export const {export_name} = `(.*?)`(?=;|\n\nexport|\n\n\/\/|$)'
            match = re.search(pattern, ts_content, re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                # Unescape backticks from TypeScript template literals
                content = content.replace('\\`', '`')
                # Replace any TypeScript CLI commands with Python equivalents
                content = content.replace('`openspec ', '`openspec-py ')
                content = content.replace(' openspec ', ' openspec-py ')
                return content
                
        except Exception as e:
            print(f"Warning: Could not read TypeScript template {filename} ({e}). Using fallback.")
            
        # Return a basic fallback
        return f"# {export_name} Template\n\nTemplate could not be loaded from TypeScript."
    
    @staticmethod
    def _extract_ts_slash_command(command_id: str) -> str:
        """Extract a slash command from TypeScript templates (same logic as init.py)."""
        from pathlib import Path
        import re
        
        # Path to TypeScript slash command templates
        current_file = Path(__file__)
        python_port_root = current_file.parent.parent.parent.parent.parent  # Go up to python_port root
        openspec_root = python_port_root.parent  # Go up one more to main OpenSpec directory
        ts_templates_path = openspec_root / "src" / "core" / "templates" / "slash-command-templates.ts"
        
        # Read the TypeScript template file
        ts_content = ts_templates_path.read_text()
        
        # Map command IDs to the constants needed
        template_map = {
            "proposal": ("proposal", "proposalGuardrails", "proposalSteps", "proposalReferences"),
            "apply": ("apply", "baseGuardrails", "applySteps", "applyReferences"),
            "archive": ("archive", "baseGuardrails", "archiveSteps", "archiveReferences")
        }
        
        if command_id not in template_map:
            raise ValueError(f"Unknown command ID: {command_id}")
        
        _, *const_names = template_map[command_id]
        
        # First extract baseGuardrails since other constants may reference it
        base_guardrails = ""
        base_match = re.search(r"const baseGuardrails = `(.*?)`(?=;)", ts_content, re.DOTALL)
        if base_match:
            base_guardrails = base_match.group(1).strip()
        
        # Extract each constant's content and resolve template literals
        content_parts = []
        for const_name in const_names:
            pattern = rf"const {const_name} = `(.*?)`(?=;)"
            match = re.search(pattern, ts_content, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Resolve template literal interpolations
                content = content.replace("${baseGuardrails}\\n", base_guardrails + "\n")
                content = content.replace("${baseGuardrails}", base_guardrails)
                content_parts.append(content)
        
        if not content_parts:
            raise ValueError(f"Could not find constants for {command_id} slash command")
        
        # Join the parts as the TypeScript code does
        content = "\n\n".join(content_parts)
        
        # Unescape backticks from TypeScript template literals
        content = content.replace('\\`', '`')
        
        # Replace TypeScript CLI commands with Python equivalents
        content = content.replace('`openspec ', '`openspec-py ')
        content = content.replace(' openspec ', ' openspec-py ')
        
        return content.strip()
    
    @staticmethod
    def get_templates(context: Dict[str, Any] = None) -> List[Template]:
        """Get all templates for the openspec directory."""
        from .agents_template import create_agents_openspec_template
        from .project_template import create_project_template
        
        context = context or {}
        
        return [
            Template(
                path='AGENTS.md',
                content=create_agents_openspec_template()
            ),
            Template(
                path='project.md', 
                content=create_project_template(context)
            )
        ]
    
    @staticmethod
    def get_claude_template() -> str:
        """Get the Claude configuration template (uses agents root stub)."""
        return TemplateManager._read_ts_template("agents-root-stub.ts", "agentsRootStubTemplate")
    
    @staticmethod
    def get_cline_template() -> str:
        """Get the Cline configuration template (uses agents root stub)."""
        return TemplateManager._read_ts_template("agents-root-stub.ts", "agentsRootStubTemplate")
    
    @staticmethod
    def get_agents_root_stub() -> str:
        """Get the root AGENTS.md stub template."""
        return TemplateManager._read_ts_template("agents-root-stub.ts", "agentsRootStubTemplate")
    
    @staticmethod
    def get_slash_command_body(command_id: str) -> str:
        """Get the body content for a slash command from TypeScript."""
        try:
            # Read from TypeScript slash command templates
            content = TemplateManager._extract_ts_slash_command(command_id)
            if content:
                return content
        except Exception as e:
            print(f"Warning: Could not read TypeScript slash command {command_id} ({e}). Using fallback.")
        
        # Fallback to Python templates
        from .slash_commands import get_slash_command_body
        return get_slash_command_body(command_id)
    
