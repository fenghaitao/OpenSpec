# Implementation Tasks

## 1. Core Implementation
- [x] 1.1 Add `--archive` flag to list command CLI definition
- [x] 1.2 Implement archive scanning logic in `ListCommand.execute()`
- [x] 1.3 Parse archive directory names to extract date and change name
- [x] 1.4 Read archived `tasks.md` files for completion status
- [x] 1.5 Sort archived changes by date (newest first)

## 2. Output Formatting
- [x] 2.1 Display archive date alongside change name
- [x] 2.2 Show task completion status for archived changes
- [x] 2.3 Add header indicating archive mode

## 3. Testing
- [x] 3.1 Add unit tests for archive scanning
- [x] 3.2 Add unit tests for date parsing from archive names
- [x] 3.3 Add CLI e2e test for `openspec list --archive`
- [x] 3.4 Test with empty archive directory
- [x] 3.5 Test with multiple archived changes

## 4. Documentation
- [x] 4.1 Update CLI help text for list command
- [x] 4.2 Update AGENTS.md with archive listing example
