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
        sections = self._parse_sections_advanced(content)
        
        # Parse requirements from the entire content (not just requirements section)
        requirements = self._parse_requirements(content)
        
        return {
            "title": self._extract_title(content),
            "purpose": sections.get("purpose", ""),
            "requirements": requirements,
            "configuration": result.get("json"),
            "sections": sections,
            "raw_content": content
        }
    
    def parse_change_spec(self, content: str) -> Dict[str, Any]:
        """Parse a change specification markdown file."""
        result = parse_markdown_file(content)
        sections = self._parse_sections_advanced(content)
        
        # Parse each operation type
        added_requirements = self._parse_requirements(sections.get("added requirements", ""))
        modified_requirements = self._parse_requirements(sections.get("modified requirements", ""))
        removed_requirements = self._parse_requirements(sections.get("removed requirements", ""))
        
        return {
            "title": self._extract_title(content),
            "added_requirements": added_requirements,
            "modified_requirements": modified_requirements,
            "removed_requirements": removed_requirements,
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
    
    def _parse_sections_advanced(self, content: str) -> Dict[str, str]:
        """Parse sections with support for nested headers."""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for headers (## level and higher)
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line[3:].strip().lower()
                current_content = []
            elif line.startswith('#### Requirement:'):
                # This is a nested requirement, include it in current section
                if current_section:
                    current_content.append(line)
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _parse_requirements(self, requirements_text: str) -> list:
        """Parse requirements section into structured requirements."""
        requirements = []
        lines = requirements_text.split('\n')
        current_requirement = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('### Requirement:') or line.startswith('#### Requirement:'):
                # Save previous requirement
                if current_requirement:
                    requirements.append(current_requirement)
                
                # Start new requirement
                title_start = 16 if line.startswith('### Requirement:') else 17
                current_requirement = {
                    "title": line[title_start:].strip(),
                    "description": "",
                    "scenarios": [],
                    "change_description": "",
                    "removal_reason": ""
                }
            elif line.startswith('#### Scenario:') or line.startswith('##### Scenario:'):
                if current_requirement:
                    title_start = 14 if line.startswith('#### Scenario:') else 15
                    current_scenario = {
                        "title": line[title_start:].strip(),
                        "steps": []
                    }
                    current_requirement["scenarios"].append(current_scenario)
            elif line.startswith('**CHANGE:**') and current_requirement:
                # Change description for modified requirements
                change_desc = line[11:].strip()
                current_requirement["change_description"] = change_desc
            elif line.startswith('**REASON:**') and current_requirement:
                # Removal reason for removed requirements
                reason = line[11:].strip()
                current_requirement["removal_reason"] = reason
            elif line.startswith('- **') and current_requirement:
                # Scenario step
                if current_requirement["scenarios"]:
                    current_requirement["scenarios"][-1]["steps"].append(line)
            elif line and current_requirement and not line.startswith('#'):
                # Add to description
                if current_requirement["description"]:
                    current_requirement["description"] += " "
                current_requirement["description"] += line
        
        # Save last requirement
        if current_requirement:
            requirements.append(current_requirement)
        
        return requirements
    
    def _parse_deltas(self, deltas_text: str) -> list:
        """Parse deltas section into structured deltas."""
        deltas = []
        lines = deltas_text.split('\n')
        current_delta = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('### ') and ('Added:' in line or 'Modified:' in line or 'Removed:' in line):
                # Save previous delta
                if current_delta:
                    deltas.append(current_delta)
                
                # Parse delta header
                parts = line[4:].split(':')
                operation = parts[0].strip().lower()
                spec_path = parts[1].strip() if len(parts) > 1 else ""
                
                current_delta = {
                    "operation": operation,
                    "spec_path": spec_path,
                    "changes": []
                }
            elif line.startswith('- ') and current_delta:
                # Add change item
                current_delta["changes"].append(line[2:].strip())
            elif line and current_delta and not line.startswith('#'):
                # Add to description
                current_delta["changes"].append(line)
        
        # Save last delta
        if current_delta:
            deltas.append(current_delta)
        
        return deltas


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