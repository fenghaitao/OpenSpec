# OpenSpec Python Port

This is a Python port of the OpenSpec CLI tool - an AI-native system for spec-driven development.

## Original Project

This is ported from the TypeScript/JavaScript version at: https://github.com/Fission-AI/OpenSpec

## Installation

### Development Setup (Recommended)

Run the setup script to configure OpenSpec for development:

```bash
./setup-dev-local.sh
source ~/.bashrc  # or ~/.zshrc
```

This will:
- Add an `openspec` function to your shell config
- Allow you to run `openspec` from any directory
- Use the development version without installing

**Prerequisites:**
- Install `uv` first: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Verify Installation

```bash
openspec --version
openspec --help
```

## Usage

```bash
openspec --help
openspec init
openspec list
```

## Development

After running the setup script, you can develop and test:

```bash
# Run tests
pytest

# The openspec command automatically uses your development code
openspec --help
```

## Features

- Initialize OpenSpec projects with AI tool configurations
- Create and manage change proposals
- Validate specifications
- Archive completed changes
- Support for multiple AI tools (Claude, Cursor, Cline, etc.)