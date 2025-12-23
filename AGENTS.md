# AGENTS

<plan_mode_instruction priority="high">
When the user requests a plan, enters "plan mode", asks "how would you approach...", or is working on a complex task (3+ distinct steps):

1. Invoke the `plan-mode` skill to load the planning workflow
2. Follow the structured planning phases: Understand -> Research -> Structure -> Output
3. Ask maximum 2 clarifying questions only when critical information is missing
4. Output a Markdown plan with: Goal, Context, Approach, Steps, Assumptions, Risks, Implementation Todos (ID/task/dependencies/status)

This ensures consistent, actionable plans across Cursor, Claude, and Codex.
</plan_mode_instruction>

<plan_completion_workflow priority="high">
When a plan has been completed (all todos marked as `status: completed`), agents MUST follow this workflow:

CRITICAL: After marking the final todo as completed, you MUST verify the completion workflow ran.
If automation fails or is uncertain, you MUST manually run:
`python scripts/execute_plan_completion.py <plan_file>`
Then run: `python scripts/validate_plan_completion.py`

Enforcement Layers (all mandatory):
1. Post-todo hook (blocking, fails on errors)
2. Pre-session plan check (blocks on missing WorkDone entries)
3. Repo validation (fails when workflow skipped)
4. Explicit CRITICAL reminders in this section
5. Manual fallback command (mandatory if automation fails)

0. **Skill Check** (BEFORE writing completion summary)
   - Check for relevant skills using the skill-checking requirement above
   - If `using-skills` or other skills apply, invoke them first
   - Even cleanup tasks should check for skills

1. **Completion Detection**
   - A plan is considered complete when ALL todos in the plan file's frontmatter have `status: completed`
   - Check plan files in `.cursor/plans/` AND `~/.cursor/plans/` for completion status
   - Parse the YAML frontmatter to read todos array and verify all statuses

2. **WorkDone.md Entry Format**
   - Location: `docs/WorkDone.md`
   - Format: Each completed plan gets a structured entry with YAML frontmatter followed by Markdown content
   - Required fields in frontmatter:
     - `plan_name`: Name from plan file frontmatter (or filename if missing)
     - `completed_at`: ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ)
     - `plan_file`: Relative path to the plan file (e.g., `.cursor/plans/plan_name.plan.md`)
     - `todos_count`: Total number of todos completed
     - `status`: Always "completed"
   - Content structure:
     ```markdown
     ---
     plan_name: [Plan Name]
     completed_at: [ISO timestamp]
     plan_file: [relative path]
     todos_count: [number]
     status: completed
     ---
     
     ## Plan: [Plan Name]
     
     **Completed:** [ISO timestamp]
     
     **Overview:** [Brief overview from plan frontmatter]
     
     ### Completed Todos
     [List all completed todos with their IDs and descriptions]
     
     ### Summary
     [Brief summary of what was accomplished]
     ```

