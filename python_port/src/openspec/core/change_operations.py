"""Change operations for OpenSpec."""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .templates.change_template import create_change_template
from .parsers import parse_markdown_file
from ..utils.file_system import (
    find_openspec_root, ensure_directory, write_file, 
    list_directories, file_exists, read_file
)


def create_change(project_path: str, name: Optional[str] = None) -> str:
    """Create a new change proposal."""
    
    if not name:
        # Generate a name based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"change-{timestamp}"
    
    # Sanitize name
    name = name.lower().replace(" ", "-").replace("_", "-")
    
    # Create change directory
    changes_dir = Path(project_path) / "openspec" / "changes"
    change_dir = changes_dir / name
    
    if change_dir.exists():
        raise ValueError(f"Change '{name}' already exists")
    
    ensure_directory(str(change_dir))
    ensure_directory(str(change_dir / "specs"))
    
    # Create proposal.md
    proposal_content = create_change_template(name)
    proposal_path = change_dir / "proposal.md"
    write_file(str(proposal_path), proposal_content)
    
    # Create tasks.md
    tasks_content = f"""# {name} - Tasks

## TODO

- [ ] Define requirements in proposal.md
- [ ] Create or update relevant specs
- [ ] Implement changes
- [ ] Test implementation
- [ ] Validate all specs
- [ ] Archive change when complete

## Progress Notes

<!-- Add progress notes here -->
"""
    
    tasks_path = change_dir / "tasks.md"
    write_file(str(tasks_path), tasks_content)
    
    return str(change_dir)


def list_changes(project_path: str) -> List[Dict[str, Any]]:
    """List all changes in the project."""
    
    changes = []
    
    # Active changes
    changes_dir = Path(project_path) / "openspec" / "changes"
    if changes_dir.exists():
        for change_name in list_directories(str(changes_dir)):
            if change_name != "archive":
                changes.append({
                    "name": change_name,
                    "path": str(changes_dir / change_name),
                    "is_archived": False
                })
    
    # Archived changes
    archive_dir = changes_dir / "archive"
    if archive_dir.exists():
        for change_name in list_directories(str(archive_dir)):
            changes.append({
                "name": change_name,
                "path": str(archive_dir / change_name),
                "is_archived": True
            })
    
    return sorted(changes, key=lambda x: x["name"])


def show_change(project_path: str, name: str) -> Optional[Dict[str, Any]]:
    """Show details of a specific change."""
    
    changes_dir = Path(project_path) / "openspec" / "changes"
    
    # Check active changes
    change_path = changes_dir / name
    if not change_path.exists():
        # Check archived changes
        change_path = changes_dir / "archive" / name
        if not change_path.exists():
            return None
    
    change_info = {
        "name": name,
        "path": str(change_path),
        "is_archived": "archive" in str(change_path)
    }
    
    # Read proposal if it exists
    proposal_path = change_path / "proposal.md"
    if file_exists(str(proposal_path)):
        try:
            content = read_file(str(proposal_path))
            parsed = parse_markdown_file(content)
            if parsed["json"]:
                change_info["proposal"] = parsed["json"]
        except Exception:
            pass  # Ignore parsing errors
    
    return change_info


def archive_change(project_path: str, name: str) -> str:
    """Archive a change by moving it to the archive directory."""
    
    changes_dir = Path(project_path) / "openspec" / "changes"
    source_path = changes_dir / name
    
    if not source_path.exists():
        raise ValueError(f"Change '{name}' not found")
    
    # Create archive directory
    archive_dir = changes_dir / "archive"
    ensure_directory(str(archive_dir))
    
    # Move to archive with date prefix
    from datetime import date
    date_prefix = date.today().isoformat()
    archived_name = f"{date_prefix}-{name}"
    dest_path = archive_dir / archived_name
    source_path.rename(dest_path)
    
    return str(dest_path)