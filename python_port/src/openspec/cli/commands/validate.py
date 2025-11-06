"""Validate command for OpenSpec CLI."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import List, Optional

from ...core.validation import validate_project, ValidationResult
from ...utils.file_system import find_openspec_root

console = Console()


@click.command()
@click.option("--scope", help="Scope to validate (change name or spec name)")
@click.option("--enriched", is_flag=True, help="Show enriched validation output")
@click.argument("path", required=False)
def validate(scope: Optional[str], enriched: bool, path: Optional[str]):
    """Validate OpenSpec project files."""
    
    # Find project root
    if path:
        project_path = Path(path).resolve()
    else:
        project_path = find_openspec_root()
        
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        # Run validation
        results = validate_project(str(project_path), scope=scope)
        
        if not results:
            console.print("[green]✓ No files found to validate.[/green]")
            return
        
        # Display results
        has_errors = any(not result.is_valid for result in results)
        
        if enriched:
            _display_enriched_results(results)
        else:
            _display_standard_results(results)
        
        if has_errors:
            raise click.Abort()
        else:
            console.print(f"\n[green]✓ All {len(results)} file(s) validated successfully.[/green]")
            
    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        raise click.Abort()


def _display_standard_results(results: List[ValidationResult]):
    """Display standard validation results."""
    
    table = Table(title="Validation Results")
    table.add_column("File", style="cyan")
    table.add_column("Type", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Errors", style="red")
    
    for result in results:
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        error_count = str(len(result.errors)) if result.errors else "0"
        
        table.add_row(
            result.file_path,
            result.file_type,
            status,
            error_count
        )
    
    console.print(table)
    
    # Show errors
    for result in results:
        if result.errors:
            console.print(f"\n[red]Errors in {result.file_path}:[/red]")
            for error in result.errors:
                console.print(f"  • {error}")


def _display_enriched_results(results: List[ValidationResult]):
    """Display enriched validation results with detailed information."""
    
    for result in results:
        console.print(f"\n[bold]File:[/bold] {result.file_path}")
        console.print(f"[bold]Type:[/bold] {result.file_type}")
        
        if result.is_valid:
            console.print("[green]✓ Valid[/green]")
            if result.metadata:
                console.print(f"[dim]Metadata: {result.metadata}[/dim]")
        else:
            console.print("[red]✗ Invalid[/red]")
            console.print(f"[red]Errors ({len(result.errors)}):[/red]")
            for i, error in enumerate(result.errors, 1):
                console.print(f"  {i}. {error}")
        
        console.print("─" * 60)