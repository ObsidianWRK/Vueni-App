---
name: plan-mode
description: Standardized planning workflow for Cursor, Claude, and Codex. Invoke when user requests a plan, enters "plan mode", or needs structured thinking before implementation. Produces Markdown plans with actionable steps, assumptions, risks, and implementation todos with IDs and dependencies.
license: MIT
compatibility: Designed for Cursor, Claude, and Codex
metadata:
  version: 1.0.0
  author: Agent Skills
allowed-tools: read_file codebase_search grep list_dir web_search
---

# Plan Mode Skill

<purpose>
Produce clear, actionable implementation plans that work across Cursor, Claude, and Codex. Plans follow a consistent structure, use XML tags for prompt engineering best practices, and output human-readable Markdown.
</purpose>

## When to Invoke

Trigger this skill when:
- User explicitly asks for a "plan" or enters "plan mode"
- User requests "think through this first" or "plan before implementing"
- Task is complex enough to benefit from structured thinking (3+ distinct steps)
- User asks "how would you approach..." or "what's the strategy for..."

## Planning Workflow

<workflow>

### Phase 1: Understand

<understand>
1. **Parse the request**: Identify the core goal, constraints, and success criteria.
2. **Assess complexity**: Simple (1-2 steps) → skip to output. Complex → proceed.
3. **Check for gaps**: If critical information is missing, ask **1-2 high-leverage clarifying questions** maximum. Otherwise, proceed with reasonable assumptions and document them.
</understand>

### Phase 2: Research (if needed)

<research>
- Explore the codebase to understand existing patterns, conventions, and relevant code.
- Identify dependencies, risks, and integration points.
- Note any constraints from existing architecture.
</research>

### Phase 3: Structure

<structure>
Organize the plan using these sections:
1. **Goal** – One sentence summary of what we're building/changing.
2. **Context** – Relevant background, constraints, existing patterns.
3. **Approach** – High-level strategy (2-4 sentences).
4. **Steps** – Numbered, actionable implementation steps.
5. **Assumptions** – What we're assuming to be true.
6. **Risks** – Potential issues and mitigations.
7. **Implementation Todos** – Machine-parseable task list with IDs and dependencies.
</structure>

### Phase 4: Output

<output_format>
Produce a Markdown plan following this template:

```markdown
# Plan: [Brief Title]

## Goal
[One sentence describing the desired outcome]

## Context
[Relevant background: existing code, constraints, patterns to follow]

## Approach
[High-level strategy in 2-4 sentences]

## Steps

1. **[Step title]**
   - What: [specific action]
   - Where: [file(s) or location]
   - Why: [rationale]

2. **[Step title]**
   ...

## Assumptions
- [Assumption 1]
- [Assumption 2]

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [H/M/L] | [How to address] |

## Implementation Todos

<!-- Machine-parseable format for task tracking -->
| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | [Task description] | – | pending |
| T2 | [Task description] | T1 | pending |
| T3 | [Task description] | T1 | pending |
| T4 | [Task description] | T2, T3 | pending |
```
</output_format>

</workflow>

## Prompt Engineering Best Practices

<best_practices>

### For Claude (XML Tags)

Use consistent XML tag names as delimiters:
- `<instructions>` for directives
- `<context>` for background information
- `<examples>` for few-shot demonstrations
- `<constraints>` for limitations and rules
- `<thinking>` for chain-of-thought reasoning (internal)
- `<output>` for final response content

Nest tags when relationships matter:
```xml
<planning_request>
  <goal>Build a user authentication system</goal>
  <constraints>
    <constraint>Must use existing database schema</constraint>
    <constraint>OAuth2 required for SSO</constraint>
  </constraints>
</planning_request>
```

### For OpenAI/Codex (Structure Order)

Follow the optimal prompt structure:
1. **Identity** – Who/what the assistant is
2. **Instructions** – What to do
3. **Examples** – Demonstrations (if helpful)
4. **Context** – Input data and background

### For Cursor (MDC Format)

Cursor supports namespaced XML-like directives:
- `<cursor:context>` for project context
- `<cursor:rules>` for specific guidelines
- `<cursor:patterns>` for code patterns

### Universal Principles

- Be specific and concrete; avoid vague language
- Prefer numbered steps over bullets for sequences
- Include success criteria so completion is verifiable
- Separate "what" from "how" and "why"

</best_practices>

## Chain-of-Thought Planning

<chain_of_thought>

When planning complex tasks, use explicit reasoning markers:

