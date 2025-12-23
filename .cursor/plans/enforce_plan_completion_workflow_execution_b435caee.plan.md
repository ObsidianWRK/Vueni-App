---
name: Enforce Plan Completion Workflow Execution
overview: Create a multi-layered enforcement system to ensure plan completion workflow executes every single time, fixing hook failures, adding explicit reminders, making validation blocking, and preventing any way to skip the workflow.
todos:
  - id: T1
    content: Fix post-todo hook to check both workspace and home plan directories
    status: pending
  - id: T2
    content: Make hook fail loudly (non-zero exit, stderr logging) on errors
    status: pending
    dependencies:
      - T1
  - id: T3
    content: Add explicit CRITICAL reminders to AGENTS.md plan_completion_workflow
    status: pending
  - id: T4
    content: Create pre-session validation hook to check for completed plans
    status: pending
  - id: T5
    content: Add post-final-todo explicit reminder in hook
    status: pending
    dependencies:
      - T1
  - id: T6
    content: Make validate_plan_completion.py blocking (errors, not warnings) in validate_repo.py
    status: pending
  - id: T7
    content: Add fallback manual trigger instructions to AGENTS.md
    status: pending
    dependencies:
      - T3
  - id: T8
    content: Test complete workflow with plan in workspace directory
    status: pending
    dependencies:
      - T1
      - T2
  - id: T9
    content: Test complete workflow with plan in home directory
    status: pending
    dependencies:
      - T1
      - T2
  - id: T10
    content: Verify validation fails when workflow skipped
    status: pending
    dependencies:
      - T6
  - id: T11
    content: Document all enforcement layers
    status: pending
    dependencies:
      - T1
      - T2
      - T3
      - T4
      - T5
      - T6
      - T7
---

# Plan: Enforce Plan Completion Workflow Execution

## Goal

Create a foolproof, multi-layered enforcement system that makes it **impossible** for agents to skip the plan completion workflow. Fix all existing automation failures and add multiple redundant checks.

## Context

**Current Problem:**

- Automation exists but fails silently
- Hook checks wrong plan file location (`~/.cursor/plans/` vs `.cursor/plans/`)
- Hook exits with 0 even on errors (silent failures)
- Validation exists but only shows warnings (not blocking)
- Agents aren't explicitly reminded
- No pre-session checks for completed plans

**Root Causes:**

1. Plan file location mismatch (workspace vs home directory)
2. Hook fails silently (`process.exit(0)` on errors)
3. Validation is non-blocking (warnings only)
4. No explicit agent reminders in workflow
5. No pre-session validation

## Approach

Create **5 layers of enforcement** that make skipping impossible:

1. **Fix Hook** - Make it robust and check all plan locations
2. **Make Validation Blocking** - Fail validation if workflow skipped
3. **Add Explicit Reminders** - Force agents to acknowledge completion
4. **Pre-Session Check** - Check for completed plans at session start
5. **Post-Todo Reminder** - Explicit reminder after final todo completion

## Steps

### 1. Fix Post-Todo Hook

**What:** Fix the hook to:

- Check both workspace `.cursor/plans/` AND home `~/.cursor/plans/`
- Fail loudly on errors (log to stderr, exit with non-zero)
- Add better error messages
- Check plan file sync status

**Where:** `.claude/hooks/post-todo-completion-check.js`**Why:** Current hook fails silently and misses plans in home directory

### 2. Make Validation Blocking

**What:** Change `validate_plan_completion.py` to:

- Return exit code 1 on violations (currently does this)
- Integrate into `validate_repo.py` as ERROR not warning
- Make it fail CI/CD if workflow skipped

**Where:** `scripts/validate_plan_completion.py`, `scripts/validate_repo.py`**Why:** Warnings are ignored; errors force action

### 3. Add Explicit Reminders to AGENTS.md

**What:** Add explicit reminders in `<plan_completion_workflow>`:

- "CRITICAL: After marking final todo complete, you MUST..."
- Add checklist that agents must follow
- Make it impossible to miss

**Where:** `AGENTS.md` (plan_completion_workflow section)**Why:** Agents need explicit, unmissable instructions

### 4. Add Pre-Session Validation Hook

**What:** Create a session-start hook that:

- Checks for completed plans without WorkDone entries
- Warns agent immediately if found
- Provides command to fix

**Where:** `.claude/hooks/pre-session-plan-check.js`, `.claude/hooks.json`**Why:** Catch violations at session start before work begins

### 5. Add Post-Final-Todo Reminder

**What:** Enhance hook to:

- Detect when final todo is marked complete
- Print explicit reminder: "⚠️ PLAN COMPLETE - You must execute completion workflow"
- Provide exact command to run

**Where:** `.claude/hooks/post-todo-completion-check.js`**Why:** Remind agent at the exact moment completion happens

### 6. Add Validation to Standard Checks

**What:** Ensure `validate_repo.py`:

- Runs plan completion validation as ERROR (not warning)
- Fails entire validation if workflow skipped
- Provides clear fix instructions

**Where:** `scripts/validate_repo.py`**Why:** Make it part of standard quality checks

### 7. Create Fallback Manual Trigger

**What:** Add explicit instruction in AGENTS.md:

- "If automation fails, you MUST manually run: `python scripts/execute_plan_completion.py <plan_file>`"
- Make this a required step, not optional

**Where:** `AGENTS.md`**Why:** Provide fallback that agents must use

## Assumptions

- Hooks system supports both workspace and home directory checks
- Python scripts can access home directory via `os.path.expanduser()`
- Validation can be made blocking without breaking existing workflows
- Agents will follow explicit reminders if they're prominent enough

## Risks & Mitigations

| Risk | Impact | Mitigation ||------|--------|------------|| Hook still fails silently | H | Make hook exit with non-zero on errors; add logging || Plan location still wrong | H | Check both workspace AND home directory || Validation warnings ignored | M | M| Validation warnings ignored | M | Make validation blocking (errorsake validation blocking (errors, not warnings) || Agents skip reminders | H | Make reminders impossible to miss (CRITICAL labels) || Multiple plan files confuse hook | M | Process all completed plans, not just one |

## Implementation Todos

| ID | Task | Dependencies ||----|------|--------------|| T1 | Fix post-todo hook to check both workspace and home plan directories | - || T2 | Make hook fail loudly (non-zero exit, stderr logging) on errors | T1 || T3| Add explicit CRITICAL reminders to AGENTS.md plan_completion_workflow | - || T4 | Create pre-session validation hook to check for completed plans | - || T5 | Add post-final-todo explicit reminder in hook | T1 || T6 | Make validate_plan_completion.py blocking (errors, not warnings) in validate_repo.py | - || T7 | Add fallback manual trigger instructions to AGENTS.md | T3 || T8 | Test complete workflow with plan in workspace directory | T1, T2 || T9 | Test complete workflow with plan in home directory | T1, T2 || T10 | Verify validation fails when workflow skipped | T6 || T11 | Document all enforcement layers | T1-T7 |

## Success Criteria

1. ✅ Hook checks both workspace `.cursor/plans/` AND `~/.cursor/plans/`
2. ✅ Hook fails loudly (non-zero exit) on errors
3. ✅ Validation is blocking (fails CI/CD if workflow skipped)
4. ✅ AGENTS.md has explicit CRITICAL reminders
5. ✅ Pre-session hook warns about completed plans
6. ✅ Post-todo hook provides explicit reminder
7. ✅ All layers tested and working

This creates a **5-layer enforcement system** that makes skipping the workflow impossible.