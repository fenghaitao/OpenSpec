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


def archive_change(project_path: str, name: str, skip_specs: bool = False) -> str:
    """Archive a change by moving it to the archive directory and updating specs."""
    
    changes_dir = Path(project_path) / "openspec" / "changes"
    source_path = changes_dir / name
    
    if not source_path.exists():
        raise ValueError(f"Change '{name}' not found")
    
    # Apply spec deltas before archiving (unless skipped)
    if not skip_specs:
        _apply_spec_deltas(project_path, source_path, name)
    
    # Create archive directory
    archive_dir = changes_dir / "archive"
    ensure_directory(str(archive_dir))
    
    # Move to archive with date prefix
    from datetime import date
    date_prefix = date.today().isoformat()
    archived_name = f"{date_prefix}-{name}"
    dest_path = archive_dir / archived_name
    
    # Check if archive already exists
    if dest_path.exists():
        raise FileExistsError(f"Archive '{archived_name}' already exists")
    
    source_path.rename(dest_path)
    
    return str(dest_path)


def _apply_spec_deltas(project_path: str, change_path: Path, change_name: str) -> None:
    """Apply spec deltas from a change to the main specs."""
    
    # Find all spec deltas in the change
    change_specs_dir = change_path / "specs"
    if not change_specs_dir.exists():
        return
    
    for spec_name in list_directories(str(change_specs_dir)):
        spec_delta_path = change_specs_dir / spec_name / "spec.md"
        if not spec_delta_path.exists():
            continue
        
        # Read the spec delta
        try:
            delta_content = read_file(str(spec_delta_path))
            from .parsers.markdown_parser import MarkdownParser
            parser = MarkdownParser()
            delta_spec = parser.parse_change_spec(delta_content)
            
            # Apply deltas to main spec
            _update_main_spec(project_path, spec_name, delta_spec, change_name)
            
        except Exception as e:
            print(f"Warning: Failed to apply spec delta for {spec_name}: {e}")


def _update_main_spec(project_path: str, spec_name: str, delta_spec: Dict[str, Any], change_name: str) -> None:
    """Update a main spec with deltas from a change spec."""
    
    specs_dir = Path(project_path) / "openspec" / "specs"
    main_spec_dir = specs_dir / spec_name
    main_spec_path = main_spec_dir / "spec.md"
    
    # Create spec directory if it doesn't exist
    ensure_directory(str(main_spec_dir))
    
    # Read existing spec or create from skeleton
    if main_spec_path.exists():
        existing_content = read_file(str(main_spec_path))
        from .parsers.markdown_parser import MarkdownParser
        parser = MarkdownParser()
        existing_spec = parser.parse_spec(existing_content)
    else:
        # Create new spec from skeleton
        existing_spec = {
            "title": f"{spec_name} Specification",
            "purpose": f"Specification created by archiving change {change_name}",
            "requirements": [],
            "sections": {},
            "raw_content": ""
        }
    
    # Merge requirements
    updated_requirements = list(existing_spec.get("requirements", []))
    
    # Add new requirements
    for req in delta_spec.get("added_requirements", []):
        updated_requirements.append(req)
    
    # Modify existing requirements
    for modified_req in delta_spec.get("modified_requirements", []):
        # Find and update existing requirement
        for i, existing_req in enumerate(updated_requirements):
            if existing_req.get("title") == modified_req.get("title"):
                # Apply modifications
                if modified_req.get("change_description"):
                    existing_req["description"] = modified_req.get("description", existing_req.get("description", ""))
                updated_requirements[i] = existing_req
                break
        else:
            # Requirement not found, add as new
            updated_requirements.append(modified_req)
    
    # Remove requirements
    for removed_req in delta_spec.get("removed_requirements", []):
        updated_requirements = [
            req for req in updated_requirements 
            if req.get("title") != removed_req.get("title")
        ]
    
    # Generate updated spec content
    updated_content = _generate_spec_content(
        title=existing_spec.get("title", f"{spec_name} Specification"),
        purpose=existing_spec.get("purpose", f"Specification for {spec_name}"),
        requirements=updated_requirements
    )
    
    # Write updated spec
    write_file(str(main_spec_path), updated_content)


def _generate_spec_content(title: str, purpose: str, requirements: List[Dict[str, Any]]) -> str:
    """Generate markdown content for a spec."""
    
    content_lines = [
        f"# {title}",
        "",
        "## Purpose",
        purpose,
        "",
        "## Requirements",
        ""
    ]
    
    for req in requirements:
        content_lines.append(f"### Requirement: {req.get('title', 'Untitled')}")
        if req.get('description'):
            content_lines.append(req['description'])
            content_lines.append("")
        
        # Add scenarios if present
        for scenario in req.get('scenarios', []):
            content_lines.append(f"#### Scenario: {scenario.get('title', 'Untitled')}")
            for step in scenario.get('steps', []):
                content_lines.append(step)
            content_lines.append("")
    
    return "\n".join(content_lines)