"""Update command for OpenSpec CLI."""

import click
from rich.console import Console

from ...core.templates.agents_template import create_agents_openspec_template
from ...utils.file_system import find_openspec_root, write_file, ensure_directory
from pathlib import Path

console = Console()


@click.command()
@click.option("--agents", is_flag=True, help="Update AGENTS.md files")
def update(agents: bool):
    """Update OpenSpec project files."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        if agents:
            _update_agents_files(project_path)
        else:
            console.print("[yellow]No update options specified. Use --agents to update AGENTS.md files.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error updating project: {e}[/red]")
        raise click.Abort()


def _update_agents_files(project_path: Path):
    """Update AGENTS.md files."""
    
    # Update openspec/AGENTS.md
    openspec_dir = project_path / "openspec"
    ensure_directory(str(openspec_dir))
    
    agents_content = create_agents_openspec_template()
    agents_path = openspec_dir / "AGENTS.md"
    
    write_file(str(agents_path), agents_content)
    console.print(f"[green]✓[/green] Updated: {agents_path}")
    
    # TODO: Update root AGENTS.md with OpenSpec markers
    # This would require parsing existing content and updating the OpenSpec section
    
    console.print("[green]✓[/green] Updated AGENTS.md files")