"""Spec schema definitions."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from .base import RequirementSchema


class SpecMetadata(BaseModel):
    """Metadata for specs."""
    version: str = "1.0.0"
    format: Literal["openspec-spec"] = "openspec-spec"
    source_path: Optional[str] = Field(None, alias="sourcePath")


class Spec(BaseModel):
    """Spec schema."""
    name: str = Field(..., min_length=1, description="Name of the spec")
    purpose: str = Field(..., min_length=1, description="Purpose of the spec")
    requirements: List[RequirementSchema] = Field(
        ..., 
        description="List of requirements"
    )
    metadata: Optional[SpecMetadata] = None


# Export schema for validation
SpecSchema = Spec