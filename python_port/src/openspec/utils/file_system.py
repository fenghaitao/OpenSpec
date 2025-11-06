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
    Path(path).write_text(content, encoding="utf-8")


def read_file(path: str) -> str:
    """Read content from a file."""
    return Path(path).read_text(encoding="utf-8")


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return Path(path).exists()


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