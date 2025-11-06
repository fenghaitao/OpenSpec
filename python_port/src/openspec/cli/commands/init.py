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


@click.command()
@click.option("--force", "-f", is_flag=True, help="Force initialization even if directory exists")
@click.option("--non-interactive", is_flag=True, help="Run in non-interactive mode")
@click.option("--ai-tools", help="Comma-separated list of AI tools to configure")
def init(force: bool, non_interactive: bool, ai_tools: str):
    """Initialize a new OpenSpec project."""
    
    current_dir = Path.cwd()
    openspec_dir = current_dir / OPENSPEC_DIR_NAME
    
    # Check if openspec directory already exists
    if openspec_dir.exists() and not force:
        if non_interactive:
            console.print(f"[red]Error: {OPENSPEC_DIR_NAME} directory already exists. Use --force to overwrite.[/red]")
            raise click.Abort()
        
        if not click.confirm(f"{OPENSPEC_DIR_NAME} directory already exists. Continue?"):
            raise click.Abort()
    
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
        # Interactive selection
        available_choices = [
            (f"{tool.name}", tool.value) 
            for tool in AI_TOOLS 
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
            raise click.Abort()
            
        tool_lookup = {tool.value: tool for tool in AI_TOOLS}
        selected_tools = [tool_lookup[value] for value in answers["ai_tools"]]
    
    if not selected_tools:
        console.print("[red]Error: At least one AI tool must be selected.[/red]")
        raise click.Abort()
    
    # Create directory structure
    try:
        ensure_directory(str(openspec_dir))
        ensure_directory(str(openspec_dir / "changes"))
        ensure_directory(str(openspec_dir / "specs"))
        
        # Create project.md
        project_content = create_project_template()
        write_file(str(openspec_dir / "project.md"), project_content)
        
        # Configure AI tools
        import asyncio
        asyncio.run(configure_ai_tools(str(current_dir), OPENSPEC_DIR_NAME, [tool.value for tool in selected_tools]))
        
        # Create AGENTS.md in root
        agents_content = create_agents_template(selected_tools)
        write_file(str(current_dir / "AGENTS.md"), agents_content)
        
        console.print(f"[green]✓[/green] Initialized OpenSpec project in {current_dir}")
        console.print(f"[green]✓[/green] Created {OPENSPEC_DIR_NAME}/ directory")
        console.print(f"[green]✓[/green] Created AGENTS.md with {len(selected_tools)} AI tool(s)")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Edit openspec/project.md to describe your project")
        console.print("2. Create your first change with: [cyan]openspec change create[/cyan]")
        console.print("3. Validate your specs with: [cyan]openspec validate[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error initializing project: {e}[/red]")
        raise click.Abort()


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