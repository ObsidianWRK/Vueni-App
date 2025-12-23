---
name: Plan
overview: Create a portable “Plan Mode” skill package and wire it into this repo’s `AGENTS.md` so Cursor + Claude + Codex all follow the same XML-structured planning workflow and output format.
todos: []
---

# Plan Mode Skill (Cursor + Claude + Codex)

## Goals

- Add a **portable “Plan Mode” skill** that standardizes how planning is done across Cursor, Claude, and Codex.
- Ensure the plan workflow follows:
    - Cursor’s **Agent Skills + AGENTS.md** guidance (`https://cursor.com/docs/context/rules`, `https://cursor.com/docs/context/skills#agent-skills`)
    - Agent Skills **SKILL.md** spec (`https://agentskills.io/specification`)
    - Claude’s latest **XML tagging best practices** (`https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags`)
    - OpenAI/Codex **prompt engineering + Markdown/XML message structuring** (`https://platform.openai.com/docs/guides/prompt-engineering`)
    - Codex’s **AGENTS.md discovery/precedence** (`https://developers.openai.com/codex/guides/agents-md`)

## Key design decisions (defaults)

- **Skill name**: `plan-mode` (matches Agent Skills naming constraints and directory name).
- **Primary output**: **Markdown plan** (human-friendly), but the skill will include an **XML prompt template** (for Claude/OpenAI best practice) and an **optional XML-wrapped output mode** if the user asks for machine parsing.
- **“Always invoke” strategy**:
    - **Cursor + Codex**: enforce via **repo `AGENTS.md` instructions** (“when planning / in plan mode, apply the Plan Mode skill workflow”), leveraging that both products read `AGENTS.md` as project guidance.
    - **Cursor Agent Skills**: also ship as an Agent Skill package so Cursor can treat it as an **agent-decided rule** when enabled.
    - **Claude**: ship a copy/paste “Plan Mode system prompt block” in the skill’s reference docs.

## Files to add/change

- Add [`skills/plan-mode/SKILL.md`](skills/plan-mode/SKILL.md)
    - Frontmatter fields per Agent Skills spec: `name`, `description`, `license`, optional `compatibility`, optional `metadata`, optional `allowed-tool`.
    - Body content:
        - Trigger guidance: when user requests planning / “plan mode”.
        - Workflow: ask 1–2 high-leverage clarifying questions when needed; otherwise produce plan.
        - Claude XML best practices: consistent tag names, nested tags when useful, and tag-based separation of **instructions/examples/context**.
        - OpenAI prompt structuring: **Identity → Instructions → Examples → Context**.
        - Output contract: Markdown plan sections + implementation todos (IDs + dependencies).
- Add [`skills/plan-mode/reference/REFERENCE.md`](skills/plan-mode/reference/REFERENCE.md)
    - Copy/paste snippets:
        - Cursor `AGENTS.md` block for “Plan Mode always applies when planning”.
        - Claude “Plan Mode” system prompt template using XML tags.
        - Codex notes: how `AGENTS.md` + `AGENTS.override.md` are discovered/merged; recommended placement.
    - Quick self-check examples (“given this request, here’s the expected plan shape”).
- Update [`AGENTS.md`](AGENTS.md)
    - Register the new skill in `<available_skills>`.
    - Add a short **always-on instruction** at the top: when a user is in “plan mode” / requests a plan, the agent must follow `plan-mode`’s workflow/template.

## Platform wiring notes

- **Cursor**
    - User enables Agent Skills in **Cursor Settings → Rules → Import Settings** (per Cursor docs). Once enabled, Cursor can treat imported skills as **agent-decided rules**.
    - `AGENTS.md` ensures “Plan Mode” behavior is applied even if Agent Skills aren’t enabled.
- **Codex**
    - Codex reads `AGENTS.md` **before doing any work** and supports global + project + nested overrides (per `developers.openai.com/codex/guides/agents-md`).
    - This repo’s `AGENTS.md` will make plan mode behavior the default when planning is requested.
- **Claude**
    - Claude
    - Claude doesn doesn’t auto-read repo files; we’ll provide a **Plan Mode system prompt snippet** (XML-structured) to paste into Claude’s project/system instructions.

## Validation checklist

- Confirm `skills/plan-mode/SKILL.md` frontmatter conforms to Agent Skills constraints (name matches directory; description includes keywords for planning).
- Confirm `AGENTS.md` includes the new skill and the plan-mode always-on instruction.
- Run a quick manual “plan request” against each product (Cursor/Codex/Claude) and verify:
    - Clarifying questions appear when required.
    - Output follows the agreed plan format (and uses XML tags only as delimiters/templates, unless XML output requested).