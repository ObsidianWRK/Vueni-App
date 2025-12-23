---
name: Skills Alignment Refactor
overview: Complete refactor to ensure alignment between Skill files, AGENTS.md, and hooks across Cursor, Claude Code, and Codex platforms. Standardizes frontmatter, removes platform-specific dependencies, and ensures cross-platform compatibility.
todos: []
---

# Skills Alig

nment Refactor Plan

## Goal

Refactor the entire skills system to ensure complete alignment between Skill files (SKILL.md), AGENTS.md registry, and hooks across Cursor, Claude Code, and Codex. Standardize formats, remove platform-specific dependencies, and ensure cross-platform compatibility.

## Context

### Current State

- **Skills locations**: `.claude/skills/` (canonical), `.codex/skills/` (mirror), `skills/` (Cursor subset)
- **Registry**: `AGENTS.md` contains skill registry with XML-formatted entries
- **Validation**: Scripts exist (`validate_skills.py`, `validate_repo.py`) but may not catch all alignment issues
- **Hooks**: Previously removed from OCR (Claude Code-specific), but need to verify no other hook dependencies exist
- **Frontmatter inconsistencies**: Some skills have `compatibility`, `metadata`, `allowed-tools`; others don't

### Key Issues Identified

1. **Frontmatter inconsistency**: Not all skills have standardized frontmatter fields
2. **AGENTS.md alignment**: Need to verify all skills in directories are registered in AGENTS.md
3. **Cross-platform compatibility**: Some skills may have platform-specific references
4. **Hook dependencies**: Need to ensure no Claude Code-specific hooks remain
5. **Sync status**: `.codex/skills/` may be out of sync with `.claude/skills/`

## Approach

1. **Audit Phase**: Inventory all skills, check frontmatter consistency, verify AGENTS.md alignment
2. **Standardization Phase**: Standardize all skill frontmatter with

required fields (name, description, license, compatibility)

3. **Alignment Phase**: Ensure AGENTS.md entries match all skill directories exactly
4. **Compatibility Phase**: Remove platform-specific dependencies, ensure cross-platform compatibility
5. **Sync Phase**: Ensure `.codex/skills/` mirrors `.claude/skills/` correctly
6. **Validation Phase**: Update and run validation scripts to verify alignment

## Steps

### 1. Audit All Skills and Create Inventory

**What**: Create comprehensive inventory of all skills across all three directories

- List all skills in `.claude/skills/`
- List all skills in `.codex/skills/`
- List all skills in `skills/`
- Extract frontmatter from each SKILL.md
- Compare with AGENTS.md entries

**Where**: Create `docs/refactor-inventory.md` with full inventory**Why**: Need baseline understanding before refactoring**Files to check**:

- `.claude/skills/*/SKILL.md` (all skills)
- `.codex/skills/*/SKILL.md` (if exists)
- `skills/*/SKILL.md` (if exists)
- `AGENTS.md` (skill registry)

### 2. Standardize Skill Frontmatt

er**What**: Ensure all skills have consistent frontmatter:

- `name`: Required, must match directory name
- `description`: Required, max 1024 chars
- `license`: Required (per validation script)
- `compatibility`: Standardize to "Designed for Cursor, Claude Code, and Codex" (or specific if needed)
- `metadata`: Optional, but standardize format if present
- `allowed-tools`: Optional, space-delimited string format

**Where**: Update all `SKILL.md` files in `.claude/skills/`**Why**: Consistency ensures proper discovery and invocation across platforms**Standard template**:

```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it.
license: MIT|Apache-2.0|Complete terms in LICENSE.txt
compatibility: Designed for Cursor, Claude Code, and Codex
metadata:
  version: 1.0.0
  author: Agent Skills
allowed-tools: tool1 tool2 tool3
---
```



### 3. Verify and Fix AGENTS.md Alignment

**What**:

- Extract all skill names from `.claude/skills/` directories
- Extract all skill entries from `AGENTS.md` (XML `<skill><name>` tags)
- Compare and identify:
    - Skills i

n directories but not in AGENTS.md

    - Skills in AGENTS.md but not in directories
    - Mismatched descriptions between AGENTS.md and SKILL.md frontmatter

**Where**: `AGENTS.md` and all skill directories**Why**: AGENTS.md is the registry that agents read; must match reality**Fix actions**:

- Add missing skills to AGENTS.md
- Remove orphaned entries from AGENTS.md
- Update descriptions to match SKILL.md frontmatter

### 4. Remove Platform-Specific Dependencies

**What**: Scan all skills for:

- Claude Code-specific hooks references
- Platform-specific invocation methods
- Hardcoded paths or platform assumptions
- References to `.claude/hooks/` or similar

**Where**: All `SKILL.md` files and related documentation**Why**: Ensure skills work identically across all platforms**Actions**:

