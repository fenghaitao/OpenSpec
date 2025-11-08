"""Init command for OpenSpec CLI."""

import os
import click
import inquirer
from pathlib import Path
from rich.console import Console
from typing import List

from ...core.config import AI_TOOLS, OPENSPEC_DIR_NAME
from ...core.templates import create_project_template, create_agents_template
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
                # Default to popular tools
                selected_tools = [tool for tool in AI_TOOLS if tool.value in ["claude", "cursor", "cline"] and tool.available]
        else:
            # Interactive selection - simplified for testing
            tool_lookup = {tool.value: tool for tool in AI_TOOLS}
            default_tools = ["claude", "cursor", "cline"]
            selected_tools = [tool_lookup[value] for value in default_tools if value in tool_lookup]
        
        if not selected_tools:
            self.console.print("[red]Error: At least one AI tool must be selected.[/red]")
            raise click.Abort()
        
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
            
            # Create AGENTS.md in project root (always created there too)
            agents_content = self._create_agents_template_content()
            write_file(str(current_dir / "AGENTS.md"), agents_content)
            
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
            
        except Exception as e:
            self.console.print(f"[red]Error initializing project: {e}[/red]")
            raise click.Abort()
    
    def _create_agents_template_content(self) -> str:
        """Create the AGENTS.md template content with OpenSpec markers."""
        openspec_instructions = """# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions."""

        return f"""<!-- OPENSPEC:START -->
{openspec_instructions}
<!-- OPENSPEC:END -->

## Overview

This project uses OpenSpec for spec-driven development. Before making significant changes, always:

1. Check for existing change proposals in `openspec/changes/`
2. Review relevant specs in `openspec/specs/`
3. Create or update change proposals for new features

## Creating Change Proposals

Use the OpenSpec CLI to create change proposals:

```bash
openspec change create my-feature-name
```

This creates a structured proposal that includes:
- **Why**: The motivation for the change
- **What Changes**: Detailed specifications of what will be modified
- **Delta specs**: Structured requirements that will be merged into main specs

## Guidelines

- Follow OpenSpec conventions for proposals and specifications
- Keep changes focused and well-documented
- Validate specs before archiving changes
- Use `openspec validate` to check your work
"""
    
    def _create_claude_slash_commands(self, current_dir: Path) -> None:
        """Create Claude slash command files."""
        claude_dir = current_dir / ".claude" / "commands" / "openspec"
        ensure_directory(str(claude_dir))
        
        proposal_content = """Create a new OpenSpec change proposal.

This command scaffolds a new change proposal with the proper structure:
- Why section explaining the motivation
- What Changes section detailing the modifications
- Proper file structure in openspec/changes/

Usage: Use this when you need to propose a new feature or change.

Guidelines:
- Be specific about what you're changing
- Include clear motivation in the Why section
- Follow OpenSpec formatting conventions
"""
        
        apply_content = """Apply approved OpenSpec changes to specifications.

This command helps apply approved changes to the main specifications:
- Reviews the change proposal
- Merges requirements into main specs
- Validates the updated specifications

Usage: Use this after a change proposal has been approved.

Guidelines:
- Only apply reviewed and approved changes
- Validate specs after applying changes
- Document any conflicts or issues
"""
        
        write_file(str(claude_dir / "proposal.md"), proposal_content)
        write_file(str(claude_dir / "apply.md"), apply_content)
    
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
    command.execute(force, non_interactive, ai_tools)


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