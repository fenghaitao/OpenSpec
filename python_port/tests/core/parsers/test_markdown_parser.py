"""Tests for MarkdownParser - ported from test/core/parsers/markdown-parser.test.ts"""

import pytest
from openspec.core.parsers.markdown_parser import MarkdownParser


class TestMarkdownParser:
    """Test cases for MarkdownParser."""
    
    @pytest.fixture
    def parser(self):
        """Create a MarkdownParser instance."""
        return MarkdownParser()
    
    def test_parse_simple_proposal(self, parser):
        """Test parsing a simple proposal."""
        content = """# Test Change

## Why
Because we need to implement this feature for better functionality.

## What Changes
- **api:** Add new endpoint
- **auth:** Update authentication logic"""
        
        result = parser.parse_proposal(content)
        
        assert result["title"] == "Test Change"
        assert "Because we need to implement this feature" in result["why"]
        assert "api:" in result["what_changes"]
        assert "auth:" in result["what_changes"]
    
    def test_parse_proposal_with_configuration_block(self, parser):
        """Test parsing proposal with JSON configuration block."""
        content = """# Feature Change

## Why
This change is needed for validation purposes and testing.

## What Changes
- **core:** Add validation logic

## Configuration

```json
{
  "name": "feature-change",
  "why": "This change is needed for validation purposes and testing framework improvements",
  "whatChanges": "Add comprehensive validation logic to the core system",
  "deltas": [
    {
      "spec": "core-validation",
      "operation": "ADDED",
      "description": "Add new validation requirements",
      "requirements": [
        {
          "id": "val-1",
          "description": "System shall validate inputs"
        }
      ]
    }
  ]
}
```"""
        
        result = parser.parse_proposal(content)
        
        assert result["title"] == "Feature Change"
        assert "validation purposes" in result["why"]
        assert result["configuration"]["name"] == "feature-change"
        assert len(result["configuration"]["deltas"]) == 1
        assert result["configuration"]["deltas"][0]["spec"] == "core-validation"
    
    def test_parse_proposal_with_crlf_line_endings(self, parser):
        """Test parsing proposal with CRLF line endings."""
        content = "# CRLF Change\r\n\r\n## Why\r\nThis tests CRLF handling.\r\n\r\n## What Changes\r\n- **test:** Add CRLF support"
        
        result = parser.parse_proposal(content)
        
        assert result["title"] == "CRLF Change"
        assert "This tests CRLF handling" in result["why"]
        assert "test:" in result["what_changes"]
    
    def test_parse_spec_with_purpose_and_requirements(self, parser):
        """Test parsing spec with purpose and requirements."""
        content = """# Auth Specification

## Purpose
This specification defines the authentication system requirements.

## Requirements

### Requirement: User Authentication
The system SHALL provide secure user authentication.

#### Scenario: Login Flow
- **GIVEN** a registered user
- **WHEN** they provide valid credentials
- **THEN** they should be authenticated

### Requirement: Session Management
The system SHALL manage user sessions securely.

#### Scenario: Session Timeout
- **GIVEN** an active user session
- **WHEN** the timeout period expires
- **THEN** the session should be terminated"""
        
        result = parser.parse_spec(content)
        
        assert result["title"] == "Auth Specification"
        assert "authentication system requirements" in result["purpose"]
        assert len(result["requirements"]) == 2
        
        # Check first requirement
        req1 = result["requirements"][0]
        assert req1["title"] == "User Authentication"
        assert "secure user authentication" in req1["description"]
        assert len(req1["scenarios"]) == 1
        assert req1["scenarios"][0]["title"] == "Login Flow"
        
        # Check second requirement
        req2 = result["requirements"][1]
        assert req2["title"] == "Session Management"
        assert "manage user sessions" in req2["description"]
    
    def test_parse_spec_with_configuration_block(self, parser):
        """Test parsing spec with JSON configuration block."""
        content = """# API Specification

## Purpose
Defines the REST API endpoints and behaviors.

## Requirements

### Requirement: GET /users endpoint
The API SHALL provide user listing functionality.

## Configuration

```json
{
  "name": "api-spec",
  "purpose": "Defines the REST API endpoints and behaviors for user management",
  "requirements": [
    {
      "id": "api-1",
      "description": "GET /users endpoint shall return user list",
      "priority": "high"
    },
    {
      "id": "api-2", 
      "description": "POST /users endpoint shall create new users"
    }
  ]
}
```"""
        
        result = parser.parse_spec(content)
        
        assert result["title"] == "API Specification"
        assert "REST API endpoints" in result["purpose"]
        assert result["configuration"]["name"] == "api-spec"
        assert len(result["configuration"]["requirements"]) == 2
        assert result["configuration"]["requirements"][0]["id"] == "api-1"
    
    def test_parse_change_spec_delta_added(self, parser):
        """Test parsing change spec with ADDED delta operations."""
        content = """# User Management Changes

## ADDED Requirements

### Requirement: User Registration
The system SHALL allow new user registration.

#### Scenario: Valid Registration
- **GIVEN** valid user data
- **WHEN** registration is submitted
- **THEN** user account should be created

## MODIFIED Requirements

### Requirement: User Authentication
**CHANGE:** Add two-factor authentication support.

The system SHALL provide secure user authentication with 2FA.

## REMOVED Requirements

### Requirement: Anonymous Access
**REASON:** Security policy no longer allows anonymous access."""
        
        result = parser.parse_change_spec(content)
        
        assert result["title"] == "User Management Changes"
        assert len(result["added_requirements"]) == 1
        assert len(result["modified_requirements"]) == 1
        assert len(result["removed_requirements"]) == 1
        
        # Check ADDED requirement
        added_req = result["added_requirements"][0]
        assert added_req["title"] == "User Registration"
        assert "allow new user registration" in added_req["description"]
        assert len(added_req["scenarios"]) == 1
        
        # Check MODIFIED requirement
        modified_req = result["modified_requirements"][0]
        assert modified_req["title"] == "User Authentication"
        assert "Add two-factor authentication" in modified_req["change_description"]
        
        # Check REMOVED requirement
        removed_req = result["removed_requirements"][0]
        assert removed_req["title"] == "Anonymous Access"
        assert "Security policy no longer allows" in removed_req["removal_reason"]
    
    def test_parse_empty_content(self, parser):
        """Test parsing empty content."""
        result = parser.parse_proposal("")
        
        assert result["title"] == ""
        assert result["why"] == ""
        assert result["what_changes"] == ""
        assert result.get("configuration") is None
    
    def test_parse_malformed_json_configuration(self, parser):
        """Test parsing with malformed JSON configuration."""
        content = """# Test Change

## Why
Testing malformed JSON.

## What Changes
- **test:** Add error handling

## Configuration

```json
{
  "name": "test-change"
  "missing_comma": true
}
```"""
        
        result = parser.parse_proposal(content)
        
        assert result["title"] == "Test Change"
        assert result["why"] == "Testing malformed JSON."
        # Configuration should be None or empty due to malformed JSON
        assert result.get("configuration") is None
    
    def test_parse_multiple_code_blocks(self, parser):
        """Test parsing content with multiple code blocks."""
        content = """# Multi-Block Change

## Why
Testing multiple code blocks.

## What Changes
- **api:** Add endpoints

```typescript
// This is example code
function example() {
  return true;
}
```

## Configuration

```json
{
  "name": "multi-block-change"
}
```"""
        
        result = parser.parse_proposal(content)
        
        assert result["title"] == "Multi-Block Change"
        assert result["configuration"]["name"] == "multi-block-change"
    
    def test_parse_requirement_with_multiple_scenarios(self, parser):
        """Test parsing requirement with multiple scenarios."""
        content = """## Requirements

### Requirement: Data Validation
The system SHALL validate all input data.

#### Scenario: Valid Input
- **GIVEN** valid input data
- **WHEN** validation runs
- **THEN** data should be accepted

#### Scenario: Invalid Input
- **GIVEN** invalid input data
- **WHEN** validation runs
- **THEN** appropriate error should be returned

#### Scenario: Missing Input
- **GIVEN** missing required fields
- **WHEN** validation runs
- **THEN** validation error should be raised"""
        
        result = parser.parse_spec(content)
        
        assert len(result["requirements"]) == 1
        req = result["requirements"][0]
        assert req["title"] == "Data Validation"
        assert len(req["scenarios"]) == 3
        
        scenarios = req["scenarios"]
        assert scenarios[0]["title"] == "Valid Input"
        assert scenarios[1]["title"] == "Invalid Input"
        assert scenarios[2]["title"] == "Missing Input"
    
    def test_parse_nested_headers(self, parser):
        """Test parsing content with nested headers."""
        content = """# Main Title

## Section 1

### Subsection 1.1

#### Requirement: Test Requirement
Description here.

##### Scenario: Test Scenario
Scenario details.

## Section 2

### Subsection 2.1"""
        
        result = parser.parse_spec(content)
        
        assert result["title"] == "Main Title"
        assert len(result["requirements"]) == 1
        assert result["requirements"][0]["title"] == "Test Requirement"
    
    def test_extract_json_from_code_block(self, parser):
        """Test extracting JSON from code blocks."""
        content = '''## Configuration

```json
{
  "test": "value",
  "number": 42
}
```'''
        
        json_data = parser._extract_json_config(content)
        
        assert json_data["test"] == "value"
        assert json_data["number"] == 42
    
    def test_extract_json_with_no_code_block(self, parser):
        """Test extracting JSON when no code block exists."""
        content = "## Configuration\n\nNo JSON here."
        
        json_data = parser._extract_json_config(content)
        
        assert json_data is None