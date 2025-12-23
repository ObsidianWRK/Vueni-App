# Plan Completion Workflow

**Priority:** High
**Applies to:** All plan-related operations

## Plan Completion Detection

When a plan has been completed (all todos marked as `status: completed`), agents MUST follow this workflow:

### 0. Skill Check (BEFORE writing completion summary)
- Check for relevant skills using the skill-checking requirement
- If `using-skills` or other skills apply, invoke them first
- Even cleanup tasks should check for skills

### 1. Completion Detection
- A plan is considered complete when ALL todos in the plan file's frontmatter have `status: completed`
- Check plan files in `.cursor/plans/` directory for completion status
- Parse the YAML frontmatter to read todos array and verify all statuses

### 2. WorkDone.md Entry Format

**Location:** `docs/WorkDone.md`

**Format:** Each completed plan gets a structured entry with YAML frontmatter followed by Markdown content

**Required fields in frontmatter:**
- `plan_name`: Name from plan file frontmatter (or filename if missing)
- `completed_at`: ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ)
- `plan_file`: Relative path to the plan file (e.g., `.cursor/plans/plan_name.plan.md`)
- `todos_count`: Total number of todos completed
- `status`: Always "completed"

**Content structure:**
```markdown
---
plan_name: [Plan Name]
completed_at: [ISO timestamp]
plan_file: [relative path]
todos_count: [number]
status: completed
---

## Plan: [Plan Name]

**Completed:** [ISO timestamp]

**Overview:** [Brief overview from plan frontmatter]

### Completed Todos
[List all completed todos with their IDs and descriptions]

### Summary
[Brief summary of what was accomplished]
```

### 3. Writing Completion Summary
- Read existing `docs/WorkDone.md` content (create file if it doesn't exist)
- Append new entry to the end of the file
- Use atomic operation: read entire file → append new entry → write back
- Include all completed todos with their IDs and descriptions
- Add a brief summary of accomplishments

### 4. Plan File Deletion
- ONLY delete the plan file AFTER successfully writing to WorkDone.md
- Verify write operation succeeded before deletion
- Delete plan file from `.cursor/plans/` directory
- If write fails, do NOT delete plan file (preserve for retry)

### 5. Multi-Agent Coordination
- When reading WorkDone.md: Read entire file first, then process
- When writing WorkDone.md: Use atomic read-modify-write pattern
- Include timestamps in entries to enable chronological ordering
- If WorkDone.md is locked or in use, wait briefly and retry (max 3 attempts)
- Never overwrite existing entries - always append
- Format entries consistently to enable parsing by other agents

## Example WorkDone.md Entry

```markdown
---
plan_name: Plan File Cleanup and WorkDone Tracking
completed_at: 2025-01-15T14:30:00Z
plan_file: .cursor/plans/plan_file_cleanup_and_workdone_tracking_ea88ad91.plan.md
todos_count: 5
status: completed
---

## Plan: Plan File Cleanup and WorkDone Tracking

**Completed:** 2025-01-15T14:30:00Z

**Overview:** Update AGENTS.md to instruct agents to automatically delete plan files after completion and write structured entries to docs/WorkDone.md for multi-agent coordination.

### Completed Todos
- T1: Add `<plan_completion_workflow>` section to AGENTS.md with completion detection logic
- T2: Define WorkDone.md entry format (frontmatter + structured content)
- T3: Add instructions for writing completion summary to WorkDone.md
- T4: Add instructions for deleting plan file after successful write
- T5: Add coordination rules for multi-agent access to WorkDone.md

### Summary
Successfully added plan completion workflow instructions to AGENTS.md, defining the structured format for WorkDone.md entries, completion detection logic, and multi-agent coordination rules. The workflow ensures plan files are cleaned up after successful summary writing.
```

## Automation

The completion workflow is **automated** to prevent agents from skipping it:

### 1. Post-Todo Hook (`.claude/hooks/post-todo-completion-check.js`)
- Automatically runs after `todo_write` operations
- Detects when all todos in a plan are completed
- Triggers the completion workflow automatically

### 2. Workflow Executor (`scripts/execute_plan_completion.py`)
- Executes the completion workflow programmatically
- Writes WorkDone.md entry atomically
- Deletes plan file after successful write

### 3. Validation (`scripts/validate_plan_completion.py`)
- Validates that completed plans have WorkDone.md entries
- Detects when workflow was skipped
- Integrated into `validate_repo.py` for standard checks

### 4. Todo Sync (`scripts/sync_plan_todos.py`)
- Syncs todos from `todo_write` to plan file frontmatter
- Ensures plan files have accurate todo state for detection

**How It Works:**
- When a todo is marked complete via `todo_write`, the post-todo hook checks if all todos are done
- If all todos are completed, the hook automatically calls `execute_plan_completion.py`
- The executor writes to WorkDone.md and deletes the plan file
- Validation scripts verify the workflow executed correctly

**Manual Override:**
If automation fails, agents can manually run:
```bash
python scripts/execute_plan_completion.py .cursor/plans/plan_name.plan.md
```

**Verification:**
Run validation to check for skipped workflows:
```bash
python scripts/validate_plan_completion.py
```
