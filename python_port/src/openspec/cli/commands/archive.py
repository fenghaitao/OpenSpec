"""Archive command for OpenSpec CLI."""

import click
from pathlib import Path
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
                    if not prompt_for_confirmation(f"Archive {len(active_changes)} active change(s)?"):
                        self.console.print("[yellow]Archive cancelled.[/yellow]")
                        return
                
                for change in active_changes:
                    try:
                        archived_path = archive_change(str(project_path), change["name"], skip_specs=skip_specs)
                        self.console.print(f"[green]✓[/green] Archived: {change['name']}")
                    except Exception as e:
                        self.console.print(f"[red]✗[/red] Failed to archive {change['name']}: {e}")
                
                self.console.print(f"\n[green]Archived {len(active_changes)} change(s).[/green]")
                
            else:
                # Check if change exists
                changes_dir = project_path / "openspec" / "changes"
                change_path = changes_dir / name
                if not change_path.exists():
                    raise FileNotFoundError(f"Change '{name}' not found")
                
                # Check for incomplete tasks and warn
                self._check_incomplete_tasks(change_path)
                
                # Prompt for confirmation if not using --yes flag
                if not yes:
                    if not prompt_for_confirmation(f"Archive change '{name}'?"):
                        self.console.print("[yellow]Archive cancelled.[/yellow]")
                        return
                
                # Archive specific change
                archived_path = archive_change(str(project_path), name, skip_specs=skip_specs)
                self.console.print(f"[green]✓[/green] Archived change: {name}")
                self.console.print(f"[dim]Moved to: {archived_path}[/dim]")
            
        except (FileNotFoundError, FileExistsError, click.Abort):
            # Re-raise these exceptions as-is for tests
            raise
        except Exception as e:
            self.console.print(f"[red]Error archiving change(s): {e}[/red]")
            raise click.Abort()
    
    def _check_incomplete_tasks(self, change_path: Path) -> None:
        """Check for incomplete tasks and warn if found."""
        tasks_file = change_path / "tasks.md"
        if not tasks_file.exists():
            return
        
        try:
            content = tasks_file.read_text()
            import re
            
            # Count incomplete tasks
            incomplete_tasks = re.findall(r'^\s*-\s*\[\s*\]', content, re.MULTILINE)
            incomplete_count = len(incomplete_tasks)
            
            if incomplete_count > 0:
                self.console.print(f"[yellow]Warning: {incomplete_count} incomplete task(s) found[/yellow]")
        except Exception:
            # Ignore errors reading tasks file
            pass


def prompt_for_confirmation(message: str) -> bool:
    """Prompt user for confirmation."""
    import click
    return click.confirm(message)


@click.command()
@click.argument("name", required=False)
@click.option("--all", "archive_all", is_flag=True, help="Archive all active changes")
def archive(name: str, archive_all: bool):
    """Archive completed changes."""
    command = ArchiveCommand()
    command.execute(name, archive_all)