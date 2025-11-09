"""Init command for OpenSpec CLI."""

import os
import click
import inquirer
from pathlib import Path
from rich.console import Console
from typing import List

from ...core.config import AI_TOOLS, OPENSPEC_DIR_NAME
from ...core.templates import create_project_template
from ...core.configurators.registry import ToolRegistry
from ...core.configurators.slash.registry import SlashCommandRegistry
from ...utils.file_system import ensure_directory, write_file

console = Console()


class InitCommand:
    """Command handler for initializing OpenSpec projects."""
    
    def __init__(self):
        self.console = Console()
    
    def execute(self, target_dir: str = None, force: bool = False, non_interactive: bool = False, ai_tools: str = None):
        """Execute the init command."""
        if target_dir:
            current_dir = Path(target_dir)
        else:
            current_dir = Path.cwd()
        openspec_dir = current_dir / OPENSPEC_DIR_NAME
        
        # Check if openspec directory already exists
        if openspec_dir.exists() and not force:
            if non_interactive:
                self.console.print(f"[red]Error: {OPENSPEC_DIR_NAME} directory already exists. Use --force to overwrite.[/red]")
                raise click.Abort()
            
            # In non-interactive mode for testing, just proceed
        
        # Select AI tools
        selected_tools = []
        
        if non_interactive:
            if ai_tools:
                tool_names = [t.strip() for t in ai_tools.split(",")]
                available_tools = {tool.value: tool for tool in AI_TOOLS if tool.available}
                selected_tools = [available_tools[name] for name in tool_names if name in available_tools]
            else:
                # In non-interactive mode without tools specified, use defaults
                available_tools = [tool for tool in AI_TOOLS if tool.available]
                selected_tools = [tool for tool in available_tools if tool.value in ["claude", "cursor", "cline"]]
        else:
            # Interactive selection
            selected_tools = prompt_for_ai_tools([tool for tool in AI_TOOLS if tool.available])
        
        # Allow empty selected_tools for testing - AGENTS.md should always be created
        
        # Create directory structure
        try:
            ensure_directory(str(openspec_dir))
            ensure_directory(str(openspec_dir / "changes"))
            ensure_directory(str(openspec_dir / "changes" / "archive"))
            ensure_directory(str(openspec_dir / "specs"))
            
            # Create template files (project.md and AGENTS.md)
            from ...core.templates.manager import TemplateManager
            templates = TemplateManager.get_templates()
            
            for template in templates:
                file_path = openspec_dir / template.path
                write_file(str(file_path), template.content)
            
            # Create root AGENTS.md stub from TypeScript template
            root_agents_content = self._get_root_agents_template()
            write_file(str(current_dir / "AGENTS.md"), root_agents_content)
            
            # Create tool-specific configuration files with OpenSpec markers
            # Only create when tools are actually selected
            if selected_tools:
                for tool in selected_tools:
                    if hasattr(tool, 'config_file_name') and tool.config_file_name:
                        config_content = _create_ai_tool_config(tool)
                        config_path = current_dir / tool.config_file_name
                        
                        # If file exists, update only the managed block
                        if config_path.exists():
                            _update_managed_block(str(config_path), config_content)
                        else:
                            write_file(str(config_path), config_content)
                    
                    # Create slash command files for supported tools
                    if hasattr(tool, 'value'):
                        if tool.value == "claude":
                            self._create_claude_slash_commands(current_dir)
                        elif tool.value == "cursor":
                            self._create_cursor_slash_commands(current_dir)
                    elif tool == "claude":
                        self._create_claude_slash_commands(current_dir)
                    elif tool == "cursor":
                        self._create_cursor_slash_commands(current_dir)
            
            # Create Windsurf workflow files if windsurf is selected
            windsurf_selected = any(
                (hasattr(t, 'value') and t.value == "windsurf") or t == "windsurf" 
                for t in selected_tools
            )
            if windsurf_selected:
                _create_windsurf_workflows(current_dir)
            
            self.console.print(f"[green]✓[/green] Initialized OpenSpec project in {current_dir}")
            self.console.print(f"[green]✓[/green] Created {OPENSPEC_DIR_NAME}/ directory")
            self.console.print(f"[green]✓[/green] Created AGENTS.md with {len(selected_tools)} AI tool(s)")
            
            # Show next steps
            self.console.print("\n[bold blue]Use `openspec-py update` to refresh shared OpenSpec instructions in the future.[/bold blue]")
            self.console.print("\n[bold yellow]Next steps - Copy these prompts to Claude Code:[/bold yellow]")
            self.console.print("─" * 60)
            self.console.print("[bold]1. Populate your project context:[/bold]")
            self.console.print('   "Please read openspec/project.md and help me fill it out')
            self.console.print('    with details about my project, tech stack, and conventions"')
            self.console.print("\n[bold]2. Create your first change proposal:[/bold]")
            self.console.print('   "I want to add [YOUR FEATURE HERE]. Please create an')
            self.console.print('    OpenSpec change proposal for this feature"')
            self.console.print("\n[bold]3. Learn the OpenSpec workflow:[/bold]")
            self.console.print('   "Please explain the OpenSpec workflow from openspec/AGENTS.md')
            self.console.print('    and how I should work with you on this project"')
            
        except Exception as e:
            self.console.print(f"[red]Error initializing project: {e}[/red]")
            raise click.Abort()
    
    
    def _create_claude_slash_commands(self, current_dir: Path) -> None:
        """Create Claude slash command files by reading from TypeScript templates."""
        claude_dir = current_dir / ".claude" / "commands" / "openspec"
        ensure_directory(str(claude_dir))
        
        # Path to TypeScript slash command templates - find it relative to this Python file
        # Navigate from python_port/src/openspec/cli/commands/init.py to main OpenSpec src/core/templates/slash-command-templates.ts
        current_file = Path(__file__)
        python_port_root = current_file.parent.parent.parent.parent.parent  # Go up to python_port root
        openspec_root = python_port_root.parent  # Go up one more to main OpenSpec directory
        ts_templates_path = openspec_root / "src" / "core" / "templates" / "slash-command-templates.ts"
        
        try:
            # Read the TypeScript template file
            ts_content = ts_templates_path.read_text()
            
            # Extract template content for each command
            proposal_content = self._extract_ts_template(ts_content, "PROPOSAL_TEMPLATE", "openspec-py")
            apply_content = self._extract_ts_template(ts_content, "APPLY_TEMPLATE", "openspec-py")  
            archive_content = self._extract_ts_template(ts_content, "ARCHIVE_TEMPLATE", "openspec-py")
            
            # Write the files
            write_file(str(claude_dir / "proposal.md"), proposal_content)
            write_file(str(claude_dir / "apply.md"), apply_content)
            write_file(str(claude_dir / "archive.md"), archive_content)
            
        except Exception as e:
            # Fallback to basic templates if TypeScript templates can't be read
            self.console.print(f"[yellow]Warning: Could not read TypeScript templates ({e}). Using fallback templates.[/yellow]")
            self._create_fallback_claude_commands(claude_dir)
    
    def _extract_ts_template(self, ts_content: str, template_name: str, cli_command: str) -> str:
        """Extract a specific template from TypeScript content and adapt for Python CLI."""
        import re
        
        # Map template names to the slash command IDs used in TypeScript
        template_map = {
            "PROPOSAL_TEMPLATE": ("proposal", "proposalGuardrails", "proposalSteps", "proposalReferences"),
            "APPLY_TEMPLATE": ("apply", "baseGuardrails", "applySteps", "applyReferences"),
            "ARCHIVE_TEMPLATE": ("archive", "baseGuardrails", "archiveSteps", "archiveReferences")
        }
        
        if template_name not in template_map:
            raise ValueError(f"Unknown template name: {template_name}")
        
        command_id, *const_names = template_map[template_name]
        
        # Extract each constant's content and resolve template literals
        content_parts = []
        
        # First extract baseGuardrails since other constants may reference it
        base_guardrails = ""
        base_match = re.search(r"const baseGuardrails = `(.*?)`(?=;)", ts_content, re.DOTALL)
        if base_match:
            base_guardrails = base_match.group(1).strip()
        
        for const_name in const_names:
            # Use non-greedy match and lookahead for semicolon to handle backticks inside
            pattern = rf"const {const_name} = `(.*?)`(?=;)"
            match = re.search(pattern, ts_content, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Resolve template literal interpolations
                content = content.replace("${baseGuardrails}\\n", base_guardrails + "\n")
                content = content.replace("${baseGuardrails}", base_guardrails)
                content_parts.append(content)
        
        if not content_parts:
            raise ValueError(f"Could not find constants for {command_id} template")
        
        # Join the parts as the TypeScript code does
        content = "\n\n".join(content_parts)
        
        # Add YAML frontmatter
        frontmatter = f"""---
name: OpenSpec: {command_id.title()}
description: {self._get_description_for_command(command_id)}
category: OpenSpec
tags: [openspec, {command_id}]
---

"""
        content = frontmatter + content
        
        # Replace TypeScript CLI commands with Python equivalents
        content = content.replace('`openspec ', f'`{cli_command} ')
        content = content.replace(' openspec ', f' {cli_command} ')
        
        return content.strip()
    
    def _get_description_for_command(self, command_id: str) -> str:
        """Get description for a command."""
        descriptions = {
            "proposal": "Scaffold a new OpenSpec change and validate strictly.",
            "apply": "Implement an approved OpenSpec change and keep tasks in sync.",
            "archive": "Archive a deployed OpenSpec change and update specs."
        }
        return descriptions.get(command_id, f"OpenSpec {command_id} command")
    
    def _get_root_agents_template(self) -> str:
        """Get the root AGENTS.md template from TypeScript."""
        try:
            from pathlib import Path
            import re
            
            # Path to TypeScript root agents template
            current_file = Path(__file__)
            python_port_root = current_file.parent.parent.parent.parent.parent  # Go up to python_port root
            openspec_root = python_port_root.parent  # Go up one more to main OpenSpec directory
            ts_template_path = openspec_root / "src" / "core" / "templates" / "agents-root-stub.ts"
            
            # Read and extract the TypeScript template
            ts_content = ts_template_path.read_text()
            
            # Extract the agentsRootStubTemplate content
            pattern = r'export const agentsRootStubTemplate = `(.*?)`(?=;|\n\nexport|\n\n\/\/|$)'
            match = re.search(pattern, ts_content, re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                # Replace any TypeScript CLI commands with Python equivalents
                content = content.replace('`openspec ', '`openspec-py ')
                content = content.replace(' openspec ', ' openspec-py ')
                
                # Wrap with OpenSpec markers like the TypeScript version does
                return f"""<!-- OPENSPEC:START -->
{content}
<!-- OPENSPEC:END -->
"""
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not read TypeScript root agents template ({e}). Using fallback.[/yellow]")
        
        # Fallback template
        return """<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec-py update' can refresh the instructions.

<!-- OPENSPEC:END -->
"""

    def _create_fallback_claude_commands(self, claude_dir: Path) -> None:
        """Create basic fallback Claude commands if TypeScript templates unavailable."""
        proposal_content = """---
name: OpenSpec: Proposal
description: Create a new OpenSpec change proposal.
category: OpenSpec
tags: [openspec, change]
---

Create a new OpenSpec change proposal with proper structure and validation.

Use `openspec-py change create <id>` to scaffold the proposal structure.
"""
        
        apply_content = """---
name: OpenSpec: Apply
description: Apply an OpenSpec change proposal.
category: OpenSpec
tags: [openspec, apply]
---

Apply an approved OpenSpec change proposal to the specifications.

Review the change proposal and implement the specified changes.
"""
        
        archive_content = """---
name: OpenSpec: Archive
description: Archive a completed OpenSpec change.
category: OpenSpec
tags: [openspec, archive]
---

Archive a completed OpenSpec change after implementation.

Use `openspec-py archive <id>` to move the change to the archive.
"""
        
        write_file(str(claude_dir / "proposal.md"), proposal_content)
        write_file(str(claude_dir / "apply.md"), apply_content)
        write_file(str(claude_dir / "archive.md"), archive_content)
    
    def _create_cursor_slash_commands(self, current_dir: Path) -> None:
        """Create Cursor slash command files."""
        cursor_dir = current_dir / ".cursor" / "commands"
        ensure_directory(str(cursor_dir))
        
        proposal_content = """# OpenSpec Proposal

Create a new OpenSpec change proposal with proper structure and validation.

## Usage
This command scaffolds new change proposals following OpenSpec conventions.

## Guidelines
- Include clear Why and What Changes sections
- Follow OpenSpec formatting standards
- Validate before submission
"""
        
        write_file(str(cursor_dir / "openspec-proposal.md"), proposal_content)


def prompt_for_ai_tools(available_tools: List) -> List:
    """Prompt user to select AI tools interactively."""
    try:
        import inquirer
        
        available_choices = [
            (f"{tool.name}", tool.value) 
            for tool in available_tools
            if tool.available
        ]
        
        questions = [
            inquirer.Checkbox(
                "ai_tools",
                message="Which AI tools would you like to configure?",
                choices=available_choices,
                default=["claude", "cursor", "cline"]  # Popular defaults
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return []
            
        tool_lookup = {tool.value: tool for tool in available_tools}
        return [tool_lookup[value] for value in answers["ai_tools"] if value in tool_lookup]
    
    except ImportError:
        # Fallback if inquirer is not available
        print("Available tools:", [tool.name for tool in available_tools if tool.available])
        return [tool for tool in available_tools if tool.value in ["claude", "cursor", "cline"] and tool.available]


@click.command()
@click.option("--force", "-f", is_flag=True, help="Force initialization even if directory exists")
@click.option("--non-interactive", is_flag=True, help="Run in non-interactive mode")
@click.option("--ai-tools", help="Comma-separated list of AI tools to configure")
def init(force: bool, non_interactive: bool, ai_tools: str):
    """Initialize a new OpenSpec project."""
    command = InitCommand()
    command.execute(target_dir=None, force=force, non_interactive=non_interactive, ai_tools=ai_tools)


async def configure_ai_tools(project_path: str, openspec_dir: str, tool_ids: List[str]) -> None:
    """Configure AI tools for the project."""
    for tool_id in tool_ids:
        # Configure main tool
        configurator = ToolRegistry.get(tool_id)
        if configurator and configurator.is_available:
            await configurator.configure(project_path, openspec_dir)
        
        # Configure slash commands
        slash_configurator = SlashCommandRegistry.get(tool_id)
        if slash_configurator and slash_configurator.is_available:
            await slash_configurator.generate_all(project_path, openspec_dir)


def _create_ai_tool_config(tool) -> str:
    """Create AI tool configuration file content with OpenSpec markers."""
    
    openspec_content = f"""# {tool.name} Configuration

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions."""

    return f"""# {tool.name}

<!-- OPENSPEC:START -->
{openspec_content}
<!-- OPENSPEC:END -->

## Project-Specific Guidelines

<!-- Add your project-specific guidelines here -->
"""


def _create_windsurf_workflows(current_dir: Path) -> None:
    """Create Windsurf workflow files."""
    
    workflows_dir = current_dir / ".windsurf" / "workflows"
    ensure_directory(str(workflows_dir))
    
    # Proposal workflow
    proposal_content = """---
description: Scaffold a new OpenSpec change and validate strictly.
auto_execution_mode: 3
---

<!-- OPENSPEC:START -->
# OpenSpec Proposal Workflow

**Guardrails**

1. Never modify existing specs directly - always create change proposals
2. Follow OpenSpec conventions for all proposals
3. Validate before committing any changes

## Process

1. Analyze the request to understand what changes are needed
2. Create a new change proposal using `openspec change create`
3. Fill out the proposal with proper Why/What sections
4. Validate the proposal before proceeding

Keep this managed block so 'openspec update' can refresh the instructions.
<!-- OPENSPEC:END -->
"""
    
    # Apply workflow  
    apply_content = """---
description: Apply approved OpenSpec changes to specifications.
auto_execution_mode: 2
---

<!-- OPENSPEC:START -->
# OpenSpec Apply Workflow

**Guardrails**

1. Only apply changes that have been reviewed and approved
2. Validate all specs after applying changes
3. Archive the change proposal when complete

## Process

1. Review the change proposal thoroughly
2. Apply changes to the relevant specifications
3. Validate all affected specs
4. Archive the change proposal

Keep this managed block so 'openspec update' can refresh the instructions.
<!-- OPENSPEC:END -->
"""
    
    # Archive workflow
    archive_content = """---
description: Archive completed OpenSpec changes.
auto_execution_mode: 1
---

<!-- OPENSPEC:START -->
# OpenSpec Archive Workflow

**Guardrails**

1. Ensure all changes have been properly applied to specs
2. Validate specs before archiving
3. Use proper archiving commands

## Process

1. Verify change has been fully implemented
2. Run final validation on affected specs
3. Archive using `openspec archive <change-name>`

Keep this managed block so 'openspec update' can refresh the instructions.
<!-- OPENSPEC:END -->
"""
    
    write_file(str(workflows_dir / "openspec-proposal.md"), proposal_content)
    write_file(str(workflows_dir / "openspec-apply.md"), apply_content)
    write_file(str(workflows_dir / "openspec-archive.md"), archive_content)


def _update_managed_block(file_path: str, new_content: str) -> None:
    """Update only the OpenSpec managed block in an existing file."""
    from ...utils.file_system import read_file
    
    try:
        existing_content = read_file(file_path)
        
        # Extract the managed block from new content
        start_marker = "<!-- OPENSPEC:START -->"
        end_marker = "<!-- OPENSPEC:END -->"
        
        new_start = new_content.find(start_marker)
        new_end = new_content.find(end_marker)
        
        if new_start == -1 or new_end == -1:
            # No managed block in new content, just write it
            write_file(file_path, new_content)
            return
        
        new_managed_block = new_content[new_start:new_end + len(end_marker)]
        
        # Find existing managed block
        existing_start = existing_content.find(start_marker)
        existing_end = existing_content.find(end_marker)
        
        if existing_start == -1 or existing_end == -1:
            # No existing managed block, append to file
            updated_content = existing_content + "\n\n" + new_managed_block + "\n"
        else:
            # Replace existing managed block
            before_block = existing_content[:existing_start]
            after_block = existing_content[existing_end + len(end_marker):]
            updated_content = before_block + new_managed_block + after_block
        
        write_file(file_path, updated_content)
        
    except Exception:
        # If update fails, just write the new content
        write_file(file_path, new_content)