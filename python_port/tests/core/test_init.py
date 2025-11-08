"""Tests for InitCommand - ported from test/core/init.test.ts"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch

from openspec.cli.commands.init import InitCommand


class TestInitCommand:
    """Test cases for InitCommand."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def init_command(self):
        """Create an InitCommand instance."""
        return InitCommand()
    
    def directory_exists(self, path: Path) -> bool:
        """Check if directory exists."""
        return path.exists() and path.is_dir()
    
    def file_exists(self, path: Path) -> bool:
        """Check if file exists."""
        return path.exists() and path.is_file()
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_create_openspec_directory_structure(self, mock_prompt, temp_dir, init_command):
        """Test creation of OpenSpec directory structure."""
        mock_prompt.return_value = ['claude']
        
        init_command.execute(str(temp_dir))
        
        openspec_path = temp_dir / "openspec"
        assert self.directory_exists(openspec_path)
        assert self.directory_exists(openspec_path / "specs")
        assert self.directory_exists(openspec_path / "changes")
        assert self.directory_exists(openspec_path / "changes" / "archive")
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_create_agents_md_and_project_md(self, mock_prompt, temp_dir, init_command):
        """Test creation of AGENTS.md and project.md files."""
        mock_prompt.return_value = ['claude']
        
        init_command.execute(str(temp_dir))
        
        openspec_path = temp_dir / "openspec"
        agents_path = openspec_path / "AGENTS.md"
        project_path = openspec_path / "project.md"
        
        assert self.file_exists(agents_path)
        assert self.file_exists(project_path)
        
        agents_content = agents_path.read_text()
        assert "OpenSpec Instructions" in agents_content
        
        project_content = project_path.read_text()
        assert "Project Context" in project_content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_create_claude_md_when_claude_code_is_selected(self, mock_prompt, temp_dir, init_command):
        """Test creation of CLAUDE.md when Claude Code is selected."""
        mock_prompt.return_value = ['claude']
        
        init_command.execute(str(temp_dir))
        
        claude_path = temp_dir / "CLAUDE.md"
        assert self.file_exists(claude_path)
        
        content = claude_path.read_text()
        assert "<!-- OPENSPEC:START -->" in content
        assert "@/openspec/AGENTS.md" in content
        assert "openspec update" in content
        assert "<!-- OPENSPEC:END -->" in content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_update_existing_claude_md_with_markers(self, mock_prompt, temp_dir, init_command):
        """Test updating existing CLAUDE.md with markers."""
        mock_prompt.return_value = ['claude']
        
        claude_path = temp_dir / "CLAUDE.md"
        existing_content = "# My Project Instructions\nCustom instructions here"
        claude_path.write_text(existing_content)
        
        init_command.execute(str(temp_dir))
        
        updated_content = claude_path.read_text()
        assert "<!-- OPENSPEC:START -->" in updated_content
        assert "@/openspec/AGENTS.md" in updated_content
        assert "openspec update" in updated_content
        assert "<!-- OPENSPEC:END -->" in updated_content
        assert "Custom instructions here" in updated_content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_create_cline_md_when_cline_is_selected(self, mock_prompt, temp_dir, init_command):
        """Test creation of CLINE.md when Cline is selected."""
        mock_prompt.return_value = ['cline']
        
        init_command.execute(str(temp_dir))
        
        cline_path = temp_dir / "CLINE.md"
        assert self.file_exists(cline_path)
        
        content = cline_path.read_text()
        assert "<!-- OPENSPEC:START -->" in content
        assert "@/openspec/AGENTS.md" in content
        assert "openspec update" in content
        assert "<!-- OPENSPEC:END -->" in content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_update_existing_cline_md_with_markers(self, mock_prompt, temp_dir, init_command):
        """Test updating existing CLINE.md with markers."""
        mock_prompt.return_value = ['cline']
        
        cline_path = temp_dir / "CLINE.md"
        existing_content = "# My Cline Rules\nCustom Cline instructions here"
        cline_path.write_text(existing_content)
        
        init_command.execute(str(temp_dir))
        
        updated_content = cline_path.read_text()
        assert "<!-- OPENSPEC:START -->" in updated_content
        assert "@/openspec/AGENTS.md" in updated_content
        assert "openspec update" in updated_content
        assert "<!-- OPENSPEC:END -->" in updated_content
        assert "Custom Cline instructions here" in updated_content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_create_windsurf_workflows_when_windsurf_is_selected(self, mock_prompt, temp_dir, init_command):
        """Test creation of Windsurf workflows when Windsurf is selected."""
        mock_prompt.return_value = ['windsurf']
        
        init_command.execute(str(temp_dir))
        
        ws_proposal = temp_dir / ".windsurf" / "workflows" / "openspec-proposal.md"
        ws_apply = temp_dir / ".windsurf" / "workflows" / "openspec-apply.md"
        ws_archive = temp_dir / ".windsurf" / "workflows" / "openspec-archive.md"
        
        assert self.file_exists(ws_proposal)
        assert self.file_exists(ws_apply)
        assert self.file_exists(ws_archive)
        
        proposal_content = ws_proposal.read_text()
        assert "---" in proposal_content
        assert "description: Scaffold a new OpenSpec change and validate strictly." in proposal_content
        assert "auto_execution_mode: 3" in proposal_content
        assert "<!-- OPENSPEC:START -->" in proposal_content
        assert "**Guardrails**" in proposal_content
        
        apply_content = ws_apply.read_text()
        assert "---" in apply_content
        assert "description: Implement an approved OpenSpec change and keep tasks in sync." in apply_content
        assert "auto_execution_mode: 3" in apply_content
        assert "<!-- OPENSPEC:START -->" in apply_content
        assert "Work through tasks sequentially" in apply_content
        
        archive_content = ws_archive.read_text()
        assert "---" in archive_content
        assert "description: Archive a deployed OpenSpec change and update specs." in archive_content
        assert "auto_execution_mode: 3" in archive_content
        assert "<!-- OPENSPEC:START -->" in archive_content
        assert "Run `openspec archive <id> --yes`" in archive_content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_always_create_agents_md_in_project_root(self, mock_prompt, temp_dir, init_command):
        """Test that AGENTS.md is always created in project root."""
        mock_prompt.return_value = []  # No AI tools selected
        
        init_command.execute(str(temp_dir))
        
        root_agents_path = temp_dir / "AGENTS.md"
        assert self.file_exists(root_agents_path)
        
        content = root_agents_path.read_text()
        assert "<!-- OPENSPEC:START -->" in content
        assert "@/openspec/AGENTS.md" in content
        assert "openspec update" in content
        assert "<!-- OPENSPEC:END -->" in content
        
        claude_path = temp_dir / "CLAUDE.md"
        assert not self.file_exists(claude_path)
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_create_claude_slash_command_files_with_templates(self, mock_prompt, temp_dir, init_command):
        """Test creation of Claude slash command files with templates."""
        mock_prompt.return_value = ['claude']
        
        init_command.execute(str(temp_dir))
        
        claude_proposal = temp_dir / ".claude" / "commands" / "openspec" / "proposal.md"
        claude_apply = temp_dir / ".claude" / "commands" / "openspec" / "apply.md"
        claude_archive = temp_dir / ".claude" / "commands" / "openspec" / "archive.md"
        
        assert self.file_exists(claude_proposal)
        assert self.file_exists(claude_apply)
        assert self.file_exists(claude_archive)
        
        proposal_content = claude_proposal.read_text()
        assert "name: OpenSpec: Proposal" in proposal_content
        assert "<!-- OPENSPEC:START -->" in proposal_content
        assert "**Guardrails**" in proposal_content
        
        apply_content = claude_apply.read_text()
        assert "name: OpenSpec: Apply" in apply_content
        assert "Work through tasks sequentially" in apply_content
        
        archive_content = claude_archive.read_text()
        assert "name: OpenSpec: Archive" in archive_content
        assert "openspec archive <id>" in archive_content
        assert "`--skip-specs` only for tooling-only work" in archive_content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_create_cursor_slash_command_files_with_templates(self, mock_prompt, temp_dir, init_command):
        """Test creation of Cursor slash command files with templates."""
        mock_prompt.return_value = ['cursor']
        
        init_command.execute(str(temp_dir))
        
        cursor_proposal = temp_dir / ".cursor" / "commands" / "openspec-proposal.md"
        cursor_apply = temp_dir / ".cursor" / "commands" / "openspec-apply.md"
        cursor_archive = temp_dir / ".cursor" / "commands" / "openspec-archive.md"
        
        assert self.file_exists(cursor_proposal)
        assert self.file_exists(cursor_apply)
        assert self.file_exists(cursor_archive)
        
        proposal_content = cursor_proposal.read_text()
        assert "name: /openspec-proposal" in proposal_content
        assert "<!-- OPENSPEC:END -->" in proposal_content
        
        apply_content = cursor_apply.read_text()
        assert "id: openspec-apply" in apply_content
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_support_multiple_ai_tools(self, mock_prompt, temp_dir, init_command):
        """Test support for multiple AI tools."""
        mock_prompt.return_value = ['claude', 'cursor', 'cline']
        
        init_command.execute(str(temp_dir))
        
        # Check that all tools are configured
        assert self.file_exists(temp_dir / "CLAUDE.md")
        assert self.file_exists(temp_dir / "CLINE.md")
        assert self.file_exists(temp_dir / ".cursor" / "commands" / "openspec-proposal.md")
        assert self.file_exists(temp_dir / ".claude" / "commands" / "openspec" / "proposal.md")
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_handle_empty_directory(self, mock_prompt, temp_dir, init_command):
        """Test handling of empty directory."""
        mock_prompt.return_value = ['claude']
        
        init_command.execute(str(temp_dir))
        
        # Verify basic structure is created
        assert self.directory_exists(temp_dir / "openspec")
        assert self.file_exists(temp_dir / "AGENTS.md")
        assert self.file_exists(temp_dir / "CLAUDE.md")
    
    @patch('openspec.cli.commands.init.prompt_for_ai_tools')
    def test_should_preserve_existing_content_when_updating_files(self, mock_prompt, temp_dir, init_command):
        """Test preservation of existing content when updating files."""
        mock_prompt.return_value = ['claude']
        
        # Create existing files with content
        agents_path = temp_dir / "AGENTS.md"
        existing_agents = "# My Custom Instructions\nThis is my existing content."
        agents_path.write_text(existing_agents)
        
        init_command.execute(str(temp_dir))
        
        # Verify existing content is preserved
        updated_content = agents_path.read_text()
        assert "My Custom Instructions" in updated_content
        assert "This is my existing content." in updated_content
        assert "<!-- OPENSPEC:START -->" in updated_content
        assert "<!-- OPENSPEC:END -->" in updated_content