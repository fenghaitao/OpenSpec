# openspec change

<cite>
**Referenced Files in This Document**   
- [change.ts](file://src/commands/change.ts)
- [change.schema.ts](file://src/core/schemas/change.schema.ts)
- [change-parser.ts](file://src/core/parsers/change-parser.ts)
- [validator.ts](file://src/core/validation/validator.ts)
- [interactive.ts](file://src/utils/interactive.ts)
- [task-progress.ts](file://src/utils/task-progress.ts)
- [item-discovery.ts](file://src/utils/item-discovery.ts)
- [cli-change/spec.md](file://openspec/specs/cli-change/spec.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
The `openspec change` command provides a comprehensive interface for managing change operations within the OpenSpec system. It enables users to create, view, validate, and manage change proposals that document modifications to specifications. The command supports both interactive and non-interactive modes, allowing for flexible workflow integration. Change operations are central to the OpenSpec methodology, serving as the primary mechanism for proposing, tracking, and implementing specification modifications. The command integrates with the specification system through delta-based change tracking, where changes are represented as additions, modifications, removals, or renamings of requirements.

## Project Structure
The `openspec change` functionality is organized within the OpenSpec repository according to a modular architecture. The core implementation resides in the `src/commands/change.ts` file, which contains the `ChangeCommand` class responsible for all change-related operations. Supporting functionality is distributed across various directories: schema definitions in `src/core/schemas/`, parsers in `src/core/parsers/`, validation logic in `src/core/validation/`, and utility functions in `src/utils/`. The changes themselves are stored in the `openspec/changes/` directory, with each change occupying its own subdirectory containing proposal, tasks, and specification files. Archived changes are moved to the `openspec/changes/archive/` directory with timestamped names.

```mermaid
graph TB
subgraph "Source Code"
CLI[src/cli/index.ts]
Commands[src/commands/]
Core[src/core/]
Utils[src/utils/]
end
subgraph "Data Storage"
Changes[openspec/changes/]
Archive[openspec/changes/archive/]
Specs[openspec/specs/]
end
CLI --> Commands
Commands --> Core
Commands --> Utils
Commands --> Changes
Changes --> Specs
style CLI fill:#4CAF50,stroke:#388E3C
style Commands fill:#2196F3,stroke:#1976D2
style Core fill:#9C27B0,stroke:#7B1FA2
style Utils fill:#FF9800,stroke:#F57C00
style Changes fill:#607D8B,stroke:#455A64
style Archive fill:#607D8B,stroke:#455A64
style Specs fill:#607D8B,stroke:#455A64
```

**Diagram sources**
- [change.ts](file://src/commands/change.ts)
- [change.schema.ts](file://src/core/schemas/change.schema.ts)

**Section sources**
- [change.ts](file://src/commands/change.ts)
- [project.md](file://openspec/project.md)

## Core Components
The `openspec change` command is implemented as a class-based system with distinct components for different operations. The `ChangeCommand` class in `change.ts` serves as the primary interface, exposing methods for showing, listing, and validating changes. Each operation follows a consistent pattern of input validation, data retrieval, processing, and output formatting. The command integrates with the specification system through the `ChangeParser` and `Validator` classes, which extract and validate delta information from specification files. Task management is supported through the `task-progress.ts` utility, which parses task completion status from markdown files. Interactive functionality is enabled by the `isInteractive` function and `@inquirer/prompts` library, providing user-friendly selection interfaces when appropriate.

**Section sources**
- [change.ts](file://src/commands/change.ts#L16-L292)
- [task-progress.ts](file://src/utils/task-progress.ts#L1-L44)

## Architecture Overview
The `openspec change` command follows a layered architecture that separates concerns between command interface, data processing, and storage. At the top layer, the command interface handles user input and output formatting. Below this, the processing layer parses change proposals and validates their structure against defined schemas. The storage layer interacts with the filesystem to read and write change data. The system uses a delta-based approach to track changes, where modifications to specifications are explicitly declared as additions, modifications, removals, or renamings of requirements. This architecture enables both human-readable documentation and machine-processable change descriptions, supporting both collaborative development and automated tooling.

```mermaid
graph TD
A[User Interface] --> B[Command Interface]
B --> C[Data Processing]
C --> D[Storage Layer]
subgraph "Command Interface"
B1[show]
B2[list]
B3[validate]
end
subgraph "Data Processing"
C1[ChangeParser]
C2[Validator]
C3[JsonConverter]
end
subgraph "Storage Layer"
D1[File System]
D2[changes/ directory]
D3[specs/ directory]
end
B --> C1
B --> C2
B --> C3
C1 --> D1
C2 --> D1
C3 --> D1
D1 --> D2
D1 --> D3
style A fill:#4CAF50,stroke:#388E3C
style B fill:#2196F3,stroke:#1976D2
style C fill:#9C27B0,stroke:#7B1FA2
style D fill:#607D8B,stroke:#455A64
```

**Diagram sources**
- [change.ts](file://src/commands/change.ts#L16-L292)
- [change-parser.ts](file://src/core/parsers/change-parser.ts#L1-L234)
- [validator.ts](file://src/core/validation/validator.ts#L1-L449)

## Detailed Component Analysis

### Change Command Implementation
The `ChangeCommand` class provides three primary operations: show, list, and validate. Each method follows a consistent pattern of input handling, data retrieval, processing, and output formatting. The command supports both interactive and non-interactive modes, automatically detecting the appropriate behavior based on environment and user preferences.

#### For API/Service Components:
```mermaid
sequenceDiagram
participant User as "User"
participant CLI as "CLI Interface"
participant Command as "ChangeCommand"
participant Parser as "ChangeParser"
participant Validator as "Validator"
participant FS as "File System"
User->>CLI : Execute command
CLI->>Command : Call method
alt Interactive Mode
Command->>Command : Check available changes
Command->>User : Present selection prompt
User->>Command : Select change
else Non-Interactive Mode
Command->>Command : Use provided change name
end
Command->>FS : Read proposal.md
FS-->>Command : Return content
alt show operation
Command->>Parser : Parse change with deltas
Parser-->>Command : Return parsed change
Command->>CLI : Format output
else validate operation
Command->>Validator : Validate change
Validator-->>Command : Return validation report
Command->>CLI : Format validation results
else list operation
Command->>FS : Scan changes directory
FS-->>Command : Return change IDs
Command->>CLI : Format list output
end
CLI-->>User : Display results
```

**Diagram sources**
- [change.ts](file://src/commands/change.ts#L16-L292)
- [change-parser.ts](file://src/core/parsers/change-parser.ts#L1-L234)
- [validator.ts](file://src/core/validation/validator.ts#L1-L449)

**Section sources**
- [change.ts](file://src/commands/change.ts#L16-L292)

### Change Schema and Validation
The change system uses a structured schema to ensure consistency and validity of change proposals. The schema defines required fields, data types, and validation rules that must be satisfied for a change to be considered valid. Validation occurs at multiple levels, from basic structural requirements to semantic rules about content quality.

#### For Object-Oriented Components:
```mermaid
classDiagram
class ChangeSchema {
+name : string
+why : string
+whatChanges : string
+deltas : Delta[]
+metadata? : object
}
class DeltaSchema {
+spec : string
+operation : DeltaOperation
+description : string
+requirement? : Requirement
+requirements? : Requirement[]
+rename? : object
}
class RequirementSchema {
+text : string
+scenarios : Scenario[]
+metadata? : object
}
class Scenario {
+condition : string
+result : string
}
class DeltaOperationType {
+ADDED
+MODIFIED
+REMOVED
+RENAMED
}
ChangeSchema --> DeltaSchema : "contains"
DeltaSchema --> RequirementSchema : "references"
RequirementSchema --> Scenario : "contains"
DeltaSchema --> DeltaOperationType : "uses"
```

**Diagram sources**
- [change.schema.ts](file://src/core/schemas/change.schema.ts#L1-L42)
- [base.schema.ts](file://src/core/schemas/base.schema.ts)

**Section sources**
- [change.schema.ts](file://src/core/schemas/change.schema.ts#L1-L42)
- [constants.ts](file://src/core/validation/constants.ts#L1-L49)

### Interactive Mode and Task Management
The change command supports interactive mode for user-friendly change selection and management. When no change name is provided, the command automatically detects whether interactive prompts should be used based on the environment. Task management is integrated through the tasks.md file in each change directory, which tracks implementation progress using a simple checklist format.

#### For Complex Logic Components:
```mermaid
flowchart TD
Start([Command Execution]) --> CheckArgs["Check for change name argument"]
CheckArgs --> |No argument| CheckInteractive["Check interactive capability"]
CheckInteractive --> |Interactive| ShowPrompt["Show interactive selection prompt"]
ShowPrompt --> UserSelect["User selects change"]
UserSelect --> ProcessChange["Process selected change"]
CheckInteractive --> |Non-interactive| ShowHint["Show available changes hint"]
ShowHint --> ExitError["Exit with error code"]
CheckArgs --> |With argument| ValidateChange["Validate change name"]
ValidateChange --> |Valid| ProcessChange
ValidateChange --> |Invalid| ShowError["Show error message"]
ShowError --> ExitError
ProcessChange --> Output["Format and display output"]
Output --> End([Command Complete])
ExitError --> End
```

**Diagram sources**
- [change.ts](file://src/commands/change.ts#L32-L50)
- [interactive.ts](file://src/utils/interactive.ts#L1-L8)
- [item-discovery.ts](file://src/utils/item-discovery.ts#L1-L46)

**Section sources**
- [change.ts](file://src/commands/change.ts#L32-L50)
- [interactive.ts](file://src/utils/interactive.ts#L1-L8)

## Dependency Analysis
The `openspec change` command has a well-defined dependency structure that follows the dependency inversion principle. The command depends on abstract interfaces rather than concrete implementations, allowing for flexibility and testability. Key dependencies include the `ChangeParser` for extracting structured data from markdown files, the `Validator` for ensuring change validity, and the `JsonConverter` for formatting output. Utility functions for interactive prompts and file system operations are imported as needed. The command has no circular dependencies and maintains a clear separation of concerns between input handling, data processing, and output formatting.

```mermaid
graph TD
ChangeCommand --> ChangeParser
ChangeCommand --> Validator
ChangeCommand --> JsonConverter
ChangeCommand --> interactive
ChangeCommand --> item-discovery
ChangeParser --> MarkdownParser
ChangeParser --> base.schema
Validator --> change.schema
Validator --> requirement-blocks
JsonConverter --> change.schema
style ChangeCommand fill:#2196F3,stroke:#1976D2
style ChangeParser fill:#9C27B0,stroke:#7B1FA2
style Validator fill:#9C27B0,stroke:#7B1FA2
style JsonConverter fill:#9C27B0,stroke:#7B1FA2
style interactive fill:#FF9800,stroke:#F57C00
style item-discovery fill:#FF9800,stroke:#F57C00
style MarkdownParser fill:#9C27B0,stroke:#7B1FA2
style base.schema fill:#607D8B,stroke:#455A64
style change.schema fill:#607D8B,stroke:#455A64
style requirement-blocks fill:#9C27B0,stroke:#7B1FA2
```

**Diagram sources**
- [change.ts](file://src/commands/change.ts)
- [change-parser.ts](file://src/core/parsers/change-parser.ts)
- [validator.ts](file://src/core/validation/validator.ts)

**Section sources**
- [change.ts](file://src/commands/change.ts)
- [change-parser.ts](file://src/core/parsers/change-parser.ts)
- [validator.ts](file://src/core/validation/validator.ts)

## Performance Considerations
The `openspec change` command is designed for optimal performance in typical usage scenarios. File operations are minimized through efficient directory scanning and selective file reading. The command uses asynchronous operations to avoid blocking the event loop during file I/O. For large projects with many changes, the list operation has been optimized to read only essential files and cache results when possible. The validation process is designed to fail fast, reporting the first encountered error rather than attempting to validate the entire structure. Memory usage is kept low by processing files in a streaming fashion rather than loading entire directories into memory at once.

## Troubleshooting Guide
Common issues with the `openspec change` command typically relate to file structure, naming conventions, or validation rules. When a change cannot be found, verify that the change directory exists in `openspec/changes/` and contains a `proposal.md` file. Naming conflicts can occur when attempting to create a change with an existing name; resolve this by choosing a unique name that follows kebab-case convention. Invalid change states often result from missing required sections in the proposal.md file; ensure that both "## Why" and "## What Changes" sections are present. Validation errors may indicate issues with delta specifications in the specs/ directory; use the `--deltas-only` flag to inspect parsed deltas and identify formatting problems. For interactive mode issues, check that stdin is connected to a TTY or that the `OPEN_SPEC_INTERACTIVE` environment variable is not set to '0'.

**Section sources**
- [change.ts](file://src/commands/change.ts)
- [validator.ts](file://src/core/validation/validator.ts)
- [constants.ts](file://src/core/validation/constants.ts)

## Conclusion
The `openspec change` command provides a robust and flexible interface for managing specification changes within the OpenSpec system. Its architecture balances ease of use with powerful functionality, supporting both interactive and automated workflows. The command's integration with the specification system through delta-based change tracking enables precise documentation of modifications while maintaining backward compatibility with existing content. By enforcing consistent structure through schema validation and providing helpful feedback for common issues, the command lowers the barrier to entry for contributing to specification development. The modular design allows for future enhancements while maintaining stability for existing workflows.