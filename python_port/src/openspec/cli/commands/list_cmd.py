"""List command for OpenSpec CLI."""

import click
from rich.console import Console

from ...core.change_operations import list_changes
from ...utils.file_system import find_openspec_root, list_directories
from pathlib import Path

console = Console()


class ListCommand:
    """Command handler for listing project items."""
    
    def __init__(self):
        self.console = Console()
    
    def execute(self, project_path: str = None, item_type: str = "changes", archived: bool = False):
        """Execute the list command."""
        if project_path is None:
            project_path = find_openspec_root()
            if not project_path:
                self.console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
                raise click.Abort()
            project_path = str(project_path)
        
        # Check if changes directory exists
        changes_dir = Path(project_path) / "openspec" / "changes"
        if not changes_dir.exists():
            raise FileNotFoundError("No OpenSpec changes directory found")
        
        try:
            if item_type in ["changes", "all"]:
                self._list_changes(project_path, archived)
            
            if item_type in ["specs", "all"]:
                self._list_specs(project_path)
                
        except Exception as e:
            if "No OpenSpec changes directory found" in str(e):
                raise
            self.console.print(f"[red]Error listing items: {e}[/red]")
            raise click.Abort()
    
    def _list_changes(self, project_path: str, include_archived: bool):
        """List changes."""
        from ...core.change_operations import list_changes as list_changes_op
        
        changes = list_changes_op(project_path)
        
        if not include_archived:
            changes = [c for c in changes if not c["is_archived"]]
        
        if not changes:
            status = "active changes" if not include_archived else "changes (including archived)"
            self.console.print(f"No {status} found.")
            return
        
        self.console.print("Changes:")
        
        # Group by status
        active_changes = [c for c in changes if not c["is_archived"]]
        archived_changes = [c for c in changes if c["is_archived"]]
        
        if active_changes:
            for change in sorted(active_changes, key=lambda x: x['name']):
                # Get task info
                task_info = self._get_task_info(change['path'])
                if task_info['total'] > 0:
                    if task_info['completed'] == task_info['total']:
                        self.console.print(f"  ✓ Complete {change['name']}")
                    else:
                        self.console.print(f"  🔄 {change['name']} {task_info['completed']}/{task_info['total']} tasks")
                else:
                    self.console.print(f"  🔄 {change['name']} No tasks")
        
        if archived_changes and include_archived:
            for change in sorted(archived_changes, key=lambda x: x['name']):
                self.console.print(f"  📁 {change['name']}")
    
    def _list_specs(self, project_path: str):
        """List specs."""
        specs_dir = Path(project_path) / "openspec" / "specs"
        
        if not specs_dir.exists():
            self.console.print("[yellow]No specs directory found.[/yellow]")
            return
        
        specs = list_directories(str(specs_dir))
        
        if not specs:
            self.console.print("[yellow]No specs found.[/yellow]")
            return
        
        self.console.print("\n[bold]Specifications:[/bold]")
        for spec_name in sorted(specs):
            self.console.print(f"  📋 {spec_name}")
    
    def _get_task_info(self, change_path: str) -> dict:
        """Get task completion information for a change."""
        tasks_file = Path(change_path) / "tasks.md"
        if not tasks_file.exists():
            return {'completed': 0, 'total': 0}
        
        try:
            content = tasks_file.read_text()
            import re
            
            # Find task lines
            completed_tasks = re.findall(r'^\s*-\s*\[x\]', content, re.MULTILINE)
            incomplete_tasks = re.findall(r'^\s*-\s*\[\s*\]', content, re.MULTILINE)
            
            completed = len(completed_tasks)
            total = completed + len(incomplete_tasks)
            
            return {'completed': completed, 'total': total}
        except Exception:
            return {'completed': 0, 'total': 0}


@click.command("list")
@click.option("--type", "item_type", type=click.Choice(["changes", "specs", "all"]), default="changes", help="Type of items to list")
@click.option("--archived", is_flag=True, help="Include archived items")
def list_changes(item_type: str, archived: bool):
    """List changes, specs, or all items in the project."""
    command = ListCommand()
    command.execute(item_type, archived)
    
    project_path = find_openspec_root()
    if not project_path:
        console.print("[red]Error: Not in an OpenSpec project directory.[/red]")
        raise click.Abort()
    
    try:
        if item_type in ["changes", "all"]:
            _list_changes(str(project_path), archived)
        
        if item_type in ["specs", "all"]:
            _list_specs(str(project_path))
            
    except Exception as e:
        console.print(f"[red]Error listing items: {e}[/red]")
        raise click.Abort()


def _list_changes(project_path: str, include_archived: bool):
    """List changes."""
    
    changes = list_changes(project_path)
    
    if not include_archived:
        changes = [c for c in changes if not c["is_archived"]]
    
    if not changes:
        status = "changes" if not include_archived else "changes (including archived)"
        console.print(f"[yellow]No {status} found.[/yellow]")
        return
    
    console.print("[bold]Changes:[/bold]")
    
    # Group by status
    active_changes = [c for c in changes if not c["is_archived"]]
    archived_changes = [c for c in changes if c["is_archived"]]
    
    if active_changes:
        console.print("\n[green]Active:[/green]")
        for change in active_changes:
            console.print(f"  🔄 {change['name']}")
    
    if archived_changes and include_archived:
        console.print("\n[yellow]Archived:[/yellow]")
        for change in archived_changes:
            console.print(f"  📁 {change['name']}")


def _list_specs(project_path: str):
    """List specs."""
    
    specs_dir = Path(project_path) / "openspec" / "specs"
    
    if not specs_dir.exists():
        console.print("[yellow]No specs directory found.[/yellow]")
        return
    
    specs = list_directories(str(specs_dir))
    
    if not specs:
        console.print("[yellow]No specs found.[/yellow]")
        return
    
    console.print("\n[bold]Specifications:[/bold]")
    for spec_name in sorted(specs):
        console.print(f"  📋 {spec_name}")