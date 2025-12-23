# Enforce Plan Completion Workflow Execution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make plan completion workflow enforcement unavoidable across Codex, Claude Code, and Cursor.

**Architecture:** Strengthen hooks and validators to detect completed plans in both workspace and home directories, fail loudly on violations, and add explicit CRITICAL reminders plus manual fallback guidance in AGENTS.md. Add automated tests for hook logic and validation scripts; run manual integration checks for workspace/home plan workflows.

**Tech Stack:** Node.js (hooks + node:test), Python (pytest), Markdown (AGENTS.md).

## Goal
Ensure plan completion workflow is enforced with multiple layers: hooks, validators, explicit reminders, and manual fallback instructions.

## Context
- Existing plan file: `.cursor/plans/enforce_plan_completion_workflow_execution_b435caee.plan.md`.
- Hooks/scripts currently live in `.claude/hooks/` and `scripts/` but are not tracked in this branch yet.
- Validation scripts run from `scripts/` and should block if completion workflow is skipped.
- Plan files can exist in both workspace `.cursor/plans/` and home `~/.cursor/plans/`.

## Approach
1. Add tests first (TDD) for post-todo hook logic, pre-session checks, and validation scripts.
2. Update hook scripts to search both plan directories, fail loudly on errors, and emit CRITICAL reminders.
3. Add a pre-session hook to detect skipped completion workflows before any work starts.
4. Integrate plan-completion validation into `validate_repo.py` as blocking errors.
5. Update AGENTS.md with explicit CRITICAL reminders, manual fallback, and enforcement-layer docs.
6. Run manual integration tests for workspace/home plan files and validation failure.

## Steps
1. Add Node tests and update post-todo hook (T1, T2, T5).
2. Add Node tests and implement pre-session hook (T4).
3. Add Python test for hooks config and update `.claude/hooks.json` (T4, T2).
4. Add Python tests and update plan-completion validation + repo validation (T6).
5. Update AGENTS.md with CRITICAL reminders and fallback instructions (T3, T7, T11).
6. Run manual integration tests for workspace/home plan files and validation failures (T8-T10).

## Assumptions
- Node.js is available for running `node --test`.
- `.venv` exists in this worktree for pytest (`./.venv/bin/python`).
- Hooks config is `.claude/hooks.json` (not `.claude/settings.json`).

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Hooks fail silently | H | Exit non-zero on errors + set continueOnError=false |
| Plan files in home directory are ignored | H | Search both workspace and home plan dirs |
| Validation remains non-blocking | H | Promote plan completion violations to errors |
| Manual steps missed | M | Add CRITICAL reminders and manual fallback commands |

## Implementation Todos
| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | Update post-todo hook to check workspace + home plan dirs | – | pending |
| T2 | Make post-todo hook fail loudly on errors | T1 | pending |
| T3 | Add explicit CRITICAL reminders to AGENTS.md | – | pending |
| T4 | Add pre-session validation hook | – | pending |
| T5 | Add post-final-todo explicit reminder in hook | T1 | pending |
| T6 | Make plan completion validation blocking in validate_repo.py | – | pending |
| T7 | Add fallback manual trigger instructions to AGENTS.md | T3 | pending |
| T8 | Test complete workflow with plan in workspace directory | T1, T2 | pending |
| T9 | Test complete workflow with plan in home directory | T1, T2 | pending |
| T10 | Verify validation fails when workflow skipped | T6 | pending |
| T11 | Document enforcement layers | T1-T7 | pending |

---

### Task 1: Post-todo hook tests + behavior updates (T1, T2, T5)

**Files:**
- Create: `scripts/tests/test_post_todo_completion_check.js`
- Create/Modify: `.claude/hooks/post-todo-completion-check.js`

**Step 1: Write failing tests (Node)**

Create `scripts/tests/test_post_todo_completion_check.js`:

```javascript
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
```

**Step 2: Run tests to verify they fail**

Run: `node --test scripts/tests/test_post_todo_completion_check.js`  
Expected: FAIL (missing exports / behavior).

**Step 3: Update post-todo hook implementation**

Replace `.claude/hooks/post-todo-completion-check.js` with:

