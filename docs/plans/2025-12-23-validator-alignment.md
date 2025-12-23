# Validator Alignment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Align validation scripts with the minimal frontmatter spec (name + description only) and verify the report's items against current repo state.

**Architecture:** Keep LICENSE.txt checks as-is, make frontmatter `license` optional in validators, and update validator documentation to match behavior. Verify AGENTS.md and `references/` directories are already aligned before changing code.

**Tech Stack:** Python 3, `unittest`, repo validation scripts.

## Goal
Align validator behavior with the minimal frontmatter standard while confirming that previously reported AGENTS/skills issues are already resolved.

## Context
- `scripts/validate_repo.py` already treats frontmatter `license` as optional but its docstring still mentions `license` as required.
- `scripts/verify_codex_invocation.py` currently fails self-tests when `license` is missing, which conflicts with the minimal spec.
- `AGENTS.md` excludes the internal `template` skill, and `skills/mcp-builder` already uses `references/` (not `reference/`).

## Approach
Re-verify the reported issues, then add a unit test that fails under the current `license` requirement in `check_selftest`. Update `check_selftest` to accept missing `license` while keeping `LICENSE.txt` required, and refresh validator documentation to match the actual rules.

## Steps

1. **Re-verify report findings**
   - What: Confirm current AGENTS/skills alignment and reference directory naming, plus current validator behavior.
   - Where: `AGENTS.md`, `skills/`, `.claude/skills/`, `scripts/validate_repo.py`.
   - Why: Avoid changing already-fixed issues or chasing stale findings.

2. **Add failing test for optional `license`**
   - What: Write a unit test that expects `check_selftest` to pass with name + description only.
   - Where: `scripts/tests/test_verify_codex_invocation.py`.
   - Why: TDD proof of current failure and future regression guard.

3. **Make `license` optional in `check_selftest`**
   - What: Remove the frontmatter `license` requirement while keeping `LICENSE.txt` required.
   - Where: `scripts/verify_codex_invocation.py`.
   - Why: Align validator behavior with the minimal frontmatter spec.

4. **Update validator documentation**
   - What: Fix `validate_repo.py` docstring to reflect required frontmatter fields (name + description only).
   - Where: `scripts/validate_repo.py`.
   - Why: Keep docs consistent with actual validation rules.

5. **Re-run tests and spot-check validation**
   - What: Re-run the unit test and ensure validation output stays clean.
   - Where: `python3 -m unittest ...`, `python3 scripts/validate_repo.py`.
   - Why: Confirm the change works and no regressions were introduced.

## Assumptions
- The minimal frontmatter standard (name + description only) is still the desired spec.
- `LICENSE.txt` remains required for skills.
- No AGENTS.md or directory fixes are needed beyond validation updates.

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Validator change hides missing license metadata someone still expects | M | Keep `LICENSE.txt` required and document the change in-script |
| Tests fail due to import path assumptions | M | Use explicit `sys.path` insertion in the unit test |
| Report findings are stale and changes are unnecessary | L | Verify current state before editing code |

## Implementation Todos

| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | Re-verify report findings and current validator behavior | – | pending |
| T2 | Write failing unit test for optional `license` in `check_selftest` | T1 | pending |
| T3 | Update `check_selftest` to treat `license` as optional | T2 | pending |
| T4 | Update `validate_repo.py` docstring to remove `license` requirement | T3 | pending |
| T5 | Run unit tests and validate repo output | T3, T4 | pending |

### Task 1: Re-verify report findings

**Files:**
- Read: `AGENTS.md`
- Read: `scripts/validate_repo.py`
- Read: `skills/mcp-builder/`
- Read: `.claude/skills/`

**Step 1: Run repository validator**

Run: `python3 scripts/validate_repo.py --verbose`
Expected: `Validation passed` with no errors.

**Step 2: Confirm AGENTS.md excludes internal template**

Run: `python3 - <<'PY'\nimport re\nfrom pathlib import Path\nskills = set(re.findall(r"<name>([^<]+)</name>", Path('AGENTS.md').read_text()))\nprint('template' in skills)\nPY`
Expected: `False`

**Step 3: Confirm no `reference/` directories**

Run: `find skills -type d -name 'reference'`
Expected: no output

### Task 2: Add failing unit test for optional `license`

**Files:**
- Create: `scripts/tests/test_verify_codex_invocation.py`

**Step 1: Write the failing test**

```python
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_codex_invocation import check_selftest


class TestCheckSelftest(unittest.TestCase):
    def test_license_optional(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "example-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: Example.\n---\n\nBody\n",
                encoding="utf-8",
            )
            (skill_dir / "LICENSE.txt").write_text("MIT\n", encoding="utf-8")
            result = check_selftest(skill_dir)
            self.assertEqual(result.status, "pass")


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest scripts/tests/test_verify_codex_invocation.py`
Expected: FAIL with `license missing`

### Task 3: Make `license` optional in `check_selftest`

**Files:**
- Modify: `scripts/verify_codex_invocation.py`

**Step 1: Update self-test logic**

```python
    license_val = fm.get("license", "")

    missing = []
    if name != skill_dir.name:
        missing.append(f"name mismatch (found '{name}')")
    if not description:
        missing.append("description missing")
    # license is optional per minimal frontmatter spec
```

**Step 2: Re-run test to verify it passes**

Run: `python3 -m unittest scripts/tests/test_verify_codex_invocation.py`
Expected: PASS

**Step 3: Commit (optional)**

```bash
git add scripts/tests/test_verify_codex_invocation.py scripts/verify_codex_invocation.py
git commit -m "fix: make license optional in codex selftest"
```

### Task 4: Update validator documentation

**Files:**
- Modify: `scripts/validate_repo.py`

**Step 1: Update docstring to match minimal frontmatter**

```python
- Every skill has SKILL.md with required frontmatter (name, description)
```

**Step 2: Spot-check validator output**

Run: `python3 scripts/validate_repo.py`
Expected: `Validation passed`

**Step 3: Commit (optional)**

```bash
git add scripts/validate_repo.py
git commit -m "docs: align validate_repo frontmatter docs"
```
