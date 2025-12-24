# Discovery Report

## Inventory Summary
- AGENTS files: 1 (root `AGENTS.md`). No scoped AGENTS.md variants found.
- Claude rules: none present (`.claude/` missing).
- Cursor rules: none present (`.cursor/` missing).
- Skills installed: 21 skill directories under `skills/` (see "Skills Audit").

## Instruction Scope Tree (current)
- `/` → `AGENTS.md` (covers repository, skills, and all subpaths).
  - No nested AGENTS.md overrides detected.
  - No `.claude/rules` or `.cursor/rules` to adjust scope.

## AGENTS & Rules Status
- Root `AGENTS.md` is the only instruction source; it embeds skill-checking, plan-mode, and completion workflows.
- No CLAUDE or Cursor rule files exist; scopes currently rely solely on `AGENTS.md`.
- No WorkDone/plan automation artifacts (.cursor/plans) present.

## Skills Audit
Installed skill folders (all listed in `AGENTS.md` available-skills table):
`algorithmic-art`, `brand-guidelines`, `canvas-design`, `deep-research`, `doc-coauthoring`, `docx`, `expo-ios-designer`, `frontend-design`, `internal-comms`, `mcp-builder`, `ocr`, `pdf`, `plan-mode`, `pptx`, `shadcn-ui`, `skill-creator`, `slack-gif-creator`, `theme-factory`, `web-artifacts-builder`, `webapp-testing`, `xlsx`.

Findings (representative samples):
- Skills do not follow the required contract (purpose, triggers, tools/permissions, deterministic steps, acceptance tests, non-goals). Examples: `skills/plan-mode/SKILL.md` and `skills/theme-factory/SKILL.md` lack acceptance tests and non-goals, and embed procedural guidance instead of referencing canonical instructions.
- Embedded policy/behavioral guidance appears inside skill files rather than referencing `AGENTS.md`.

## Duplication / Conflict Check (g1)
- Only one AGENTS source; no scoped variants → no direct conflicting scopes detected.
- Potential duplication: policy text replicated inside skills instead of referencing canonical instructions. No explicit contradictions found, but decentralization increases risk.

## Codex Instruction Chain Size (g2)
- Root chain (`/`): `AGENTS.md` size 30,225 bytes (<32 KiB threshold).
- Representative nested directories (e.g., `skills/*`): inherit the same single `AGENTS.md` (≈30,225 bytes); no additional rule files, so chain remains under limit.
- No `project_doc_max_bytes` override present or required based on current size.

## Official Skill List Compliance
- Compared installed skills to the Anthropic official list published in root `AGENTS.md`; no extra/unlisted skills detected. No uninstall actions required.

## Gaps / Next Steps
- Create `.claude/CLAUDE.md` index and scoped `.claude/rules/*.yaml` without overlapping globs.
- Add `.cursor/rules/00-operating-contract.mdc` (alwaysApply) plus minimal high-risk scoped rules.
- Refactor `AGENTS.md` into concise canonical contract and introduce scoped overrides where behavior differs.
- Rewrite all `skills/*/SKILL.md` files to the required contract format and reference canonical instructions.
- Implement `scripts/validate-agent-system` and CI workflow to enforce instruction topology, size limits, rule formats, and skill quality gates.
- Document local validation commands in `VALIDATION.md`.
