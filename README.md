# Vueni App

A repository for AI agent skills and Cursor IDE commands that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

## Repository Structure

```
.
├── AGENTS.md                    # Skill registry for AI agents
├── LICENSES.md                  # License summary for all skills
├── .claude/
│   └── skills/                  # Canonical skill source (Claude Code)
│       ├── <skill-name>/
│       │   ├── SKILL.md         # Skill instructions + frontmatter
│       │   ├── LICENSE.txt      # Skill-specific license
│       │   ├── scripts/         # Optional executable scripts
│       │   ├── references/      # Optional reference docs
│       │   └── assets/          # Optional templates/resources
│       └── ...
├── .codex/
│   └── skills/                  # Mirror for OpenAI Codex
│       └── ...                  # (synced from .claude/skills/)
├── skills/                      # Curated subset for Cursor
│   ├── plan-mode/
│   ├── skill-creator/
│   └── deep-research/
├── .cursor/
│   └── commands/                # Cursor IDE slash commands
│       ├── commit.md
│       ├── deslop.md
│       └── pr.md
└── scripts/
    ├── validate_skills.py       # Skill validation script
    ├── validate_repo.py         # Repository validation script
    └── sync_skills.py           # Sync skills to .codex/skills/
```

## Skills

Skills are modular packages that provide Claude with specialized capabilities. Each skill includes:

- **SKILL.md**: YAML frontmatter (`name`, `description`, `license`) + markdown instructions
- **LICENSE.txt**: License terms for the skill
- **Optional resources**: `scripts/`, `references/`, `assets/` directories

### Available Skills

See `AGENTS.md` for the complete list of available skills with descriptions.

### Adding a New Skill

Use the `skill-creator` skill to create new skills:

1. Invoke the skill-creator skill
2. Follow the guided workflow to define your skill
3. Run `python3 scripts/validate_repo.py` to verify the skill structure

Or manually:

1. Create a directory under `.claude/skills/<skill-name>/`
2. Add `SKILL.md` with required frontmatter (`name`, `description`, `license`)
3. Add `LICENSE.txt` with appropriate license text
4. Register the skill in `AGENTS.md`
5. Run validation to confirm

## Cursor Commands

Custom slash commands for the Cursor IDE:

- `/commit` - Generate conventional commit messages
- `/deslop` - Remove AI-generated filler text
- `/pr` - Generate PR titles and descriptions

## Validation

Run the repository validator to check skill structure and consistency:

```bash
python3 scripts/validate_repo.py
```

The validator checks:
- Skill registry alignment (AGENTS.md ↔ skill directories)
- Required frontmatter fields (`name`, `description`, `license`)
- Presence of `LICENSE.txt` in each skill
- No placeholder text in published skills

## Licensing

This repository contains mixed-license content. See `LICENSES.md` for details.

- Most skills are licensed under Apache-2.0
- Some skills (docx, pdf, pptx, xlsx) are proprietary (Anthropic)

**Important**: Due to mixed licensing, keep this repository private unless proprietary components are removed.
