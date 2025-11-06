"""Show command for OpenSpec CLI."""

import click
from rich.console import Console

from ...core.change_operations import show_change
from ...utils.file_system import find_openspec_root

console = Console()


@click.command()
@click.argument("name")
@click.option("--type", "item_type", type=click.Choice(["change", "spec"]), default="change", help="Type of item to show")
def show(name: str, item_type: str):
    """Show details of a change or spec."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        if item_type == "change":
            change_info = show_change(str(project_path), name)
            
            if not change_info:
                console.print(f"[red]Change '{name}' not found.[/red]")
                raise click.Abort()
            
            _display_change_info(change_info)
            
        else:  # spec
            # TODO: Implement spec showing
            console.print("[yellow]Spec showing not yet implemented.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error showing {item_type}: {e}[/red]")
        raise click.Abort()


def _display_change_info(change_info):
    """Display change information."""
    
    console.print(f"[bold]Change: {change_info['name']}[/bold]")
    console.print(f"[bold]Path:[/bold] {change_info['path']}")
    
    if change_info.get("is_archived"):
        console.print("[yellow]Status:[/yellow] Archived")
    else:
        console.print("[green]Status:[/green] Active")
    
    if "proposal" in change_info:
        proposal = change_info["proposal"]
        
        console.print(f"\n[bold]Why:[/bold]")
        console.print(f"  {proposal.get('why', 'Not specified')}")
        
        console.print(f"\n[bold]What Changes:[/bold]")
        console.print(f"  {proposal.get('whatChanges', 'Not specified')}")
        
        if "deltas" in proposal:
            console.print(f"\n[bold]Deltas ({len(proposal['deltas'])}):[/bold]")
            for i, delta in enumerate(proposal["deltas"], 1):
                operation = delta.get("operation", "UNKNOWN")
                spec = delta.get("spec", "N/A")
                description = delta.get("description", "No description")
                
                console.print(f"  {i}. [{operation}] {spec}")
                console.print(f"     {description}")
                
                if "requirements" in delta:
                    req_count = len(delta["requirements"])
                    console.print(f"     Requirements: {req_count}")
    else:
        console.print("\n[yellow]No proposal configuration found.[/yellow]")