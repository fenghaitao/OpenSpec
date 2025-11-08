"""Tests for OpenSpec validation."""

import pytest
import tempfile
import shutil
from pathlib import Path

from openspec.core.validation import validate_project, ValidationResult
from openspec.utils.file_system import ensure_directory, write_file


@pytest.fixture
def temp_project():
    """Create a temporary project with OpenSpec structure."""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)
    
    # Create OpenSpec structure
    openspec_dir = project_path / "openspec"
    ensure_directory(str(openspec_dir))
    ensure_directory(str(openspec_dir / "changes"))
    ensure_directory(str(openspec_dir / "specs"))
    
    yield project_path
    shutil.rmtree(temp_dir)


def test_validate_empty_project(temp_project):
    """Test validation of empty project."""
    
    results = validate_project(str(temp_project))
    assert len(results) == 0


def test_validate_valid_change(temp_project):
    """Test validation of valid change."""
    
    # Create a valid change
    change_dir = temp_project / "openspec" / "changes" / "test-change"
    ensure_directory(str(change_dir))
    
    change_content = """# Test Change

This is a test change.

## Configuration

```json
{
  "name": "test-change",
  "why": "This is a test change that needs to be implemented for testing purposes and validation",
  "whatChanges": "Test changes will be made to the system",
  "deltas": [
    {
      "spec": "test-spec",
      "operation": "ADDED",
      "description": "Add new test specification",
      "requirements": [
        {
          "id": "req-1",
          "description": "Test requirement for validation"
        }
      ]
    }
  ]
}
```
"""
    
    write_file(str(change_dir / "proposal.md"), change_content)
    
    # Validate
    results = validate_project(str(temp_project))
    assert len(results) == 1
    assert results[0].is_valid
    assert results[0].file_type == "change"
    assert len(results[0].errors) == 0


def test_validate_invalid_change(temp_project):
    """Test validation of invalid change."""
    
    # Create an invalid change (missing required fields)
    change_dir = temp_project / "openspec" / "changes" / "invalid-change"
    ensure_directory(str(change_dir))
    
    change_content = """# Invalid Change

## Configuration

```json
{
  "name": "invalid-change",
  "why": "Too short",
  "deltas": []
}
```
"""
    
    write_file(str(change_dir / "proposal.md"), change_content)
    
    # Validate
    results = validate_project(str(temp_project))
    assert len(results) == 1
    assert not results[0].is_valid
    assert len(results[0].errors) > 0


def test_validate_valid_spec(temp_project):
    """Test validation of valid spec."""
    
    # Create a valid spec
    spec_dir = temp_project / "openspec" / "specs" / "test-spec"
    ensure_directory(str(spec_dir))
    
    spec_content = """# Test Spec

This is a test specification.

## Configuration

```json
{
  "name": "test-spec",
  "purpose": "This is a test specification for validation testing",
  "requirements": [
    {
      "id": "req-1",
      "description": "First test requirement"
    },
    {
      "id": "req-2",
      "description": "Second test requirement",
      "priority": "high"
    }
  ]
}
```
"""
    
    write_file(str(spec_dir / "spec.md"), spec_content)
    
    # Validate
    results = validate_project(str(temp_project))
    assert len(results) == 1
    assert results[0].is_valid
    assert results[0].file_type == "spec"
    assert len(results[0].errors) == 0


def test_validate_scope_filtering(temp_project):
    """Test validation with scope filtering."""
    
    # Create multiple changes
    for name in ["change-1", "change-2"]:
        change_dir = temp_project / "openspec" / "changes" / name
        ensure_directory(str(change_dir))
        
        change_content = f"""# {name}

## Configuration

```json
{{
  "name": "{name}",
  "why": "This is a test change that needs to be implemented for testing purposes and validation",
  "whatChanges": "Test changes will be made",
  "deltas": [
    {{
      "spec": "test-spec",
      "operation": "ADDED",
      "description": "Add new spec"
    }}
  ]
}}
```
"""
        write_file(str(change_dir / "proposal.md"), change_content)
    
    # Validate all
    results = validate_project(str(temp_project))
    assert len(results) == 2
    
    # Validate with scope
    results = validate_project(str(temp_project), scope="change-1")
    assert len(results) == 1
    assert "change-1" in results[0].file_path