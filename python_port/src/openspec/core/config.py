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


AI_TOOLS: List[AIToolOption] = [
    AIToolOption("Auggie (Augment CLI)", "auggie", True, "Auggie"),
    AIToolOption("Claude Code", "claude", True, "Claude Code"),
    AIToolOption("Cline", "cline", True, "Cline"),
    AIToolOption("CodeBuddy Code (CLI)", "codebuddy", True, "CodeBuddy Code"),
    AIToolOption("CoStrict", "costrict", True, "CoStrict"),
    AIToolOption("Crush", "crush", True, "Crush"),
    AIToolOption("Cursor", "cursor", True, "Cursor"),
    AIToolOption("Factory Droid", "factory", True, "Factory Droid"),
    AIToolOption("OpenCode", "opencode", True, "OpenCode"),
    AIToolOption("Kilo Code", "kilocode", True, "Kilo Code"),
    AIToolOption("Qoder (CLI)", "qoder", True, "Qoder"),
    AIToolOption("Windsurf", "windsurf", True, "Windsurf"),
    AIToolOption("Codex", "codex", True, "Codex"),
    AIToolOption("GitHub Copilot", "github-copilot", True, "GitHub Copilot"),
    AIToolOption("Amazon Q Developer", "amazon-q", True, "Amazon Q Developer"),
    AIToolOption("Qwen Code", "qwen", True, "Qwen Code"),
    AIToolOption("AGENTS.md (works with Amp, VS Code, …)", "agents", False, "your AGENTS.md-compatible assistant"),
]