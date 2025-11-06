"""Spec command for OpenSpec CLI."""

import click
from pathlib import Path
from rich.console import Console

from ...core.templates.change_template import create_spec_template
from ...utils.file_system import find_openspec_root, ensure_directory, write_file, list_directories

console = Console()


@click.group()
def spec():
    """Manage specs in OpenSpec project."""
    pass


@spec.command()
@click.argument("name")
def create(name: str):
    """Create a new spec."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        # Sanitize name
        name = name.lower().replace(" ", "-").replace("_", "-")
        
        # Create spec directory
        specs_dir = Path(project_path) / "openspec" / "specs"
        spec_dir = specs_dir / name
        
        if spec_dir.exists():
            console.print(f"[red]Error: Spec '{name}' already exists.[/red]")
            raise click.Abort()
        
        ensure_directory(str(spec_dir))
        
        # Create spec.md
        spec_content = create_spec_template(name)
        spec_path = spec_dir / "spec.md"
        write_file(str(spec_path), spec_content)
        
        console.print(f"[green]✓[/green] Created spec: {spec_path}")
        console.print(f"[dim]Edit the spec.md file to define your specification.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error creating spec: {e}[/red]")
        raise click.Abort()


@spec.command()
def list():
    """List all specs in the project."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        specs_dir = Path(project_path) / "openspec" / "specs"
        
        if not specs_dir.exists():
            console.print("[yellow]No specs directory found.[/yellow]")
            return
        
        specs = list_directories(str(specs_dir))
        
        if not specs:
            console.print("[yellow]No specs found.[/yellow]")
            return
        
        console.print(f"[bold]Found {len(specs)} spec(s):[/bold]")
        for spec_name in sorted(specs):
            console.print(f"  📋 {spec_name}")
            
    except Exception as e:
        console.print(f"[red]Error listing specs: {e}[/red]")
        raise click.Abort()


@spec.command()
@click.argument("name")
def show(name: str):
    """Show details of a specific spec."""
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        specs_dir = Path(project_path) / "openspec" / "specs"
        spec_path = specs_dir / name / "spec.md"
        
        if not spec_path.exists():
            console.print(f"[red]Spec '{name}' not found.[/red]")
            raise click.Abort()
        
        console.print(f"[bold]Spec: {name}[/bold]")
        console.print(f"[bold]Path:[/bold] {spec_path}")
        
        # TODO: Parse and display spec content
        console.print("\n[dim]Use 'openspec validate' to check spec validity.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error showing spec: {e}[/red]")
        raise click.Abort()