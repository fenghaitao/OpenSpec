"""Change schema definitions."""

from typing import List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator

from .base import RequirementSchema


class DeltaOperation(str, Enum):
    """Delta operation types."""
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    REMOVED = "REMOVED"
    RENAMED = "RENAMED"


class RenameInfo(BaseModel):
    """Rename information for delta operations."""
    from_name: str = Field(..., alias="from")
    to: str


class Delta(BaseModel):
    """Delta schema for changes."""
    spec: str = Field(..., min_length=1, description="Spec being changed")
    operation: DeltaOperation
    description: str = Field(..., min_length=1, description="Description of the change")
    requirement: Optional[RequirementSchema] = None
    requirements: Optional[List[RequirementSchema]] = None
    rename: Optional[RenameInfo] = None


class ChangeMetadata(BaseModel):
    """Metadata for changes."""
    version: str = "1.0.0"
    format: Literal["openspec-change"] = "openspec-change"
    source_path: Optional[str] = Field(None, alias="sourcePath")


class Change(BaseModel):
    """Change schema."""
    name: str = Field(..., min_length=1, description="Name of the change")
    why: str = Field(
        ..., 
        min_length=50,  # MIN_WHY_SECTION_LENGTH
        max_length=2000,  # MAX_WHY_SECTION_LENGTH  
        description="Why this change is needed"
    )
    what_changes: str = Field(..., min_length=1, alias="whatChanges", description="What changes")
    deltas: List[Delta] = Field(
        ..., 
        min_items=1, 
        max_items=50,  # MAX_DELTAS_PER_CHANGE
        description="List of deltas"
    )
    metadata: Optional[ChangeMetadata] = None


# Export schemas for validation
ChangeSchema = Change
DeltaSchema = Delta