```xml
<thinking>
Analyzing the request...
- Core goal: [identify main objective]
- Constraints: [list limitations]
- Dependencies: [what needs to happen first]
- Risks: [potential issues]
</thinking>

<reasoning>
Based on analysis:
1. [First logical step and why]
2. [Second step builds on first because...]
3. [Final step completes the goal]
</reasoning>

<plan>
[The actual plan output]
</plan>
```

**When to use chain-of-thought:**
- Multi-step tasks with dependencies
- Ambiguous requirements needing interpretation
- Technical decisions with tradeoffs
- Risk assessment and mitigation planning

</chain_of_thought>

## Output Modes

<output_modes>

Plans can be output in three formats depending on the consumer:

### Human-Readable (Default)
Standard Markdown with `##` headers. Best for developers reading plans.

### Machine-Parseable
XML-tagged sections for automated processing:
```xml
<goal>Add dark mode toggle</goal>
<steps>
  <step id="1">Create CSS variables</step>
  <step id="2" depends="1">Build toggle component</step>
</steps>
<todos format="json">
[{"id": "T1", "task": "...", "status": "pending"}]
</todos>
```

### Hybrid (Recommended for AI Agents)
XML tags wrapping Markdown content:
```xml
<goal>
Add a user-toggleable dark mode setting that persists across sessions.
</goal>

<steps>
1. **Create theme CSS variables**
   - What: Define light/dark color tokens
   - Where: `styles/globals.css`

2. **Add toggle component**
   - What: Switch with sun/moon icons
   - Where: `components/ThemeToggle.tsx`
</steps>
```

**Selection guidance:**
- Use **Human-Readable** for direct developer consumption
- Use **Machine-Parseable** when plans feed into automation
- Use **Hybrid** for AI agent workflows (best of both)

</output_modes>

## Clarifying Questions

<clarifying_questions>
When information gaps exist, ask targeted questions:

**Good questions** (high-leverage):
- "Should this integrate with the existing auth system, or be standalone?"
- "What's the expected scale: tens, thousands, or millions of users?"

**Avoid** (low-value):
- "Can you tell me more about what you want?"
- "What technology stack do you prefer?" (when it's obvious from context)

**Rules**:
- Maximum 2 questions per planning request
- Skip questions if reasonable defaults exist
- Document assumptions when proceeding without answers
</clarifying_questions>

## Examples

<examples>

### Example 1: Simple Request (No Questions Needed)

**User**: "Add a dark mode toggle to the settings page"

**Plan Output**:
```markdown
# Plan: Dark Mode Toggle

## Goal
Add a user-toggleable dark mode setting that persists across sessions.

## Context
The app uses Tailwind CSS with CSS variables for theming. Settings page exists at `/settings`.

## Approach
Add a toggle component to settings, wire it to localStorage for persistence, and use CSS variables to switch themes.

## Steps
1. **Create theme CSS variables**
   - What: Define light/dark color tokens in CSS
   - Where: `styles/globals.css`
   - Why: Enables theme switching without JS re-renders

2. **Add toggle component**
   - What: Switch component with sun/moon icons
   - Where: `components/ThemeToggle.tsx`
   - Why: Reusable, accessible toggle

3. **Wire persistence**
   - What: Read/write preference to localStorage, respect `prefers-color-scheme`
   - Where: `hooks/useTheme.ts`
   - Why: Persists across sessions, respects OS preference

4. **Integrate into settings**
   - What: Add ThemeToggle to settings page
   - Where: `pages/settings.tsx`
   - Why: User-accessible control

## Assumptions
- Tailwind CSS is already configured
- Settings page has a "Preferences" section

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Flash of wrong theme on load | M | Use blocking script in `<head>` |

## Implementation Todos
| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | Define CSS variables for light/dark themes | – | pending |
| T2 | Create useTheme hook with localStorage | – | pending |
| T3 | Build ThemeToggle component | T2 | pending |
| T4 | Add toggle to settings page | T1, T3 | pending |
```

### Example 2: Complex Request (Questions First)

**User**: "Build a notification system"

**Agent Response**:
> Before planning, I have two quick questions:
> 1. Should notifications be real-time (WebSocket) or polling-based?
> 2. Do you need push notifications (mobile/desktop), or just in-app?

</examples>

## Integration Notes

<integration>

### Cursor
- This skill is auto-invoked when users request plans (via `AGENTS.md` instruction)
- Works with Cursor's native todo system for task tracking
- Compatible with Agent Skills import

### Claude
- Use the XML prompt template in `references/REFERENCE.md` for system prompts
- XML tags serve as delimiters for clean parsing

### Codex
- `AGENTS.md` instruction ensures plan mode is applied automatically
- Supports `AGENTS.override.md` for per-directory customization
- Compatible with Codex's Markdown-first output style

</integration>
