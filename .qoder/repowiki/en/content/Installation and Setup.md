# Installation and Setup

<cite>
**Referenced Files in This Document**   
- [package.json](file://package.json)
- [bin/openspec.js](file://bin/openspec.js)
- [src/cli/index.ts](file://src/cli/index.ts)
- [src/core/init.ts](file://src/core/init.ts)
- [src/core/config.ts](file://src/core/config.ts)
- [src/core/templates/index.ts](file://src/core/templates/index.ts)
- [src/core/configurators/registry.ts](file://src/core/configurators/registry.ts)
- [src/core/configurators/slash/registry.ts](file://src/core/configurators/slash/registry.ts)
- [README.md](file://README.md)
- [openspec/AGENTS.md](file://openspec/AGENTS.md)
- [python_port/README.md](file://python_port/README.md)
- [python_port/pyproject.toml](file://python_port/pyproject.toml)
- [src/utils/file-system.ts](file://src/utils/file-system.ts)
</cite>

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Global Installation](#global-installation)
3. [Initialization Workflow](#initialization-workflow)
4. [Directory Structure Creation](#directory-structure-creation)
5. [AI Tool Configuration](#ai-tool-configuration)
6. [Project Context Population](#project-context-population)
7. [Python Port Alternative](#python-port-alternative)
8. [Troubleshooting](#troubleshooting)
9. [Post-Setup Verification](#post-setup-verification)

## Prerequisites

Before installing OpenSpec, ensure your system meets the following requirements:

- **Node.js version ≥ 20.19.0**: The OpenSpec CLI requires a modern version of Node.js to function properly. Verify your Node.js version by running `node --version` in your terminal. If you need to update Node.js, download the latest version from the official Node.js website or use a version manager like nvm.

OpenSpec supports multiple package managers including npm, pnpm, and yarn. The installation examples in this documentation use npm, but you can substitute your preferred package manager as needed.

**Section sources**
- [package.json](file://package.json#L55-L57)
- [README.md](file://README.md#L123-L124)

## Global Installation

To install OpenSpec globally on your system, use the npm package manager with the following command:

```bash
npm install -g @fission-ai/openspec@latest
```

This command installs the OpenSpec CLI tool globally, making the `openspec` command available from any directory in your terminal. The installation includes all necessary dependencies and creates a binary executable that can be invoked from anywhere in your system.

After installation, verify that OpenSpec was installed correctly by checking its version:

```bash
openspec --version
```

This command should output the current version of OpenSpec (e.g., 0.14.0), confirming that the installation was successful and the command is properly registered in your system's PATH.

**Section sources**
- [package.json](file://package.json#L29-L31)
- [bin/openspec.js](file://bin/openspec.js)
- [README.md](file://README.md#L131-L137)

## Initialization Workflow

Once OpenSpec is installed, initialize it in your project directory by running:

```bash
openspec init
```

This command triggers an interactive initialization workflow that guides you through setting up OpenSpec in your project. The process begins with a banner display and step-by-step prompts that help configure your development environment for AI-assisted coding.

The initialization is designed to be user-friendly and informative, providing clear instructions at each step. If OpenSpec detects an existing configuration in your project, it will switch to "extend mode" and offer to refresh or add new integrations rather than creating a duplicate setup.

During initialization, you'll be prompted to select which AI coding assistants you use from a list of supported tools. The selection process uses an interactive interface with keyboard navigation (↑/↓ to move, Space to toggle, Enter to confirm selections).

**Section sources**
- [src/cli/index.ts](file://src/cli/index.ts#L40-L74)
- [src/core/init.ts](file://src/core/init.ts#L376-L460)
- [README.md](file://README.md#L148-L149)

## Directory Structure Creation

When you run `openspec init`, the system automatically creates a standardized directory structure in your project root:

```text
openspec/
├── specs/
├── changes/
│   └── archive/
└── AGENTS.md
```

The initialization process creates these directories and essential files:

1. The main `openspec/` directory serves as the root for all specification-related content
2. The `specs/` directory is created to store current specifications that represent the "source of truth" for your project's capabilities
3. The `changes/` directory is created to manage proposed changes, with an `archive/` subdirectory for completed changes
4. Essential configuration files are generated, including templates for specifications and project context

This structure follows OpenSpec's philosophy of separating current truth (`specs/`) from proposed changes (`changes/`), enabling clear tracking of what is currently implemented versus what is being proposed.

**Section sources**
- [src/core/init.ts](file://src/core/init.ts#L708-L719)
- [src/core/templates/index.ts](file://src/core/templates/index.ts#L16-L25)

## AI Tool Configuration

During initialization, OpenSpec prompts you to select AI coding assistants that support native slash commands. The interactive tool selection presents two categories:

- **Natively supported providers**: AI tools that support OpenSpec's custom slash commands (indicated with a ✔ symbol)
- **Other tools**: AI assistants that use the universal AGENTS.md approach for instruction following

When you select tools with native slash command support, OpenSpec automatically configures the appropriate command files in your project. For example:
- Claude Code, Cursor, and GitHub Copilot receive slash command configurations
- Tools like Amp, VS Code, and Gemini CLI use the universal AGENTS.md file

The configuration process generates tool-specific files with OpenSpec markers (`<!-- OPENSPEC:START -->` and `<!-- OPENSPEC:END -->`) that allow OpenSpec to manage and update these files safely without interfering with other content.

After configuration, AI assistants can use slash commands like `/openspec:proposal`, `/openspec:apply`, and `/openspec:archive` to interact with the OpenSpec workflow directly.

**Section sources**
- [src/core/init.ts](file://src/core/init.ts#L763-L785)
- [src/core/config.ts](file://src/core/config.ts#L19-L37)
- [src/core/configurators/registry.ts](file://src/core/configurators/registry.ts)
- [src/core/configurators/slash/registry.ts](file://src/core/configurators/slash/registry.ts)

## Project Context Population

After initialization completes, OpenSpec generates a `openspec/project.md` file that serves as a template for defining your project's context. This file allows you to document important project-specific information that should be consistent across all AI-assisted development activities.

To populate your project context, use the following prompt with your AI assistant:

```text
Please read openspec/project.md and help me fill it out with details about my project, tech stack, and conventions
```

The `project.md` file is designed to capture:
- Technology stack and framework choices
- Coding conventions and style guidelines
- Architectural patterns and design principles
- Project-specific standards and best practices
- Any other contextual information that should inform AI-generated code

This context file becomes part of the shared understanding between human developers and AI assistants, ensuring consistency in implementation approaches across the project.

**Section sources**
- [src/core/templates/index.ts](file://src/core/templates/index.ts#L22-L24)
- [README.md](file://README.md#L167-L171)

## Python Port Alternative

For users who prefer Python, OpenSpec provides a Python port that offers the same functionality through the `uv` and `uvx` tools. This alternative installation method is particularly useful for developers who work primarily in Python environments or want faster installation times.

To use the Python port:

1. First install `uv`, a fast Python package installer and resolver:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Set up the development environment:
```bash
./python_port/setup-dev-local.sh
source ~/.bashrc  # or ~/.zshrc
```

3. Use the `openspec-py` command to access all OpenSpec functionality:
```bash
openspec-py --version
openspec-py init
openspec-py list
```

The Python port maintains feature parity with the Node.js version and supports all the same commands and workflows, providing a native Python experience for OpenSpec users.

**Section sources**
- [python_port/README.md](file://python_port/README.md)
- [python_port/pyproject.toml](file://python_port/pyproject.toml#L5-L7)

## Troubleshooting

### Slash Commands Not Appearing

If slash commands do not appear in your AI coding assistant after initialization, restart the AI tool. Slash commands are typically loaded at startup, so a fresh launch ensures that newly created command files are recognized and available in the interface.

### Permission Errors During Global Installation

If you encounter permission errors when running `npm install -g`, this indicates that npm lacks the necessary permissions to write to the global installation directory. Resolve this issue by:

1. Using a Node.js version manager like nvm, which installs Node.js in your user directory and avoids system-level permission requirements
2. Fixing npm permissions by configuring npm to use a different directory:
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
```
Then add `~/.npm-global/bin` to your PATH environment variable.

### Insufficient Write Permissions

If OpenSpec reports insufficient permissions to write to your project directory during initialization, ensure that:
- You have write permissions to the project directory
- The directory is not read-only
- No file locking mechanisms are preventing writes
- You're not attempting to initialize in a system-protected directory

The initialization process checks write permissions before proceeding and will fail early if it cannot write to the target directory.

**Section sources**
- [src/core/init.ts](file://src/core/init.ts#L468-L471)
- [src/utils/file-system.ts](file://src/utils/file-system.ts#L167-L185)
- [README.md](file://README.md#L159-L160)

## Post-Setup Verification

After completing the initialization process, verify that OpenSpec is properly configured by running:

```bash
openspec list
```

This command displays all active changes in your project and confirms that the OpenSpec system is correctly set up and operational. The output should show an empty list or any existing changes, indicating that OpenSpec can access and read the project structure.

Additional verification steps include:
- Checking that the `openspec/` directory was created with the expected subdirectories
- Verifying that `AGENTS.md` was generated in the project root
- Confirming that tool-specific configuration files were created for selected AI assistants
- Ensuring that all generated files contain the proper OpenSpec markers

Successful verification means your project is now ready for AI-assisted spec-driven development, with all necessary infrastructure in place for creating change proposals, implementing features, and maintaining specifications.

**Section sources**
- [src/cli/index.ts](file://src/cli/index.ts#L91-L106)
- [README.md](file://README.md#L158)