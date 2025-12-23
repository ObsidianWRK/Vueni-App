# AGENTS

**Repository:** Vueni-App - AI agent skills and workflows
**Instruction System:** Portable across Cursor, Claude Code, and OpenAI Codex CLI

---

## Operating Contract

This repository provides:
- **Skills**: Specialized capabilities for AI agents (`.claude/skills/`)
- **Workflows**: Plan mode, skill checking, completion tracking
- **Policies**: Development guidelines and enforcement

### For Tool-Specific Instructions
- **Claude Code**: See `.claude/CLAUDE.md` + `.claude/rules/`
- **Cursor**: See `.cursor/rules/`
- **Codex CLI**: This file (AGENTS.md) + nested scopes

---

<skill_checking_requirement priority="1">
<EXTREMELY_IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST read the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY_IMPORTANT>

## The Rule

**Check for skills BEFORE ANY RESPONSE.** This includes clarifying questions. Even 1% chance means invoke the Skill tool first.

```mermaid
flowchart TD
    A[User message received] --> B{Might any skill apply?}
    B -->|yes, even 1%| C[Invoke Skill tool]
    B -->|definitely not| H[Respond including clarifications]
    C --> D[Announce: Using skill to purpose]
    D --> E{Has checklist?}
    E -->|yes| F[Create TodoWrite todo per item]
    E -->|no| G[Follow skill exactly]
    F --> G
    G --> H
```

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |

## Skill Priority

When multiple skills could apply, use this order:

1. **Process skills first** (brainstorming, debugging) - these determine HOW to approach the task
2. **Implementation skills second** (frontend-design, mcp-builder) - these guide execution

"Let's build X" → brainstorming first, then implementation skills.
"Fix this bug" → debugging first, then domain-specific skills.

## Mandatory Pre-Task Checklist

Before responding to ANY user message, you MUST complete this checklist:

1. ☐ List available skills in your mind (from `<skills_system>` section below)
2. ☐ Ask yourself: "Does ANY skill match this request?"
3. ☐ If yes → Use `openskills read <skill-name>` to read and run the skill file
4. ☐ Announce which skill you're using: "I've read the [Skill Name] skill and I'm using it to [purpose]"
5. ☐ Follow the skill exactly

**Responding WITHOUT completing this checklist = automatic failure.**

## Explicit Skill Invocation

- **For Cursor/Claude:** Use `openskills read <skill-name>` command (e.g., `openskills read using-skills`)
- **The `using-skills` skill:** This skill establishes mandatory workflows for finding and using skills. If you're unsure about skill-checking protocol, invoke `using-skills` first.

## Skill Types

**Rigid** (TDD, debugging): Follow exactly. Don't adapt away discipline.

**Flexible** (patterns): Adapt principles to context.

The skill itself tells you which.

## Instructions ≠ Permission to Skip Workflows

Your human partner's specific instructions describe WHAT, not HOW. "Add X" or "Fix Y" doesn't mean skip workflows.

## Violation Examples

These are REAL examples of violations that occurred even after this requirement was added:

### Example 1: Implementing a Plan Without Skill Check
**Violation:**
```
User: "Implement the plan"
Agent: [Immediately starts reading files and making changes]
       [No mention of checking skills]
       [No openskills read command]
```

**Correct Behavior:**
```
User: "Implement the plan"
Agent: [First checks for relevant skills]
       openskills read using-skills
       openskills read plan-mode
       "I've read the using-skills and plan-mode skills and I'm using them to implement the plan correctly."
       [Then proceeds with implementation]
```

### Example 2: Starting Task Without Skill Check
**Violation:**
```
User: "Add authentication to the app"
Agent: read_file("auth.js")
       [Starts implementing immediately]
```

**Correct Behavior:**
```
User: "Add authentication to the app"
Agent: openskills read using-skills
       openskills read frontend-design  # if applicable
       "I've checked for relevant skills. Using frontend-design skill for UI components."
       [Then reads files and implements]
```

### Example 3: Rationalizing Away Skill Check
**Violation:**
```
Agent thinks: "This is just implementing a plan, I don't need to check skills"
Agent: [Proceeds without skill check]
```

**Correct Behavior:**
```
Agent thinks: "This is implementing a plan - plan-mode skill might apply"
Agent: openskills read plan-mode
       [Then proceeds]
```

## Detection Patterns

The validation script (`scripts/validate_skill_checks.py`) detects violations by looking for:

1. **Task triggers without skill checks**: If user message contains words like "implement", "create", "build", "add", "fix" but agent response has no skill check evidence
2. **Tool usage without skill context**: If agent uses tools (read_file, write, etc.) in first 500 chars without mentioning skills
3. **Missing skill announcements**: If agent proceeds without "I've read the [skill] skill" or similar

## Enforcement

Multiple layers enforce this requirement:

1. **AGENTS.md instruction** (this section) - Highest priority, read first
2. **Pre-task hooks** (`.claude/hooks/pre-task-skill-check.js`) - Blocks tool execution without skill checks
3. **Validation scripts** (`scripts/validate_skill_checks.py`) - Detects violations in responses
4. **using-skills skill** - Establishes mandatory workflow

</skill_checking_requirement>

---

<plan_mode_instruction priority="high">
When the user requests a plan, enters "plan mode", asks "how would you approach...", or is working on a complex task (3+ distinct steps):

**STEP 0 (MANDATORY - CANNOT BE SKIPPED):**
- **BEFORE ANY OTHER ACTION**, check for relevant skills using the skill-checking requirement above
- **MUST** invoke `openskills read using-skills` if unsure about skill-checking protocol
- **MUST** check for other potentially relevant skills (plan-mode, skill-creator, etc.)
- **MUST** announce which skills you're using before proceeding
- **VIOLATION**: Starting planning without skill check = automatic failure

