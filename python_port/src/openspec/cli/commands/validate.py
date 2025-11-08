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
@click.option("--all", is_flag=True, help="Validate all files")
@click.option("--changes", is_flag=True, help="Validate only changes")
@click.option("--specs", is_flag=True, help="Validate only specs")
@click.option("--scope", help="Scope to validate (change name or spec name)")
@click.option("--enriched", is_flag=True, help="Show enriched validation output")
@click.option("--json", is_flag=True, help="Output as JSON")
@click.option("--concurrency", type=int, default=4, help="Number of concurrent validations")
@click.argument("items", nargs=-1)
def validate(all: bool, changes: bool, specs: bool, scope: Optional[str], enriched: bool, json: bool, concurrency: int, items: tuple):
    """Validate OpenSpec project files."""
    
    # Find project root
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    # Check if no validation scope specified
    if not any([all, changes, specs, scope, items]):
        console.print("Nothing to validate. Try one of:")
        console.print("  openspec validate --all")
        console.print("  openspec validate --changes") 
        console.print("  openspec validate --specs")
        console.print("  openspec validate <item>")
        raise click.Abort()
    
    try:
        # Determine what to validate based on flags
        if all:
            scope = None  # Validate everything
        elif changes:
            scope = "changes"
        elif specs:
            scope = "specs"
        elif items:
            scope = list(items)[0]  # Validate specific items
            
            # Check for ambiguous item names
            if scope and scope not in ["changes", "specs"]:
                changes_dir = project_path / "openspec" / "changes"
                specs_dir = project_path / "openspec" / "specs"
                
                has_change = (changes_dir / scope).exists() if changes_dir.exists() else False
                has_spec = (specs_dir / scope).exists() if specs_dir.exists() else False
                
                if has_change and has_spec:
                    console.print(f"[red]Ambiguous item '{scope}' found in both changes and specs.[/red]")
                    console.print("Please specify --changes or --specs to clarify.")
                    raise click.Abort()
        
        # Run validation
        results = validate_project(str(project_path), scope=scope)
        
        if not results:
            console.print("[green]✓ No files found to validate.[/green]")
            return
        
        # Display results
        has_errors = any(not result.is_valid for result in results)
        
        if json:
            import json as json_lib
            output = {
                "version": "1.0",
                "summary": {
                    "totals": {
                        "total": len(results),
                        "valid": sum(1 for r in results if r.is_valid),
                        "invalid": sum(1 for r in results if not r.is_valid)
                    }
                },
                "items": [
                    {
                        "path": r.file_path,
                        "type": r.file_type,
                        "valid": r.is_valid,
                        "errors": r.errors or []
                    }
                    for r in results
                ]
            }
            console.print(json_lib.dumps(output, indent=2))
        elif enriched:
            _display_enriched_results(results)
        else:
            _display_standard_results(results)
        
        if has_errors:
            raise click.Abort()
        else:
            if not json:
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