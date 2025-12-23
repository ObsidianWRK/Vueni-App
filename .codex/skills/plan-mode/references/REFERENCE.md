# Plan Mode Reference

Copy/paste templates and integration notes for Cursor, Claude, and Codex.

---

## Cursor Integration

### AGENTS.md Block

Add this to your repository's `AGENTS.md` to enable Plan Mode:

```xml
<plan_mode_instruction priority="high">
When the user requests a plan, enters "plan mode", or asks "how would you approach..." for a complex task:

1. Invoke the `plan-mode` skill via `Bash("openskills read plan-mode")`
2. Follow the planning workflow defined in the skill
3. Output a structured Markdown plan with:
   - Goal, Context, Approach
   - Numbered implementation steps
   - Assumptions and risks
   - Implementation todos (ID, task, dependencies, status)

Do not skip planning for complex tasks (3+ steps). Ask 1-2 clarifying questions only when critical information is missing.
</plan_mode_instruction>
```

### Enabling Agent Skills in Cursor

1. Open **Cursor Settings** → **Rules**
2. Enable **Agent Skills** in import settings
3. Skills from the `skills/` directory become available as agent-decided rules
4. The skill will auto-trigger when planning keywords are detected

---

## Claude Integration

### System Prompt Template

Add this to your Claude project or conversation system prompt:

```xml
<plan_mode>
<identity>
You are an expert technical planner. When asked to plan, you produce clear, actionable implementation plans.
</identity>

<instructions>
When the user requests a plan or asks "how would you approach..." for a complex task:

1. **Understand**: Parse the goal, constraints, and success criteria
2. **Clarify** (if needed): Ask maximum 2 high-leverage questions when critical info is missing
3. **Research**: Consider existing patterns, dependencies, and risks
4. **Output**: Produce a structured Markdown plan

Your plan must include:
- Goal (one sentence)
- Context (relevant background)
- Approach (2-4 sentence strategy)
- Steps (numbered, with what/where/why)
- Assumptions
- Risks & Mitigations (table format)
- Implementation Todos (table with ID, task, dependencies, status)
</instructions>

<constraints>
- Maximum 2 clarifying questions per request
- Proceed with documented assumptions when reasonable defaults exist
- Be specific and concrete; avoid vague language
- Separate "what" from "how" and "why"
</constraints>

<output_format>
Use this Markdown structure:

# Plan: [Title]

## Goal
[One sentence]

## Context
[Background, constraints, patterns]

## Approach
[High-level strategy]

## Steps
1. **[Title]**
   - What: [action]
   - Where: [location]
   - Why: [rationale]

## Assumptions
- [List assumptions]

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|

## Implementation Todos
| ID | Task | Depends On | Status |
|----|------|------------|--------|
</output_format>
</plan_mode>
```

### Quick Invocation

You can also invoke Plan Mode on-demand by starting your message with:

```
[Plan Mode] Build a user authentication system with OAuth2 support.
```

---

## Codex Integration

### AGENTS.md Discovery

Codex reads `AGENTS.md` before doing any work, following this precedence:

1. `~/.codex/AGENTS.md` (global defaults)
2. Repository root `AGENTS.md` (project defaults)
3. Subdirectory `AGENTS.md` files (directory-specific)
4. `AGENTS.override.md` at any level (final overrides)

### Recommended Setup

Add the Plan Mode instruction to your repository's root `AGENTS.md`:

```markdown
## Plan Mode

When the user requests planning:
- Follow the structured planning workflow
- Output Markdown with: Goal, Context, Approach, Steps, Assumptions, Risks, Todos
- Use the implementation todos table format: | ID | Task | Depends On | Status |
- Ask maximum 2 clarifying questions when critical info is missing
```

### Per-Directory Customization

Create `AGENTS.override.md` in specific directories to customize planning:

```markdown
## Plan Mode Override

For this directory:
- Always consider the existing test patterns in `__tests__/`
- Plans must include a "Testing Strategy" section
- Database migrations require a rollback plan
```

---

## Self-Check Examples

Use these to verify Plan Mode is working correctly.

### Test Case 1: Simple Feature

**Input**: "Add a loading spinner to the submit button"

**Expected**: Direct plan output (no clarifying questions), 2-3 steps, simple todo list.

### Test Case 2: Complex Feature

**Input**: "Build a real-time collaboration system"

**Expected**: 1-2 clarifying questions first (e.g., "What data needs to sync in real-time?" and "How many concurrent users should this support?"), then detailed plan after user responds.

### Test Case 3: Ambiguous Request

**Input**: "Improve the homepage"

**Expected**: Clarifying questions ("What aspect should improve: performance, design, or content?" and "Are there specific metrics or user feedback to address?").

---

## XML Tag Reference

### Consistent Tag Names

Use these tags for prompt engineering:

| Tag | Purpose | Example |
|-----|---------|---------|
| `<instructions>` | Directives for the model | `<instructions>Always output JSON</instructions>` |
| `<context>` | Background information | `<context>The app uses React 18</context>` |
| `<examples>` | Few-shot demonstrations | `<examples><example>...</example></examples>` |
| `<constraints>` | Limitations and rules | `<constraints>Max 100 words</constraints>` |
| `<output_format>` | Expected output structure | `<output_format>Markdown table</output_format>` |

### Nesting Example

```xml
<planning_request>
  <goal>Build authentication system</goal>
  <context>
    <codebase>React + Node.js monorepo</codebase>
    <existing_patterns>JWT tokens for API auth</existing_patterns>
  </context>
  <constraints>
    <constraint>Must support OAuth2 for Google</constraint>
    <constraint>Session timeout: 24 hours</constraint>
  </constraints>
</planning_request>
```

---

## Troubleshooting

### Plan output is too vague

- Ensure the skill workflow is followed (Phase 1-4)
- Check that "what/where/why" format is used for steps
- Verify implementation todos have specific, actionable descriptions

### Too many clarifying questions

- Skill limits to 2 questions maximum
- Proceed with assumptions when reasonable defaults exist
- Document assumptions in the plan's "Assumptions" section

### Platform not recognizing Plan Mode

- **Cursor**: Verify Agent Skills is enabled in settings; check `AGENTS.md` has the skill registered
- **Claude**: Add the system prompt template to project instructions
- **Codex**: Confirm `AGENTS.md` exists in repository root and contains Plan Mode instruction

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01 | Initial release with Cursor, Claude, Codex support |
