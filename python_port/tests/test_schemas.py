"""Tests for OpenSpec schemas."""

import pytest
from pydantic import ValidationError

from openspec.core.schemas import ChangeSchema, SpecSchema, Delta, Change, Spec


def test_change_schema_valid():
    """Test valid change schema."""
    
    data = {
        "name": "test-change",
        "why": "This is a test change that needs to be implemented for testing purposes",
        "whatChanges": "Test changes will be made",
        "deltas": [
            {
                "spec": "test-spec",
                "operation": "ADDED",
                "description": "Add new test spec",
                "requirements": [
                    {
                        "id": "req-1",
                        "description": "Test requirement"
                    }
                ]
            }
        ]
    }
    
    change = ChangeSchema.model_validate(data)
    assert change.name == "test-change"
    assert len(change.deltas) == 1
    assert change.deltas[0].operation == "ADDED"


def test_change_schema_invalid_why_too_short():
    """Test change schema with why section too short."""
    
    data = {
        "name": "test-change",
        "why": "Too short",  # Less than 50 characters
        "whatChanges": "Test changes",
        "deltas": [
            {
                "spec": "test-spec",
                "operation": "ADDED",
                "description": "Add new spec"
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        ChangeSchema.model_validate(data)


def test_change_schema_invalid_no_deltas():
    """Test change schema without deltas."""
    
    data = {
        "name": "test-change",
        "why": "This is a test change that needs to be implemented for testing purposes",
        "whatChanges": "Test changes",
        "deltas": []  # Empty deltas
    }
    
    with pytest.raises(ValidationError):
        ChangeSchema.model_validate(data)


def test_spec_schema_valid():
    """Test valid spec schema."""
    
    data = {
        "name": "test-spec",
        "purpose": "This is a test specification",
        "requirements": [
            {
                "id": "req-1",
                "description": "First requirement"
            },
            {
                "id": "req-2", 
                "description": "Second requirement",
                "priority": "high"
            }
        ]
    }
    
    spec = SpecSchema.model_validate(data)
    assert spec.name == "test-spec"
    assert len(spec.requirements) == 2
    assert spec.requirements[0].id == "req-1"


def test_delta_with_rename():
    """Test delta with rename operation."""
    
    data = {
        "spec": "test-spec",
        "operation": "RENAMED",
        "description": "Rename the spec",
        "rename": {
            "from": "old-name",
            "to": "new-name"
        }
    }
    
    delta = Delta.model_validate(data)
    assert delta.operation == "RENAMED"
    assert delta.rename.from_name == "old-name"
    assert delta.rename.to == "new-name"


def test_change_metadata():
    """Test change with metadata."""
    
    data = {
        "name": "test-change",
        "why": "This is a test change that needs to be implemented for testing purposes",
        "whatChanges": "Test changes",
        "deltas": [
            {
                "spec": "test-spec",
                "operation": "ADDED",
                "description": "Add new spec"
            }
        ],
        "metadata": {
            "version": "1.0.0",
            "format": "openspec-change",
            "sourcePath": "/path/to/change"
        }
    }
    
    change = ChangeSchema.model_validate(data)
    assert change.metadata.version == "1.0.0"
    assert change.metadata.format == "openspec-change"