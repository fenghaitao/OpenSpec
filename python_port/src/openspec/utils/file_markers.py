"""Utilities for managing OpenSpec file markers."""

from pathlib import Path
from typing import Optional
from .file_system import write_file, read_file, file_exists


async def create_file_with_markers(file_path: str, content: str) -> None:
    """Create a new file with OpenSpec markers."""
    marked_content = f"""<!-- OPENSPEC:START -->
{content}
<!-- OPENSPEC:END -->"""
    
    write_file(file_path, marked_content)


async def update_file_with_markers(file_path: str, new_content: str) -> None:
    """Update an existing file with OpenSpec markers."""
    
    if not file_exists(file_path):
        await create_file_with_markers(file_path, new_content)
        return
    
    existing_content = read_file(file_path)
    
    if has_openspec_markers(existing_content):
        # Replace content between markers
        updated_content = replace_content_between_markers(existing_content, new_content)
        write_file(file_path, updated_content)
    else:
        # Add markers around new content
        await create_file_with_markers(file_path, new_content)

from pathlib import Path
from typing import Optional
from .file_system import read_file, write_file


async def update_file_with_markers(
    file_path: str,
    content: str,
    start_marker: str,
    end_marker: str
) -> None:
    """Update content between OpenSpec markers in a file."""
    file_path_obj = Path(file_path)
    
    if file_path_obj.exists():
        # Update existing file
        existing_content = read_file(file_path)
        updated_content = _replace_content_between_markers(
            existing_content, content, start_marker, end_marker
        )
    else:
        # Create new file
        updated_content = f"{start_marker}\n{content}\n{end_marker}\n"
    
    # Ensure parent directory exists
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    write_file(file_path, updated_content)


def _replace_content_between_markers(
    existing_content: str,
    new_content: str,
    start_marker: str,
    end_marker: str
) -> str:
    """Replace content between markers, preserving everything else."""
    start_index = existing_content.find(start_marker)
    end_index = existing_content.find(end_marker)
    
    if start_index == -1 or end_index == -1:
        # No markers found, append at end
        return f"{existing_content}\n{start_marker}\n{new_content}\n{end_marker}\n"
    
    if end_index <= start_index:
        raise ValueError("End marker appears before start marker")
    
    # Replace content between markers
    before = existing_content[:start_index + len(start_marker)]
    after = existing_content[end_index:]
    
    return f"{before}\n{new_content}\n{after}"


def has_openspec_markers(file_path: str, start_marker: str, end_marker: str) -> bool:
    """Check if a file contains OpenSpec markers."""
    try:
        content = read_file(file_path)
        return start_marker in content and end_marker in content
    except (FileNotFoundError, PermissionError):
        return False


def extract_content_between_markers(
    file_path: str,
    start_marker: str,
    end_marker: str
) -> Optional[str]:
    """Extract content between OpenSpec markers."""
    try:
        content = read_file(file_path)
        start_index = content.find(start_marker)
        end_index = content.find(end_marker)
        
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            return None
        
        start_pos = start_index + len(start_marker)
        return content[start_pos:end_index].strip()
    except (FileNotFoundError, PermissionError):
        return None