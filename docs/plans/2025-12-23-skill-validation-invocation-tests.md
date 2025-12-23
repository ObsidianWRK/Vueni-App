# Skills Validation & Invocation Testing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Validate every installed skill across Cursor, Claude Code, and Codex; run Skills Ref tests; verify automatic invocation per skill with documented results.

**Architecture:** Use the existing validation scripts for structural checks, then generate a per-skill prompt matrix and run invocation tests via CLI (Claude Code/Codex) and manual UI checks (Cursor). Record results in a single test log and remediate any failures before re-running affected tests.

**Tech Stack:** Python (validation scripts), shell, Claude Code CLI, Codex CLI, Cursor app.

## Goal
Validate all skills across Cursor, Claude Code, and Codex with structural checks (A & B) and per-skill invocation tests, producing a single documented results log.

## Context
- Canonical skills live in `.claude/skills`; mirrors in `.codex/skills`; Cursor subset in `skills/`.
- Validation scripts: `scripts/validate_repo.py` and `scripts/validate_skills.py` (`--all`, `--codex`, `--cursor`).
- CLI tools are available: `claude`, `codex`, and `cursor` (Cursor agent appears manual).
- This workspace is not a git repo, so commit steps may be skipped or handled elsewhere.

## Approach
1. Inventory skills per platform and create a test matrix (skill, platform, prompt, expected invocation).
2. Run Skills Ref tests (A & B) for each platform and capture results.
3. Execute invocation tests: CLI automation for Claude Code and Codex, manual checks for Cursor.
4. Record outcomes, remediate any failures, and re-run only affected tests.

## Steps

1. **Inventory skills + create test matrix**
   - What: List skills per platform and create a matrix with columns: Skill, Platform, Prompt, Expected Invocation, Pass/Fail, Notes.
   - Where: Create `docs/plans/2025-12-23-skill-test-matrix.md`.
   - Why: Guarantees each skill is tested and tracked.

2. **Run Skills Ref tests (A & B)**
   - What: Run repo-level and per-platform validation and capture outputs.
   - Where: Repo root; log results in `docs/plans/2025-12-23-skill-test-matrix.md`.
   - Why: Confirms structural compliance before invocation testing.
   - Commands:
     - `python3 scripts/validate_repo.py`
     - `python3 scripts/validate_skills.py --all`
     - `python3 scripts/validate_skills.py --codex`
     - `python3 scripts/validate_skills.py --cursor`

3. **Draft per-skill invocation prompts**
   - What: For each skill, write at least one concrete prompt that should trigger it.
   - Where: Fill the matrix rows in `docs/plans/2025-12-23-skill-test-matrix.md`.
   - Why: Creates explicit test cases before running models (TDD-style).

4. **Claude Code invocation tests**
   - What: Run each prompt using Claude Code CLI and record whether the response declares the expected skill usage.
   - Where: Run in repo root; record results in `docs/plans/2025-12-23-skill-test-matrix.md`.
   - Why: Verifies automatic skill invocation for Claude Code.
   - Command pattern: `claude --print "<prompt>"`

5. **Codex invocation tests**
   - What: Run each prompt using Codex CLI and record whether the response declares the expected skill usage.
   - Standard: Triple verification per skill (keyword trigger, specific invocation, disambiguation).
   - Where: Run in repo root; record results in `docs/plans/2025-12-23-skill-test-matrix.md`.
   - Why: Verifies automatic skill invocation for Codex.
   - Command pattern: `codex exec "<prompt>"`

6. **Cursor invocation tests (manual)**
   - What: Use the Cursor UI to run each prompt and confirm the expected skill invocation.
   - Where: Cursor app; record results in `docs/plans/2025-12-23-skill-test-matrix.md`.
   - Why: Cursor CLI does not expose agent output for automation.

7. **Remediate failures + re-test**
   - What: Fix any failed skills (description triggers, missing registrations, or structural issues) and re-run only affected tests.
   - Where: `.claude/skills/<skill>/SKILL.md`, `.codex/skills/<skill>/SKILL.md`, `skills/<skill>/SKILL.md`, `AGENTS.md`.
   - Why: Ensures corrected skills pass both structural and invocation checks.

8. **Finalize results log**
   - What: Summarize pass/fail counts and outstanding risks in the matrix file.
   - Where: `docs/plans/2025-12-23-skill-test-matrix.md`.
   - Why: Provides a single, auditable record of the test run.

## Assumptions
- Running `claude --print` and `codex exec` from the repo root uses the local skill registry and AGENTS instructions.
- Cursor invocation tests must be performed manually in the UI.

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| CLI output does not explicitly mention skill usage | M | Treat as failure; add explicit skill-usage declaration to SKILL.md instructions if required. |
| Cursor agent cannot be automated | M | Perform manual test run and capture screenshots/notes in the matrix file. |
| Validation scripts only check `.claude/skills` | M | Run `validate_skills.py --codex` and `--cursor` explicitly. |
| No git repo for commits | L | Record changes and results in `docs/plans` instead of commits. |

## Codex Triple Verification Contract (keyword, explicit, self-test)

- **Scope:** All skills under `.codex/skills/`.
- **Markers:** Require responses to include `INVOCATION_OK:<skill>` for invocation and `SELFTEST_OK:<skill>` for self-tests.
- **Standard 1 — Keyword invocation:** Prompt pattern: `Use the <skill> skill to help with its intended task. Respond with INVOCATION_OK:<skill> once loaded.` Expect Codex to surface the skill and include the marker.
- **Standard 2 — Explicit invocation:** Prompt pattern: `Invoke skill <skill> now. Respond with INVOCATION_OK:<skill> once loaded.` Expect explicit load acknowledgement.
- **Standard 3 — Runtime self-test:** Harness-level check that `SKILL.md` frontmatter is readable and name/description/license are present; harness emits `SELFTEST_OK:<skill>` when these readiness checks pass.

## Codex Triple Verification Rerun Guide

1. Run structural checks (Codex scope):
   - `python3 scripts/validate_skills.py --codex --codex-invoke-ready`
2. Run invocation + self-test harness:
   - `python3 scripts/verify_codex_invocation.py --skills-root .codex/skills --report-json reports/codex_invocation_report.json --append-md docs/plans/2025-12-23-skill-validation-invocation-tests.md`
3. Review artifacts:
   - JSON report: `reports/codex_invocation_report.json`
   - Markdown summary appended to this file under “Codex Triple Verification Results”.

## Implementation Todos

| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | Create skill inventory and matrix file | – | pending |
| T2 | Run `validate_repo.py` and capture results | T1 | pending |
| T3 | Run `validate_skills.py --all` and capture results | T1 | pending |
| T4 | Run `validate_skills.py --codex` and capture results | T1 | pending |
| T5 | Run `validate_skills.py --cursor` and capture results | T1 | pending |
| T6 | Draft per-skill invocation prompts in matrix | T1 | pending |
| T7 | Execute Claude Code invocation tests and record results | T6 | pending |
| T8 | Execute Codex invocation tests and record results | T6 | pending |
| T9 | Execute Cursor invocation tests and record results | T6 | pending |
| T10 | Remediate failures and re-run affected tests | T2, T3, T4, T5, T7, T8, T9 | pending |
| T11 | Summarize outcomes in matrix file | T10 | pending |

## Codex Triple Verification Status

- Harness script: `scripts/verify_codex_invocation.py` (produces `reports/codex_invocation_report.json` and can append a markdown summary here).
- Current run status: not yet executed; run the commands in the rerun guide above to populate results.
