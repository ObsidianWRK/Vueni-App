---
name: Fix Unstaged Changes and Untracked Files
overview: Organize and commit remaining unstaged changes (AGENTS.md improvements) and properly handle untracked files (new skills, plan files, documentation, zip packages).
todos:
  - id: T1
    content: Review and commit AGENTS.md improvements (plan completion workflow enhancements)
    status: pending
  - id: T2
    content: Sync new skills from .claude/skills/ to .codex/skills/ using sync_skills.py
    status: pending
    dependencies:
      - T1
  - id: T3
    content: Register new skills in AGENTS.md if they're not already listed
    status: pending
    dependencies:
      - T2
  - id: T4
    content: Commit .cursor/plans/ directory (active plan files should be tracked)
    status: pending
  - id: T5
    content: Review and commit documentation files in docs/ directory
    status: pending
  - id: T6
    content: Handle zip files (decide: commit, move to archive, or add to .gitignore)
    status: pending
  - id: T7
    content: Commit test scripts and validation utilities
    status: pending
  - id: T8
    content: Verify repository state is clean after all changes
    status: pending
    dependencies:
      - T1
      - T2
      - T3
      - T4
      - T5
      - T6
      - T7
---

# Plan: Fix Unstaged Changes and Untracked Files

## Goal

Organize and commit all remaining unstaged changes and untracked files to achieve a clean repository state while preserving important work (skills, documentation, plans).

## Context

- **Unstaged changes**: AGENTS.md has improvements to plan completion workflow (CRITICAL reminders, enforcement layers)
- **Untracked skills**: New skill directories in `.claude/skills/` and `.codex/skills/` that need syncing
- **Plan files**: `.cursor/plans/` directory with active plan files (should be tracked)
- **Documentation**: Various docs in `docs/` directory from previous work
- **Zip files**: Skill package archives (need decision on handling)
- **Test scripts**: New validation and test utilities

## Approach

1. Commit AGENTS.md improvements first (foundational changes)
2. Sync skills between directories using existing tooling
3. Verify and update AGENTS.md skill registry
4. Commit plan files (active work should be tracked)
5. Review and commit documentation
6. Handle zip files appropriately (archive or ignore)
7. Commit test utilities
8. Verify clean state

## Steps

1. **Commit AGENTS.md improvements**
   - What: Stage and commit AGENTS.md changes (plan completion workflow enhancements)
   - Where: `AGENTS.md`
   - Why: These are important improvements that should be preserved

2. **Sync skills to .codex/skills/**
   - What: Run `python scripts/sync_skills.py` to mirror .claude/skills/ to .codex/skills/
   - Where: `scripts/sync_skills.py`
   - Why: Maintains consistency between platforms per INSTALLATION_GUIDE.md

3. **Verify AGENTS.md skill registry**
   - What: Check if new skills are registered in AGENTS.md, add if missing
   - Where: `AGENTS.md`
   - Why: All skills should be discoverable via AGENTS.md

4. **Commit plan files**
   - What: Add .cursor/plans/ directory to git
   - Where: `.cursor/plans/`
   - Why: Active plan files should be tracked for collaboration

5. **Review and commit documentation**
   - What: Review docs/ files and commit relevant documentation
   - Where: `docs/`
   - Why: Preserve important documentation from previous work

6. **Handle zip files**
   - What: Decide whether to commit, archive, or ignore zip skill packages
   - Where: Root directory zip files
   - Why: Avoid cluttering repository with temporary artifacts

7. **Commit test utilities**
   - What: Add new test scripts and validation utilities
   - Where: `scripts/tests/`, `scripts/validate_*.py`
   - Why: Test infrastructure should be tracked

8. **Verify clean state**
   - What: Run `git status` and `python scripts/validate_repo.py` to confirm clean state
   - Where: Repository root
   - Why: Ensure all important work is committed and repository is valid

## Assumptions

- New skills in `.claude/skills/` are intentionally added and should be preserved
- Plan files in `.cursor/plans/` are active work that should be tracked
- Documentation files are valuable and should be committed
- Zip files are temporary artifacts that can be archived or ignored
- Test scripts are part of the repository infrastructure

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Committing temporary/duplicate files | M | Review each category before committing |
| Breaking skill sync | M | Use existing sync_skills.py tool |
| Missing skill registrations | M | Verify against AGENTS.md after sync |
| Cluttering repo with zip files | L | Move to archive or add to .gitignore |

## Implementation Todos

| ID | Task | Depends On | Status |
|----|------|------------|--------|
| T1 | Review and commit AGENTS.md improvements | – | pending |
| T2 | Sync new skills from .claude/skills/ to .codex/skills/ | T1 | pending |
| T3 | Register new skills in AGENTS.md if missing | T2 | pending |
| T4 | Commit .cursor/plans/ directory | – | pending |
| T5 | Review and commit documentation files | – | pending |
| T6 | Handle zip files (archive or ignore) | – | pending |
| T7 | Commit test scripts and validation utilities | – | pending |
| T8 | Verify repository state is clean | T1-T7 | pending |
