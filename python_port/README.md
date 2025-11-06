# OpenSpec Python Port

This is a Python port of the OpenSpec CLI tool - an AI-native system for spec-driven development.

## Original Project

This is ported from the TypeScript/JavaScript version at: https://github.com/Fission-AI/OpenSpec

## Installation

```bash
pip install -e .
```

## Usage

```bash
openspec --help
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Features

- Initialize OpenSpec projects with AI tool configurations
- Create and manage change proposals
- Validate specifications
- Archive completed changes
- Support for multiple AI tools (Claude, Cursor, Cline, etc.)