**Only after completing Step 0, proceed with:**

1. Invoke the `plan-mode` skill to load the planning workflow
2. Follow the structured planning phases: Understand → Research → Structure → Output
3. Ask maximum 2 clarifying questions only when critical information is missing
4. Output a Markdown plan with: Goal, Context, Approach, Steps, Assumptions, Risks, Implementation Todos (ID/task/dependencies/status)

**Common Violation:** Starting with "Let me read some files first" or "Let me understand the codebase" BEFORE checking skills. This violates Step 0.

**For detailed plan completion workflow**, see `.claude/rules/plan-workflows.md`

This ensures consistent, actionable plans across Cursor, Claude, and Codex.
</plan_mode_instruction>

---

## Additional Policies

**Plan Completion**: See `.claude/rules/plan-workflows.md` for automated plan cleanup and WorkDone.md tracking

**Web Search**: See `.claude/rules/web-search-policy.md` - Only use web_search inside `deep-research` skill workflow

**OCR Auto-Invocation**: See `.claude/rules/ocr-auto-invoke.md` - Automatically invoke OCR skill when OCR-suitable files are present

**Skills Architecture**: See `.claude/rules/skills-architecture.md` for canonical skills location, structure, and validation

---

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke: Bash("openskills read <skill-name>")
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>algorithmic-art</name>
<description>Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing artists' work to avoid copyright violations.</description>
<location>project</location>
</skill>

<skill>
<name>brand-guidelines</name>
<description>Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.</description>
<location>project</location>
</skill>

<skill>
<name>canvas-design</name>
<description>Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static piece. Create original visual designs, never copying existing artists' work to avoid copyright violations.</description>
<location>project</location>
</skill>

<skill>
<name>deep-research</name>
<description>Deep research skill combining Perplexity-style iterative depth with Manus-style parallel breadth. Use when users request "deep research", "research this", "investigate", or need comprehensive analysis with citations. Analyzes queries to select optimal research mode, executes multi-phase searches, and produces rich Markdown reports with inline citations, structured JSON exports, and Mermaid visualizations.</description>
<location>project</location>
</skill>

<skill>
<name>doc-coauthoring</name>
<description>Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps users efficiently transfer context, refine content through iteration, and verify the doc works for readers. Trigger when user mentions writing docs, creating proposals, drafting specs, or similar documentation tasks.</description>
<location>project</location>
</skill>

<skill>
<name>docx</name>
<description>"Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. When Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"</description>
<location>project</location>
</skill>

<skill>
<name>expo-ios-designer</name>
<description>Design iOS-first UIs for Expo/React Native apps: layout, typography, safe areas, motion, haptics, and accessibility aligned with iOS conventions.</description>
<location>project</location>
</skill>

<skill>
<name>frontend-design</name>
<description>Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.</description>
<location>project</location>
</skill>

<skill>
<name>internal-comms</name>
<description>A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newsletters, FAQs, incident reports, project updates, etc.).</description>
<location>project</location>
</skill>

<skill>
<name>mcp-builder</name>
<description>Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).</description>
<location>project</location>
</skill>

<skill>
<name>ocr</name>
<description>Extract accurate text and structured information from screenshots/images. Use when the user provides a screenshot/photo and asks to OCR, transcribe, extract tables or key/value fields, capture UI/error text, or pull specific details from an image. Prioritize fidelity; avoid hallucination; output verbatim text plus structured JSON.</description>
<location>project</location>
</skill>

<skill>
<name>pdf</name>
<description>Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.</description>
<location>project</location>
</skill>

<skill>
<name>plan-mode</name>
<description>Standardized planning workflow for Cursor, Claude, and Codex. Invoke when user requests a plan, enters "plan mode", asks "how would you approach...", or needs structured thinking before implementation. Produces Markdown plans with actionable steps, assumptions, risks, and implementation todos with IDs and dependencies.</description>
<location>project</location>
</skill>

<skill>
<name>pptx</name>
<description>"Presentation creation, editing, and analysis. When Claude needs to work with presentations (.pptx files) for: (1) Creating new presentations, (2) Modifying or editing content, (3) Working with layouts, (4) Adding comments or speaker notes, or any other presentation tasks"</description>
<location>project</location>
</skill>

<skill>
<name>shadcn-ui</name>
<description>Install and use shadcn/ui (Radix-based) components in React/Next.js/Vite projects with Tailwind, theming, and best-practice composition.</description>
<location>project</location>
</skill>

<skill>
<name>skill-creator</name>
<description>Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.</description>
<location>project</location>
</skill>

<skill>
<name>slack-gif-creator</name>
<description>Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like "make me a GIF of X doing Y for Slack."</description>
<location>project</location>
</skill>

<skill>
<name>theme-factory</name>
<description>Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.</description>
<location>project</location>
</skill>

<skill>
<name>web-artifacts-builder</name>
<description>Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.</description>
<location>project</location>
</skill>

<skill>
<name>webapp-testing</name>
<description>Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.</description>
<location>project</location>
</skill>

<skill>
<name>xlsx</name>
<description>"Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xlsm, .csv, .tsv, etc) for: (1) Creating new spreadsheets with formulas and formatting, (2) Reading or analyzing data, (3) Modify existing spreadsheets while preserving formulas, (4) Data analysis and visualization in spreadsheets, or (5) Recalculating formulas"</description>
<location>project</location>
</skill>



</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
