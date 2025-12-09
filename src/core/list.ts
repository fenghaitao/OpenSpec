import { promises as fs } from 'fs';
import path from 'path';
import { getTaskProgressForChange, formatTaskStatus } from '../utils/task-progress.js';
import { readFileSync } from 'fs';
import { join } from 'path';
import { MarkdownParser } from './parsers/markdown-parser.js';

interface ChangeInfo {
  name: string;
  completedTasks: number;
  totalTasks: number;
}

interface ArchivedChangeInfo {
  archiveDate: string;
  changeName: string;
  completedTasks: number;
  totalTasks: number;
}

export class ListCommand {
  async execute(targetPath: string = '.', mode: 'changes' | 'specs' | 'archive' = 'changes'): Promise<void> {
    if (mode === 'archive') {
      await this.listArchivedChanges(targetPath);
      return;
    }

    if (mode === 'changes') {
      const changesDir = path.join(targetPath, 'openspec', 'changes');
      
      // Check if changes directory exists
      try {
        await fs.access(changesDir);
      } catch {
        throw new Error("No OpenSpec changes directory found. Run 'openspec init' first.");
      }

      // Get all directories in changes (excluding archive)
      const entries = await fs.readdir(changesDir, { withFileTypes: true });
      const changeDirs = entries
        .filter(entry => entry.isDirectory() && entry.name !== 'archive')
        .map(entry => entry.name);

      if (changeDirs.length === 0) {
        console.log('No active changes found.');
        return;
      }

      // Collect information about each change
      const changes: ChangeInfo[] = [];
      
      for (const changeDir of changeDirs) {
        const progress = await getTaskProgressForChange(changesDir, changeDir);
        changes.push({
          name: changeDir,
          completedTasks: progress.completed,
          totalTasks: progress.total
        });
      }

      // Sort alphabetically by name
      changes.sort((a, b) => a.name.localeCompare(b.name));

      // Display results
      console.log('Changes:');
      const padding = '  ';
      const nameWidth = Math.max(...changes.map(c => c.name.length));
      for (const change of changes) {
        const paddedName = change.name.padEnd(nameWidth);
        const status = formatTaskStatus({ total: change.totalTasks, completed: change.completedTasks });
        console.log(`${padding}${paddedName}     ${status}`);
      }
      return;
    }

    // specs mode
    const specsDir = path.join(targetPath, 'openspec', 'specs');
    try {
      await fs.access(specsDir);
    } catch {
      console.log('No specs found.');
      return;
    }

    const entries = await fs.readdir(specsDir, { withFileTypes: true });
    const specDirs = entries.filter(e => e.isDirectory()).map(e => e.name);
    if (specDirs.length === 0) {
      console.log('No specs found.');
      return;
    }

    type SpecInfo = { id: string; requirementCount: number };
    const specs: SpecInfo[] = [];
    for (const id of specDirs) {
      const specPath = join(specsDir, id, 'spec.md');
      try {
        const content = readFileSync(specPath, 'utf-8');
        const parser = new MarkdownParser(content);
        const spec = parser.parseSpec(id);
        specs.push({ id, requirementCount: spec.requirements.length });
      } catch {
        // If spec cannot be read or parsed, include with 0 count
        specs.push({ id, requirementCount: 0 });
      }
    }

    specs.sort((a, b) => a.id.localeCompare(b.id));
    console.log('Specs:');
    const padding = '  ';
    const nameWidth = Math.max(...specs.map(s => s.id.length));
    for (const spec of specs) {
      const padded = spec.id.padEnd(nameWidth);
      console.log(`${padding}${padded}     requirements ${spec.requirementCount}`);
    }
  }

  private async listArchivedChanges(targetPath: string): Promise<void> {
    const archiveDir = path.join(targetPath, 'openspec', 'changes', 'archive');

    // Check if archive directory exists
    try {
      await fs.access(archiveDir);
    } catch {
      console.log('No archived changes found.');
      return;
    }

    // Get all directories in archive
    const entries = await fs.readdir(archiveDir, { withFileTypes: true });
    const archiveDirs = entries
      .filter(entry => entry.isDirectory())
      .map(entry => entry.name);

    if (archiveDirs.length === 0) {
      console.log('No archived changes found.');
      return;
    }

    // Parse archive directory names and collect information
    const archivedChanges: ArchivedChangeInfo[] = [];

    for (const dirName of archiveDirs) {
      const parsed = this.parseArchiveName(dirName);
      if (!parsed) {
        // Skip directories that don't match the expected pattern
        continue;
      }

      const changeDir = path.join(archiveDir, dirName);
      const progress = await getTaskProgressForChange(archiveDir, dirName);

      archivedChanges.push({
        archiveDate: parsed.date,
        changeName: parsed.name,
        completedTasks: progress.completed,
        totalTasks: progress.total
      });
    }

    if (archivedChanges.length === 0) {
      console.log('No archived changes found.');
      return;
    }

    // Sort by date (newest first)
    archivedChanges.sort((a, b) => b.archiveDate.localeCompare(a.archiveDate));

    // Display results
    console.log('Archived Changes:');
    const padding = '  ';
    const dateWidth = 10; // YYYY-MM-DD
    const nameWidth = Math.max(...archivedChanges.map(c => c.changeName.length));

    for (const change of archivedChanges) {
      const paddedDate = change.archiveDate.padEnd(dateWidth);
      const paddedName = change.changeName.padEnd(nameWidth);
      const status = formatTaskStatus({ total: change.totalTasks, completed: change.completedTasks });
      console.log(`${padding}${paddedDate}  ${paddedName}     ${status}`);
    }
  }

  private parseArchiveName(dirName: string): { date: string; name: string } | null {
    // Expected format: YYYY-MM-DD-<change-name>
    const match = dirName.match(/^(\d{4}-\d{2}-\d{2})-(.+)$/);
    if (!match) {
      return null;
    }
    return {
      date: match[1],
      name: match[2]
    };
  }
}