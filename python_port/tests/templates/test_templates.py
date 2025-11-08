"""Tests for template system."""

import pytest
from openspec.core.templates.manager import TemplateManager
from openspec.core.templates.slash_commands import get_slash_command_body, ALL_COMMANDS


def test_claude_template():
    """Test Claude template generation."""
    template = TemplateManager.get_claude_template()
    
    assert "OpenSpec Instructions" in template
    assert "Always open `@/openspec/AGENTS.md`" in template
    assert "proposals" in template


def test_cline_template():
    """Test Cline template generation."""
    template = TemplateManager.get_cline_template()
    
    assert "OpenSpec Instructions" in template
    assert "Always open `@/openspec/AGENTS.md`" in template


def test_agents_standard_template():
    """Test universal AGENTS.md template."""
    template = TemplateManager.get_agents_standard_template()
    
    assert "OpenSpec Instructions" in template
    assert "Always open `@/openspec/AGENTS.md`" in template


def test_slash_command_bodies():
    """Test slash command body generation."""
    for command_id in ALL_COMMANDS:
        body = TemplateManager.get_slash_command_body(command_id)
        assert len(body) > 0
        assert "**Guardrails**" in body or "**Steps**" in body
    
    # Test specific commands
    proposal_body = get_slash_command_body("proposal")
    assert "Scaffold a new OpenSpec change" in proposal_body
    assert "openspec validate <id> --strict" in proposal_body
    
    apply_body = get_slash_command_body("apply")
    assert "Implement an approved OpenSpec change" in apply_body
    assert "tasks.md" in apply_body
    
    archive_body = get_slash_command_body("archive")
    assert "Archive a deployed OpenSpec change" in archive_body
    assert "openspec archive <id> --yes" in archive_body


def test_slash_command_invalid_id():
    """Test error handling for invalid slash command ID."""
    with pytest.raises(ValueError, match="Unknown slash command ID"):
        get_slash_command_body("invalid-command")


def test_project_template():
    """Test project template generation."""
    template = TemplateManager.get_project_template()
    
    assert len(template) > 0
    # Project template should be basic for now
    assert isinstance(template, str)