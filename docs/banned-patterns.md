# Banned Patterns for Cross-Platform Skills

**Purpose**: Ensure all skills work across Cursor, Claude Code, and Codex without platform-specific dependencies.

## Banned Pattern Categories

### 1. Platform-Specific Hooks

❌ **BANNED**: References to `.claude/hooks/` or any platform-specific hook system

```markdown
<!-- BANNED -->
Configure the hook in `.claude/hooks/`:
```

✅ **ALLOWED**: Platform-agnostic workflow descriptions

```markdown
<!-- ALLOWED -->
## Platform-specific guidance

### Claude Code
Users can configure hooks for this skill in their settings.
```

### 2. Hardcoded Absolute Paths

❌ **BANNED**: Platform-specific absolute paths

```markdown
<!-- BANNED -->
/Users/username/.claude/skills/
C:\Users\username\.claude\skills\
```

✅ **ALLOWED**: Relative paths or environment-agnostic descriptions

```markdown
<!-- ALLOWED -->
Skills are located in the `.claude/skills/` directory relative to your workspace.
```

### 3. Hard Model Dependencies (Enforcement)

❌ **BANNED**: Forcing specific models with "must" or "required" language

```markdown
<!-- BANNED -->
You MUST use Gemini 3 Pro for this skill.
This skill requires Claude Sonnet.
```

✅ **ALLOWED**: Model recommendations as guidance in platform sections

```markdown
<!-- ALLOWED -->
### Cursor
- Prefer using Gemini 3 Pro for better vision capabilities
- The `/ocr` slash command automatically selects Gemini 3 Pro

### Claude Code & Codex
- Use the best available vision-capable model
```

### 4. Platform-Specific Invocation as Requirements

❌ **BANNED**: Enforcing platform-specific invocation methods outside of guidance sections

```markdown
<!-- BANNED -->
To use this skill, run: openskills read skill-name
```

✅ **ALLOWED**: Document invocation in platform-specific guidance sections

```markdown
<!-- ALLOWED -->
## Platform-specific guidance

### Cursor
Invoke with `/skill-name` slash command or Skill tool

### Claude Code
Invoke with `openskills read skill-name` or Skill tool

### Codex
Auto-discovered from `.codex/skills/` or invoke naturally
```

### 5. Extended Frontmatter Fields

❌ **BANNED**: Fields beyond `name` and `description` in frontmatter (per superpowers:writing-skills)

```yaml
# BANNED
---
name: skill-name
description: Description
license: MIT
compatibility: Cursor only
metadata:
  version: 1.0.0
allowed-tools: bash read write
---
```

✅ **ALLOWED**: Minimal frontmatter only

```yaml
# ALLOWED
---
name: skill-name
description: Clear description of what this skill does and when to use it
---
```

## Detection Rules

Skills MUST NOT contain:
1. The string `.claude/hooks/` or `.codex/hooks/` or similar hook paths
2. Absolute paths starting with `/Users/`, `/home/`, `C:\`, or similar
3. Phrases like "MUST use [model name]" or "requires [model name]" outside of platform guidance
4. Frontmatter fields other than `name` and `description`
5. Platform-specific invocation requirements in the main skill body (must be in platform guidance sections)

## Validation

These patterns will be checked by:
1. Updated `validate_skills.py` script
2. Manual review during standardization (Phase 2)
3. TDD pressure-scenario tests for each skill

## Exceptions

### Acceptable Platform-Specific Content
Platform-specific content IS allowed when:
1. Contained within clearly marked "Platform-specific guidance" sections
2. Presented as recommendations, not requirements
3. Provides alternative approaches for other platforms

Example:
```markdown
## Platform-specific guidance

### Cursor
- Prefer the `/skill-name` slash command for best results
- [Cursor-specific tips]

### Claude Code
- Use `openskills read skill-name` or the Skill tool
- [Claude Code-specific tips]

### Codex
- Skills are auto-discovered; invoke naturally or use Skill tool
- [Codex-specific tips]
```

## Rationale

These banned patterns ensure:
- **Portability**: Skills work across all platforms
- **Maintainability**: No platform-specific code to maintain separately
- **User Experience**: Consistent behavior regardless of platform
- **Standards Compliance**: Follows superpowers:writing-skills minimal frontmatter standard

## Audit Checklist

For each skill during Phase 2:
- [ ] No `.claude/hooks/` or similar hook references
- [ ] No hardcoded absolute paths
- [ ] No hard model requirements (only recommendations)
- [ ] Frontmatter has ONLY `name` and `description`
- [ ] Platform-specific content in designated guidance sections
- [ ] License information moved to LICENSE.txt or body
- [ ] Compatibility information removed or moved to body
- [ ] Metadata removed
- [ ] Allowed-tools removed
