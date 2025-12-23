---
name: template
description: Internal scaffold for creating new skills. Not intended for direct use. Use the skill-creator skill to initialize new skills from this template.
---

# Skill Template

This directory serves as an internal scaffold for creating new skills. It is intentionally excluded from the AGENTS.md registry.

To create a new skill, use the `skill-creator` skill which will initialize a new skill directory with proper structure and guidance.

## Template Structure

When creating a new skill, include:
- `SKILL.md` with YAML frontmatter (`name`, `description`, `license`) and markdown instructions
- `LICENSE.txt` with appropriate license text
- Optional subdirectories: `scripts/`, `references/`, `assets/`
