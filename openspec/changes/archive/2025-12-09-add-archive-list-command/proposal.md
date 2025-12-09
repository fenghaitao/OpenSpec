# Change: Add Archive Listing to List Command

## Why

Developers need visibility into archived changes to understand project history, reference past decisions, and learn from completed work. Currently, there's no easy way to view archived changes without manually browsing the `openspec/changes/archive/` directory.

## What Changes

- Add `--archive` flag to `openspec list` command to display archived changes
- Show archived changes with their archive date and original change name
- Display in chronological order (newest first) with task completion status
- Maintain consistent output format with existing list command

## Impact

- Affected specs: `cli-list`
- Affected code: `src/core/list.ts`, `src/cli/index.ts`
- No breaking changes - purely additive feature
