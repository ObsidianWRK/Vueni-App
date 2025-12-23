# Agent Systems Discovery Report

**Date:** 2025-12-23
**Repository:** Vueni-App
**Purpose:** Discovery phase for agent systems refactoring

## Executive Summary

The Vueni-App repository contains a comprehensive agent instruction system with **critical duplication issues** and **missing adapters** for Claude Code and Cursor. The root `AGENTS.md` is well-structured but approaching size limits. Skills are duplicated across three directories with content drift. No dedicated Claude Code or Cursor rules exist, violating the portability requirement.

**Key Findings:**
- ✅ Root AGENTS.md exists (30,225 bytes, under 32KB Codex limit)
- ❌ Three duplicate skills directories (.claude/skills, .codex/skills, skills/)
- ❌ No Claude Code adapter (.claude/CLAUDE.md or .claude/rules/)
- ❌ No Cursor rules adapter (.cursor/rules/)
- ✅ Validation infrastructure exists (scripts + CI)
- ⚠️  Content drift detected between skill copies

---

## 1. File Inventory

### 1.1 Agent Instruction Files

| Location | Type | Size | Status |
|----------|------|------|--------|
| `/AGENTS.md` | Canonical instructions | 30,225 bytes | ✅ Exists |
| `.claude/CLAUDE.md` | Claude Code index | N/A | ❌ Missing |
| `.claude/rules/` | Claude Code rules | N/A | ❌ Missing |
| `.cursor/rules/` | Cursor rules | N/A | ❌ Missing |

**Nested AGENTS.md files:** None found (flat structure)

### 1.2 Skills Directories

Three separate skills directories exist, creating **duplication and maintenance burden**:

| Directory | Count | Purpose | Status |
|-----------|-------|---------|--------|
| `.claude/skills/` | 22 skills | Claude Code | ⚠️ Duplicated |
| `.codex/skills/` | 22 skills | OpenAI Codex | ⚠️ Duplicated |
| `skills/` | 21 skills | Cursor (curated subset) | ⚠️ Duplicated |

**Key Skills:**
- algorithmic-art, brand-guidelines, canvas-design, deep-research
- doc-coauthoring, docx, expo-ios-designer, frontend-design
- internal-comms, mcp-builder, ocr, pdf, plan-mode, pptx
- shadcn-ui, skill-creator, slack-gif-creator, template (internal)
- theme-factory, web-artifacts-builder, webapp-testing, xlsx
- Plus custom skills: Agent Development, autonomous-skill, ceo-advisor, codex-cli, content-research-writer, data-storytelling, denario, hive-mind-advanced, Hooks Automation, prompt-engineering-patterns, pyhealth, rag-implementation, scientific-brainstorming, stream-chain, using-skills, ux-researcher-designer

**Duplication Issues:**
- `.claude/skills/` and `.codex/skills/` are identical (22 skills each)
- `skills/` missing "template" skill (21 vs 22)
- Content drift detected: `plan-mode/SKILL.md` has different descriptions:
  - `.claude/skills/`: "Standardized planning workflow..."
  - `skills/`: "Create structured plans using a standardized planning workflow..."

### 1.3 Hooks & Commands

| Type | Location | Files | Status |
|------|----------|-------|--------|
| Claude Hooks | `.claude/hooks/` | 3 hooks | ✅ Configured |
| Hook Config | `.claude/hooks.json` | 1 config | ✅ Active |
| Cursor Commands | `.cursor/commands/` | 6 commands | ✅ Exists |

**Claude Hooks:**
- `pre-task-skill-check.js` - Enforces skill checking before tool use
- `pre-session-plan-check.js` - Checks for plans at session start
- `post-todo-completion-check.js` - Triggers plan completion workflow

**Cursor Commands:**
- `commit.md`, `debug.md`, `deslop.md`, `ocr.md`, `pr.md`, `refactor.md`

### 1.4 Validation & Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `scripts/validate_repo.py` | Repo validation | ✅ Exists |
| `scripts/validate_skills.py` | Skill validation | ✅ Exists |
| `scripts/validate_plan_completion.py` | Plan completion check | ✅ Exists |
| `scripts/sync_skills.py` | Sync skills to .codex | ✅ Exists |
| `scripts/execute_plan_completion.py` | Auto plan completion | ✅ Exists |
| `scripts/sync_plan_todos.py` | Todo sync | ✅ Exists |
| `.github/workflows/validate.yml` | CI validation | ✅ Configured |

---

## 2. Scope Boundaries Analysis

### 2.1 Current Scope Structure

**Project Type:** Skills repository (not an application codebase)

**Top-level Directories:**
```
.
├── docs/           # Documentation & reports
├── scripts/        # Validation & automation
└── skills/         # Curated skills subset (Cursor)
```

**No nested subsystems requiring scoped AGENTS.md files** - this is a flat repository focused on agent skills and tooling.

### 2.2 Proposed Scope Tree

Given the repository structure, **no nested AGENTS.md files are needed**. The canonical instruction hierarchy should be:

