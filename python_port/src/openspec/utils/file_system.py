"""File system utilities for OpenSpec."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..core.config import OPENSPEC_DIR_NAME


def find_openspec_root(start_path: Optional[str] = None) -> Optional[Path]:
    """Find the root directory containing an openspec folder."""
    
    if start_path:
        current = Path(start_path).resolve()
    else:
        current = Path.cwd().resolve()
    
    # Check current directory and parents
    for path in [current] + list(current.parents):
        openspec_dir = path / OPENSPEC_DIR_NAME
        if openspec_dir.exists() and openspec_dir.is_dir():
            return path
    
    return None


def ensure_directory(path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def write_file(path: str, content: str) -> None:
    """Write content to a file."""
    path_obj = Path(path)
    # Ensure parent directories exist
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(content, encoding="utf-8")


def read_file(path: str) -> str:
    """Read content from a file."""
    return Path(path).read_text(encoding="utf-8")


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    path_obj = Path(path)
    return path_obj.exists() and path_obj.is_file()


def directory_exists(path: str) -> bool:
    """Check if a directory exists."""
    return Path(path).is_dir()


def list_files(path: str, pattern: str = None) -> List[str]:
    """List all files in a given path, optionally with a pattern."""
    path_obj = Path(path)
    if not path_obj.exists():
        return []
    
    if pattern:
        import fnmatch
        return [
            item.name for item in path_obj.iterdir() 
            if item.is_file() and not item.name.startswith(".") and fnmatch.fnmatch(item.name, pattern)
        ]
    else:
        return [
            item.name for item in path_obj.iterdir() 
            if item.is_file() and not item.name.startswith(".")
        ]


def list_directories(path: str) -> List[str]:
    """List all directories in a given path."""
    path_obj = Path(path)
    if not path_obj.exists():
        return []
    
    return [
        item.name for item in path_obj.iterdir() 
        if item.is_dir() and not item.name.startswith(".")
    ]


def find_files_with_extension(directory: str, extension: str) -> List[str]:
    """Find all files with a specific extension in a directory."""
    path_obj = Path(directory)
    if not path_obj.exists():
        return []
    
    return [
        str(file_path) for file_path in path_obj.rglob(f"*.{extension}")
    ]


def read_json_file(path: str) -> Dict[Any, Any]:
    """Read and parse a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(path: str, data: Dict[Any, Any]) -> None:
    """Write data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def copy_file(src: str, dest: str) -> None:
    """Copy a file from source to destination."""
    import shutil
    dest_path = Path(dest)
    # Ensure parent directories exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def move_file(src: str, dest: str) -> None:
    """Move a file from source to destination."""
    import shutil
    dest_path = Path(dest)
    # Ensure parent directories exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dest)


def delete_file(path: str) -> None:
    """Delete a file."""
    Path(path).unlink(missing_ok=True)


def delete_directory(path: str) -> None:
    """Delete a directory and all its contents."""
    import shutil
    path_obj = Path(path)
    if path_obj.exists():
        shutil.rmtree(path)