```javascript
#!/usr/bin/env node
/**
 * Post-Todo Completion Check Hook
 *
 * Detects when all todos in a plan are completed and triggers the completion workflow.
 * This hook runs after todo_write operations to check for plan completion.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

// Find repo root
function findRepoRoot() {
  if (process.env.HOOK_REPO_ROOT) {
    return path.resolve(process.env.HOOK_REPO_ROOT);
  }
  let current = __dirname;
  for (let i = 0; i < 5; i++) {
    const agentsPath = path.join(current, 'AGENTS.md');
    if (fs.existsSync(agentsPath)) {
      return current;
    }
    current = path.dirname(current);
  }
  return path.dirname(__dirname);
}

function getPlanDirectories(repoRoot, homeDir = os.homedir()) {
  const repoPlans = path.join(repoRoot, '.cursor', 'plans');
  const homePlans = path.join(homeDir, '.cursor', 'plans');
  const dirs = [repoPlans, homePlans];
  return [...new Set(dirs)];
}

// Parse YAML frontmatter from plan file
function parsePlanFrontmatter(planPath) {
  const content = fs.readFileSync(planPath, 'utf-8');
  if (!content.startsWith('---')) {
    return null;
  }

  const lines = content.split('\n');
  let endIdx = null;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') {
      endIdx = i;
      break;
    }
  }

  if (endIdx === null) {
    return null;
  }

  const frontmatterStr = lines.slice(1, endIdx).join('\n');
  const frontmatter = {};
  const todos = [];
  let inTodos = false;
  let currentTodo = {};

  for (const line of frontmatterStr.split('\n')) {
    const stripped = line.trim();
    if (!stripped) continue;

    if (stripped.startsWith('todos:')) {
      inTodos = true;
      continue;
    }

    if (inTodos) {
      if (stripped.startsWith('- ')) {
        if (currentTodo.id) {
          todos.push(currentTodo);
        }
        currentTodo = {};
        continue;
      } else if (stripped.includes(':') && !stripped.startsWith('  ')) {
        if (currentTodo.id) {
          todos.push(currentTodo);
        }
        inTodos = false;
        currentTodo = {};
      }

      if (inTodos && currentTodo) {
        if (stripped.includes('id:')) {
          currentTodo.id = stripped.split('id:')[1].trim();
        } else if (stripped.includes('content:')) {
          currentTodo.content = stripped.split('content:')[1].trim();
        } else if (stripped.includes('status:')) {
          currentTodo.status = stripped.split('status:')[1].trim();
        }
      }
    } else {
      if (stripped.includes(':')) {
        const [key, ...valueParts] = stripped.split(':');
        frontmatter[key.trim()] = valueParts.join(':').trim().replace(/^["']|["']$/g, '');
      }
    }
  }

  if (currentTodo.id && inTodos) {
    todos.push(currentTodo);
  }

  if (todos.length > 0) {
    frontmatter.todos = todos;
  }

  return frontmatter;
}

// Check if all todos are completed
function areAllTodosCompleted(todos) {
  if (!todos || todos.length === 0) {
    return false;
  }
  return todos.every(todo => todo.status === 'completed');
}

// Find active plan files across workspace and home
function findActivePlanFiles(repoRoot, homeDir) {
  const planFiles = [];
  const errors = [];

  const planDirs = getPlanDirectories(repoRoot, homeDir);
  for (const plansDir of planDirs) {
    if (!fs.existsSync(plansDir)) {
      continue;
    }

    const files = fs.readdirSync(plansDir);
    for (const file of files) {
      if (!file.endsWith('.plan.md')) {
        continue;
      }

      const planPath = path.join(plansDir, file);
      try {
        const frontmatter = parsePlanFrontmatter(planPath);
        if (frontmatter && frontmatter.todos && frontmatter.todos.length > 0) {
          planFiles.push({
            path: planPath,
            frontmatter: frontmatter,
          });
        }
      } catch (error) {
        errors.push(`Failed to parse plan file: ${planPath} (${error.message})`);
      }
    }
  }

  return { planFiles, errors };
}

// Trigger completion workflow
function triggerCompletionWorkflow(planPath, repoRoot) {
  const executeScript = path.join(repoRoot, 'scripts', 'execute_plan_completion.py');
  if (!fs.existsSync(executeScript)) {
    return { ok: false, error: `Completion workflow script not found: ${executeScript}` };
  }

  try {
    execSync(`python3 "${executeScript}" "${planPath}"`, {
      cwd: repoRoot,
      encoding: 'utf-8',
      stdio: 'inherit',
    });
    return { ok: true };
  } catch (error) {
    return { ok: false, error: `Error executing completion workflow: ${error.message}` };
  }
}

function buildCompletionReminder(planPath, repoRoot) {
  const planPathDisplay = planPath.startsWith(repoRoot)
    ? path.relative(repoRoot, planPath)
    : planPath;
  return [
    'CRITICAL: Plan completed.',
    `If automation failed, run: python3 scripts/execute_plan_completion.py "${planPathDisplay}"`,
    'Then re-run: python3 scripts/validate_plan_completion.py',
  ].join(' ');
}

// Sync todos to plan file (if plan file can be determined from context)
function syncTodosToPlanFile(repoRoot, homeDir, todos) {
  const result = findActivePlanFiles(repoRoot, homeDir);
  if (result.planFiles.length === 1) {
    const plan = result.planFiles[0];
    const syncScript = path.join(repoRoot, 'scripts', 'sync_plan_todos.py');
    if (fs.existsSync(syncScript)) {
      const todosJson = JSON.stringify(todos);
      execSync(`python3 "${syncScript}" "${plan.path}" --todos-json '${todosJson}'`, {
        cwd: repoRoot,
        encoding: 'utf-8',
        stdio: 'ignore',
      });
      return { ok: true };
    }
    return { ok: false, error: `Todo sync script not found: ${syncScript}` };
  }

  if (result.errors.length > 0) {
    return { ok: false, error: result.errors.join('; ') };
  }

  return { ok: false, error: `Expected exactly one active plan, found ${result.planFiles.length}` };
}

function runCompletionChecks({ repoRoot, homeDir, todoContext, dryRun = false }) {
  const errors = [];
  const reminders = [];

  if (todoContext && Array.isArray(todoContext)) {
    try {
      const syncResult = syncTodosToPlanFile(repoRoot, homeDir, todoContext);
      if (!syncResult.ok) {
        errors.push(syncResult.error);
      }
    } catch (error) {
      errors.push(`Failed to sync todos: ${error.message}`);
    }
  }

  const result = findActivePlanFiles(repoRoot, homeDir);
  if (result.errors.length > 0) {
    errors.push(...result.errors);
  }

  for (const plan of result.planFiles) {
    const todos = plan.frontmatter.todos || [];
    if (areAllTodosCompleted(todos)) {
      console.log(`✓ Plan completed: ${path.basename(plan.path)}`);
      console.log(`  Todos completed: ${todos.length}`);

      reminders.push(buildCompletionReminder(plan.path, repoRoot));

      if (!dryRun) {
        const execResult = triggerCompletionWorkflow(plan.path, repoRoot);
        if (execResult.ok) {
          console.log('  ✓ Completion workflow executed');
        } else {
          errors.push(execResult.error);
        }
      }
    }
  }

  return { errors, reminders, exitCode: errors.length > 0 ? 1 : 0 };
}

// Main hook execution
function main() {
  const repoRoot = findRepoRoot();
  let todosFromContext = null;
  if (process.env.TODO_CONTEXT) {
    try {
      todosFromContext = JSON.parse(process.env.TODO_CONTEXT);
    } catch (e) {
      console.error(`Invalid TODO_CONTEXT JSON: ${e.message}`);
      process.exit(1);
    }
  }

  const result = runCompletionChecks({
    repoRoot,
    homeDir: os.homedir(),
    todoContext: todosFromContext,
    dryRun: false,
  });

  result.reminders.forEach(reminder => {
    console.error(reminder);
  });

  if (result.errors.length > 0) {
    console.error('Hook execution errors:');
    result.errors.forEach(error => console.error(`  - ${error}`));
    process.exit(1);
  }

  process.exit(0);
}

if (require.main === module) {
  main();
} else {
  module.exports = {
    parsePlanFrontmatter,
    areAllTodosCompleted,
    findActivePlanFiles,
    getPlanDirectories,
    buildCompletionReminder,
    runCompletionChecks,
  };
}
```

