# Skills Architecture

**Priority:** High
**Applies to:** All skill operations

## Canonical Skills Location

**Single source of truth:** `.claude/skills/`

All skills are stored in a single canonical location. Other tools reference this location:
- **Claude Code**: Reads directly from `.claude/skills/`
- **Cursor**: References `.claude/skills/` via operating contract
- **Codex CLI**: Uses `.codex/skills/` (synced from canonical or symlinked)

## Skill Structure

Each skill is a directory containing:

### Required
- `SKILL.md` - Skill instructions with YAML frontmatter

### Optional
- `LICENSE.txt` - Skill-specific license
- `scripts/` - Executable scripts
- `references/` or `resources/` - Reference documentation
- `assets/` - Templates and resources

## SKILL.md Format

```markdown
---
name: skill-name
description: Brief description for skill discovery
license: Apache-2.0 (optional)
---

# Skill Name

<purpose>
Clear statement of what this skill does
</purpose>

## When to Invoke
- Trigger condition 1
- Trigger condition 2

## Workflow
[Deterministic procedure]

## Required Tools/Permissions
[List of required capabilities]

## Acceptance Tests
[How to verify success]

## Non-Goals
[What this skill explicitly does not do]
```

## Skill Contract

All skills MUST:
1. Have `SKILL.md` with frontmatter containing `name` and `description`
2. Specify clear "when to invoke" triggers
3. Provide deterministic procedure (not vague guidance)
4. List required tools/permissions
5. Include acceptance tests
6. Define explicit non-goals

All skills MUST NOT:
- Duplicate global policies (reference canonical instructions instead)
- Provide vague or ambiguous procedures
- Overlap with other skills without explicit coordination

## Internal Skills

Skills in `INTERNAL_SKILLS` set (e.g., `template`) are:
- Not listed in AGENTS.md registry
- Used for development/scaffolding only
- Not intended for production use

## Validation

Skills are validated by `scripts/validate_skills.py` and `scripts/validate_repo.py`:
- Frontmatter presence and correctness
- Required fields (name, description)
- No placeholder text in production skills
- Alignment with AGENTS.md registry
- LICENSE.txt presence (if applicable)

## Skill Discovery

Skills are registered in `AGENTS.md` in the `<available_skills>` section:

```xml
<skill>
<name>skill-name</name>
<description>Brief description</description>
<location>project</location>
</skill>
```

This enables:
- Agent awareness of available skills
- Skill invocation via `openskills read <skill-name>`
- Automatic skill checking workflows

## Adding New Skills

Use the `skill-creator` skill:
1. Invoke skill-creator
2. Follow guided workflow
3. Validate with `python3 scripts/validate_repo.py`

Or manually:
1. Create directory under `.claude/skills/<skill-name>/`
2. Add `SKILL.md` with required frontmatter
3. Add `LICENSE.txt` if applicable
4. Register in `AGENTS.md`
5. Run validation

## References

- Skill validation: `scripts/validate_skills.py`
- Repository validation: `scripts/validate_repo.py`
- Skill creator skill: `.claude/skills/skill-creator/`
- Agent Skills Specification: https://agentskills.io/specification
