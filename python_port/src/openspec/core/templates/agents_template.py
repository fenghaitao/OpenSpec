"""AGENTS.md template for OpenSpec."""

from typing import List
from ..config import AIToolOption


def create_agents_template(selected_tools: List["AIToolOption"]) -> str:
    """Create AGENTS.md template with selected AI tools."""
    
    template = """# AI Agent Instructions

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

<!-- OPENSPEC:START -->
# OpenSpec Instructions

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

<!-- OPENSPEC:END -->

## Project-Specific Guidelines

<!-- Add your project-specific guidelines here -->

"""
    
    if selected_tools:
        template += f"""
## Configured AI Tools

This project is configured for the following AI tools:
"""
        
        for tool in selected_tools:
            template += f"- {tool.name}\n"
    
    return template


def create_agents_openspec_template() -> str:
    """Create the openspec/AGENTS.md template."""
    
    return """# OpenSpec Agent Instructions

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