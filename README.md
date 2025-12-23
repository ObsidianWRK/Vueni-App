# Vueni App

A repository for AI agent skills and workflows that extend Claude's capabilities with specialized knowledge and tool integrations. Provides a portable instruction system across Cursor IDE, Claude Code, and OpenAI Codex CLI.

## Repository Structure

```
.
├── AGENTS.md                    # Canonical instruction registry (Codex, all tools)
├── LICENSES.md                  # License summary for all skills
│
├── .claude/
│   ├── CLAUDE.md                # Claude Code project memory index
│   ├── rules/                   # Domain-specific policies (Claude Code)
│   │   ├── skills-architecture.md
│   │   ├── plan-workflows.md
│   │   ├── web-search-policy.md
│   │   └── ocr-auto-invoke.md
│   ├── hooks/                   # Execution hooks
│   │   ├── pre-task-skill-check.js
│   │   ├── pre-session-plan-check.js
│   │   └── post-todo-completion-check.js
│   ├── hooks.json               # Hook configuration
│   └── skills/                  # CANONICAL skills source (22 skills)
│       ├── <skill-name>/
│       │   ├── SKILL.md         # Skill instructions + YAML frontmatter
│       │   ├── LICENSE.txt      # Skill-specific license (optional)
│       │   ├── scripts/         # Optional executable scripts
│       │   ├── references/      # Optional reference docs
│       │   └── assets/          # Optional templates/resources
│       └── ...
│
├── .codex/
│   └── skills/ → ../.claude/skills/  # Symlink to canonical skills
│
├── .cursor/
│   ├── rules/                   # Cursor adapter rules
│   │   └── 00-operating-contract.mdc
│   └── commands/                # Cursor IDE slash commands
│       ├── commit.md
│       ├── debug.md
│       ├── ocr.md
│       ├── pr.md
│       └── refactor.md
│
├── skills/ → .claude/skills/    # Symlink to canonical skills
│
├── scripts/
│   ├── validate_skills.py       # Skills validation
│   ├── validate_repo.py         # Repository validation
│   ├── validate_plan_completion.py
│   ├── execute_plan_completion.py
│   ├── sync_plan_todos.py
│   └── sync_skills.py           # Sync utility (if symlinks unavailable)
│
└── docs/
    ├── WorkDone.md              # Completed plan tracking
    ├── DISCOVERY_REPORT.md      # Agent system architecture analysis
    └── ...
```

## Agent Instruction System

### Single Source of Truth
- **AGENTS.md**: Canonical instruction registry with skill checking, plan mode, and skills table
- **Adapters not forks**: Claude Code and Cursor adapters reference AGENTS.md without duplicating

### Tool-Specific Instructions
- **Codex CLI**: Reads `AGENTS.md` directly
- **Claude Code**: Reads `.claude/CLAUDE.md` + `.claude/rules/` + AGENTS.md
- **Cursor**: Reads `.cursor/rules/` + AGENTS.md

### Skills Architecture
- **Canonical location**: `.claude/skills/` (22 skills)
- **Symlinks**: `skills/` and `.codex/skills/` → `.claude/skills/`
- **No duplication**: Single source, referenced by all tools

## Skills

Skills are modular packages that provide Claude with specialized capabilities. Each skill includes:

- **SKILL.md**: YAML frontmatter (`name`, `description`) + markdown instructions
- **LICENSE.txt**: License terms (optional)
- **Optional resources**: `scripts/`, `references/`, `assets/` directories

### Available Skills

See `AGENTS.md` <available_skills> section for the complete list with descriptions.

**Key Skills:**
- `plan-mode` - Structured planning workflow
- `skill-creator` - Create new skills
- `deep-research` - Comprehensive research with citations
- `frontend-design` - Production-grade UI/UX design
- `ocr` - Extract text from images/screenshots
- `mcp-builder` - Build Model Context Protocol servers
- `using-skills` - Mandatory workflow for skill discovery

### Adding a New Skill

Use the `skill-creator` skill to create new skills:

1. Invoke the skill-creator skill
2. Follow the guided workflow to define your skill
3. Run `python3 scripts/validate_repo.py` to verify the skill structure

Or manually:

1. Create a directory under `.claude/skills/<skill-name>/`
2. Add `SKILL.md` with required frontmatter (`name`, `description`)
3. Add `LICENSE.txt` if applicable
4. Register the skill in `AGENTS.md` <available_skills> section
5. Run validation to confirm

## Workflows

### Skill Checking (Mandatory)
Before ANY response, agents must check if a skill applies:
1. Review available skills in `AGENTS.md`
2. If applicable (even 1% chance), invoke: `openskills read <skill-name>`
3. Announce skill usage
4. Follow skill exactly

Enforced by:
- AGENTS.md instructions (highest priority)
- Pre-task hooks (`.claude/hooks/pre-task-skill-check.js`)
- Validation scripts

### Plan Mode
For complex tasks (3+ steps):
1. Check for skills first
2. Invoke `plan-mode` skill
3. Follow structured workflow: Understand → Research → Structure → Output
4. Output Markdown plan with todos

### Plan Completion (Automated)
When all plan todos are completed:
- Hook detects completion (`.claude/hooks/post-todo-completion-check.js`)
- Writes structured entry to `docs/WorkDone.md`
- Deletes plan file from `.cursor/plans/`

See `.claude/rules/plan-workflows.md` for details.

## Cursor Commands

Custom slash commands for the Cursor IDE:

- `/commit` - Generate conventional commit messages
- `/pr` - Generate PR titles and descriptions
- `/debug` - Debugging workflow
- `/ocr` - OCR workflow for images
- `/refactor` - Refactoring workflow

## Validation

Run the repository validator to check system integrity:

```bash
python3 scripts/validate_repo.py --verbose
```

The validator checks:
- Skill registry alignment (AGENTS.md ↔ `.claude/skills/` directories)
- Required frontmatter fields (`name`, `description`)
- Presence of `LICENSE.txt` in each skill (if applicable)
- No placeholder text in published skills
- Plan completion workflow integrity
- Hook configuration

## CI/CD

Validation runs automatically on:
- Push to main/master branches
- Pull requests to main/master
- Changes to AGENTS.md, .claude/skills/, or validation scripts

Workflow: `.github/workflows/validate.yml`

## Licensing

This repository contains mixed-license content. See `LICENSES.md` for details.

- Most skills are licensed under Apache-2.0
- Some skills (docx, pdf, pptx, xlsx) are proprietary (Anthropic)

**Important**: Due to mixed licensing, keep this repository private unless proprietary components are removed.

## Documentation

- **AGENTS.md** - Canonical instruction registry
- **.claude/CLAUDE.md** - Claude Code project memory index
- **.claude/rules/** - Domain-specific policies (Claude Code)
- **.cursor/rules/** - Cursor adapter rules
- **docs/DISCOVERY_REPORT.md** - Agent system architecture analysis
- **docs/WorkDone.md** - Completed plan tracking

## Contributing

When adding or modifying agent instructions:
1. Update canonical source (AGENTS.md for global, .claude/rules/ for domain-specific)
2. Do NOT duplicate content across tools
3. Use adapters (.claude/CLAUDE.md, .cursor/rules/) to reference canonical sources
4. Run validation before committing
5. Ensure all validation gates pass

## Support

- Validation issues: Check `scripts/validate_repo.py` output
- Skill structure: See `.claude/rules/skills-architecture.md`
- Workflows: See `.claude/rules/plan-workflows.md`
- System architecture: See `docs/DISCOVERY_REPORT.md`
