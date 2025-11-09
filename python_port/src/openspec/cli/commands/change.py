"""Change command for OpenSpec CLI."""

import click
from pathlib import Path
from rich.console import Console

from ...core.change_operations import list_changes, show_change
from ...utils.file_system import find_openspec_root

console = Console()


@click.group()
def change():
    """Manage changes in OpenSpec project."""
    pass


@change.command()
def list():
    """List all changes in the project."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        changes = list_changes(str(project_path))
        
        if not changes:
            console.print("[yellow]No changes found.[/yellow]")
            return
        
        console.print(f"[bold]Found {len(changes)} change(s):[/bold]")
        for change_info in changes:
            status = "📁" if change_info.get("is_archived", False) else "📝"
            console.print(f"  {status} {change_info['name']}")
            
    except Exception as e:
        console.print(f"[red]Error listing changes: {e}[/red]")
        raise click.Abort()


@change.command()
@click.argument("name")
def show(name: str):
    """Show details of a specific change."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        change_info = show_change(str(project_path), name)
        
        if not change_info:
            console.print(f"[red]Change '{name}' not found.[/red]")
            raise click.Abort()
        
        console.print(f"[bold]Change: {change_info['name']}[/bold]")
        console.print(f"[bold]Path:[/bold] {change_info['path']}")
        
        if "proposal" in change_info:
            proposal = change_info["proposal"]
            console.print(f"\n[bold]Why:[/bold] {proposal.get('why', 'N/A')}")
            console.print(f"[bold]What Changes:[/bold] {proposal.get('whatChanges', 'N/A')}")
            
            if "deltas" in proposal:
                console.print(f"\n[bold]Deltas ({len(proposal['deltas'])}):[/bold]")
                for delta in proposal["deltas"]:
                    console.print(f"  • {delta.get('operation', 'UNKNOWN')} {delta.get('spec', 'N/A')}")
        
    except Exception as e:
        console.print(f"[red]Error showing change: {e}[/red]")
        raise click.Abort()