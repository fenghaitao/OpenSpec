"""Base schema definitions."""

from typing import Optional
from pydantic import BaseModel, Field


class RequirementSchema(BaseModel):
    """Base requirement schema."""
    id: str = Field(..., min_length=1, description="Unique identifier for the requirement")
    description: str = Field(..., min_length=1, description="Description of the requirement")
    priority: Optional[str] = Field(None, description="Priority level of the requirement")