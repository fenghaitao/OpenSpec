import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';
import { ListCommand } from '../../src/core/list.js';

describe('ListCommand', () => {
  let tempDir: string;
  let originalLog: typeof console.log;
  let logOutput: string[] = [];

  beforeEach(async () => {
    // Create temp directory
    tempDir = path.join(os.tmpdir(), `openspec-list-test-${Date.now()}`);
    await fs.mkdir(tempDir, { recursive: true });

    // Mock console.log to capture output
    originalLog = console.log;
    console.log = (...args: any[]) => {
      logOutput.push(args.join(' '));
    };
    logOutput = [];
  });

  afterEach(async () => {
    // Restore console.log
    console.log = originalLog;

    // Clean up temp directory
    await fs.rm(tempDir, { recursive: true, force: true });
  });

  describe('execute', () => {
    it('should handle missing openspec/changes directory', async () => {
      const listCommand = new ListCommand();
      
      await expect(listCommand.execute(tempDir, 'changes')).rejects.toThrow(
        "No OpenSpec changes directory found. Run 'openspec init' first."
      );
    });

    it('should handle empty changes directory', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      await fs.mkdir(changesDir, { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'changes');

      expect(logOutput).toEqual(['No active changes found.']);
    });

    it('should exclude archive directory', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      await fs.mkdir(path.join(changesDir, 'archive'), { recursive: true });
      await fs.mkdir(path.join(changesDir, 'my-change'), { recursive: true });
      
      // Create tasks.md with some tasks
      await fs.writeFile(
        path.join(changesDir, 'my-change', 'tasks.md'),
        '- [x] Task 1\n- [ ] Task 2\n'
      );

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'changes');

      expect(logOutput).toContain('Changes:');
      expect(logOutput.some(line => line.includes('my-change'))).toBe(true);
      expect(logOutput.some(line => line.includes('archive'))).toBe(false);
    });

    it('should count tasks correctly', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      await fs.mkdir(path.join(changesDir, 'test-change'), { recursive: true });
      
      await fs.writeFile(
        path.join(changesDir, 'test-change', 'tasks.md'),
        `# Tasks
- [x] Completed task 1
- [x] Completed task 2
- [ ] Incomplete task 1
- [ ] Incomplete task 2
- [ ] Incomplete task 3
Regular text that should be ignored
`
      );

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'changes');

      expect(logOutput.some(line => line.includes('2/5 tasks'))).toBe(true);
    });

    it('should show complete status for fully completed changes', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      await fs.mkdir(path.join(changesDir, 'completed-change'), { recursive: true });
      
      await fs.writeFile(
        path.join(changesDir, 'completed-change', 'tasks.md'),
        '- [x] Task 1\n- [x] Task 2\n- [x] Task 3\n'
      );

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'changes');

      expect(logOutput.some(line => line.includes('✓ Complete'))).toBe(true);
    });

    it('should handle changes without tasks.md', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      await fs.mkdir(path.join(changesDir, 'no-tasks'), { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'changes');

      expect(logOutput.some(line => line.includes('no-tasks') && line.includes('No tasks'))).toBe(true);
    });

    it('should sort changes alphabetically', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      await fs.mkdir(path.join(changesDir, 'zebra'), { recursive: true });
      await fs.mkdir(path.join(changesDir, 'alpha'), { recursive: true });
      await fs.mkdir(path.join(changesDir, 'middle'), { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir);

      const changeLines = logOutput.filter(line => 
        line.includes('alpha') || line.includes('middle') || line.includes('zebra')
      );
      
      expect(changeLines[0]).toContain('alpha');
      expect(changeLines[1]).toContain('middle');
      expect(changeLines[2]).toContain('zebra');
    });

    it('should handle multiple changes with various states', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      
      // Complete change
      await fs.mkdir(path.join(changesDir, 'completed'), { recursive: true });
      await fs.writeFile(
        path.join(changesDir, 'completed', 'tasks.md'),
        '- [x] Task 1\n- [x] Task 2\n'
      );

      // Partial change
      await fs.mkdir(path.join(changesDir, 'partial'), { recursive: true });
      await fs.writeFile(
        path.join(changesDir, 'partial', 'tasks.md'),
        '- [x] Done\n- [ ] Not done\n- [ ] Also not done\n'
      );

      // No tasks
      await fs.mkdir(path.join(changesDir, 'no-tasks'), { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir);

      expect(logOutput).toContain('Changes:');
      expect(logOutput.some(line => line.includes('completed') && line.includes('✓ Complete'))).toBe(true);
      expect(logOutput.some(line => line.includes('partial') && line.includes('1/3 tasks'))).toBe(true);
      expect(logOutput.some(line => line.includes('no-tasks') && line.includes('No tasks'))).toBe(true);
    });
  });

  describe('archive mode', () => {
    it('should handle missing archive directory', async () => {
      const changesDir = path.join(tempDir, 'openspec', 'changes');
      await fs.mkdir(changesDir, { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      expect(logOutput).toEqual(['No archived changes found.']);
    });

    it('should handle empty archive directory', async () => {
      const archiveDir = path.join(tempDir, 'openspec', 'changes', 'archive');
      await fs.mkdir(archiveDir, { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      expect(logOutput).toEqual(['No archived changes found.']);
    });

    it('should list archived changes with dates', async () => {
      const archiveDir = path.join(tempDir, 'openspec', 'changes', 'archive');
      await fs.mkdir(path.join(archiveDir, '2025-01-15-feature-a'), { recursive: true });
      await fs.writeFile(
        path.join(archiveDir, '2025-01-15-feature-a', 'tasks.md'),
        '- [x] Task 1\n- [x] Task 2\n'
      );

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      expect(logOutput).toContain('Archived Changes:');
      expect(logOutput.some(line => line.includes('2025-01-15') && line.includes('feature-a'))).toBe(true);
    });

    it('should sort archived changes by date (newest first)', async () => {
      const archiveDir = path.join(tempDir, 'openspec', 'changes', 'archive');
      await fs.mkdir(path.join(archiveDir, '2025-01-10-old'), { recursive: true });
      await fs.mkdir(path.join(archiveDir, '2025-03-15-newest'), { recursive: true });
      await fs.mkdir(path.join(archiveDir, '2025-02-20-middle'), { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      const archiveLines = logOutput.filter(line => 
        line.includes('old') || line.includes('newest') || line.includes('middle')
      );
      
      expect(archiveLines[0]).toContain('newest');
      expect(archiveLines[1]).toContain('middle');
      expect(archiveLines[2]).toContain('old');
    });

    it('should skip invalid archive directory names', async () => {
      const archiveDir = path.join(tempDir, 'openspec', 'changes', 'archive');
      await fs.mkdir(path.join(archiveDir, '2025-01-15-valid-change'), { recursive: true });
      await fs.mkdir(path.join(archiveDir, 'invalid-name'), { recursive: true });
      await fs.mkdir(path.join(archiveDir, '2025-invalid'), { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      expect(logOutput.some(line => line.includes('valid-change'))).toBe(true);
      expect(logOutput.some(line => line.includes('invalid-name'))).toBe(false);
      expect(logOutput.some(line => line.includes('2025-invalid'))).toBe(false);
    });

    it('should show task completion status for archived changes', async () => {
      const archiveDir = path.join(tempDir, 'openspec', 'changes', 'archive');
      
      // Complete archive
      await fs.mkdir(path.join(archiveDir, '2025-01-15-complete'), { recursive: true });
      await fs.writeFile(
        path.join(archiveDir, '2025-01-15-complete', 'tasks.md'),
        '- [x] Task 1\n- [x] Task 2\n'
      );

      // Partial archive
      await fs.mkdir(path.join(archiveDir, '2025-01-16-partial'), { recursive: true });
      await fs.writeFile(
        path.join(archiveDir, '2025-01-16-partial', 'tasks.md'),
        '- [x] Done\n- [ ] Not done\n'
      );

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      expect(logOutput.some(line => line.includes('complete') && line.includes('✓ Complete'))).toBe(true);
      expect(logOutput.some(line => line.includes('partial') && line.includes('1/2 tasks'))).toBe(true);
    });

    it('should handle archived changes without tasks.md', async () => {
      const archiveDir = path.join(tempDir, 'openspec', 'changes', 'archive');
      await fs.mkdir(path.join(archiveDir, '2025-01-15-no-tasks'), { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      expect(logOutput.some(line => line.includes('no-tasks') && line.includes('No tasks'))).toBe(true);
    });

    it('should display only valid archives when mixed with invalid names', async () => {
      const archiveDir = path.join(tempDir, 'openspec', 'changes', 'archive');
      await fs.mkdir(path.join(archiveDir, '2025-01-15-valid-one'), { recursive: true });
      await fs.mkdir(path.join(archiveDir, 'not-a-date-format'), { recursive: true });
      await fs.mkdir(path.join(archiveDir, '2025-02-20-valid-two'), { recursive: true });

      const listCommand = new ListCommand();
      await listCommand.execute(tempDir, 'archive');

      const archiveLines = logOutput.filter(line => 
        line.includes('valid-one') || line.includes('valid-two')
      );
      
      expect(archiveLines.length).toBe(2);
      expect(logOutput.some(line => line.includes('not-a-date-format'))).toBe(false);
    });
  });
});