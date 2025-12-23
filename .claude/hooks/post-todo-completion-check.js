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
    const rawLine = line;
    const stripped = line.trim();
    if (!stripped) continue;

    if (stripped.startsWith('todos:')) {
      inTodos = true;
      continue;
    }

    if (inTodos) {
      if (stripped.startsWith('- ')) {
        if (Object.keys(currentTodo).length > 0) {
          todos.push(currentTodo);
        }
        currentTodo = {};
        const inline = stripped.slice(2).trim();
        if (inline) {
          const [key, ...valueParts] = inline.split(':');
          const value = valueParts.join(':').trim();
          if (key && value) {
            const normalizedKey = key.trim();
            if (normalizedKey === 'id') {
              currentTodo.id = value;
            } else if (normalizedKey === 'content') {
              currentTodo.content = value;
            } else if (normalizedKey === 'status') {
              currentTodo.status = value;
            }
          }
        }
        continue;
      } else if (stripped.includes(':') && !rawLine.startsWith('  ')) {
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
