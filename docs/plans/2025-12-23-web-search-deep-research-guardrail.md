# Web Search Guardrail and Deep-Research Alignment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enforce "no web_search unless deep-research is invoked" across Cursor, Claude, and Codex.

**Architecture:** Use documentation-level guardrails: `AGENTS.md` as the global policy, `skills/plan-mode/SKILL.md` to route any external research to `deep-research`, and `skills/deep-research/SKILL.md` as the sole `web_search` workflow with explicit Perplexity/Manus hybrid guidance.

**Tech Stack:** Markdown docs and skill specs in this repo.

## Goal
Make `deep-research` the only approved path for `web_search` while keeping its hybrid Perplexity/Manus workflow explicit and consistent across guidance.

## Context
- Global instructions live in `AGENTS.md`.
- The only skill specs referencing `web_search` are `skills/deep-research/SKILL.md` and `skills/plan-mode/SKILL.md`.
- Deep-research already describes Perplexity-style depth and Manus-style breadth, but does not declare itself as the exclusive web_search entry point.
- There is no existing `docs/plans/` directory and this repository does not appear to be a git worktree.

## Approach
Add a high-priority guardrail in `AGENTS.md`, remove `web_search` from plan-mode allowed tools, and explicitly require that any external research invoke `deep-research`. Then strengthen the deep-research skill and workflow reference with an explicit guardrail and hybrid framing. Validate with targeted ripgrep checks to ensure no other skills can call `web_search` directly.

## Steps
1. **Add global guardrail**
   - What: Insert a `web_search` policy block in `AGENTS.md`.
   - Where: After `<plan_mode_instruction>` in `AGENTS.md`.
   - Why: Ensures all agents see the rule before touching tools.

2. **Align plan-mode to route research**
   - What: Remove `web_search` from allowed-tools and add a note to invoke `deep-research` for external research.
   - Where: `skills/plan-mode/SKILL.md` header and Research phase.
   - Why: Prevents plan-mode from authorizing web_search directly.

3. **Strengthen deep-research guardrails**
   - What: Explicitly declare deep-research as the only web_search entry point.
   - Where: `skills/deep-research/SKILL.md` purpose/constraints and When to Invoke.
   - Why: Keeps the policy enforceable and obvious in the skill itself.

4. **Update deep-research workflow reference**
   - What: Add a guardrail note and hybrid framing in `skills/deep-research/references/WORKFLOW.md`.
   - Where: Top of the document after the intro.
   - Why: Ensures the detailed workflow matches the policy.

5. **Verify consistency**
   - What: Run `rg -n "web_search" -S` and scan results.
   - Where: Repo root.
   - Why: Confirms no other skills or docs authorize direct web_search usage.

## Assumptions
- Enforcement is doc- and workflow-based rather than code-level.
- Only `deep-research` should mention `web_search` after updates.
- If git is available later, commits will be created per task.

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Other skills reintroduce `web_search` later | M | Add a quick `rg -n "web_search" -S` check to future reviews |
| Agents ignore the guardrail text | M | Keep the policy high-priority and repeat it inside the deep-research skill |
| Plan-mode still implies external research | L | Explicitly route all research to deep-research |

## Implementation Todos
| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | Add global web_search guardrail to `AGENTS.md` | - | pending |
| T2 | Remove web_search from plan-mode and add deep-research routing | T1 | pending |
| T3 | Add deep-research guardrails and hybrid framing | T1 | pending |
| T4 | Update deep-research workflow reference | T3 | pending |
| T5 | Verify `web_search` usage and consistency | T2, T4 | pending |

### Task 1: Add global web_search guardrail to AGENTS

**Files:**
- Modify: `AGENTS.md`
- Test: N/A (docs-only)

**Step 1: Write the failing test**

Run: `rg -n "<web_search_policy" AGENTS.md`
Expected: No matches (exit code 1) because the policy block does not exist yet.

**Step 2: Write minimal implementation**

Insert the following block directly after `</plan_mode_instruction>`:

```xml
<web_search_policy priority="high">
No `web_search` unless the `deep-research` skill is explicitly invoked and its workflow followed.
If external sources are needed, invoke `deep-research` and perform all searches inside that workflow.
</web_search_policy>
```