```
Root Scope (AGENTS.md)
├── Global policies: skill checking, plan mode, completion workflow
├── Skills registry: available skills table
└── References:
    ├── .claude/CLAUDE.md → AGENTS.md (thin index)
    ├── .claude/rules/ → detailed policies by domain
    └── .cursor/rules/ → Cursor-specific adapters
```

**Rationale:**
- Repository is focused on agent tooling, not a complex codebase with subsystems
- No security-critical modules, monorepo packages, or services requiring different rules
- All skills follow the same contract (SKILL.md + frontmatter)
- Scoping would add unnecessary complexity without benefit

---

## 3. Contradictions & Duplication

### 3.1 Critical Duplication

**Problem:** Skills are duplicated across three directories, creating maintenance burden and drift risk.

**Evidence:**
1. `.claude/skills/plan-mode/SKILL.md` line 3:
   ```
   description: Standardized planning workflow for Cursor, Claude, and Codex...
   ```

2. `skills/plan-mode/SKILL.md` line 3:
   ```
   description: Create structured plans using a standardized planning workflow...
   ```

**Impact:**
- Updates must be applied to 3 locations
- High risk of inconsistency
- Violates "single source of truth" principle

### 3.2 Architecture Violations

**Missing Claude Code Adapter:**
- `.claude/CLAUDE.md` does not exist
- `.claude/rules/` directory does not exist
- Claude Code currently loads from system defaults only
- Violates requirement: "All .md files in .claude/rules/ load as project memory"

**Missing Cursor Rules:**
- `.cursor/rules/` directory does not exist
- No `.mdc` files for Cursor rule system
- Cursor currently has no operating contract or scoped rules
- Violates requirement: "All Cursor rules live under .cursor/rules/"

**Skills Architecture:**
- Skills should be in ONE canonical location
- Current README.md claims `.claude/skills/` is "canonical source"
- But `.codex/skills/` and `skills/` duplicate content
- Violates: "Adapters not forks"

### 3.3 Size Approaching Limit

**Current State:**
- `AGENTS.md` = 30,225 bytes (92% of 32,768 byte Codex limit)
- Adding more skills or policies risks exceeding limit

**Recommendation:**
- Keep root AGENTS.md thin (registry + high-priority policies)
- Move detailed policies to .claude/rules/ for Claude Code
- Keep skill checking, plan mode as high-priority inline (widely used)
- Extract less-critical sections (OCR auto-invocation, web search policy) to rules

---

## 4. Compatibility Assessment

### 4.1 Codex CLI Compatibility

**Status:** ✅ Mostly Compatible

**Passes:**
- Root AGENTS.md exists and is under 32KB limit
- No nested AGENTS.md files to concatenate
- Well-structured, runnable instructions

**Concerns:**
- Size at 92% of limit leaves little room for growth
- No documented override for `project_doc_max_bytes` if needed

### 4.2 Claude Code Compatibility

**Status:** ❌ Not Compatible

**Missing:**
- No `.claude/CLAUDE.md` (project memory index)
- No `.claude/rules/*.md` (scoped rules)
- Claude Code cannot load project-specific instructions beyond skills

**Required:**
- Create `.claude/CLAUDE.md` as thin index referencing AGENTS.md
- Create `.claude/rules/` with modules:
  - `code-style.md` (if any coding standards exist)
  - `testing.md` (test policies)
  - `security.md` (security considerations)
  - `architecture.md` (skills architecture contract)

### 4.3 Cursor Compatibility

**Status:** ❌ Not Compatible

**Missing:**
- No `.cursor/rules/` directory
- No `.mdc` rule files
- Cursor has slash commands but no rules system

**Required:**
- Create `.cursor/rules/00-operating-contract.mdc` (alwaysApply: true)
- Optional: Create scoped rules for high-impact areas
- Optional: Agent-requested playbooks

### 4.4 Skills Compatibility

**Status:** ⚠️ Partially Compatible

**Passes:**
- All skills have `SKILL.md` with frontmatter
- Directory structure follows contract
- Optional `references/`, `scripts/`, `assets/` used correctly

**Issues:**
- Skills duplicated across 3 directories
- Content drift between copies
- No clear canonical source despite README claim

---

## 5. Recommendations

### 5.1 Critical (Must Fix)

1. **Consolidate Skills** → ONE canonical location
   - **Proposal:** Keep `.claude/skills/` as canonical (22 skills including template)
   - Delete `.codex/skills/` (duplicated, use symlink or sync script if needed)
   - Delete `skills/` (Cursor can read from `.claude/skills/` or use symlink)
   - Update all references in AGENTS.md and documentation

2. **Create Claude Code Adapter**
   - Create `.claude/CLAUDE.md` (thin index)
   - Create `.claude/rules/` with domain-scoped policies
   - Reference AGENTS.md as canonical, don't duplicate

3. **Create Cursor Adapter**
   - Create `.cursor/rules/00-operating-contract.mdc` (alwaysApply)
   - Reference canonical AGENTS.md and skills
   - Keep rules minimal to avoid duplication

### 5.2 Important (Should Fix)

