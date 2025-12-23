# Installation Guide: Skills Across Platforms

This guide covers how skills are organized in this repository and how they load in **Claude Code**, **Cursor**, and **OpenAI Codex**.

---

## Repository Structure

Skills are stored in multiple locations to support different platforms:

```
.
├── .claude/skills/      # Canonical source (Claude Code + openskills)
│   ├── plan-mode/
│   ├── skill-creator/
│   ├── deep-research/
│   └── ... (21 skills)
│
├── .codex/skills/       # Mirror for OpenAI Codex
│   └── ... (synced from .claude/skills/)
│
├── skills/              # Curated subset for Cursor
│   ├── plan-mode/
│   ├── skill-creator/
│   └── deep-research/
│
└── AGENTS.md            # Skill registry (lists all available skills)
```

### Which Directory is Used by Each Platform?

| Platform | Primary Directory | Discovery Method |
|----------|------------------|------------------|
| **Claude Code** | `.claude/skills/` | Auto-discovered + `openskills read <name>` |
| **Codex** | `.codex/skills/` | Auto-discovered at startup |
| **Cursor** | `.claude/skills/` | Via `openskills read <name>` (listed in AGENTS.md) |

---

## Claude Code

### How Skills Work

Claude Code automatically discovers skills in:
- **Personal skills**: `~/.claude/skills/`
- **Project skills**: `.claude/skills/` (this repo)

Skills are also available via the `openskills` command:

```bash
openskills read <skill-name>
```

### Available Skills

All skills listed in `AGENTS.md` are available. Key skills include:
- `plan-mode` - Standardized planning workflow
- `skill-creator` - Guide for creating new skills
- `deep-research` - Comprehensive research with citations
- `mcp-builder` - MCP server development guide
- And 17+ more...

### Verify Skills

```bash
openskills read plan-mode
```

---

## OpenAI Codex

### How Skills Work

Codex discovers project skills from `.codex/skills/` at startup.

This repository includes a `.codex/skills/` directory that mirrors `.claude/skills/`, so all skills are automatically available when you open the project in Codex.

### Keep Skills in Sync

If you modify skills in `.claude/skills/`, run the sync script:

```bash
python3 scripts/sync_skills.py
```

This copies all skills from `.claude/skills/` to `.codex/skills/`.

---

## Cursor

### How Skills Work

Cursor uses skills via the `openskills` command. Skills are listed in `AGENTS.md` and loaded from `.claude/skills/`.

The `skills/` directory contains a curated subset of skills for quick reference:
- `plan-mode`
- `skill-creator`
- `deep-research`

### Invoking Skills

Skills are invoked via the `openskills` command:

```bash
openskills read <skill-name>
```

Example:
```bash
openskills read skill-creator
```

---

## Validation

Validate skills to ensure they follow the Agent Skills specification:

```bash
# Validate all skills in .claude/skills/ (canonical source)
python3 scripts/validate_skills.py --all

# Validate Codex mirror
python3 scripts/validate_skills.py --codex

# Validate Cursor subset
python3 scripts/validate_skills.py --cursor

# Validate a specific skill
python3 scripts/validate_skills.py .claude/skills/plan-mode
```

---

## Adding New Skills

Use the `skill-creator` skill:

```bash
openskills read skill-creator
```

Or manually:

1. Create a directory under `.claude/skills/<skill-name>/`
2. Add `SKILL.md` with required frontmatter (`name`, `description`, `license`)
3. Add `LICENSE.txt` with appropriate license text
4. Register the skill in `AGENTS.md`
5. Run validation: `python3 scripts/validate_skills.py .claude/skills/<skill-name>`
6. Sync to Codex: `python3 scripts/sync_skills.py`

---

## Quick Reference

| Task | Command |
|------|---------|
| Load a skill | `openskills read <skill-name>` |
| Validate all skills | `python3 scripts/validate_skills.py --all` |
| Sync to Codex | `python3 scripts/sync_skills.py` |
| List available skills | See `AGENTS.md` |

---

## Resources

- **Agent Skills Specification**: https://agentskills.io/specification
- **Anthropic Skills Repo**: https://github.com/anthropics/skills
- **Claude Code Skills Docs**: https://code.claude.com/docs/en/skills
- **Codex Skills Docs**: https://developers.openai.com/codex/skills
- **Cursor Skills Docs**: https://cursor.com/docs/context/skills
