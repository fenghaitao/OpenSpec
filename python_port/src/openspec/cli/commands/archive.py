"""Archive command for OpenSpec CLI."""

import click
from rich.console import Console

from ...core.change_operations import archive_change, list_changes
from ...utils.file_system import find_openspec_root

console = Console()


class ArchiveCommand:
    """Command handler for archiving changes."""
    
    def __init__(self):
        self.console = Console()
    
    def execute(self, name: str = None, archive_all: bool = False, yes: bool = False, skip_specs: bool = False, no_validate: bool = False):
        """Execute the archive command."""
        project_path = find_openspec_root()
        if not project_path:
            self.console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
            raise click.Abort()
        
        if archive_all and name:
            self.console.print("[red]Error: Cannot specify both --all and a change name.[/red]")
            raise click.Abort()
        
        if not archive_all and not name:
            self.console.print("[red]Error: Must specify either a change name or --all.[/red]")
            raise click.Abort()
        
        try:
            if archive_all:
                # Archive all active changes
                changes = list_changes(str(project_path))
                active_changes = [c for c in changes if not c["is_archived"]]
                
                if not active_changes:
                    self.console.print("[yellow]No active changes to archive.[/yellow]")
                    return
                
                # Prompt for confirmation if not using --yes flag
                if not yes:
                    import click
                    if not click.confirm(f"Archive {len(active_changes)} active change(s)?"):
                        raise click.Abort()
                
                for change in active_changes:
                    try:
                        archived_path = archive_change(str(project_path), change["name"])
                        self.console.print(f"[green]✓[/green] Archived: {change['name']}")
                    except Exception as e:
                        self.console.print(f"[red]✗[/red] Failed to archive {change['name']}: {e}")
                
                self.console.print(f"\n[green]Archived {len(active_changes)} change(s).[/green]")
                
            else:
                # Check if change exists
                changes_dir = project_path / "openspec" / "changes"
                change_path = changes_dir / name
                if not change_path.exists():
                    self.console.print(f"[red]Change '{name}' not found.[/red]")
                    raise click.Abort()
                
                # Prompt for confirmation if not using --yes flag
                if not yes:
                    import click
                    if not click.confirm(f"Archive change '{name}'?"):
                        raise click.Abort()
                
                # Archive specific change
                archived_path = archive_change(str(project_path), name)
                self.console.print(f"[green]✓[/green] Archived change: {name}")
                self.console.print(f"[dim]Moved to: {archived_path}[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]Error archiving change(s): {e}[/red]")
            raise click.Abort()


@click.command()
@click.argument("name", required=False)
@click.option("--all", "archive_all", is_flag=True, help="Archive all active changes")
def archive(name: str, archive_all: bool):
    """Archive completed changes."""
    command = ArchiveCommand()
    command.execute(name, archive_all)
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    if archive_all and name:
        console.print("[red]Error: Cannot specify both --all and a change name.[/red]")
        raise click.Abort()
    
    if not archive_all and not name:
        console.print("[red]Error: Must specify either a change name or --all.[/red]")
        raise click.Abort()
    
    try:
        if archive_all:
            # Archive all active changes
            changes = list_changes(str(project_path))
            active_changes = [c for c in changes if not c["is_archived"]]
            
            if not active_changes:
                console.print("[yellow]No active changes to archive.[/yellow]")
                return
            
            if not click.confirm(f"Archive {len(active_changes)} active change(s)?"):
                raise click.Abort()
            
            for change in active_changes:
                try:
                    archived_path = archive_change(str(project_path), change["name"])
                    console.print(f"[green]✓[/green] Archived: {change['name']}")
                except Exception as e:
                    console.print(f"[red]✗[/red] Failed to archive {change['name']}: {e}")
            
            console.print(f"\n[green]Archived {len(active_changes)} change(s).[/green]")
            
        else:
            # Archive specific change
            archived_path = archive_change(str(project_path), name)
            console.print(f"[green]✓[/green] Archived change: {name}")
            console.print(f"[dim]Moved to: {archived_path}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error archiving change(s): {e}[/red]")
        raise click.Abort()