**Step 4: Run tests to verify they pass**

Run: `node --test scripts/tests/test_post_todo_completion_check.js`  
Expected: PASS.

**Step 5: Commit**

```bash
git add .claude/hooks/post-todo-completion-check.js scripts/tests/test_post_todo_completion_check.js
git commit -m "feat: enforce post-todo completion checks across plan dirs"
```

---

### Task 2: Pre-session hook tests + new hook (T4)

**Files:**
- Create: `.claude/hooks/pre-session-plan-check.js`
- Create: `scripts/tests/test_pre_session_plan_check.js`

**Step 1: Write failing tests (Node)**

Create `scripts/tests/test_pre_session_plan_check.js`:

```javascript
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
```

**Step 2: Run tests to verify they fail**

Run: `node --test scripts/tests/test_pre_session_plan_check.js`  
Expected: FAIL (module missing).

**Step 3: Implement pre-session hook**

Create `.claude/hooks/pre-session-plan-check.js`:

```javascript
#!/usr/bin/env node
/**
 * Pre-Session Plan Completion Check Hook
 *
 * Detects completed plans missing WorkDone.md entries at session start.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  parsePlanFrontmatter,
  areAllTodosCompleted,
  getPlanDirectories,
} = require('./post-todo-completion-check.js');

function findRepoRoot() {
  if (process.env.HOOK_REPO_ROOT) {
    return path.resolve(process.env.HOOK_REPO_ROOT);
  }
  let current = __dirname;
  for (let i = 0; i < 5; i++) {
    const agentsPath = path.join(current, 'AGENTS.md');
    if (fs.existsSync(agentsPath)) {
      return current;
    }
    current = path.dirname(current);
  }
  return path.dirname(__dirname);
}

function getCompletedPlans(repoRoot, homeDir) {
  const planDirs = getPlanDirectories(repoRoot, homeDir);
  const completedPlans = [];

  for (const plansDir of planDirs) {
    if (!fs.existsSync(plansDir)) {
      continue;
    }
    const files = fs.readdirSync(plansDir).filter(file => file.endsWith('.plan.md'));
    for (const file of files) {
      const planPath = path.join(plansDir, file);
      const frontmatter = parsePlanFrontmatter(planPath);
      if (!frontmatter || !frontmatter.todos) {
        continue;
      }
      if (areAllTodosCompleted(frontmatter.todos)) {
        completedPlans.push({
          planName: frontmatter.name || path.basename(planPath, '.plan.md'),
          planPath,
        });
      }
    }
  }

  return completedPlans;
}

function getWorkDonePlanNames(repoRoot) {
  const workdonePath = path.join(repoRoot, 'docs', 'WorkDone.md');
  if (!fs.existsSync(workdonePath)) {
    return new Set();
  }
  const content = fs.readFileSync(workdonePath, 'utf8');
  const matches = content.match(/plan_name:\s*([^\n]+)/g) || [];
  return new Set(matches.map(match => match.split(':')[1].trim()));
}

function findMissingWorkDoneEntries(repoRoot, homeDir) {
  const completedPlans = getCompletedPlans(repoRoot, homeDir);
  const workDonePlans = getWorkDonePlanNames(repoRoot);
  return completedPlans.filter(plan => !workDonePlans.has(plan.planName));
}

function main() {
  try {
    const repoRoot = findRepoRoot();
    const missing = findMissingWorkDoneEntries(repoRoot, os.homedir());

    if (missing.length > 0) {
      console.error('CRITICAL: Completed plans missing WorkDone.md entries:');
      missing.forEach(plan => {
        console.error(`- ${plan.planName}: ${plan.planPath}`);
        console.error(`  Run: python3 scripts/execute_plan_completion.py "${plan.planPath}"`);
      });
      console.error('Then run: python3 scripts/validate_plan_completion.py');
      process.exit(1);
    }

    process.exit(0);
  } catch (error) {
    console.error(`Pre-session plan check failed: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
} else {
  module.exports = { findMissingWorkDoneEntries };
}
```

**Step 4: Run tests to verify they pass**

Run: `node --test scripts/tests/test_pre_session_plan_check.js`  
Expected: PASS.

**Step 5: Commit**

```bash
git add .claude/hooks/pre-session-plan-check.js scripts/tests/test_pre_session_plan_check.js
git commit -m "feat: add pre-session plan completion check hook"
```

---

### Task 3: Hook configuration enforcement (T2, T4)

**Files:**
- Create: `scripts/tests/test_hooks_config.py`
- Create/Modify: `.claude/hooks.json`
- Create: `.claude/hooks/pre-task-skill-check.js` (copy current version if missing)

**Step 1: Write failing test (pytest)**

Create `scripts/tests/test_hooks_config.py`:

```python
import json
from pathlib import Path


