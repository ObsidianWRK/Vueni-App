const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  findMissingWorkDoneEntries,
} = require('../../.claude/hooks/pre-session-plan-check.js');

function writePlanFile(dir, name, todos) {
  const content = [
    '---',
    `name: ${name}`,
    'todos:',
    ...todos.map(todo => `  - id: ${todo.id}\n    content: ${todo.content}\n    status: ${todo.status}`),
    '---',
    '',
    '# Plan',
  ].join('\n');
  fs.mkdirSync(dir, { recursive: true });
  const filePath = path.join(dir, `${name}.plan.md`);
  fs.writeFileSync(filePath, content, 'utf8');
  return filePath;
}

function writeWorkDone(repoRoot, planName) {
  const content = [
    '---',
    `plan_name: ${planName}`,
    'completed_at: 2025-01-01T00:00:00Z',
    'plan_file: .cursor/plans/sample.plan.md',
    'todos_count: 1',
    'status: completed',
    '---',
    '',
  ].join('\n');
  const workdonePath = path.join(repoRoot, 'docs', 'WorkDone.md');
  fs.mkdirSync(path.dirname(workdonePath), { recursive: true });
  fs.writeFileSync(workdonePath, content, 'utf8');
}

test('findMissingWorkDoneEntries reports completed plan without WorkDone entry', () => {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'repo-'));
  const homeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'home-'));

  const plansDir = path.join(repoRoot, '.cursor', 'plans');
  writePlanFile(plansDir, 'completed-plan', [
    { id: 'T1', content: 'Done', status: 'completed' },
  ]);

  const missing = findMissingWorkDoneEntries(repoRoot, homeDir);
  assert.equal(missing.length, 1);
  assert.equal(missing[0].planName, 'completed-plan');
});

test('findMissingWorkDoneEntries returns empty when WorkDone entry exists', () => {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'repo-'));
  const homeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'home-'));

  const plansDir = path.join(repoRoot, '.cursor', 'plans');
  writePlanFile(plansDir, 'completed-plan', [
    { id: 'T1', content: 'Done', status: 'completed' },
  ]);

  writeWorkDone(repoRoot, 'completed-plan');
  const missing = findMissingWorkDoneEntries(repoRoot, homeDir);
  assert.equal(missing.length, 0);
});
