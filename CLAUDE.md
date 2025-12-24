# CLAUDE

## Purpose
Clean-slate Agent Skills library. Only keep AGENTS.md, CLAUDE.md, the canonical `skills/` directory, and tool discovery adapters.

## How to work in this repo
- Always read and follow `AGENTS.md` (skill check, no web search unless allowed, planning rules).
- Use the canonical skills under `skills/` for all tooling; do not duplicate skills elsewhere.
- Keep adapters pointing to the canonical library: `.claude/skills`, `.codex/skills`, `.cursor/skills` → `../skills`.
- Treat additions as new skills following the Agent Skills spec (folder name matches `name` in `SKILL.md` frontmatter).

## Commands / verification
- Spot-check skills: `find skills -maxdepth 2 -name SKILL.md`
- Validate frontmatter names vs folders (example): `python scripts/validate_skill_names.py` (if available) or a one-off check.

## Notes
- No other project files should be added beyond the allowlist.
- Audit new skills for safety (no untrusted scripts/network fetches) before committing.
