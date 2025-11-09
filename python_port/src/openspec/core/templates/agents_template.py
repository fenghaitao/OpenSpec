"""AGENTS.md template for OpenSpec."""

from typing import List
from ..config import AIToolOption

def create_agents_openspec_template() -> str:
    """Create the openspec/AGENTS.md template - reads from canonical TypeScript template."""
    
    # Read the canonical template from the TypeScript implementation
    try:
        from pathlib import Path
        import re
        
        # Path to TypeScript agents template - find it relative to this Python file
        # Navigate from python_port/src/openspec/core/templates/agents_template.py to main OpenSpec src/core/templates/agents-template.ts
        current_file = Path(__file__)
        python_port_root = current_file.parent.parent.parent.parent.parent  # Go up to python_port root
        openspec_root = python_port_root.parent  # Go up one more to main OpenSpec directory
        ts_template_path = openspec_root / "src" / "core" / "templates" / "agents-template.ts"
        
        # Read and extract the TypeScript template
        ts_content = ts_template_path.read_text()
        
        # Extract the agentsTemplate content - use non-greedy match and proper lookahead
        pattern = r'export const agentsTemplate = `(.*?)`(?=;\s*$)'
        match = re.search(pattern, ts_content, re.DOTALL | re.MULTILINE)
        
        if match:
            content = match.group(1).strip()
            # Unescape backticks from TypeScript template literals
            content = content.replace('\\`', '`')
            # Replace any TypeScript CLI commands with Python equivalents
            # content = content.replace('`openspec ', '`openspec-py ')
            # content = content.replace(' openspec ', ' openspec-py ')
            return content
            
    except Exception as e:
        print(f"Warning: Could not read TypeScript agents template ({e}). Using fallback template.")
    
    # Fallback to embedded template that matches TypeScript content
    return """# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)  
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

## Overview

This project uses OpenSpec for spec-driven development. Before making significant changes, always:

1. Check for existing change proposals in `openspec/changes/`
2. Review relevant specs in `openspec/specs/`
3. Create or update change proposals for new features

## Creating Change Proposals

Use the OpenSpec CLI to create change proposals:

```bash
openspec change create my-feature-name
```

This creates a structured proposal with:
- **Why**: Business justification (50-2000 chars)
- **What Changes**: Description of changes
- **Deltas**: Specific spec modifications

## Validation

Always validate your changes:

```bash
openspec validate
```

## Workflow

1. **Plan**: Create change proposal
2. **Specify**: Define or update specs
3. **Implement**: Write code following specs
4. **Validate**: Check all specs are valid
5. **Archive**: Move completed changes to archive

## Change Proposal Format

```json
{
  "name": "descriptive-change-name",
  "why": "Business justification for the change",
  "whatChanges": "Description of what will change",
  "deltas": [
    {
      "spec": "spec-name",
      "operation": "ADDED|MODIFIED|REMOVED|RENAMED",
      "description": "What changes in this spec",
      "requirements": [
        {
          "id": "req-1",
          "description": "Requirement description"
        }
      ]
    }
  ]
}
```

## Best Practices

- Keep change proposals focused and atomic
- Write clear requirement descriptions
- Validate before committing
- Archive completed changes
- Reference specs in code comments
"""