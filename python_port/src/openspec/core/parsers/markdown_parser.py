"""Markdown parser for OpenSpec files."""

import json
import re
from typing import Optional, Dict, Any


class MarkdownParser:
    """Parser for OpenSpec markdown files."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse a markdown file and extract structured data."""
        return parse_markdown_file(content)
    
    @staticmethod
    def extract_json(content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON configuration from markdown content."""
        return extract_json_from_markdown(content)
    
    def parse_proposal(self, content: str) -> Dict[str, Any]:
        """Parse a proposal markdown file."""
        result = parse_markdown_file(content)
        sections = result.get("sections", {})
        
        return {
            "title": self._extract_title(content),
            "why": sections.get("why", ""),
            "what_changes": sections.get("what changes", ""),
            "configuration": result.get("json"),
            "sections": sections,
            "raw_content": content
        }
    
    def parse_spec(self, content: str) -> Dict[str, Any]:
        """Parse a specification markdown file."""
        result = parse_markdown_file(content)
        sections = result.get("sections", {})
        
        return {
            "title": self._extract_title(content),
            "purpose": sections.get("purpose", ""),
            "requirements": sections.get("requirements", ""),
            "configuration": result.get("json"),
            "sections": sections,
            "raw_content": content
        }
    
    def parse_change_spec(self, content: str) -> Dict[str, Any]:
        """Parse a change specification markdown file."""
        result = parse_markdown_file(content)
        sections = result.get("sections", {})
        
        return {
            "title": self._extract_title(content),
            "deltas": sections.get("deltas", ""),
            "configuration": result.get("json"),
            "sections": sections,
            "raw_content": content
        }
    
    def _extract_json_config(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON configuration from markdown content."""
        return extract_json_from_markdown(content)
    
    def _extract_title(self, content: str) -> str:
        """Extract the title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return ""


def parse_markdown_file(content: str) -> Dict[str, Any]:
    """Parse a markdown file and extract structured data."""
    
    # Extract JSON block
    json_data = extract_json_from_markdown(content)
    
    # Extract other markdown sections
    sections = _extract_markdown_sections(content)
    
    return {
        "json": json_data,
        "sections": sections,
        "raw_content": content
    }


def extract_json_from_markdown(content: str) -> Optional[Dict[str, Any]]:
    """Extract JSON configuration from markdown content."""
    
    # Look for JSON code blocks
    json_pattern = r'```json\s*\n(.*?)\n```'
    matches = re.findall(json_pattern, content, re.DOTALL)
    
    if matches:
        try:
            # Use the last JSON block found
            json_str = matches[-1].strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    
    return None


def _extract_markdown_sections(content: str) -> Dict[str, str]:
    """Extract sections from markdown content."""
    
    sections = {}
    
    # Split by headers
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        # Check for headers
        if line.startswith('#'):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = line.strip('#').strip().lower()
            current_content = []
        else:
            if current_section:
                current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections