const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  getPlanDirectories,
  findActivePlanFiles,
  buildCompletionReminder,
  runCompletionChecks,
} = require('../../.claude/hooks/post-todo-completion-check.js');

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

test('getPlanDirectories includes repo and home .cursor/plans', () => {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'repo-'));
  const homeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'home-'));

  const dirs = getPlanDirectories(repoRoot, homeDir);
  const repoPlans = path.join(repoRoot, '.cursor', 'plans');
  const homePlans = path.join(homeDir, '.cursor', 'plans');

  assert.ok(dirs.includes(repoPlans));
  assert.ok(dirs.includes(homePlans));
});

test('findActivePlanFiles returns plan files from repo and home dirs', () => {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'repo-'));
  const homeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'home-'));

  const repoPlansDir = path.join(repoRoot, '.cursor', 'plans');
  const homePlansDir = path.join(homeDir, '.cursor', 'plans');

  writePlanFile(repoPlansDir, 'repo-plan', [
    { id: 'T1', content: 'Do repo thing', status: 'completed' },
  ]);
  writePlanFile(homePlansDir, 'home-plan', [
    { id: 'T1', content: 'Do home thing', status: 'completed' },
  ]);

  const result = findActivePlanFiles(repoRoot, homeDir);
  const planNames = result.planFiles.map(item => item.frontmatter.name);

  assert.equal(result.errors.length, 0);
  assert.ok(planNames.includes('repo-plan'));
  assert.ok(planNames.includes('home-plan'));
});

test('buildCompletionReminder includes manual command', () => {
  const reminder = buildCompletionReminder('/tmp/sample.plan.md', '/tmp/repo');
  assert.ok(reminder.includes('python3'));
  assert.ok(reminder.includes('execute_plan_completion.py'));
});

test('runCompletionChecks reports error when execute script missing', () => {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'repo-'));
  const plansDir = path.join(repoRoot, '.cursor', 'plans');

  writePlanFile(plansDir, 'missing-exec', [
    { id: 'T1', content: 'Done', status: 'completed' },
  ]);

  const result = runCompletionChecks({ repoRoot, homeDir: repoRoot, dryRun: false });
  assert.equal(result.exitCode, 1);
  assert.ok(result.errors.length > 0);
});
