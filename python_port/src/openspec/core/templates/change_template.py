"""Change template for OpenSpec."""


def create_change_template(change_name: str) -> str:
    """Create a change proposal template."""
    
    return f"""# {change_name}

<!-- Describe the purpose and context of this change -->

## Implementation Notes

<!-- Add implementation notes, considerations, and references -->

## Configuration

```json
{{
  "name": "{change_name}",
  "why": "Why is this change needed? (Business justification - 50-2000 characters)",
  "whatChanges": "What will change in the system?",
  "deltas": [
    {{
      "spec": "spec-name",
      "operation": "ADDED",
      "description": "Description of what changes in this spec",
      "requirements": [
        {{
          "id": "req-1",
          "description": "Specific requirement description"
        }}
      ]
    }}
  ]
}}
```

## Tasks

- [ ] Define requirements
- [ ] Update or create specs
- [ ] Implement changes
- [ ] Test implementation
- [ ] Validate specs
- [ ] Archive change
"""


def create_spec_template(spec_name: str) -> str:
    """Create a spec template."""
    
    return f"""# {spec_name}

<!-- Describe the purpose and scope of this specification -->

## Overview

<!-- High-level description of what this spec covers -->

## Configuration

```json
{{
  "name": "{spec_name}",
  "purpose": "Purpose and scope of this specification",
  "requirements": [
    {{
      "id": "req-1",
      "description": "Specific requirement description",
      "priority": "high"
    }}
  ]
}}
```

## Implementation Details

<!-- Detailed implementation guidelines -->

## Examples

<!-- Usage examples and code samples -->

## Testing

<!-- Testing guidelines and requirements -->
"""