- Remove any hook references (already done for OCR, verify others)
- Replace platform-specific instructions with cross-platform alternatives
- Update platform guidance sections to be consistent

### 5. Standardize Platform Guidance Sections

**What**: Ensure all skills with platform-specific guidance follow consistent format:

- Use same section structure
- Consistent platform names (Cursor, Claude Code, Codex)
- Standardized invocation methods

**Where**: Skills that have platform-specific sections (e.g., `ocr`, `plan-mode`)**Why**: Consistency improves maintainability and user experience**Template**:

```markdown
## Platform-specific guidance

### Cursor
- [Specific Cursor instructions]

### Claude Code
- [Specific Claude Code instructions]

### Codex
- [Specific Codex instructions]
```



### 6. Sync Skills to Codex Directory

**What**: Run sync script to ensure `.codex/skills/` mirrors `.claude/skills/`:

- Run `python3 scripts/sync_skills.py`
- Verify all skills copied correctly
- Check for any sync errors

**Where**: Run from repo root**Why**: Codex requires skills in `.codex/skills/` directory

### 7. Update Validation Scripts

**What**: Review and update validation scripts to catch alignment issues:

- `validate_skills.py`: Ensure it checks frontmatter consistency
- `validate_repo.py`: Ensure it verifies AGENTS.md alignment
- Add checks for compatibility field standardization
- Add checks for platform-specific dependencies

**Where**: `scripts/validate_skills.py`, `scripts/validate_repo.py`**Why**: Automated validation prevents future misalignment

### 8. Update Documentation

**What**: Update relevant documentation:

- `README.md`: Reflect standardized structure
- `INSTALLATION_GUIDE.md`: Update if needed
- `AGENTS.md`: Ensure usage instructions are accurate

**Where**: Root-level documentation files**Why**: Documentation must match implementation

### 9. Run Full Validation Suite

**What**: Execute all validation checks:

- `python3 scripts/validate_repo.py`
- `python3 scripts/validate_skills.py --all`
- `python3 scripts/validate_skills.py --codex`
- `python3 scripts/validate_skills.py --cursor`
- Fix any errors found

**Where**: Run from repo root**Why**: Verify all changes are correct and complete

### 10. Create Alignment Report

**What**: Document the refactoring:

- List all changes made
- Document standardization decisions
- Note any platform-specific considerations
- Create checklist for future skill additions

**Where**: `docs/refactor-alignment-report.md`**Why**: Provides audit trail and guidance for future maintenance

## Assumptions

- All skills should work across Cursor, Claude Code, and Codex (unless explicitly documented otherwise)
- `.claude/skills/` is the canonical source; `.codex/skills/` is a mirror
- `skills/` directory is a curated subset for Cursor (may not need full alignment)
- Hooks are Claude Code-specific and should not be used (confirmed from OCR implementation)
- Validation scripts can be updated to catch alignment issues

## Risks & Mitigations

| Risk | Impact | Mitigation ||------|--------|------------|| Breaking existing skill functionality | H | Test each skill after standardization; preserve behavior while standardizing format || Missing skills in AGENTS.md | M | Automated comparison script; manual verification || Platform-specific behavior lost | M | Document platform differences in compatibility field or platform sections || Sync script fails | L | Manual verification; check sync script logs || Validation scripts miss issues | M | Manual review; add comprehensive test cases |

## Implementation Todos

| ID | Task | Depends On | Status ||----|------|------------|--------|| T1 | Create comprehensive skill inventory | – | pending || T2 | Standardize frontmatter for all skills in `.claude/skills/` | T1 | pending || T3 | Verify AGENTS.md entries match skill directories | T1 | pending || T4 | Fix AGENTS.md alignment issues | T3 | pending || T5 | Remove platform-specific dependencies from skills | T1 | pending || T6 | Standardize platform guidance sections | T5 | pending || T7 | Sync skills to `.codex/skills/` directory | T2 | pending || T8 | Update validation scripts | T2, T4 | pending || T9 | Update documentation | T2, T4 | pending || T10 | Run full validation suite | T2, T4, T7, T8 | pending || T11 | Create alignment report | T10 | pending |

## Cross-Platform Compatibility Standards

### Required Frontmatter Fields

- `name`: Must match directory name exactly
- `description`: Must clearly state when to use the skill
- `license`: Required (MIT, Apache

-2.0, or reference to LICENSE.txt)

- `compatibility`: Standardized format: "Designed for Cursor, Claude Code, and Codex"

### Platform Invocation Methods

- **Cursor**: `/skill-name` slash command or Skill tool
- **Claude Code**: `openskills read <skill-name>` or Skill tool
- **Codex**: Auto-discovered from `.codex/skills/` or natural request

### Prohibited Patterns

- No Claude Code-specific hooks
- No hardcoded platform paths
- No platform-specific tool dependencies (unless documented in compatibility field)