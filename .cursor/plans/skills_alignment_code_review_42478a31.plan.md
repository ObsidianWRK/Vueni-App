---
name: Skills Alignment Code Review
overview: Complete code review ensuring alignment between Skill files (SKILL.md), AGENTS.md registry, and hooks across Cursor, Claude Code, and Codex. Standardizes frontmatter to minimal format, verifies registry alignment, removes platform-specific dependencies, and ensures cross-platform compatibility.
todos:
  - id: T1
    content: Create comprehensive skill inventory - extract frontmatter from all SKILL.md files, list all skills in .claude/skills/, .codex/skills/, and skills/, compare with AGENTS.md entries
    status: pending
  - id: T2
    content: Verify AGENTS.md alignment - compare skill names in AGENTS.md XML entries with .claude/skills/ directory names, identify mismatches
    status: pending
    dependencies:
      - T1
  - id: T3
    content: Fix AGENTS.md entries - add missing skills, remove orphaned entries, update descriptions to match SKILL.md frontmatter
    status: pending
    dependencies:
      - T2
  - id: T4
    content: Standardize frontmatter for all skills - remove all fields except name and description from all .claude/skills/*/SKILL.md files
    status: pending
    dependencies:
      - T1
  - id: T5
    content: Scan for banned patterns - check all SKILL.md and reference files for hooks, hardcoded paths, hard model requirements, platform-specific requirements
    status: pending
    dependencies:
      - T1
  - id: T6
    content: Fix banned pattern violations - remove hook references, replace absolute paths, move model requirements to platform guidance sections
    status: pending
    dependencies:
      - T5
  - id: T7
    content: Verify no hooks exist - check .claude/hooks/ directory, .claude/settings.local.json for hook configs, search all files for hook references
    status: pending
  - id: T8
    content: Standardize platform guidance sections - ensure consistent format across skills with platform-specific content
    status: pending
    dependencies:
      - T4
  - id: T9
    content: Sync skills to .codex/skills/ directory - run sync script to mirror .claude/skills/ to .codex/skills/
    status: pending
    dependencies:
      - T4
  - id: T10
    content: Update validation scripts - enhance validate_skills.py and validate_repo.py to check minimal frontmatter, banned patterns, AGENTS.md alignment
    status: pending
    dependencies:
      - T4
      - T6
  - id: T11
    content: Update documentation - ensure INSTALLATION_GUIDE.md, README.md, docs/banned-patterns.md reflect standards
    status: pending
    dependencies:
      - T4
      - T6
  - id: T12
    content: Run full validation suite - execute validate_repo.py and validate_skills.py on all directories, fix any errors
    status: pending
    dependencies:
      - T3
      - T4
      - T6
      - T9
      - T10
  - id: T13
    content: Create alignment report - document all changes, findings, and provide checklist for future skill additions
    status: pending
    dependencies:
      - T12
---

# Skills Alignment Code Review Plan

## Goal

Conduct a complete code review to ensure alignment between:

- Skill files (`SKILL.md` in `.claude/skills/`, `.codex/skills/`, `skills/`)
- `AGENTS.md` skill registry
- Hooks (verify none exist, as they're Claude Code-specific)

Ensure complete compatibility across Cursor, Claude Code, and Codex platforms.

## Context

### Current State

- **Skills locations**:
    - `.claude/skills/` - Canonical source (21 skills)
    - `.codex/skills/` - Mirror for Codex (synced from `.claude/skills/`)
    - `skills/` - Curated subset for Cursor (19 skills)
- **Registry**: `AGENTS.md` contains XML-formatted skill entries (21 skills listed)
- **Validation**: Scripts exist (`validate_skills.py`, `validate_repo.py`) but may not catch all alignment issues
- **Hooks**: Previously removed from OCR (Claude Code-specific), need to verify no other hooks exist
- **Frontmatter**: Mixed state - some skills have minimal (`name` + `description`), others have extra fields (`license`, `compatibility`, `metadata`, `allowed-tools`)

### Standards Reference

- **Minimal frontmatter** (per `docs/banned-patterns.md` and `skills/skill-creator/SKILL.md`): Only `name` and `description` required
- **Official spec** (`.tmp_agentskills/docs/specification.mdx`): Allows optional `license`, `compatibility`, `metadata`, `allowed-tools`
- **Banned patterns**: No hooks, no hardcoded paths, no platform-specific requirements outside guidance sections

### Platform Differences

| Platform | Skills Directory | Discovery Method | AGENTS.md Usage ||----------|-----------------|------------------|-----------------|| **Cursor** | `skills/` (subset) + `.claude/skills/` via openskills | Listed in `AGENTS.md` | Reads XML skill registry || **Claude Code** | `.claude/skills/` | Auto-discovered + `openskills read` | Reads XML skill registry || **Codex** | `.codex/skills/` | Auto-discovered at startup | Reads XML skill registry |

## Approach

1. **Audit Phase**: Inventory all skills, extract frontmatter, verify directory structure
2. **Alignment Phase**: Compare `AGENTS.md` entries with actual skill directories
3. **Standardization Phase**: Standardize frontmatter to minimal format (name + description only)
4. **Compatibility Phase**: Scan for banned patterns (hooks, hardcoded paths, platform-specific requirements)
5. **Sync Phase**: Verify `.codex/skills/` mirrors `.claude/skills/` correctly
6. **Validation Phase**: Run and update validation scripts
7. **Documentation Phase**: Update docs to reflect standards

## Steps

### 1. Create Comprehensive Skill Inventory

**What**: Extract complete inventory of all skills across all directories**Actions**:

- List all skills in `.claude/skills/` (canonical)
- List all skills in `.codex/skills/` (mirror)
- List all skills in `skills/` (Cursor subset)
- Extract frontmatter from each `SKILL.md`:
    - `name` field
    - `description` field
    - Extra fields (`license`, `compatibility`, `metadata`, `allowed-tools`)
- Extract skill entries from `AGENTS.md` (XML `<skill><name>` tags)

**Output**: `docs/alignment-inventory.md` with:

- Skill directory inventory (all three locations)
- Frontmatter comparison table
- `AGENTS.md` registry entries
- Mismatches identified

**Files**:

- `.claude/skills/*/SKILL.md` (all 21 skills)
- `.codex/skills/*/SKILL.md` (if exists)
- `skills/*/SKILL.md` (19 skills)
- `AGENTS.md`

### 2. Verify AGENTS.md Alignment

**What**: Ensure `AGENTS.md` entries exactly match skill directories**Actions**:

- Extract skill names from `AGENTS.md` XML entries
- Compare with `.claude/skills/` directory names
- Identify:
    - Skills in directories but missing from `AGENTS.md`
    - Skills in `AGENTS.md` but missing from directories
    - Description mismatches between `AGENTS.md` and `SKILL.md` frontmatter
    - Skills in `skills/` (Cursor subset) not in `AGENTS.md`

**Fix actions**:

- Add missing skills to `AGENTS.md` (if directory exists)
- Remove orphaned entries from `AGENTS.md` (if directory missing)
- Update descriptions in `AGENTS.md` to match `SKILL.md` frontmatter
- Ensure `location` field is correct (`project` for all)

**Files**: `AGENTS.md`, all skill directories

### 3. Standardize Frontmatter to Minimal Format

**What**: Remove all frontmatter fields except `name` and `description` per minimal standard**Rationale**: Per `docs/banned-patterns.md` and `skills/skill-creator/SKILL.md`, minimal frontmatter is the standard. Optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`) should be removed to ensure cross-platform compatibility.**Actions**:

