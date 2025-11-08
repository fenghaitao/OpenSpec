"""Show command for OpenSpec CLI."""

import click
from rich.console import Console

from ...core.change_operations import show_change
from ...utils.file_system import find_openspec_root

console = Console()


@click.command()
@click.argument("name", required=False)
@click.option("--type", "item_type", type=click.Choice(["change", "spec"]), help="Type of item to show")
@click.option("--json", is_flag=True, help="Output as JSON")
@click.option("--requirements", is_flag=True, help="Show only requirements (for specs)")
def show(name: str, item_type: str, json: bool, requirements: bool):
    """Show details of a change or spec."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    # Handle case where no name is provided
    if not name:
        console.print("Nothing to show.")
        console.print("Try one of:")
        console.print("  openspec show <item>")
        console.print("  openspec change show")
        console.print("  openspec spec show")
        raise click.Abort()
    
    try:
        # Auto-detect type if not specified
        if not item_type:
            item_type = _detect_item_type(str(project_path), name)
            if not item_type:
                console.print(f"[red]Unknown item '{name}'[/red]")
                console.print("Did you mean:")
                _suggest_similar_items(str(project_path), name)
                raise click.Abort()
            elif item_type == "ambiguous":
                console.print(f"[red]Ambiguous item '{name}' found in both changes and specs.[/red]")
                console.print("Please specify --type change|spec")
                raise click.Abort()
        
        if item_type == "change":
            change_info = show_change(str(project_path), name)
            
            if not change_info:
                console.print(f"[red]Change '{name}' not found.[/red]")
                raise click.Abort()
            
            if json:
                import json as json_lib
                output = {"id": name, "deltas": []}
                console.print(json_lib.dumps(output))
            else:
                _display_change_info(change_info)
            
        else:  # spec
            if json:
                import json as json_lib
                output = {"id": name, "requirements": []}
                console.print(json_lib.dumps(output))
            else:
                console.print("[yellow]Spec showing not yet implemented.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error showing {item_type or 'item'}: {e}[/red]")
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


def _detect_item_type(project_path: str, name: str) -> str:
    """Auto-detect whether an item is a change or spec."""
    from pathlib import Path
    
    changes_dir = Path(project_path) / "openspec" / "changes"
    specs_dir = Path(project_path) / "openspec" / "specs"
    
    has_change = (changes_dir / name).exists()
    has_spec = (specs_dir / name).exists()
    
    if has_change and has_spec:
        return "ambiguous"
    elif has_change:
        return "change"
    elif has_spec:
        return "spec"
    else:
        return None


def _suggest_similar_items(project_path: str, name: str) -> None:
    """Suggest similar items when not found."""
    from pathlib import Path
    from ...utils.file_system import list_directories
    
    changes_dir = Path(project_path) / "openspec" / "changes"
    specs_dir = Path(project_path) / "openspec" / "specs"
    
    all_items = []
    
    if changes_dir.exists():
        changes = list_directories(str(changes_dir))
        all_items.extend([(c, "change") for c in changes if c != "archive"])
    
    if specs_dir.exists():
        specs = list_directories(str(specs_dir))
        all_items.extend([(s, "spec") for s in specs])
    
    # Simple similarity check (starts with same letter)
    suggestions = [item for item, item_type in all_items if item.lower().startswith(name[0].lower())]
    
    if suggestions:
        for suggestion in suggestions[:3]:  # Show max 3 suggestions
            console.print(f"  {suggestion}")
    else:
        console.print("  No similar items found")