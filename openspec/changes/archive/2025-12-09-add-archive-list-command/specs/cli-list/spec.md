# List Command Specification - Changes

## ADDED Requirements

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

## MODIFIED Requirements

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