4. **Reduce AGENTS.md Size**
   - Move OCR auto-invocation policy to `.claude/rules/ocr-auto-invoke.md`
   - Keep skill checking, plan mode inline (high priority)
   - Target: <25KB to leave growth room

5. **Strengthen Validation**
   - Add validator for .claude/CLAUDE.md existence
   - Add validator for .cursor/rules/ structure
   - Add validator for skills duplication check
   - Add size check for Codex limit warning

### 5.3 Optional (Nice to Have)

6. **Skills Organization**
   - Group skills by category (design, documents, research, development)
   - Update AGENTS.md skills table with categories
   - Improve skill discovery

7. **Documentation**
   - Add "How This Works" guide for each tool (Cursor/Claude/Codex)
   - Document the canonical → adapter flow
   - Create ARCHITECTURE.md explaining instruction system

---

## 6. Validation Gate Status

| Gate ID | Gate Name | Status | Notes |
|---------|-----------|--------|-------|
| g1 | Instruction Topology | ⚠️ Partial | No contradictions, but duplication exists |
| g2 | Codex Limits | ✅ Pass | 30KB < 32KB limit |
| g3 | Claude Memory | ❌ Fail | .claude/CLAUDE.md missing, no .claude/rules/ |
| g4 | Cursor Rules | ❌ Fail | .cursor/rules/ missing entirely |
| g5 | Skills Quality | ⚠️ Partial | Skills have SKILL.md but are duplicated |

**Summary:** 1 Pass, 2 Fail, 2 Partial - **Refactoring Required**

---

## 7. Proposed Canonical Structure

```
Vueni-App/
├── AGENTS.md                           # Canonical instruction registry (thin)
│
├── .claude/
│   ├── CLAUDE.md                       # Index: "See AGENTS.md + rules/"
│   ├── rules/                          # Domain-scoped policies
│   │   ├── skills-architecture.md      # Skills contract + usage
│   │   ├── plan-workflows.md           # Plan mode + completion
│   │   └── skill-checking.md           # Skill checking enforcement
│   ├── hooks/                          # Execution hooks
│   │   ├── pre-task-skill-check.js
│   │   ├── pre-session-plan-check.js
│   │   └── post-todo-completion-check.js
│   └── skills/                         # CANONICAL skills source
│       ├── plan-mode/
│       ├── skill-creator/
│       └── ...
│
├── .cursor/
│   ├── rules/                          # Cursor adapters
│   │   └── 00-operating-contract.mdc   # alwaysApply: true
│   └── commands/                       # Slash commands
│       ├── commit.md
│       └── ...
│
├── .codex/
│   └── skills/ → ../.claude/skills/    # Symlink or sync script
│
├── scripts/
│   ├── validate_repo.py                # Enhanced validation
│   ├── validate_agent_system.py        # NEW: Full system validator
│   └── sync_skills.py                  # Sync to .codex if needed
│
└── docs/
    ├── DISCOVERY_REPORT.md             # This document
    ├── AGENT_SYSTEM.md                 # How it works guide
    └── CHANGELOG.md                    # Refactor changelog
```

---

## 8. Next Steps

Following the 5-phase execution plan:

### ✅ Phase 1: Discovery (Complete)
- Inventory complete
- Contradictions identified
- This report written

### 🔄 Phase 2: Canonicalize AGENTS.md (Next)
- Trim AGENTS.md to <25KB
- Extract policies to .claude/rules/
- Ensure no contradictions

### 🔄 Phase 3: Generate Adapters
- Create .claude/CLAUDE.md + rules/
- Create .cursor/rules/

### 🔄 Phase 4: Skills Refactor
- Consolidate to single canonical location
- Delete duplicates
- Update all references

### 🔄 Phase 5: Validation & CI
- Enhance validation scripts
- Update CI workflow
- Document verification process

---

## Appendix A: File Sizes

| File | Size (bytes) | % of Codex Limit |
|------|--------------|------------------|
| AGENTS.md | 30,225 | 92.2% |
| Target after refactor | <25,000 | <76.3% |

## Appendix B: Skills List

**All Skills (22):**
1. algorithmic-art
2. brand-guidelines
3. canvas-design
4. deep-research
5. doc-coauthoring
6. docx
7. expo-ios-designer
8. frontend-design
9. internal-comms
10. mcp-builder
11. ocr
12. pdf
13. plan-mode
14. pptx
15. shadcn-ui
16. skill-creator
17. slack-gif-creator
18. template (internal)
19. theme-factory
20. web-artifacts-builder
21. webapp-testing
22. xlsx

**Plus Custom Skills:**
- Agent Development, autonomous-skill, ceo-advisor, codex-cli
- content-research-writer, data-storytelling, denario
- hive-mind-advanced, Hooks Automation
- prompt-engineering-patterns, pyhealth, rag-implementation
- scientific-brainstorming, stream-chain, using-skills
- ux-researcher-designer

---

**Report Status:** Complete
**Validation Gates:** 1/5 Pass
**Recommendation:** Proceed with Phase 2 (Canonicalize AGENTS.md)
