# Claude Code Project Memory

**Project:** Vueni-App
**Type:** AI Agent Skills Repository
**Purpose:** Portable agent instruction system for Cursor, Claude Code, and Codex CLI

---

## Quick Start

This repository provides a comprehensive agent skills system. Everything you need is organized as follows:

### Primary Instructions
→ **See `AGENTS.md`** for the canonical instruction registry, skill checking requirements, and available skills

### Detailed Policies (this directory)
→ **See `.claude/rules/`** for domain-specific policies and detailed workflows

### Skills
→ **See `.claude/skills/`** for the canonical skills library (22+ specialized capabilities)

---

## Operating Principles

1. **Single Source of Truth**: `AGENTS.md` is the canonical instruction registry
2. **Skills First**: Always check for applicable skills before starting any task
3. **Plan Mode**: Use structured planning for complex tasks (3+ steps)
4. **Completion Tracking**: Automatically track completed plans in `docs/WorkDone.md`

---

## Domain-Specific Rules

Claude Code automatically loads all `.md` files in `.claude/rules/` as project memory. These rules provide detailed policies:

| Rule File | Purpose | Priority |
|-----------|---------|----------|
| `skills-architecture.md` | Skills location, structure, validation | High |
| `plan-workflows.md` | Plan completion and WorkDone.md tracking | High |
| `web-search-policy.md` | Web search restrictions (use deep-research) | High |
| `ocr-auto-invoke.md` | OCR auto-invocation for image files | High |

---

## Key Workflows

### Skill Checking (Mandatory)
Before ANY response, check if a skill applies (even 1% chance):
1. Review available skills in `AGENTS.md`
2. If applicable, invoke: `openskills read <skill-name>`
3. Announce skill usage
4. Follow skill exactly

See `AGENTS.md` <skill_checking_requirement> section for details.

### Planning
For complex tasks or when user requests a plan:
1. Check for skills first (using-skills, plan-mode)
2. Invoke `plan-mode` skill
3. Follow structured workflow: Understand → Research → Structure → Output

See `AGENTS.md` <plan_mode_instruction> and `.claude/rules/plan-workflows.md`.

### Plan Completion (Automated)
When all plan todos are completed:
- Automation: `.claude/hooks/post-todo-completion-check.js` detects completion
- Writes entry to `docs/WorkDone.md` with metadata
- Deletes plan file from `.cursor/plans/`

See `.claude/rules/plan-workflows.md` for full details.

---

## Validation

Run validation before committing:
```bash
python scripts/validate_repo.py --verbose
```

Validates:
- Skills structure and frontmatter
- AGENTS.md registry alignment
- Plan completion workflow
- No placeholder text
- Hook configuration

---

## Hooks

Active Claude Code hooks (configured in `.claude/hooks.json`):

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre-task-skill-check.js` | Before tool use | Enforces skill checking |
| `pre-session-plan-check.js` | Session start | Checks for active plans |
| `post-todo-completion-check.js` | After todo_write | Auto plan completion |

---

## Directory Structure

```
.claude/
├── CLAUDE.md              # This file (project memory index)
├── rules/                 # Domain-specific policies
│   ├── skills-architecture.md
│   ├── plan-workflows.md
│   ├── web-search-policy.md
│   └── ocr-auto-invoke.md
├── hooks/                 # Execution hooks
│   ├── pre-task-skill-check.js
│   ├── pre-session-plan-check.js
│   └── post-todo-completion-check.js
├── hooks.json             # Hook configuration
└── skills/                # Canonical skills library (22+ skills)
    ├── plan-mode/
    ├── skill-creator/
    ├── deep-research/
    ├── frontend-design/
    └── ...
```

---

## For Other Tools

- **Cursor IDE**: See `.cursor/rules/` for Cursor-specific adapters
- **Codex CLI**: Reads `AGENTS.md` directly (root + nested scopes)
- **Skills Sync**: `.codex/skills/` synced from `.claude/skills/` via `scripts/sync_skills.py`

---

## References

- **Canonical Instructions**: `/AGENTS.md`
- **Skills Architecture**: `.claude/rules/skills-architecture.md`
- **Validation**: `scripts/validate_repo.py`
- **CI Workflow**: `.github/workflows/validate.yml`
- **Discovery Report**: `docs/DISCOVERY_REPORT.md`

---

**Reminder:** Always start by checking `AGENTS.md` for skill-checking requirements and available skills. This is non-negotiable.
