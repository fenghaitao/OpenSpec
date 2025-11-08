"""Tests for OpenSpec parsers (ported from TypeScript)."""

import pytest
from openspec.core.parsers.markdown_parser import parse_markdown_file, extract_json_from_markdown


class TestMarkdownParser:
    """Test markdown parsing functionality."""

    def test_parse_basic_sections(self):
        """Test parsing basic markdown sections."""
        content = """# Main Title

Some intro text.

## Section 1

Content for section 1.

## Section 2

Content for section 2.

### Subsection 2.1

Nested content.
"""
        
        result = parse_markdown_file(content)
        sections = result["sections"]
        
        # Should find the main sections
        assert "section 1" in sections  # Note: Python implementation lowercases section names
        assert "section 2" in sections

    def test_parse_requirements_section(self):
        """Test parsing requirements sections with scenarios."""
        content = """# Test Spec

## Purpose
This is a test specification.

## Requirements

### Requirement: User SHALL be authenticated
The system SHALL require user authentication for all operations.

#### Scenario: Valid login
- **GIVEN** a registered user with valid credentials
- **WHEN** the user attempts to log in
- **THEN** access is granted

#### Scenario: Invalid login  
- **GIVEN** a user with invalid credentials
- **WHEN** the user attempts to log in
- **THEN** access is denied
"""
        
        sections = parse_markdown_sections(content)
        
        # Find requirements section
        req_section = next((s for s in sections if s.title == "Requirements"), None)
        assert req_section is not None
        
        # Should contain requirement content
        assert "User SHALL be authenticated" in req_section.content
        assert "Valid login" in req_section.content
        assert "Invalid login" in req_section.content

    def test_parse_change_proposal_format(self):
        """Test parsing change proposal format."""
        content = """# Change Proposal

## Why
This change is needed because the current system lacks proper error handling.

## What Changes
- **api:** Add error handling middleware
- **frontend:** Display user-friendly error messages
- **docs:** Update API documentation
"""
        
        sections = parse_markdown_sections(content)
        
        why_section = next((s for s in sections if s.title == "Why"), None)
        what_section = next((s for s in sections if s.title == "What Changes"), None)
        
        assert why_section is not None
        assert what_section is not None
        assert "error handling" in why_section.content
        assert "api:" in what_section.content

    def test_parse_crlf_line_endings(self):
        """Test parsing content with CRLF line endings."""
        content = "# Title\r\n\r\n## Section\r\n\r\nContent with CRLF endings.\r\n"
        
        sections = parse_markdown_sections(content)
        
        # Should handle CRLF without issues
        assert len(sections) > 0
        section = next((s for s in sections if s.title == "Section"), None)
        assert section is not None
        assert "CRLF endings" in section.content

    def test_parse_nested_headings(self):
        """Test parsing nested heading structures."""
        content = """# Main

## Level 2

### Level 3

#### Level 4

Content at level 4.

### Another Level 3

More content.

## Another Level 2

Final content.
"""
        
        sections = parse_markdown_sections(content)
        
        # Should capture different heading levels
        titles = [section.title for section in sections]
        assert "Level 2" in titles
        assert "Level 3" in titles
        assert "Another Level 2" in titles

    def test_parse_empty_content(self):
        """Test parsing empty or minimal content."""
        content = ""
        sections = parse_markdown_sections(content)
        assert len(sections) == 0
        
        content = "# Only Title"
        sections = parse_markdown_sections(content)
        # Should handle gracefully

    def test_parse_code_blocks_in_sections(self):
        """Test parsing sections that contain code blocks."""
        content = """# Configuration

## JSON Format

Use the following JSON format:

```json
{
  "name": "example",
  "value": 42
}
```

## Code Example

```python
def example():
    return "hello"
```
"""
        
        sections = parse_markdown_sections(content)
        
        json_section = next((s for s in sections if s.title == "JSON Format"), None)
        code_section = next((s for s in sections if s.title == "Code Example"), None)
        
        assert json_section is not None
        assert code_section is not None
        assert "```json" in json_section.content
        assert "```python" in code_section.content

    def test_parse_lists_and_formatting(self):
        """Test parsing sections with various markdown formatting."""
        content = """# Formatting Test

## Lists

- Item 1
- Item 2
  - Nested item
- Item 3

1. Numbered item 1
2. Numbered item 2

## Text Formatting

**Bold text** and *italic text* and `code spans`.

> Quote block
> with multiple lines

## Tables

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
        
        sections = parse_markdown_sections(content)
        
        lists_section = next((s for s in sections if s.title == "Lists"), None)
        formatting_section = next((s for s in sections if s.title == "Text Formatting"), None)
        tables_section = next((s for s in sections if s.title == "Tables"), None)
        
        assert lists_section is not None
        assert formatting_section is not None  
        assert tables_section is not None
        
        assert "- Item 1" in lists_section.content
        assert "**Bold text**" in formatting_section.content
        assert "| Column 1" in tables_section.content