---
name: Enforce Mandatory Skill Checking for All Agents
overview: Update AGENTS.md and skill system to make skill-checking mandatory and impossible to skip, ensuring agents always check for relevant skills before starting any task.
todos:
  - id: T1
    content: Add `<skill_checking_requirement priority="1">` section to top of AGENTS.md
    status: pending
  - id: T2
    content: Add explicit `using-skills` skill invocation requirement
    status: pending
    dependencies:
      - T1
  - id: T3
    content: Create mandatory pre-task checklist in AGENTS.md
    status: pending
    dependencies:
      - T1
  - id: T4
    content: Update plan-mode instruction to require skill check first
    status: pending
    dependencies:
      - T1
  - id: T5
    content: Update plan_completion_workflow to require skill check
    status: pending
    dependencies:
      - T1
  - id: T6
    content: Update using-skills skill description for better discoverability
    status: pending
  - id: T7
    content: Sync changes to .codex and .claude versions if needed
    status: pending
    dependencies:
      - T1
      - T2
      - T3
      - T4
      - T5
      - T6
---

#Plan: Enforce Mandatory Skill Checking for All Agents

## Goal

Make skill-checking mandatory and impossible to skip by updating AGENTS.md with highest-priority instructions and reinforcing the workflow in multiple enforcement points.

## Context

- The `using-skills` skill exists with strong language but isn't being followed consistently
- Agents are skipping skill checks, especially for "simple" tasks or when working on infrastructure files
- AGENTS.md currently has `<plan_mode_instruction>` and `<plan_completion_workflow>` but no universal skill-checking requirement
- Need multiple enforcement layers to prevent agents from rationalizing their way out of skill checks

## Approach

1. Add a highest-priority skill-checking instruction at the top of AGENTS.md (before all other instructions)
2. Reference the `using-skills` skill explicitly in AGENTS.md
3. Add skill-checking to the plan-mode workflow
4. Create a validation pattern that agents must follow before ANY tool use
5. Update `using-skills` skill to be even more explicit about when it applies

## Steps

1. **Add universal skill-checking inst

ruction to AGENTS.md**

    - What: Insert `<skill_checking_requirement priority="1">` section at the very top (before plan_mode_instruction)
    - Where: `AGENTS.md` (line 3, before existing instructions)
    - Why: Highest priority ensures it's read first and cannot be overridden

2. **Reference using-skills skill explicitly in AGENTS.md**

    - What: Add explicit instruction to invoke `using-skills` skill before any task
    - Where: In the new skill-checking requirement section
    - Why: Makes the connection explicit rather than relying on agents to discover it

3. **Add skill-checking to plan-mode workflow**

    - What: Update plan-mode instruction to require skill check BEFORE planning
    - Where: `AGENTS.md` plan_mode_instruction section
    - Why: Even planning tasks should check for skills first

4. **Create pre-task validation checklist**

    - What: Define a mandatory checklist agents must complete before using ANY tools
    - Where: In the skill-checking requirement section
    - Why: Creates a concrete, verifiable step that can't be skipped

5. **Update using-skills skill description**

    - What: Make description more explicit about "always applies" nature
    - Where: `skills/using-skills/SKILL.md` and

`.claude/skills/using-skills/SKILL.md`

    - Why: Ensures skill appears in searches and is recognized as always-relevant

6. **Add skill-checking to plan completion workflow**

    - What: Require skill check before writing to WorkDone.md
    - Where: `AGENTS.md` plan_completion_workflow section
    - Why: Even cleanup tasks should check for skills

## Assumptions

- Agents read AGENTS.md from top to bottom, so highest priority instructions are seen first
- Multiple reinforcement points increase compliance
- Explicit references to `using-skills` skill make it harder to skip
- Priority="1" ensures this instruction takes precedence over others

## Risks & Mitigations

| Risk | Impact | Mitigation ||------|--------|------------|| Agents still skip despite instructions | H | Use multiple enforcement layers, explicit checklist, and priority="1" || Instructions become too verbose | M | Keep core instruction concise, reference skill for details || Performance impact of checking skills | L | Skill checking is fast; cost of missing skills is muchhigher || Agents rationalize "this doesn't apply" | H | Make instruction apply to ALL tasks, no exceptions |

## Implementation Todos

| ID | Task | Depends On | Status ||----|------|------------|--------|| T1 | Add `<skill_checking_requirement priority="1">` section to top of AGENTS.md | – | pending || T2 | Add explicit `using-skills` skill invocation requirement | T1 | pending || T3 | Create mandatory pre-task checklist in AGENTS.md | T1 | pending || T4 | Update plan-mode instruction to require skill check first | T1 | pending || T5 | Update plan_completion_workflow to require skill check | T1 | pending || T6 | Update using-skills skill description for better discoverability | – | pending || T7 | Sync changesto .codex and .claude versions if needed | T1-T6 | pending |