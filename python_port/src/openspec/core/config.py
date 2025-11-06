"""Configuration constants and types for OpenSpec."""

from typing import List, Optional
from dataclasses import dataclass

OPENSPEC_DIR_NAME = "openspec"

OPENSPEC_MARKERS = {
    "start": "<!-- OPENSPEC:START -->",
    "end": "<!-- OPENSPEC:END -->"
}


@dataclass
class OpenSpecConfig:
    """Configuration for OpenSpec projects."""
    ai_tools: List[str]


@dataclass
class AIToolOption:
    """Configuration option for AI tools."""
    name: str
    value: str
    available: bool
    success_label: Optional[str] = None
    config_file_name: Optional[str] = None


AI_TOOLS: List[AIToolOption] = [
    AIToolOption("Auggie (Augment CLI)", "auggie", True, "Auggie", None),
    AIToolOption("Claude Code", "claude", True, "Claude Code", "CLAUDE.md"),
    AIToolOption("Cline", "cline", True, "Cline", "CLINE.md"),
    AIToolOption("CodeBuddy Code (CLI)", "codebuddy", True, "CodeBuddy Code", None),
    AIToolOption("CoStrict", "costrict", True, "CoStrict", None),
    AIToolOption("Crush", "crush", True, "Crush", None),
    AIToolOption("Cursor", "cursor", True, "Cursor", None),
    AIToolOption("Factory Droid", "factory", True, "Factory Droid", None),
    AIToolOption("OpenCode", "opencode", True, "OpenCode", None),
    AIToolOption("Kilo Code", "kilocode", True, "Kilo Code", None),
    AIToolOption("Qoder (CLI)", "qoder", True, "Qoder", None),
    AIToolOption("Windsurf", "windsurf", True, "Windsurf", None),
    AIToolOption("Codex", "codex", True, "Codex", None),
    AIToolOption("GitHub Copilot", "github-copilot", True, "GitHub Copilot", None),
    AIToolOption("Amazon Q Developer", "amazon-q", True, "Amazon Q Developer", None),
    AIToolOption("Qwen Code", "qwen", True, "Qwen Code", None),
    AIToolOption("Universal AGENTS.md", "agents", True, "Universal AGENTS.md", "AGENTS.md"),
]