**Step 3: Run test to verify it passes**

Run: `rg -n "<web_search_policy" AGENTS.md`
Expected: Match for the new block.

**Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add global web_search guardrail"
```

### Task 2: Align plan-mode to route research to deep-research

**Files:**
- Modify: `skills/plan-mode/SKILL.md`
- Test: N/A (docs-only)

**Step 1: Write the failing test**

Run: `rg -n "allowed-tools" skills/plan-mode/SKILL.md`
Expected: Line includes `web_search` before the edit.

**Step 2: Write minimal implementation**

Update the allowed-tools line to remove `web_search`:

```yaml
allowed-tools: read_file codebase_search grep list_dir
```

Add this sentence under `<research>` in the Planning Workflow:

```
- If external sources are needed, invoke the `deep-research` skill and follow its workflow. Do not call `web_search` directly from plan-mode.
```

**Step 3: Run test to verify it passes**

Run: `rg -n "web_search" skills/plan-mode/SKILL.md`
Expected: No matches (exit code 1).

**Step 4: Commit**

```bash
git add skills/plan-mode/SKILL.md
git commit -m "docs: route plan-mode research through deep-research"
```

### Task 3: Add deep-research guardrails and hybrid framing

**Files:**
- Modify: `skills/deep-research/SKILL.md`
- Test: N/A (docs-only)

**Step 1: Write the failing test**

Run: `rg -n "only approved entry point|must invoke" skills/deep-research/SKILL.md`
Expected: No matches (exit code 1) before the edit.

**Step 2: Write minimal implementation**

Update `<purpose>` to include the guardrail sentence:

```
Execute comprehensive research by intelligently selecting between deep iterative (Perplexity-style) and wide parallel (Manus-style) approaches based on query complexity, and serve as the only approved entry point for `web_search`.
```

Add this bullet to **When to Invoke**:

```
- Any request requiring `web_search` must invoke this skill
```

Add this bullet to **Constraints**:

```
- Do not use `web_search` outside this skill
```

**Step 3: Run test to verify it passes**

Run: `rg -n "only approved entry point|must invoke" skills/deep-research/SKILL.md`
Expected: Matches for the new lines.

**Step 4: Commit**

```bash
git add skills/deep-research/SKILL.md
git commit -m "docs: add deep-research web_search guardrail"
```

### Task 4: Update deep-research workflow reference

**Files:**
- Modify: `skills/deep-research/references/WORKFLOW.md`
- Test: N/A (docs-only)

**Step 1: Write the failing test**

Run: `rg -n "Guardrail" skills/deep-research/references/WORKFLOW.md`
Expected: No matches (exit code 1) before the edit.

**Step 2: Write minimal implementation**

Insert this note near the top (after the intro paragraph):

```
> Guardrail: All `web_search` usage must occur inside the deep-research skill. If external sources are required, invoke deep-research and follow this workflow.
```

Optionally add one sentence to the intro:

```
This workflow blends Perplexity-style iterative depth with Manus-style parallel breadth.
```

**Step 3: Run test to verify it passes**

Run: `rg -n "Guardrail" skills/deep-research/references/WORKFLOW.md`
Expected: Match for the new note.

**Step 4: Commit**

```bash
git add skills/deep-research/references/WORKFLOW.md
git commit -m "docs: add deep-research workflow guardrail"
```

### Task 5: Verify `web_search` usage and consistency

**Files:**
- Test: N/A (docs-only)

**Step 1: Run verification search**

Run: `rg -n "web_search" -S`
Expected: Matches only in `AGENTS.md` policy text and `skills/deep-research/` docs.

**Step 2: Spot-check updated docs**

Open and review:
- `AGENTS.md`
- `skills/plan-mode/SKILL.md`
- `skills/deep-research/SKILL.md`
- `skills/deep-research/references/WORKFLOW.md`

**Step 3: Commit**

```bash
git add AGENTS.md skills/plan-mode/SKILL.md skills/deep-research/SKILL.md skills/deep-research/references/WORKFLOW.md
git commit -m "docs: enforce deep-research-only web_search policy"
```
