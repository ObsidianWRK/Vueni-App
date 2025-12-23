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
