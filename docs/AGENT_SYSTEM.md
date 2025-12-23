# Agent Instruction System Architecture

**Version:** 1.0
**Date:** 2025-12-23
**Status:** Production

---

## Overview

The Vueni-App repository implements a **portable agent instruction system** that works consistently across three AI coding tools:
- **Cursor IDE**
- **Claude Code**
- **OpenAI Codex CLI**

The system follows a **canonical → adapter** pattern, ensuring a single source of truth with tool-specific references rather than duplication.

---

## Architecture Principles

### 1. Single Source of Truth
- **AGENTS.md** is the canonical instruction registry
- All tools reference AGENTS.md; no duplication
- Detailed policies extracted to `.claude/rules/`

### 2. Adapters Not Forks
- **Claude Code**: `.claude/CLAUDE.md` + `.claude/rules/` reference AGENTS.md
- **Cursor**: `.cursor/rules/00-operating-contract.mdc` references AGENTS.md
- **Codex CLI**: Reads AGENTS.md directly

### 3. Progressive Disclosure
- Top-level context (AGENTS.md) stays thin (<25KB)
- Details pushed to scoped rules (`.claude/rules/`)
- Eliminates Codex 32KB limit concerns

### 4. No Silent Contradictions
- No overlapping or conflicting instructions
- Deeper scopes explicitly reference canonical sources
- Validation enforces consistency

---

## File Structure

```
Vueni-App/
│
├── AGENTS.md                           # Canonical instruction registry
│   ├── Skill checking (mandatory)
│   ├── Plan mode instruction
│   ├── Skills table (22 skills)
│   └── References to .claude/rules/
│
├── .claude/
│   ├── CLAUDE.md                       # Claude Code index
│   │   └── References AGENTS.md + rules/
│   │
│   ├── rules/                          # Domain-specific policies
│   │   ├── skills-architecture.md      # Skills contract & structure
│   │   ├── plan-workflows.md           # Plan completion automation
│   │   ├── web-search-policy.md        # Web search restrictions
│   │   └── ocr-auto-invoke.md          # OCR auto-invocation
│   │
│   ├── hooks/                          # Execution hooks
│   │   ├── pre-task-skill-check.js     # Enforces skill checking
│   │   ├── pre-session-plan-check.js   # Session plan check
│   │   └── post-todo-completion-check.js  # Auto plan completion
│   │
│   ├── hooks.json                      # Hook configuration
│   └── skills/                         # Canonical skills (22)
│       ├── plan-mode/
│       ├── skill-creator/
│       ├── deep-research/
│       └── ...
│
├── .cursor/
│   └── rules/
│       └── 00-operating-contract.mdc   # alwaysApply: true
│           └── References AGENTS.md
│
├── .codex/
│   └── skills/ → ../.claude/skills/    # Symlink to canonical
│
└── skills/ → .claude/skills/           # Symlink to canonical
```

---

## How It Works in Each Tool

### Cursor IDE

**Instruction Loading:**
1. Loads `.cursor/rules/00-operating-contract.mdc` (alwaysApply: true)
2. Operating contract references AGENTS.md as canonical source
3. User can load additional rules via description matching

**Skills:**
- Accesses skills via symlink: `skills/` → `.claude/skills/`
- Invokes skills via: `openskills read <skill-name>`

**Commands:**
- Slash commands available: `/commit`, `/pr`, `/debug`, `/ocr`, `/refactor`
- Located in `.cursor/commands/`

### Claude Code

**Instruction Loading:**
1. Loads `.claude/CLAUDE.md` as project memory index
2. Loads all `.md` files in `.claude/rules/` as project memory
3. CLAUDE.md references AGENTS.md for canonical instructions

**Skills:**
- Reads directly from `.claude/skills/` (canonical)
- Invokes skills via: `openskills read <skill-name>`

**Hooks:**
- `PreToolUse`: Enforces skill checking before tool execution
- `PostToolUse`: Detects plan completion, triggers automation
- `SessionStart`: Checks for active plans

### OpenAI Codex CLI

**Instruction Loading:**
1. Loads `AGENTS.md` from repository root
2. Walks repo root → CWD, loading at most one file per directory
3. Concatenates files root-down (later overrides earlier)
4. Truncates at `project_doc_max_bytes` (default 32KB)

**Skills:**
- Accesses skills via: `.codex/skills/` → `.claude/skills/` (symlink)
- May use `scripts/sync_skills.py` if symlinks unavailable