- For each skill in `.claude/skills/`:
    - Extract current frontmatter
    - Create minimal frontmatter with only `name` and `description`
    - Preserve body content unchanged
    - Write standardized `SKILL.md`
- Move license info to `LICENSE.txt` (if not already present)
- Move compatibility info to body content in "Platform-specific guidance" section (if needed)

**Template**:

```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it.
---
```

**Files**: All `.claude/skills/*/SKILL.md` files (21 skills)

### 4. Scan for Banned Patterns

**What**: Check all skills for banned patterns per `docs/banned-patterns.md`**Patterns to check**:

1. Hook references: `.claude/hooks/`, `.codex/hooks/`, or similar
2. Hardcoded absolute paths: `/Users/`, `/home/`, `C:\`, etc.
3. Hard model requirements: "MUST use [model]", "requires [model]" outside platform guidance
4. Platform-specific invocation requirements outside guidance sections
5. Frontmatter fields beyond `name` and `description` (after standardization)

**Actions**:

- Scan all `SKILL.md` files for banned patterns
- Scan all skill reference files (`references/*.md`)
- Document findings in inventory
- Fix violations:
    - Remove hook references
    - Replace absolute paths with relative paths
    - Move model requirements to "Platform-specific guidance" sections
    - Move platform-specific invocation to guidance sections

**Files**: All skill files (SKILL.md, references/*.md, scripts/*)

### 5. Verify Hook Removal

**What**: Ensure no Claude Code-specific hooks exist**Actions**:

- Check `.claude/hooks/` directory (should not exist or be empty)
- Check `.claude/settings.local.json` for hook configurations
- Search all files for hook references
- Verify OCR skill hook removal was complete

**Files**: `.claude/hooks/`, `.claude/settings.local.json`, all skill files

### 6. Standardize Platform Guidance Sections

**What**: Ensure consistent format for platform-specific content**Actions**:

- Identify skills with platform-specific guidance (e.g., `ocr`, `plan-mode`)
- Standardize section format:
  ```markdown
    ## Platform-specific guidance
    
    ### Cursor
    - [Cursor-specific instructions]
    
    ### Claude Code
    - [Claude Code-specific instructions]
    
    ### Codex
    - [Codex-specific instructions]
  ```




- Ensure all platform guidance is in designated sections
- Verify no platform-specific requirements exist outside these sections

**Files**: Skills with platform-specific content (`ocr/SKILL.md`, `plan-mode/SKILL.md`, etc.)

### 7. Sync Skills to Codex Directory

**What**: Ensure `.codex/skills/` mirrors `.claude/skills/` correctly**Actions**:

- Run sync script: `python3 scripts/sync_skills.py --dry-run` (verify first)
- Review sync output
- Run actual sync: `python3 scripts/sync_skills.py`
- Verify all skills copied correctly
- Check for sync errors or missing files

**Files**: `scripts/sync_skills.py`, `.codex/skills/`

### 8. Update Validation Scripts

**What**: Enhance validation scripts to catch alignment issues**Actions**:

- Update `scripts/validate_skills.py`:
    - Add check for minimal frontmatter (warn on extra fields)
    - Add banned pattern detection
    - Add hook reference detection
    - Add platform-specific requirement detection
- Update `scripts/validate_repo.py`:
    - Verify `AGENTS.md` entries match directories exactly
    - Check description alignment between `AGENTS.md` and `SKILL.md`
    - Verify no internal skills (`template`) in `AGENTS.md`
- Test validation scripts on all skills

**Files**: `scripts/validate_skills.py`, `scripts/validate_repo.py`

### 9. Update Documentation

**What**: Ensure documentation reflects standards and alignment**Actions**:

- Update `INSTALLATION_GUIDE.md` if needed
- Update `README.md` if structure changed
- Verify `docs/banned-patterns.md` is accurate
- Update `skills/skill-creator/SKILL.md` if standards changed

**Files**: `INSTALLATION_GUIDE.md`, `README.md`, `docs/banned-patterns.md`, `skills/skill-creator/SKILL.md`

### 10. Run Full Validation Suite

**What**: Execute all validation checks to verify alignment**Actions**:

- Run `python3 scripts/validate_repo.py --verbose`
- Run `python3 scripts/validate_skills.py --all`
- Run `python3 scripts/validate_skills.py --codex`
- Run `python3 scripts/validate_skills.py --cursor`
- Fix any errors found
- Re-run until all validations pass

**Files**: All validation scripts

### 11. Create Alignment Report

**What**: Document findings and changes**Actions**:

- Create `docs/alignment-report.md` with:
    - Summary of changes made
    - Skills standardized (frontmatter changes)
    - `AGENTS.md` fixes (additions/removals/updates)
    - Banned patterns found and fixed
    - Hook verification results
    - Sync status
    - Validation results
    - Checklist for future skill additions

**Files**: `docs/alignment-report.md`

## Assumptions

- `.claude/skills/` is the canonical source; `.codex/skills/` is a mirror
- `skills/` directory is a curated subset for Cursor (may not need full alignment)
- Minimal frontmatter standard (`name` + `description` only) is preferred for cross-platform compatibility
- Hooks are Claude Code-specific and should not be used
- All skills should work across Cursor, Claude Code, and Codex (unless explicitly documented otherwise)
- `AGENTS.md` must exactly match `.claude/skills/` directory contents

## Risks & Mitigations

| Risk | Impact | Mitigation ||------|--------|------------|| Breaking existing skill functionality | H | Test each skill after standardization; preserve behavior while standardizing format || Missing skills in AGENTS.md | M | Automated comparison script; manual verification || Platform-specific behavior lost | M | Document platform differences in "Platform-specific guidance" sections || Sync script fails | L | Manual verification; check sync script logs || Validation scripts miss issues | M | Manual review; add comprehensive test cases || Frontmatter standardization breaks tooling | M | Verify validation scripts handle minimal frontmatter correctly |

## Implementation Todos

| ID | Task | Depends On | Status ||----|------|------------|--------|| T1 | Create comprehensive skill inventory | – | pending || T2 | Verify AGENTS.md alignment with directories | T1 | pending || T3 | Fix AGENTS.md entries (add/remove/update) | T2 | pending || T4 | Standardize frontmatter for all skills (minimal format) | T1 | pending || T5 | Scan for banned patterns in all skills | T1 | pending || T6 | Fix banned pattern violations | T5 | pending || T7 | Verify no hooks exist | – | pending || T8 | Standardize platform guidance sections | T4 | pending || T9 | Sync skills to `.codex/skills/` directory | T4 | pending || T10 | Update validation scripts | T4, T6 | pending || T11 | Update documentation | T4, T6 | pending || T12 | Run full validation suite | T3, T4, T6, T9, T10 | pending || T13 | Create alignment report | T12 | pending |

## Cross-Platform Compatibility Standards

### Required Frontmatter Fields

- `name`: Must match directory name exactly (1-64 chars, lowercase alphanumeric + hyphens)
- `description`: Must clearly state when to use the skill (max 1024 chars)

### Prohibited Patterns

- No Claude Code-specific hooks (`.claude/hooks/` references)
- No hardcoded absolute paths (`/Users/`, `/home/`, `C:\`, etc.)
- No hard model requirements outside platform guidance sections
- No platform-specific invocation requirements outside guidance sections
- No frontmatter fields beyond `name` and `description`

### Platform Invocation Methods

- **Cursor**: `/skill-name` slash command or Skill tool (skills listed in `AGENTS.md`)
- **Claude Code**: `openskills read <skill-name>` or Skill tool (auto-discovered from `.clau

de/skills/`)

- **Codex**: Auto-discovered from `.codex/skills/` or natural request (skills listed in `AGENTS.md`)

### Platform Guidance Format

Platform-specific content must be in clearly marked sections:

```markdown
## Platform-specific guidance

### Cursor
- [Recommendations, not requirements]

### Claude Code
- [Recommendations, not requirements]

### Codex
- [Recommendations, not requirements]

```