3. **Writing Completion Summary**
   - Read existing `docs/WorkDone.md` content (create file if it doesn't exist)
   - Append new entry to the end of the file
   - Use atomic operation: read entire file -> append new entry -> write back
   - Include all completed todos with their IDs and descriptions
   - Add a brief summary of accomplishments

4. **Plan File Deletion**
   - ONLY delete the plan file AFTER successfully writing to WorkDone.md
   - Verify write operation succeeded before deletion
   - Delete plan file from `.cursor/plans/` directory
   - If write fails, do NOT delete plan file (preserve for retry)

5. **Multi-Agent Coordination**
   - When reading WorkDone.md: Read entire file first, then process
   - When writing WorkDone.md: Use atomic read-modify-write pattern
   - Include timestamps in entries to enable chronological ordering
   - If WorkDone.md is locked or in use, wait briefly and retry (max 3 attempts)
   - Never overwrite existing entries - always append
   - Format entries consistently to enable parsing by other agents

**Example WorkDone.md Entry:**
```markdown
---
plan_name: Plan File Cleanup and WorkDone Tracking
completed_at: 2025-01-15T14:30:00Z
plan_file: .cursor/plans/plan_file_cleanup_and_workdone_tracking_ea88ad91.plan.md
todos_count: 5
status: completed
---

## Plan: Plan File Cleanup and WorkDone Tracking

**Completed:** 2025-01-15T14:30:00Z

**Overview:** Update AGENTS.md to instruct agents to automatically delete plan files after completion and write structured entries to docs/WorkDone.md for multi-agent coordination.

### Completed Todos
- T1: Add `<plan_completion_workflow>` section to AGENTS.md with completion detection logic
- T2: Define WorkDone.md entry format (frontmatter + structured content)
- T3: Add instructions for writing completion summary to WorkDone.md
- T4: Add instructions for deleting plan file after successful write
- T5: Add coordination rules for multi-agent access to WorkDone.md

### Summary
Successfully added plan completion workflow instructions to AGENTS.md, defining the structured format for WorkDone.md entries, completion detection logic, and multi-agent coordination rules. The workflow ensures plan files are cleaned up after successful summary writing.
```

This ensures consistent plan cleanup and work tracking across all agents.

## Automation

The completion workflow is **automated** to prevent agents from skipping it:

1. **Post-Todo Hook** (`.claude/hooks/post-todo-completion-check.js`)
   - Automatically runs after `todo_write` operations
   - Detects when all todos in a plan are completed
   - Triggers the completion workflow automatically

2. **Pre-Session Plan Check** (`.claude/hooks/pre-session-plan-check.js`)
   - Runs at session start
   - Detects completed plans missing WorkDone entries
   - Blocks the session with explicit remediation steps

3. **Workflow Executor** (`scripts/execute_plan_completion.py`)
   - Executes the completion workflow programmatically
   - Writes WorkDone.md entry atomically
   - Deletes plan file after successful write

4. **Validation** (`scripts/validate_plan_completion.py`)
   - Validates that completed plans have WorkDone.md entries
   - Detects when workflow was skipped
   - Integrated into `validate_repo.py` for standard checks

5. **Todo Sync** (`scripts/sync_plan_todos.py`)
   - Syncs todos from `todo_write` to plan file frontmatter
   - Ensures plan files have accurate todo state for detection

**How It Works:**
- When a todo is marked complete via `todo_write`, the post-todo hook checks if all todos are done
- If all todos are completed, the hook automatically calls `execute_plan_completion.py`
- The executor writes to WorkDone.md and deletes the plan file
- Validation scripts verify the workflow executed correctly

**Manual Override (Mandatory if automation fails):**
```bash
python scripts/execute_plan_completion.py .cursor/plans/plan_name.plan.md
python scripts/validate_plan_completion.py
```
</plan_completion_workflow>

<web_search_policy priority="high">
No `web_search` unless the `deep-research` skill is explicitly invoked and its workflow followed.
If external sources are needed, invoke `deep-research` and perform all searches inside that workflow.
</web_search_policy>

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

# OCR Auto-Invocation (High Priority)
- When any OCR-suitable file (per `skills/ocr/SKILL.md` extensions) is present in context, the assistant **MUST** treat the `ocr` skill as active and follow its workflow automatically, even if the user does not type `/ocr`.
- If multiple skills could apply, **prefer `ocr`** whenever the question involves anything that could plausibly be on the image/PDF (UI text, errors, tables, receipts, documents, screenshots, scans).
- The OCR behavior is a **hard requirement (MUST/ALWAYS)**, not best-effort. Defer only when the user’s intent is clearly non-content-related (e.g., delete/rename file) or they explicitly decline OCR.
- In **auto model-selection mode**, if OCR-suitable files are present, the assistant **MUST** treat the `ocr` skill as active and **MUST** follow all instructions and output format in `skills/ocr/SKILL.md` as a hard constraint, regardless of which model runs.
- When OCR runs (implicitly or explicitly), the assistant **MUST** produce exactly the two sections defined in `skills/ocr/SKILL.md` with the same headings and fenced languages (`text`, `json`); never omit the JSON section and never rename the headings.
