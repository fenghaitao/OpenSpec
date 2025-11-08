"""Validation logic for OpenSpec files."""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..schemas import ChangeSchema, SpecSchema
from ..parsers import parse_markdown_file, extract_json_from_markdown
from ...utils.file_system import find_files_with_extension, read_file


@dataclass
class ValidationResult:
    """Result of validating a file."""
    file_path: str
    file_type: str
    is_valid: bool
    errors: List[str]
    metadata: Optional[Dict[str, Any]] = None


def validate_project(project_path: str, scope: Optional[str] = None) -> List[ValidationResult]:
    """Validate all files in an OpenSpec project."""
    
    results = []
    openspec_dir = Path(project_path) / "openspec"
    
    if not openspec_dir.exists():
        return results
    
    # Find all markdown files
    changes_dir = openspec_dir / "changes"
    specs_dir = openspec_dir / "specs"
    
    # Handle scope filtering
    validate_changes = True
    validate_specs = True
    specific_item = None
    
    if scope:
        if scope == "changes":
            validate_specs = False
        elif scope == "specs":
            validate_changes = False
        else:
            # Specific item name
            specific_item = scope
    
    # Validate change proposals
    if validate_changes and changes_dir.exists():
        for change_dir in changes_dir.iterdir():
            if change_dir.is_dir() and not change_dir.name.startswith(".") and change_dir.name != "archive":
                # Skip if specific item is specified and doesn't match
                if specific_item and specific_item != change_dir.name:
                    continue
                    
                proposal_file = change_dir / "proposal.md"
                if proposal_file.exists():
                    result = _validate_change_file(str(proposal_file))
                    results.append(result)
    
    # Validate specs
    if validate_specs and specs_dir.exists():
        for spec_dir in specs_dir.iterdir():
            if spec_dir.is_dir() and not spec_dir.name.startswith("."):
                # Skip if specific item is specified and doesn't match
                if specific_item and specific_item != spec_dir.name:
                    continue
                    
                spec_file = spec_dir / "spec.md"
                if spec_file.exists():
                    result = _validate_spec_file(str(spec_file))
                    results.append(result)
    
    return results


def _validate_change_file(file_path: str) -> ValidationResult:
    """Validate a change proposal file."""
    
    errors = []
    
    try:
        # Parse the markdown file
        content = read_file(file_path)
        
        # Basic markdown validation first
        if not content.strip():
            errors.append("File is empty")
            return ValidationResult(
                file_path=file_path,
                file_type="change", 
                is_valid=False,
                errors=errors
            )
        
        # Check for required sections - more flexible checking
        has_why = any(section in content for section in ["## Why", "## Configuration"])
        has_what_changes = any(section in content for section in ["## What Changes", "## Configuration"])
        
        if not has_why:
            errors.append("Missing required section: ## Why")
        
        if not has_what_changes:
            errors.append("Missing required section: ## What Changes")
        
        # Try to extract JSON configuration (optional for basic proposals)
        json_data = extract_json_from_markdown(content)
        
        if json_data:
            # Validate against schema if JSON is present
            try:
                change = ChangeSchema.model_validate(json_data)
                # Additional validations
                _validate_change_business_rules(change, errors)
            except Exception as e:
                errors.append(f"Schema validation failed: {str(e)}")
        
    except Exception as e:
        errors.append(f"Failed to parse file: {str(e)}")
    
    return ValidationResult(
        file_path=file_path,
        file_type="change",
        is_valid=len(errors) == 0,
        errors=errors
    )


def _validate_spec_file(file_path: str) -> ValidationResult:
    """Validate a spec file."""
    
    errors = []
    
    try:
        # Parse the markdown file
        content = read_file(file_path)
        
        # Basic markdown validation first
        if not content.strip():
            errors.append("File is empty")
            return ValidationResult(
                file_path=file_path,
                file_type="spec",
                is_valid=False,
                errors=errors
            )
        
        # Check for required sections - more flexible checking
        has_purpose = any(section in content for section in ["## Purpose", "## Configuration"])
        has_requirements = any(section in content for section in ["## Requirements", "## Configuration"])
        
        if not has_purpose:
            errors.append("Missing required section: ## Purpose")
        
        if not has_requirements:
            errors.append("Missing required section: ## Requirements")
        
        # Try to extract JSON configuration (optional for basic specs)
        json_data = extract_json_from_markdown(content)
        
        if json_data:
            # Validate against schema if JSON is present
            try:
                spec = SpecSchema.model_validate(json_data)
                # Additional validations
                _validate_spec_business_rules(spec, errors)
            except Exception as e:
                errors.append(f"Schema validation failed: {str(e)}")
        
    except Exception as e:
        errors.append(f"Failed to parse file: {str(e)}")
    
    return ValidationResult(
        file_path=file_path,
        file_type="spec",
        is_valid=len(errors) == 0,
        errors=errors
    )


def _validate_change_business_rules(change: ChangeSchema, errors: List[str]) -> None:
    """Validate business rules for changes."""
    
    # Check delta operations
    for delta in change.deltas:
        if delta.operation == "RENAMED" and not delta.rename:
            errors.append(f"Delta with RENAMED operation must include rename information: {delta.spec}")
        
        # Validate requirement constraints
        if delta.requirement and delta.requirements:
            errors.append(f"Delta cannot have both 'requirement' and 'requirements': {delta.spec}")


def _validate_spec_business_rules(spec: SpecSchema, errors: List[str]) -> None:
    """Validate business rules for specs."""
    
    # Check for duplicate requirement IDs
    requirement_ids = [req.id for req in spec.requirements]
    duplicates = set([id for id in requirement_ids if requirement_ids.count(id) > 1])
    
    if duplicates:
        errors.append(f"Duplicate requirement IDs found: {', '.join(duplicates)}")