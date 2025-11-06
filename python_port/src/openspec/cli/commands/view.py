"""View command for OpenSpec CLI."""

import click
from rich.console import Console
from rich.table import Table

from ...core.change_operations import list_changes
from ...utils.file_system import find_openspec_root, list_directories
from pathlib import Path

console = Console()


@click.command()
@click.option("--format", "output_format", type=click.Choice(["table", "list"]), default="table", help="Output format")
def view(output_format: str):
    """View project dashboard with changes and specs."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        console.print("[bold]OpenSpec Project Dashboard[/bold]\n")
        
        # Show changes
        changes = list_changes(str(project_path))
        active_changes = [c for c in changes if not c["is_archived"]]
        archived_changes = [c for c in changes if c["is_archived"]]
        
        if output_format == "table":
            _display_table_format(active_changes, archived_changes, project_path)
        else:
            _display_list_format(active_changes, archived_changes, project_path)
        
    except Exception as e:
        console.print(f"[red]Error viewing project: {e}[/red]")
        raise click.Abort()


def _display_table_format(active_changes, archived_changes, project_path):
    """Display dashboard in table format."""
    
    # Active changes table
    if active_changes:
        table = Table(title="Active Changes")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        
        for change in active_changes:
            table.add_row(change["name"], "🔄 Active")
        
        console.print(table)
    else:
        console.print("[yellow]No active changes.[/yellow]")
    
    # Specs table
    specs_dir = Path(project_path) / "openspec" / "specs"
    if specs_dir.exists():
        specs = list_directories(str(specs_dir))
        
        if specs:
            console.print()
            spec_table = Table(title="Specifications")
            spec_table.add_column("Name", style="blue")
            spec_table.add_column("Status", style="green")
            
            for spec_name in sorted(specs):
                spec_table.add_row(spec_name, "📋 Spec")
            
            console.print(spec_table)
        else:
            console.print("\n[yellow]No specs found.[/yellow]")
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Active changes: {len(active_changes)}")
    console.print(f"  Archived changes: {len(archived_changes)}")
    
    specs_count = len(list_directories(str(specs_dir))) if specs_dir.exists() else 0
    console.print(f"  Specifications: {specs_count}")


def _display_list_format(active_changes, archived_changes, project_path):
    """Display dashboard in list format."""
    
    console.print("[bold]Active Changes:[/bold]")
    if active_changes:
        for change in active_changes:
            console.print(f"  🔄 {change['name']}")
    else:
        console.print("  [dim]None[/dim]")
    
    console.print(f"\n[bold]Archived Changes:[/bold]")
    if archived_changes:
        for change in archived_changes[:5]:  # Show first 5
            console.print(f"  📁 {change['name']}")
        if len(archived_changes) > 5:
            console.print(f"  [dim]... and {len(archived_changes) - 5} more[/dim]")
    else:
        console.print("  [dim]None[/dim]")
    
    console.print(f"\n[bold]Specifications:[/bold]")
    specs_dir = Path(project_path) / "openspec" / "specs"
    if specs_dir.exists():
        specs = list_directories(str(specs_dir))
        if specs:
            for spec_name in sorted(specs):
                console.print(f"  📋 {spec_name}")
        else:
            console.print("  [dim]None[/dim]")
    else:
        console.print("  [dim]None[/dim]")