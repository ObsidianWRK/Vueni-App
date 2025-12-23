# Skills Alignment Refactor - Inventory Report

**Date**: 2025-12-23
**Purpose**: Comprehensive inventory before standardizing skills alignment

## Executive Summary

- **Total skills in `.claude/skills/`**: 22 (canonical source)
- **Total skills in `.codex/skills/`**: 22 (in sync with canonical)
- **Total skills in `skills/`**: 19 (Cursor subset, 3 missing)
- **Skills in AGENTS.md**: 21 (1 skill missing)
- **Skills with minimal frontmatter** (name + description only): 0
- **Skills with extended frontmatter**: 22 (all have license; 3 have compatibility, 2 have metadata/allowed-tools)

## Directory Comparison

### .claude/skills/ vs .codex/skills/
✅ **IN SYNC** - Both directories contain the same 22 skills

### .claude/skills/ vs skills/ (Cursor subset)
❌ **OUT OF SYNC** - skills/ is missing 3 skills:
1. `expo-ios-designer`
2. `shadcn-ui`
3. `template`

## AGENTS.md Alignment

**Skills in AGENTS.md**: 21 entries
**Skills in `.claude/skills/`**: 22 directories

### Missing from AGENTS.md
- `template` (confirmed by comparison)

### Alignment Issues
All skill names in AGENTS.md match directory names except for the missing `template` skill.

## Frontmatter Analysis

### Current State
All 22 skills have:
- ✅ `name` field
- ✅ `description` field
- ✅ `license` field

Extended fields (to be removed per plan):
- `compatibility`: 3 skills (deep-research, ocr, plan-mode)
- `metadata`: 2 skills (deep-research, plan-mode)
- `allowed-tools`: 2 skills (deep-research, plan-mode)

### Target State (Minimal Frontmatter per superpowers:writing-skills)
All skills should have **ONLY**:
- `name`
- `description`

Fields to remove:
- `license` (move to LICENSE.txt or body)
- `compatibility` (move to body or remove)
- `metadata` (remove or move to body)
- `allowed-tools` (remove or move to body)

## License Distribution

- **MIT**: 3 skills (deep-research, ocr, plan-mode)
- **Apache-2.0**: 4 skills (doc-coauthoring, expo-ios-designer, shadcn-ui, template)
- **Proprietary**: 3 skills (docx, pdf, pptx, xlsx)
- **"Complete terms in LICENSE.txt"**: 12 skills (others)

## Skills by Category

### Document Processing
- docx, pdf, pptx, xlsx

### Design & Visual
- algorithmic-art, brand-guidelines, canvas-design, frontend-design, slack-gif-creator, theme-factory

### Development Tools
- expo-ios-designer, mcp-builder, shadcn-ui, webapp-testing, web-artifacts-builder

### Workflow & Productivity
- deep-research, doc-coauthoring, internal-comms, ocr, plan-mode, skill-creator, template

## Banned Patterns Found

### Platform-Specific Paths
(To be audited in Phase 2)

### Hook References
- `ocr` - Recently cleaned, should have no hook references
- Others - To be checked

### Hard Model Dependencies
- `ocr` - Has platform-specific guidance for Gemini (this is acceptable as guidance, not hard requirement)

## Recommendations for Phase 2

1. **Standardize frontmatter**: Remove `license`, `compatibility`, `metadata`, `allowed-tools` from all skills
2. **Add `template` to AGENTS.md** to achieve alignment
3. **Update skill-auto-loader.sh** if it parses extended frontmatter fields
4. **Verify no hook references** across all skills
5. **Test each skill** after frontmatter standardization (TDD pressure-scenario testing)

## Baseline Validation Results

All 22 skills in `.claude/skills/` **PASS** validation with current extended frontmatter:
- Valid: 22
- Errors: 0
- Warnings: 0

See [baseline-validation.txt](baseline-validation.txt) for details.

## Next Steps

1. ✅ Phase 0: Git Setup & Baseline - COMPLETE
2. ➡️ Phase 1: Inventory & Verification - IN PROGRESS
3. 🔜 Phase 2: Standardize Skills with TDD
4. 🔜 Phase 3: Align AGENTS.md Registry
5. 🔜 Phase 4: Update Validators
6. 🔜 Phase 5: Sync & Validation
7. 🔜 Phase 6: Documentation & Completion