**Current State:**
- AGENTS.md: 17,488 bytes (53% of 32KB limit)
- Room for growth: 15,280 bytes remaining

---

## Key Workflows

### Skill Checking (Mandatory)

**Priority:** Highest (non-negotiable)

**Workflow:**
1. Before ANY response (including clarifying questions)
2. Check if ANY skill might apply (even 1% chance)
3. If yes, invoke: `openskills read <skill-name>`
4. Announce usage: "I've read the [Skill Name] skill and I'm using it to [purpose]"
5. Follow skill exactly

**Enforcement:**
- AGENTS.md instructions (highest priority)
- Pre-task hooks (`.claude/hooks/pre-task-skill-check.js`)
- Validation scripts (detects violations)
- `using-skills` skill (establishes workflow)

**See:** `AGENTS.md` <skill_checking_requirement>

### Plan Mode

**Priority:** High

**Trigger:** User requests plan, asks "how would you approach...", or complex task (3+ steps)

**Workflow:**
1. **STEP 0 (MANDATORY)**: Check for skills (using-skills, plan-mode)
2. Invoke `plan-mode` skill
3. Follow phases: Understand → Research → Structure → Output
4. Output Markdown plan with: Goal, Context, Approach, Steps, Assumptions, Risks, Todos

**See:** `AGENTS.md` <plan_mode_instruction>

### Plan Completion (Automated)

**Priority:** High

**Trigger:** All todos in a plan marked as `status: completed`

**Workflow (Automated):**
1. Hook detects completion (`.claude/hooks/post-todo-completion-check.js`)
2. Executor writes structured entry to `docs/WorkDone.md`
3. Plan file deleted from `.cursor/plans/`

**Manual Override:**
```bash
python scripts/execute_plan_completion.py .cursor/plans/plan_name.plan.md
```

**See:** `.claude/rules/plan-workflows.md`

---

## Validation

### Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `validate_repo.py` | Skills structure & registry alignment | `python scripts/validate_repo.py --verbose` |
| `validate_agent_system.py` | Full system validation (5 gates) | `python scripts/validate_agent_system.py --verbose` |
| `validate_plan_completion.py` | Plan completion workflow | `python scripts/validate_plan_completion.py` |

### Validation Gates

