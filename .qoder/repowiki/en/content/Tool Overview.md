# Tool Overview

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [AGENTS.md](file://openspec/AGENTS.md)
- [project.md](file://openspec/project.md)
- [bin/openspec.js](file://bin/openspec.js)
- [src/cli/index.ts](file://src/cli/index.ts)
- [src/commands/change.ts](file://src/commands/change.ts)
- [src/commands/show.ts](file://src/commands/show.ts)
- [src/commands/spec.ts](file://src/commands/spec.ts)
- [src/commands/validate.ts](file://src/commands/validate.ts)
- [src/core/validation/validator.ts](file://src/core/validation/validator.ts)
- [src/core/parsers/markdown-parser.ts](file://src/core/parsers/markdown-parser.ts)
- [src/core/parsers/change-parser.ts](file://src/core/parsers/change-parser.ts)
- [src/core/schemas/spec.schema.ts](file://src/core/schemas/spec.schema.ts)
- [openspec/changes/add-scaffold-command/proposal.md](file://openspec/changes/add-scaffold-command/proposal.md)
- [openspec/changes/add-scaffold-command/tasks.md](file://openspec/changes/add-scaffold-command/tasks.md)
- [openspec/changes/archive/2025-01-11-add-update-command/specs/cli-update/spec.md](file://openspec/changes/archive/2025-01-11-add-update-command/specs/cli-update/spec.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Value Proposition](#core-value-proposition)
3. [Architectural Foundation](#architectural-foundation)
4. [Fundamental Workflow](#fundamental-workflow)
5. [Two-Folder Model](#two-folder-model)
6. [Key Outcomes](#key-outcomes)
7. [Practical Examples](#practical-examples)
8. [AI Tool Integration](#ai-tool-integration)
9. [Brownfield-First Design Philosophy](#brownfield-first-design-philosophy)
10. [Conclusion](#conclusion)

## Introduction

OpenSpec is a specification-driven development system designed to align human and AI stakeholders through structured change management. It addresses the fundamental challenge of unpredictability in AI coding assistants when requirements exist only in chat history by establishing a deterministic, reviewable workflow. OpenSpec enables teams to agree on specifications before implementation begins, creating a shared source of truth that persists throughout the development lifecycle. This documentation provides a comprehensive overview of OpenSpec's core value proposition, architectural foundation, and practical implementation, focusing on how it transforms AI-assisted development through spec-driven workflows.

**Section sources**
- [README.md](file://README.md#L29-L31)

## Core Value Proposition

OpenSpec's core value proposition centers on creating alignment between human developers and AI coding assistants by establishing a structured specification workflow that locks intent before implementation. This approach directly addresses the unpredictability inherent in AI coding assistants when requirements exist solely in ephemeral chat history. By requiring agreement on specifications before any code is written, OpenSpec ensures deterministic and reviewable outputs, eliminating the guesswork and inconsistency that often plague AI-assisted development.

The system enables spec-driven development by providing a lightweight framework that doesn't require API keys or complex setup. It establishes a clear separation between what should change (proposals) and what is currently built (source-of-truth specs), creating a transparent audit trail for all modifications. This alignment ensures that both human stakeholders and AI assistants operate from the same understanding of requirements, reducing misinterpretations and rework.

OpenSpec's value extends beyond simple documentation by creating a shared context that persists across development sessions and team members. This shared context enables AI assistants to provide more accurate and consistent suggestions, as they can reference explicit specifications rather than relying on fragmented chat history. The result is a development process that is more predictable, auditable, and collaborative, where changes are intentional rather than emergent.

**Section sources**
- [README.md](file://README.md#L31-L35)
- [README.md](file://README.md#L37-L41)

## Architectural Foundation

OpenSpec's architectural foundation is built around a clear separation of concerns and a deterministic file structure that enables reliable parsing and validation. The system's architecture consists of three primary components: the CLI interface, the core processing logic, and the specification files, all organized within a standardized directory structure.

The CLI interface, implemented in `src/cli/index.ts`, serves as the primary entry point for users and AI assistants. It exposes commands for initializing the system (`init`), listing active changes (`list`), validating specifications (`validate`), showing details of changes or specs (`show`), and archiving completed changes (`archive`). These commands are designed to be intuitive and consistent, with both interactive and non-interactive modes to accommodate different use cases.

The core processing logic, distributed across the `src/core/` directory, handles the critical functions of parsing, validating, and transforming specification files. The `Validator` class in `src/core/validation/validator.ts` enforces strict formatting rules and semantic requirements, ensuring that all specifications adhere to the OpenSpec standard. The `MarkdownParser` and `ChangeParser` classes in `src/core/parsers/` handle the extraction of structured data from Markdown files, enabling the system to programmatically understand and process human-readable specifications.

The specification files themselves follow a standardized format that balances human readability with machine parseability. Specifications in the `openspec/specs/` directory represent the current state of the system, while proposed changes in `openspec/changes/` contain deltas that describe modifications to existing specifications. This architectural separation enables clear diff tracking and deterministic outputs, as the system can precisely determine what changes are being proposed and how they affect the current state.

**Section sources**
- [src/cli/index.ts](file://src/cli/index.ts#L1-L254)
- [src/core/validation/validator.ts](file://src/core/validation/validator.ts#L1-L449)
- [src/core/parsers/markdown-parser.ts](file://src/core/parsers/markdown-parser.ts#L1-L237)
- [src/core/parsers/change-parser.ts](file://src/core/parsers/change-parser.ts#L1-L234)

## Fundamental Workflow

OpenSpec's fundamental workflow consists of four distinct stages: drafting change proposals, reviewing specifications, implementing tasks, and archiving completed changes. This structured process ensures that all stakeholders agree on requirements before implementation begins, creating a deterministic and auditable development lifecycle.

The workflow begins with drafting a change proposal, where a developer or AI assistant creates a new directory in `openspec/changes/` with a unique identifier. This directory contains three key files: `proposal.md`, which explains the rationale and scope of the change; `tasks.md`, which outlines the implementation steps as a checklist; and specification deltas in `specs/[capability]/spec.md`, which describe the proposed modifications to existing specifications. This initial draft captures the intent of the change in a structured format that can be reviewed and refined.

The review phase involves examining the proposal with all stakeholders, including AI assistants, until consensus is reached. During this phase, the specification deltas are refined to ensure they accurately capture the desired behavior, with each requirement including at least one scenario that describes the expected outcome. The `openspec validate` command is used to check that the proposal adheres to formatting rules and contains all necessary components, ensuring that the specification is complete and unambiguous.

Once the proposal is approved, the implementation phase begins. The AI assistant works through the tasks outlined in `tasks.md`, implementing the changes described in the specification deltas. As tasks are completed, they are marked as done in the checklist, providing a clear record of progress. Throughout implementation, the assistant refers to the agreed-upon specifications, ensuring that the code produced aligns with the approved requirements.

The final stage is archiving the completed change. After implementation is finished and tested, the `openspec archive` command is used to move the change from `openspec/changes/` to `openspec/changes/archive/YYYY-MM-DD-[name]/`. During this process, the approved specification deltas are merged into the source-of-truth specifications in `openspec/specs/`, updating the system's documentation to reflect the implemented changes. This creates a complete audit trail of all modifications and ensures that the specifications remain current and accurate.

**Section sources**
- [README.md](file://README.md#L54-L82)
- [AGENTS.md](file://openspec/AGENTS.md#L15-L65)
- [src/commands/change.ts](file://src/commands/change.ts#L1-L292)
- [src/commands/validate.ts](file://src/commands/validate.ts#L1-L306)

## Two-Folder Model

OpenSpec's two-folder model is a fundamental architectural decision that separates the source-of-truth specifications (`openspec/specs/`) from proposed updates (`openspec/changes/`). This separation enables clear diff tracking, deterministic outputs, and a transparent audit trail of all changes, solving the unpredictability of AI coding assistants when requirements exist only in chat history.

The `openspec/specs/` directory contains the current state of the system, with each subdirectory representing a specific capability and containing a `spec.md` file that describes the requirements and behavior of that capability. These specifications serve as the single source of truth for what has been implemented and deployed, providing a stable reference point for all development activities. When AI assistants need to understand the current behavior of the system, they read these specifications directly, ensuring consistency across development sessions.

The `openspec/changes/` directory contains proposed modifications to the system, with each change represented by a uniquely named subdirectory. Within each change directory, specification deltas in `specs/[capability]/spec.md` describe the proposed modifications using standardized headers: `## ADDED Requirements` for new capabilities, `## MODIFIED Requirements` for changed behavior, `## REMOVED Requirements` for deprecated features, and `## RENAMED Requirements` for name changes. This delta-based approach allows for precise tracking of proposed changes and enables the system to generate clear diffs that show exactly what will be modified.

This two-folder model provides several key benefits. First, it enables deterministic outputs by ensuring that all changes are explicitly defined before implementation begins. Second, it creates a clear separation between what is currently built and what is proposed, reducing confusion and misinterpretation. Third, it facilitates auditable change tracking by maintaining a complete history of all proposals, including those that were ultimately rejected or modified. Finally, it supports the archiving process, where completed changes are moved to `openspec/changes/archive/` and their specification deltas are merged into the source-of-truth specifications, ensuring that the documentation remains current and accurate.

**Section sources**
- [README.md](file://README.md#L46-L48)
- [AGENTS.md](file://openspec/AGENTS.md#L124-L141)
- [src/core/parsers/change-parser.ts](file://src/core/parsers/change-parser.ts#L37-L82)
- [src/core/validation/validator.ts](file://src/core/validation/validator.ts#L113-L272)

## Key Outcomes

OpenSpec delivers several key outcomes that transform the AI-assisted development process, creating a more predictable, auditable, and collaborative environment. These outcomes address the fundamental challenges of working with AI coding assistants and provide tangible benefits for development teams.

First, OpenSpec ensures agreement on specifications before implementation begins. By requiring all stakeholders, including AI assistants, to review and approve specifications before any code is written, the system eliminates the ambiguity and misinterpretation that often occur when requirements exist only in chat history. This agreement creates a shared understanding of what should be built, reducing rework and ensuring that the final product aligns with stakeholder expectations.

Second, OpenSpec provides auditable change tracking through its structured file organization and archiving process. Every proposed change is captured in a dedicated directory within `openspec/changes/`, with a complete record of the proposal, tasks, and specification deltas. When a change is completed, it is moved to `openspec/changes/archive/` with a timestamped name, creating a permanent record of all modifications. This audit trail enables teams to understand the evolution of the system over time and provides valuable context for future development.

Third, OpenSpec offers shared visibility into project status through commands like `openspec list` and `openspec view`. These commands provide a clear overview of active changes, completed changes, and the current state of specifications, ensuring that all team members have access to the same information. This transparency facilitates collaboration and enables teams to coordinate their efforts effectively, even when working asynchronously.

Finally, OpenSpec ensures broad compatibility with existing AI tools through multiple integration methods. The system supports native slash commands for tools like Claude Code, Cursor, and GitHub Copilot, while also providing AGENTS.md compatibility for tools that can read workflow instructions from a shared file. This flexibility allows teams to use OpenSpec with their preferred AI assistants without requiring significant changes to their existing workflows.

**Section sources**
- [README.md](file://README.md#L37-L41)
- [src/commands/change.ts](file://src/commands/change.ts#L97-L182)
- [src/commands/show.ts](file://src/commands/show.ts#L1-L140)
- [AGENTS.md](file://openspec/AGENTS.md#L89-L109)

## Practical Examples

OpenSpec's workflow can be demonstrated through practical examples that show the complete process from proposal creation to archiving. These examples illustrate how the system works in real-world scenarios and highlight the interactions between human developers and AI assistants.

Consider the example of adding profile search filters by role and team. The process begins with a developer asking their AI assistant to create a change proposal: "Create an OpenSpec change proposal for adding profile search filters by role and team." The AI assistant responds by creating a new directory in `openspec/changes/` named `add-profile-filters`, containing `proposal.md`, `tasks.md`, and specification deltas in `specs/profile/spec.md`. The `proposal.md` file explains the rationale for the change, the `tasks.md` file outlines the implementation steps, and the specification deltas describe the proposed modifications to the profile search functionality.

The developer then reviews the proposal using commands like `openspec list`, `openspec validate`, and `openspec show`. If the specifications need refinement, the developer asks the AI assistant to make adjustments: "Can you add acceptance criteria for the role and team filters?" The AI updates the specification deltas and tasks accordingly, and the developer validates the changes until they are satisfied. Once the proposal is approved, the developer instructs the AI to implement the change: "The specs look good. Let's implement this change."

As the AI assistant works through the tasks in `tasks.md`, it marks completed items with checkmarks, providing a clear record of progress. When all tasks are complete, the developer archives the change: "Please archive the change." The `openspec archive` command moves the change directory to `openspec/changes/archive/YYYY-MM-DD-add-profile-filters/` and merges the approved specification deltas into the source-of-truth specifications in `openspec/specs/`. This completes the workflow, leaving a permanent record of the change and updated documentation for future reference.

This example demonstrates how OpenSpec creates a structured, deterministic workflow that aligns human and AI stakeholders. The process ensures that everyone agrees on the requirements before implementation begins, provides a clear audit trail of all changes, and maintains up-to-date documentation that reflects the current state of the system.

**Section sources**
- [README.md](file://README.md#L177-L236)
- [openspec/changes/add-scaffold-command/proposal.md](file://openspec/changes/add-scaffold-command/proposal.md#L1-L12)
- [openspec/changes/add-scaffold-command/tasks.md](file://openspec/changes/add-scaffold-command/tasks.md#L1-L12)
- [src/cli/index.ts](file://src/cli/index.ts#L184-L199)

## AI Tool Integration

OpenSpec integrates with AI tools through two primary methods: native slash commands and AGENTS.md compatibility. This dual approach ensures broad compatibility with existing AI assistants while providing a seamless user experience for supported tools.

For tools with native slash command support, such as Claude Code, Cursor, and GitHub Copilot, OpenSpec provides dedicated commands that can be triggered directly within the AI interface. These commands include `/openspec:proposal` for creating change proposals, `/openspec:apply` for implementing changes, and `/openspec:archive` for archiving completed changes. When a user selects one of these commands, the AI assistant automatically generates the appropriate OpenSpec files and follows the structured workflow, reducing the need for manual intervention. The initialization process (`openspec init`) automatically configures these slash commands for the tools selected by the user, ensuring that they are available immediately after setup.

For tools that do not support native slash commands, OpenSpec provides AGENTS.md compatibility. The `openspec/AGENTS.md` file contains comprehensive instructions for AI assistants, explaining the OpenSpec workflow and providing examples of how to create proposals, implement changes, and archive completed work. Tools like Amp, Jules, and Gemini CLI automatically read these instructions and can follow the OpenSpec workflow when prompted. This approach ensures that OpenSpec works with virtually any AI assistant that can read and follow text-based instructions, providing maximum flexibility for development teams.

The integration process is designed to be lightweight and non-intrusive. During initialization, OpenSpec creates a managed `AGENTS.md` file at the project root and configures slash commands for selected tools, but otherwise leaves the development environment unchanged. This allows teams to adopt OpenSpec incrementally, starting with new features and gradually expanding to existing codebases. The system also supports multiple AI tools within the same project, enabling different team members to use their preferred assistants while sharing the same specifications and change tracking system.

**Section sources**
- [README.md](file://README.md#L86-L119)
- [AGENTS.md](file://openspec/AGENTS.md#L89-L119)
- [src/cli/index.ts](file://src/cli/index.ts#L40-L74)

## Brownfield-First Design Philosophy

OpenSpec's brownfield-first design philosophy makes it particularly effective for modifying existing behavior (1→n) rather than just greenfield development (0→1). This approach recognizes that most development work involves enhancing or refactoring existing systems rather than building entirely new features from scratch, and it provides specialized support for these common scenarios.

The two-folder model, with its separation of source-of-truth specifications (`openspec/specs/`) and proposed updates (`openspec/changes/`), is especially well-suited for brownfield development. When modifying existing behavior, developers can reference the current specifications directly, ensuring that their proposed changes are consistent with the existing system. The delta-based specification format allows for precise tracking of modifications to existing requirements, making it easy to understand exactly what will change and how it will affect the system.

OpenSpec's support for multi-capability changes further enhances its effectiveness in brownfield scenarios. When a change affects multiple specifications, the system allows for specification deltas to be created in multiple directories within a single change proposal. For example, adding two-factor authentication might require modifications to both the authentication and notification systems, with deltas in `specs/auth/spec.md` and `specs/notifications/spec.md`. This capability grouping ensures that related changes are tracked together, providing a complete picture of the modification and its impact across the system.

The archiving process also reflects the brownfield-first philosophy by preserving the history of all changes, including those that modify existing behavior. When a change is archived, its specification deltas are merged into the source-of-truth specifications, creating a complete record of how the system has evolved over time. This historical context is invaluable for understanding the rationale behind existing code and for making informed decisions about future modifications.

This focus on brownfield development sets OpenSpec apart from tools that are optimized for greenfield scenarios. While it can certainly support the creation of new features, its strength lies in managing the complexity of evolving systems, where changes often involve subtle modifications to existing behavior rather than the addition of entirely new capabilities.

**Section sources**
- [README.md](file://README.md#L46-L48)
- [AGENTS.md](file://openspec/AGENTS.md#L347-L358)
- [src/core/parsers/change-parser.ts](file://src/core/parsers/change-parser.ts#L37-L82)

## Conclusion

OpenSpec provides a comprehensive solution for spec-driven development with AI coding assistants, addressing the fundamental challenges of unpredictability and misalignment that often plague AI-assisted development. By establishing a structured workflow that requires agreement on specifications before implementation begins, OpenSpec creates a deterministic, auditable, and collaborative development process that benefits both human developers and AI assistants.

The system's architectural foundation, built around a clear separation of source-of-truth specifications and proposed updates, enables precise diff tracking and deterministic outputs. This two-folder model, combined with a well-defined workflow of drafting proposals, reviewing specifications, implementing tasks, and archiving completed changes, creates a transparent audit trail that persists throughout the development lifecycle.

OpenSpec's key outcomes—agreement on specifications before implementation, auditable change tracking, shared visibility into project status, and broad compatibility with existing AI tools—transform the way teams work with AI assistants. The system's brownfield-first design philosophy makes it particularly effective for modifying existing behavior, providing specialized support for the common scenarios of enhancing and refactoring existing systems.

By integrating seamlessly with popular AI tools through both native slash commands and AGENTS.md compatibility, OpenSpec offers a flexible and lightweight solution that can be adopted incrementally. Its focus on human-readable specifications and deterministic workflows ensures that development remains transparent and controllable, even as AI assistants take on increasingly complex tasks. OpenSpec represents a significant step forward in harnessing the power of AI for software development, creating a more predictable, reliable, and collaborative development process.

**Section sources**
- [README.md](file://README.md#L31-L41)
- [AGENTS.md](file://openspec/AGENTS.md#L453-L455)