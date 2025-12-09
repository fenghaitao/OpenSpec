# List Command Specification

## Purpose

The `openspec list` command SHALL provide developers with a quick overview of all active changes in the project, showing their names and task completion status.
## Requirements
### Requirement: Command Execution
The command SHALL scan and analyze either active changes or specs based on the selected mode.

#### Scenario: Scanning for changes (default)
- **WHEN** `openspec list` is executed without flags
- **THEN** scan the `openspec/changes/` directory for change directories
- **AND** exclude the `archive/` subdirectory from results
- **AND** parse each change's `tasks.md` file to count task completion

#### Scenario: Scanning for specs
- **WHEN** `openspec list --specs` is executed
- **THEN** scan the `openspec/specs/` directory for capabilities
- **AND** read each capability's `spec.md`
- **AND** parse requirements to compute requirement counts

### Requirement: Task Counting

The command SHALL accurately count task completion status using standard markdown checkbox patterns.

#### Scenario: Counting tasks in tasks.md

- **WHEN** parsing a `tasks.md` file
- **THEN** count tasks matching these patterns:
  - Completed: Lines containing `- [x]`
  - Incomplete: Lines containing `- [ ]`
- **AND** calculate total tasks as the sum of completed and incomplete

### Requirement: Output Format
The command SHALL display items in a clear, readable table format with mode-appropriate progress or counts.

#### Scenario: Displaying change list (default)
- **WHEN** displaying the list of changes
- **THEN** show a table with columns:
  - Change name (directory name)
  - Task progress (e.g., "3/5 tasks" or "✓ Complete")

#### Scenario: Displaying spec list
- **WHEN** displaying the list of specs
- **THEN** show a table with columns:
  - Spec id (directory name)
  - Requirement count (e.g., "requirements 12")

### Requirement: Flags

The command SHALL accept flags to select the noun being listed and whether to show archived items.

#### Scenario: Default behavior (no flags)

- **WHEN** `openspec list` is executed without flags
- **THEN** list active changes (not archived)

#### Scenario: Listing specs

- **WHEN** `openspec list --specs` is executed
- **THEN** list specifications from `openspec/specs/`

#### Scenario: Listing archived changes

- **WHEN** `openspec list --archive` is executed
- **THEN** list archived changes from `openspec/changes/archive/`

#### Scenario: Conflicting flags

- **WHEN** both `--specs` and `--archive` flags are provided
- **THEN** display error: "Cannot use --specs and --archive together"
- **AND** exit with code 1

### Requirement: Empty State
The command SHALL provide clear feedback when no items are present for the selected mode.

#### Scenario: Handling empty state (changes)
- **WHEN** no active changes exist (only archive/ or empty changes/)
- **THEN** display: "No active changes found."

#### Scenario: Handling empty state (specs)
- **WHEN** no specs directory exists or contains no capabilities
- **THEN** display: "No specs found."

### Requirement: Error Handling

The command SHALL gracefully handle missing files and directories with appropriate messages.

#### Scenario: Missing tasks.md file

- **WHEN** a change directory has no `tasks.md` file
- **THEN** display the change with "No tasks" status

#### Scenario: Missing changes directory

- **WHEN** `openspec/changes/` directory doesn't exist
- **THEN** display error: "No OpenSpec changes directory found. Run 'openspec init' first."
- **AND** exit with code 1

### Requirement: Sorting

The command SHALL maintain consistent ordering of changes for predictable output.

#### Scenario: Ordering changes

- **WHEN** displaying multiple changes
- **THEN** sort them in alphabetical order by change name

### Requirement: Archive Listing

The command SHALL support listing archived changes when the `--archive` flag is provided.

#### Scenario: Listing archived changes

- **WHEN** `openspec list --archive` is executed
- **THEN** scan the `openspec/changes/archive/` directory for archived change directories
- **AND** parse directory names in format `YYYY-MM-DD-<change-name>`
- **AND** extract the archive date and original change name from each directory
- **AND** read each archived change's `tasks.md` file to count task completion
- **AND** sort results by archive date (newest first)

#### Scenario: Displaying archived changes

- **WHEN** displaying the list of archived changes
- **THEN** show a table with columns:
  - Archive date (YYYY-MM-DD format)
  - Change name (original change ID)
  - Task progress (e.g., "5/5 tasks" or "✓ Complete")
- **AND** include a header indicating archive mode

#### Scenario: Empty archive directory

- **WHEN** the archive directory is empty or doesn't exist
- **THEN** display "No archived changes found"
- **AND** exit successfully with code 0

#### Scenario: Invalid archive directory names

- **WHEN** encountering directories that don't match the `YYYY-MM-DD-<name>` pattern
- **THEN** skip those directories silently
- **AND** continue processing valid archived changes

## Why

Developers need a quick way to:
- See what changes are in progress
- Identify which changes are ready to archive
- Understand the overall project evolution status
- Get a bird's-eye view without opening multiple files

This command provides that visibility with minimal effort, following OpenSpec's philosophy of simplicity and clarity.