---
name: Plan
overview: Create a portable Plan Mode skill and wire it into AGENTS.md so Cursor, Claude, and Codex follow a consistent XML-structured planning workflow.
todos: []
---

# Plan Mode skill (Cursor + Claude + Codex)

## What we’ll build

- A **portable Agent Skill package** `plan-mode` (SKILL.md) that defines how “Plan Mode” planning should be done.
- **Repo-level wiring** so the behavior is applied by default when planning is requested.

## Sources to align with

- Cursor Rules + Agent Skills + AGENTS.md: `https://cursor.com/docs/context/rules`, `https://cursor.com/docs/context/skills#agent-skills`
- Agent Skills SKILL.md spec: `https://agentskills.io/specification`
- Claude XML tagging best practices: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags`
- OpenAI prompt engineering (Markdown + XML structuring): `https://platform.openai.com/docs/guides/prompt-engineering`
- Codex AGENTS.md discovery/precedence: `https://developers.openai.com/codex/guides/agents-md`

## Repo changes

- Add [`skills/plan-mode/SKILL.md`](skills/plan-mode/SKILL.md)
    - Frontmatter per spec: `name`, `description`, `license`, optional `compatibility`, optional `metadata`, optional `allowed-tool`.
    - Body: planning workflow + XML prompt template + Markdown plan output contract + examples.
- Add [`skills/plan-mode/reference/REFERENCE.md`](skills/plan-mode/reference/REFERENCE.md)
    - Copy/paste templates for Cursor/Claude/Codex “plan mode”.
    - Notes on enabling in Cursor and how Codex layers `AGENTS.md` / `AGENTS.override.md`.
- Update [`AGENTS.md`](AGENTS.md)
    - Register `plan-mode` in the skills list.
    - Add a short always-on instruction: **when the user requests a plan / plan mode is active, follow the `plan-mode` workflow**.

## Behavior contract (what Plan Mode will do)

- Ask 1–2 clarifying questions when required; otherwise proceed.
- Use XML tags as delimiters for **instructions / examples / context** (consistent tag names; nested tags when helpful).
- Output a concise Markdown plan with actionable steps, assumptions, risks, and implementation todos (IDs + dependencies).

## Validation

- Check the skill directory/name constraints (lowercase + hyphens; directory matches `name`).
- Dry-run with one planning request in each tool (Cursor/Claude/Codex) and confirm the same plan structure is produced.