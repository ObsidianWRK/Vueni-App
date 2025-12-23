# Plan: Skills Files Review Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Review the work in `docs/plans/2025-12-23-skill-validation-invocation-tests.md`, `skills/ocr/SKILL.md`, and `skills/plan-mode/SKILL.md` and deliver a structured review with findings and suggested fixes.

**Architecture:** Derive expected standards from `AGENTS.md` and validator scripts, then review each target file against those standards, corroborate with validation output, and produce a severity-ordered review summary with file/line references.

**Tech Stack:** Markdown docs, `rg`/`sed`/`nl`, Python validator scripts in `scripts/`.

## Goal
Review the specified plan and skill files and provide a review report with findings, risks, and actionable suggestions.

## Context
- Target files: `docs/plans/2025-12-23-skill-validation-invocation-tests.md`, `skills/ocr/SKILL.md`, `skills/plan-mode/SKILL.md`.
- Repo appears to lack a `.git` directory, so worktrees/commits may not be available unless git is initialized.
- Expected standards should follow repo validators first; superpowers skill guidance may conflict and should be flagged if it does.
- Review output should follow code-review style: severity-ordered findings with file/line references.
- Skills to reference: @plan-mode, @superpowers:writing-plans, @superpowers:executing-plans (for execution).

## Approach
Establish the review checklist from repo rules and validators, then inspect each target file for compliance, clarity, and alignment. Validate with scripts where possible, and produce a concise, severity-ordered review summary with references and questions.

## Steps

1. **Derive review criteria**
   - What: Read skill/plan rules in `AGENTS.md` and validator scripts to identify required frontmatter fields, structure, and alignment expectations.
   - Where: `AGENTS.md`, `scripts/validate_skills.py`, `scripts/validate_repo.py`, `docs/skill-validation-report.md`.
   - Why: Ensures review is based on repo-defined standards rather than assumptions.

2. **Review `skills/ocr/SKILL.md`**
   - What: Check frontmatter, OCR contract, platform guidance, and OCR auto-invocation alignment.
   - Where: `skills/ocr/SKILL.md`, `AGENTS.md`.
   - Why: Ensures the OCR skill matches mandatory behaviors and repository validation rules.

3. **Review `skills/plan-mode/SKILL.md`**
   - What: Verify triggers, output format, and required sections align with `AGENTS.md` plan-mode instructions.
   - Where: `skills/plan-mode/SKILL.md`, `AGENTS.md`.
   - Why: Prevents plan-mode drift from the registry requirements.

4. **Review `docs/plans/2025-12-23-skill-validation-invocation-tests.md`**
   - What: Check plan completeness, clarity, and consistency with skill/validation expectations.
   - Where: `docs/plans/2025-12-23-skill-validation-invocation-tests.md`.
   - Why: Confirms the plan is actionable and aligned with current standards.

5. **Validate and compile findings**
   - What: Run validation scripts (if supported) and compile review findings with severity and references.
   - Where: `scripts/validate_skills.py`, `scripts/validate_repo.py`.
   - Why: Corroborates manual review and captures automated violations.

## Assumptions
- The review will be delivered in chat unless you request a separate review report file.
- Validator scripts reflect the authoritative frontmatter/format requirements.
- No git-based diff is available; review will focus on current content unless a baseline is provided.

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Repo standards conflict with superpowers guidance | M | Defer to validator scripts and flag conflicts explicitly |
| No git history to compare changes | M | Ask for baseline or prior version if needed |
| Validator scripts lack coverage for plan docs | L | Use manual checklist for plan review |

## Implementation Todos

| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | Derive review checklist from `AGENTS.md` and validators | – | pending |
| T2 | Review `skills/ocr/SKILL.md` against checklist | T1 | pending |
| T3 | Review `skills/plan-mode/SKILL.md` against checklist | T1 | pending |
| T4 | Review `docs/plans/2025-12-23-skill-validation-invocation-tests.md` | T1 | pending |
| T5 | Run validation scripts and compile review findings | T2, T3, T4 | pending |

### Task 1: Derive Review Checklist

**Files:**
- Read: `AGENTS.md`
- Read: `scripts/validate_skills.py`
- Read: `scripts/validate_repo.py`
- Read: `docs/skill-validation-report.md`

**Step 1: Locate skill and plan rules in AGENTS**

Run: `rg -n "plan_mode_instruction|OCR Auto-Invocation|skills_system" AGENTS.md`
Expected: Matching lines show the relevant rule blocks.

**Step 2: Identify required frontmatter/format checks**

Run: `rg -n "frontmatter|license|compatibility|allowed-tools|description" scripts/validate_skills.py`
Expected: Matches show required fields and validation logic.

**Step 3: Scan repo-level alignment checks**

Run: `rg -n "AGENTS|registry|skills" scripts/validate_repo.py`
Expected: Matches reveal any AGENTS alignment checks.

**Step 4: Capture review checklist**

Action: Summarize required fields, sections, and alignment rules for use in Tasks 2-4.

### Task 2: Review OCR Skill

**Files:**
- Read: `skills/ocr/SKILL.md`
- Read: `AGENTS.md`

**Step 1: Read frontmatter and contract**

Run: `sed -n '1,200p' skills/ocr/SKILL.md`
Expected: Frontmatter plus OCR contract and workflow sections.

**Step 2: Cross-check auto-invocation rules**

Run: `rg -n "OCR Auto-Invocation" AGENTS.md`
Expected: OCR auto-invocation rules to compare against the skill.

**Step 3: Record findings with line references**

Run: `nl -ba skills/ocr/SKILL.md | sed -n '1,200p'`
Expected: Line-numbered output for precise citations.

### Task 3: Review Plan-Mode Skill

**Files:**
- Read: `skills/plan-mode/SKILL.md`
- Read: `AGENTS.md`

**Step 1: Read frontmatter and workflow**

Run: `sed -n '1,200p' skills/plan-mode/SKILL.md`
Expected: Frontmatter plus planning workflow sections.

**Step 2: Cross-check AGENTS plan-mode rules**

Run: `rg -n "plan_mode_instruction" AGENTS.md`
Expected: Plan-mode instruction block for alignment.

**Step 3: Record findings with line references**

Run: `nl -ba skills/plan-mode/SKILL.md | sed -n '1,200p'`
Expected: Line-numbered output for citations.

### Task 4: Review Plan Document

**Files:**
- Read: `docs/plans/2025-12-23-skill-validation-invocation-tests.md`

**Step 1: Read full plan**

Run: `sed -n '1,240p' docs/plans/2025-12-23-skill-validation-invocation-tests.md`
Expected: Plan content and any references to skills or validators.

**Step 2: Capture citations for review**

Run: `nl -ba docs/plans/2025-12-23-skill-validation-invocation-tests.md | sed -n '1,240p'`
Expected: Line-numbered output for citations.

### Task 5: Validate and Compile Review

**Files:**
- Run: `scripts/validate_skills.py`
- Run: `scripts/validate_repo.py`

**Step 1: Confirm validator options**

Run: `python3 scripts/validate_skills.py --help`
Expected: Usage output with supported flags.

**Step 2: Run skill validation (as supported)**

Run: `python3 scripts/validate_skills.py --all`
Expected: No errors or a list of specific validation failures.

**Step 3: Run repo validation**

Run: `python3 scripts/validate_repo.py`
Expected: No errors or a list of alignment failures.

**Step 4: Draft review output**

Action: Produce a review with severity-ordered findings, file/line references, and open questions.