| Gate ID | Gate Name | Checks |
|---------|-----------|--------|
| g1 | Instruction Topology | No contradictions, all adapters exist |
| g2 | Codex Limits | AGENTS.md ≤ 32KB, size tracking |
| g3 | Claude Memory | .claude/CLAUDE.md exists, rules valid |
| g4 | Cursor Rules | .cursor/rules/*.mdc conform to types |
| g5 | Skills Quality | SKILL.md structure, no duplication |

### CI/CD

**Workflow:** `.github/workflows/validate.yml`

**Triggers:**
- Push to main/master
- Pull requests to main/master
- Changes to AGENTS.md, .claude/**, .cursor/**, scripts/validate_*.py

**Jobs:**
1. Run `validate_repo.py --verbose`
2. Run `validate_agent_system.py --verbose`

---

## Skills Architecture

### Canonical Location

**Single source:** `.claude/skills/` (22 skills)

**Symlinks:**
- `skills/` → `.claude/skills/`
- `.codex/skills/` → `../.claude/skills/`

### Skill Structure

```
<skill-name>/
├── SKILL.md             # Required: Instructions + YAML frontmatter
├── LICENSE.txt          # Optional: License terms
├── scripts/             # Optional: Executable scripts
├── references/          # Optional: Reference docs
└── assets/              # Optional: Templates/resources
```

### SKILL.md Format

```markdown
---
name: skill-name
description: Brief description for discovery
---

# Skill Name

<purpose>
What this skill does
</purpose>

## When to Invoke
- Trigger 1
- Trigger 2

## Workflow
[Deterministic procedure]

## Required Tools/Permissions
[Capabilities needed]

## Acceptance Tests
[Success criteria]

## Non-Goals
[Explicit exclusions]
```

### Available Skills (22)

algorithmic-art, brand-guidelines, canvas-design, deep-research, doc-coauthoring, docx, expo-ios-designer, frontend-design, internal-comms, mcp-builder, ocr, pdf, plan-mode, pptx, shadcn-ui, skill-creator, slack-gif-creator, template, theme-factory, web-artifacts-builder, webapp-testing, xlsx

**See:** `AGENTS.md` <available_skills> for full descriptions

---

## Policies

### Web Search Policy

**Rule:** Only use `web_search` inside `deep-research` skill workflow

**Rationale:** Ensures structured research, proper citations, comprehensive analysis

**See:** `.claude/rules/web-search-policy.md`

### OCR Auto-Invocation

**Rule:** Automatically invoke `ocr` skill when OCR-suitable files present (png, jpg, pdf, etc.)

**Behavior:** Treat `ocr` skill as active, follow workflow exactly, produce structured output

**See:** `.claude/rules/ocr-auto-invoke.md`

### Skills Architecture

**Canonical location:** `.claude/skills/`

**Validation:** `scripts/validate_skills.py`, `scripts/validate_repo.py`

**Contract:** Required frontmatter (name, description), deterministic procedures, no duplication

**See:** `.claude/rules/skills-architecture.md`

---

## Size Metrics

| File | Size (bytes) | % of Codex Limit |
|------|--------------|------------------|
| AGENTS.md | 17,488 | 53.4% |
| .claude/CLAUDE.md | ~4,000 | N/A (Claude Code) |
| .claude/rules/* (total) | ~15,000 | N/A (Claude Code) |
| .cursor/rules/* (total) | ~6,000 | N/A (Cursor) |

**Codex Limit:** 32,768 bytes (32KB)

**Room for Growth:** 15,280 bytes (46.6% remaining)

---

## Adding New Content

### Adding a Skill

1. Use `skill-creator` skill (recommended):
   ```
   openskills read skill-creator
   ```

2. Or manually:
   ```bash
   # Create skill directory
   mkdir .claude/skills/<skill-name>

   # Create SKILL.md with frontmatter
   # name: skill-name
   # description: ...

   # Register in AGENTS.md <available_skills>
   # Add <skill> entry

   # Validate
   python scripts/validate_repo.py --verbose
   ```

### Adding a Policy

**For all tools (high-priority):**
- Add to `AGENTS.md` (keep inline if <1KB and critical)
- Or extract to `.claude/rules/<policy-name>.md`

**For Claude Code only:**
- Add to `.claude/rules/<policy-name>.md`
- Optional: Use YAML frontmatter for path scoping

**For Cursor only:**
- Add to `.cursor/rules/<policy-name>.mdc`
- Set `alwaysApply: true` or `globs: [...]`

### Adding a Command (Cursor)

```bash
# Create command file
cat > .cursor/commands/<name>.md <<EOF
# Command description
[Instructions for agent]
EOF

# Test command
# In Cursor: /<name>
```

---

## Troubleshooting

### "AGENTS.md exceeds Codex limit"

**Solution 1:** Extract content to `.claude/rules/`
```bash
# Move large policies to .claude/rules/
# Reference them in AGENTS.md
# See: .claude/rules/<policy>.md
```

**Solution 2:** Document override (if needed)
```bash
# In Codex config:
# project_doc_max_bytes = 65536  # 64KB
```

### "Skill not found"

**Check:**
1. Skill exists in `.claude/skills/<skill-name>/`
2. SKILL.md has valid frontmatter
3. Skill registered in AGENTS.md <available_skills>
4. Run: `python scripts/validate_repo.py --verbose`

### "Hook execution failed"

**Check:**
1. `.claude/hooks.json` syntax valid
2. Hook scripts executable: `chmod +x .claude/hooks/*.js`
3. Node.js installed (hooks require Node)
4. Check hook logs in Claude Code output

### "Validation failed"

**Run verbose validation:**
```bash
python scripts/validate_repo.py --verbose
python scripts/validate_agent_system.py --verbose
```

**Check specific gates:**
- g1: AGENTS.md, .claude/CLAUDE.md, .cursor/rules/ exist
- g2: AGENTS.md size ≤ 32KB
- g3: .claude/rules/*.md valid
- g4: .cursor/rules/*.mdc conform to types
- g5: Skills have SKILL.md with frontmatter

---

## References

- **Discovery Report:** `docs/DISCOVERY_REPORT.md` - Initial analysis and decisions
- **Canonical Instructions:** `AGENTS.md` - Single source of truth
- **Claude Code Index:** `.claude/CLAUDE.md` - Project memory index
- **Rules:** `.claude/rules/` - Domain-specific policies
- **Validation:** `scripts/validate_*.py` - Validation scripts
- **CI:** `.github/workflows/validate.yml` - Automated validation
- **Skills Spec:** https://agentskills.io/specification - Official specification

---

**Maintained by:** Agent refactoring system
**Last updated:** 2025-12-23
**Version:** 1.0