def test_hooks_config_enforces_plan_completion():
  config_path = Path(".claude/hooks.json")
  assert config_path.exists()

  config = json.loads(config_path.read_text())
  hooks = config.get("hooks", {})

  post_tool = hooks.get("PostToolUse", [])
  todo_hooks = [h for h in post_tool if h.get("matcher") == "^todo_write$"]
  assert todo_hooks
  hook = todo_hooks[0]["hooks"][0]
  assert hook.get("continueOnError") is False
  assert hook.get("async") is False

  session_start = hooks.get("SessionStart", [])
  assert session_start
  scripts = [h["script"] for block in session_start for h in block.get("hooks", [])]
  assert ".claude/hooks/pre-session-plan-check.js" in scripts
```

**Step 2: Run tests to verify they fail**

Run: `./.venv/bin/python -m pytest scripts/tests/test_hooks_config.py -q`  
Expected: FAIL (hooks.json missing or not configured).

**Step 3: Update hooks config**

Replace `.claude/hooks.json` with:

```json
{
  "hooks": {
    "enabled": true,
    "debug": false,
    "timeout": 5000,
    "PreToolUse": [
      {
        "matcher": "^(Write|Edit|MultiEdit|read_file|grep|codebase_search|run_terminal_cmd)$",
        "hooks": [
          {
            "type": "script",
            "script": ".claude/hooks/pre-task-skill-check.js",
            "timeout": 3000,
            "continueOnError": false
          }
        ]
      },
      {
        "matcher": "^Task$",
        "hooks": [
          {
            "type": "script",
            "script": ".claude/hooks/pre-task-skill-check.js",
            "timeout": 3000,
            "continueOnError": false
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "^todo_write$",
        "hooks": [
          {
            "type": "script",
            "script": ".claude/hooks/post-todo-completion-check.js",
            "timeout": 5000,
            "continueOnError": false,
            "async": false
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "script",
            "script": ".claude/hooks/pre-task-skill-check.js",
            "timeout": 2000,
            "continueOnError": true
          },
          {
            "type": "script",
            "script": ".claude/hooks/pre-session-plan-check.js",
            "timeout": 3000,
            "continueOnError": false
          }
        ]
      }
    ]
  }
}
```

Ensure `.claude/hooks/pre-task-skill-check.js` exists (copy the current version from the main workspace if missing).

**Step 4: Run tests to verify they pass**

Run: `./.venv/bin/python -m pytest scripts/tests/test_hooks_config.py -q`  
Expected: PASS.

**Step 5: Commit**

```bash
git add .claude/hooks.json .claude/hooks/pre-task-skill-check.js scripts/tests/test_hooks_config.py
git commit -m "feat: enforce hooks config for plan completion"
```

---

### Task 4: Plan completion validation + repo validation (T6)

**Files:**
- Create: `scripts/tests/test_validate_plan_completion.py`
- Create: `scripts/tests/test_validate_repo_plan_completion.py`
- Create/Modify: `scripts/validate_plan_completion.py`
- Modify: `scripts/validate_repo.py`

**Step 1: Write failing tests (pytest)**

Create `scripts/tests/test_validate_plan_completion.py`:

```python
from pathlib import Path
from scripts.validate_plan_completion import validate_plan_completion


def write_plan(plan_path: Path, name: str, completed: bool = True):
  status = "completed" if completed else "pending"
  content = "\n".join([
    "---",
    f"name: {name}",
    "todos:",
    f"  - id: T1",
    f"    content: Test",
    f"    status: {status}",
    "---",
    "",
    "# Plan",
  ])
  plan_path.write_text(content, encoding="utf-8")


def test_validate_plan_completion_checks_home_dir(tmp_path: Path):
  repo_root = tmp_path / "repo"
  repo_root.mkdir()
  (repo_root / "AGENTS.md").write_text("# Agents", encoding="utf-8")

  home_root = tmp_path / "home"
  home_root.mkdir()
  home_plans = home_root / ".cursor" / "plans"
  home_plans.mkdir(parents=True)

  plan_path = home_plans / "home.plan.md"
  write_plan(plan_path, "home-plan", completed=True)

  is_valid, violations = validate_plan_completion(repo_root, verbose=False)
  assert not is_valid
  assert any("home-plan" in v for v in violations)
```

Create `scripts/tests/test_validate_repo_plan_completion.py`:

```python
from pathlib import Path
from scripts.validate_repo import validate_repo


def write_plan(plan_path: Path, name: str):
  content = "\n".join([
    "---",
    f"name: {name}",
    "todos:",
    "  - id: T1",
    "    content: Done",
    "    status: completed",
    "---",
    "",
    "# Plan",
  ])
  plan_path.write_text(content, encoding="utf-8")


def test_validate_repo_flags_plan_completion_missing_workdone(tmp_path: Path):
  repo_root = tmp_path / "repo"
  repo_root.mkdir()
  (repo_root / "AGENTS.md").write_text("<name>test-skill</name>", encoding="utf-8")
  skills_dir = repo_root / ".claude" / "skills" / "test-skill"
  skills_dir.mkdir(parents=True)
  (skills_dir / "SKILL.md").write_text("---\nname: test-skill\ndescription: test\n---\n", encoding="utf-8")
  (skills_dir / "LICENSE.txt").write_text("MIT", encoding="utf-8")

  plans_dir = repo_root / ".cursor" / "plans"
  plans_dir.mkdir(parents=True)
  write_plan(plans_dir / "plan.plan.md", "missing-workdone")

  errors = validate_repo(repo_root, verbose=False)
  error_messages = [str(err) for err in errors]
  assert any("WorkDone" in msg or "plan completion" in msg for msg in error_messages)
```

**Step 2: Run tests to verify they fail**

Run: `./.venv/bin/python -m pytest scripts/tests/test_validate_plan_completion.py scripts/tests/test_validate_repo_plan_completion.py -q`  
Expected: FAIL (home dir not checked and validate_repo not enforcing).

**Step 3: Update validation scripts**

Update `scripts/validate_plan_completion.py`:
- Add a helper to search both repo and home plan directories.
- Include home plans in `get_completed_plan_files`.

Patch snippet (update `get_completed_plan_files`):

```python
from pathlib import Path


def get_plan_dirs(repo_root: Path) -> list[Path]:
  return [
    repo_root / ".cursor" / "plans",
    Path.home() / ".cursor" / "plans",
  ]


def get_completed_plan_files(repo_root: Path) -> List[Dict]:
  completed_plans = []
  for plans_dir in get_plan_dirs(repo_root):
    if not plans_dir.exists():
      continue
    for plan_file in plans_dir.glob("*.plan.md"):
      try:
        content = plan_file.read_text(encoding="utf-8")
        frontmatter, _ = parse_yaml_frontmatter(content)
        todos = frontmatter.get("todos", [])
        if todos and all(todo.get("status") == "completed" for todo in todos):
          completed_plans.append({
            "path": plan_file,
            "name": frontmatter.get("name", plan_file.stem),
            "todos_count": len(todos)
          })
      except Exception:
        continue
  return completed_plans
```

Update `scripts/validate_repo.py` to enforce plan completion:

```python
def validate_repo(repo_root: Path, verbose: bool = False) -> list[ValidationError]:
    errors = []
    # existing checks...

    try:
        from validate_plan_completion import validate_plan_completion
        is_valid, violations = validate_plan_completion(repo_root, verbose=False)
        for violation in violations:
            errors.append(ValidationError("plan_completion", violation, severity="error"))
    except Exception as exc:
        errors.append(ValidationError("plan_completion", f"Plan completion validation failed: {exc}", severity="error"))

    return errors
```

**Step 4: Run tests to verify they pass**

Run: `./.venv/bin/python -m pytest scripts/tests/test_validate_plan_completion.py scripts/tests/test_validate_repo_plan_completion.py -q`  
Expected: PASS.

**Step 5: Commit**

```bash
git add scripts/validate_plan_completion.py scripts/validate_repo.py scripts/tests/test_validate_plan_completion.py scripts/tests/test_validate_repo_plan_completion.py
git commit -m "feat: block repo validation on plan completion violations"
```

---

### Task 5: AGENTS.md CRITICAL reminders + manual fallback + enforcement layers (T3, T7, T11)

**Files:**
- Modify: `AGENTS.md`

**Step 1: Update AGENTS.md**

Add a CRITICAL reminder and explicit manual fallback under `<plan_completion_workflow>`, plus an “Enforcement Layers” list and note that home plans are checked. Example snippet:

```markdown
CRITICAL: After marking the final todo as completed, you MUST ensure the completion workflow ran.
If any automation fails, you MUST manually run:
`python scripts/execute_plan_completion.py <plan_file>`
Then run: `python scripts/validate_plan_completion.py`

Enforcement Layers:
1. Post-todo hook (blocking, fails on errors)
2. Pre-session plan check (blocks on missing WorkDone entries)
3. Repo validation (fails when workflow skipped)
4. Explicit CRITICAL reminders in this section
5. Manual fallback command (mandatory if automation fails)

Note: Plan discovery checks BOTH `.cursor/plans/` and `~/.cursor/plans/`.
```

**Step 2: No tests (docs only)**

**Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add critical plan completion reminders and enforcement layers"
```

---

### Task 6: Manual integration tests (T8, T9, T10)

**Files:**
- Temporary: `.cursor/plans/plan_completion_test_workspace.plan.md`
- Temporary: `~/.cursor/plans/plan_completion_test_home.plan.md`

**Step 1: Workspace plan test**

Create a completed plan file in workspace and run the hook:

```bash
cat > .cursor/plans/plan_completion_test_workspace.plan.md <<'EOF'
---
name: plan_completion_test_workspace
overview: test
todos:
  - id: T1
    content: Test completion
    status: completed
---
# Test plan
EOF

node .claude/hooks/post-todo-completion-check.js
```

Expected:
- WorkDone.md entry appended.
- Plan file deleted.
- CRITICAL reminder printed.

**Step 2: Home plan test**

```bash
mkdir -p ~/.cursor/plans
cat > ~/.cursor/plans/plan_completion_test_home.plan.md <<'EOF'
---
name: plan_completion_test_home
overview: test
todos:
  - id: T1
    content: Test completion
    status: completed
---
# Test plan
EOF

node .claude/hooks/post-todo-completion-check.js
```

Expected:
- WorkDone.md entry appended.
- Home plan file deleted.
- CRITICAL reminder printed.

**Step 3: Validation failure test**

```bash
cat > .cursor/plans/plan_completion_test_missing_workdone.plan.md <<'EOF'
---
name: plan_completion_test_missing_workdone
overview: test
todos:
  - id: T1
    content: Test completion
    status: completed
---
# Test plan
EOF

python3 scripts/validate_repo.py
```

Expected:
- Non-zero exit code.
- Error message about missing WorkDone entry.

**Step 4: Cleanup**

Remove test entries from `docs/WorkDone.md` and delete any leftover test plan files.

---

## Execution Handoff

Plan saved to `docs/plans/2025-12-23-enforce-plan-completion-workflow.md`.

Two execution options:
1. Subagent-driven (this session)
2. Parallel session using `superpowers:executing-plans`

Which approach?
