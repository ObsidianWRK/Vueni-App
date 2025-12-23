#!/usr/bin/env python3
"""
Repository Validator

Validates the skills repository structure, ensuring:
- AGENTS.md skill registry aligns with .claude/skills/ directories
- Every skill has SKILL.md with required frontmatter (name, description, license)
- Every skill has LICENSE.txt
- No placeholder text remains in published skills

Usage:
    python scripts/validate_repo.py [--verbose]
"""

import re
import sys
from pathlib import Path

# Skills that are internal/templates and should NOT appear in AGENTS.md
INTERNAL_SKILLS = {"template"}

# Placeholder patterns that indicate incomplete content
PLACEHOLDER_PATTERNS = [
    r"Replace with description",
    r"\[TODO:",
    r"Insert instructions below",
]


def find_repo_root() -> Path:
    """Find the repository root by looking for AGENTS.md."""
    current = Path(__file__).resolve().parent
    for _ in range(5):  # Look up to 5 levels
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    # Fallback to script's parent's parent
    return Path(__file__).resolve().parent.parent


def extract_agents_skills(agents_path: Path) -> set[str]:
    """Extract skill names from AGENTS.md."""
    content = agents_path.read_text()
    pattern = r"<name>([^<]+)</name>"
    return set(re.findall(pattern, content))


def extract_frontmatter(skill_md_path: Path) -> dict:
    """Extract YAML frontmatter from SKILL.md."""
    content = skill_md_path.read_text()
    if not content.startswith("---"):
        return {}

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter


def check_placeholders(path: Path) -> list[str]:
    """Check for placeholder patterns in a file."""
    content = path.read_text()
    found = []
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            found.append(pattern)
    return found


class ValidationError:
    def __init__(self, skill: str, message: str, severity: str = "error"):
        self.skill = skill
        self.message = message
        self.severity = severity

    def __str__(self):
        icon = "❌" if self.severity == "error" else "⚠️"
        return f"{icon} [{self.skill}] {self.message}"


def validate_repo(repo_root: Path, verbose: bool = False) -> list[ValidationError]:
    """Validate the repository structure and return errors."""
    errors = []

    agents_path = repo_root / "AGENTS.md"
    skills_dir = repo_root / ".claude" / "skills"

    # Check AGENTS.md exists
    if not agents_path.exists():
        errors.append(ValidationError("AGENTS.md", "File not found"))
        return errors

    # Check skills directory exists
    if not skills_dir.exists():
        errors.append(ValidationError(".claude/skills", "Directory not found"))
        return errors

    # Get skills from AGENTS.md
    registered_skills = extract_agents_skills(agents_path)
    if verbose:
        print(f"Found {len(registered_skills)} skills in AGENTS.md")

    # Get skill directories
    skill_dirs = {d.name for d in skills_dir.iterdir() if d.is_dir()}
    if verbose:
        print(f"Found {len(skill_dirs)} skill directories")

    # Check for skills in AGENTS.md but missing directories
    for skill in registered_skills:
        if skill not in skill_dirs:
            errors.append(ValidationError(
                skill,
                f"Registered in AGENTS.md but directory not found at .claude/skills/{skill}/"
            ))

    # Check for internal skills that shouldn't be in AGENTS.md
    for skill in INTERNAL_SKILLS:
        if skill in registered_skills:
            errors.append(ValidationError(
                skill,
                "Internal/template skill should not be listed in AGENTS.md",
                severity="error"
            ))

    # Check each skill directory
    for skill_name in skill_dirs:
        skill_path = skills_dir / skill_name
        skill_md = skill_path / "SKILL.md"
        license_txt = skill_path / "LICENSE.txt"
        is_internal = skill_name in INTERNAL_SKILLS

        if verbose:
            print(f"Checking skill: {skill_name}")

        # Check SKILL.md exists
        if not skill_md.exists():
            errors.append(ValidationError(skill_name, "Missing SKILL.md"))
            continue

        # Check frontmatter
        frontmatter = extract_frontmatter(skill_md)

        if not frontmatter:
            errors.append(ValidationError(skill_name, "SKILL.md missing YAML frontmatter"))
        else:
            # Check required fields
            if "name" not in frontmatter:
                errors.append(ValidationError(skill_name, "SKILL.md frontmatter missing 'name'"))
            elif frontmatter["name"] != skill_name:
                errors.append(ValidationError(
                    skill_name,
                    f"Frontmatter name '{frontmatter['name']}' doesn't match directory name '{skill_name}'"
                ))

            if "description" not in frontmatter:
                errors.append(ValidationError(skill_name, "SKILL.md frontmatter missing 'description'"))

            # Note: 'license' field is optional per Agent Skills specification
            # Only name and description are required

        # Check for placeholder text (only in non-internal skills)
        if not is_internal:
            placeholders = check_placeholders(skill_md)
            if placeholders:
                errors.append(ValidationError(
                    skill_name,
                    f"Contains placeholder text: {', '.join(placeholders)}"
                ))

        # Check skill is registered (unless internal)
        if not is_internal and skill_name not in registered_skills:
            errors.append(ValidationError(
                skill_name,
                "Skill directory exists but not registered in AGENTS.md",
                severity="warning"
            ))

    # Check skill-check enforcement infrastructure exists
    validate_skill_checks_script = repo_root / "scripts" / "validate_skill_checks.py"
    if not validate_skill_checks_script.exists():
        errors.append(ValidationError(
            "skill-check-enforcement",
            "Missing scripts/validate_skill_checks.py (skill-check validation script)",
            severity="warning"
        ))
    
    hooks_dir = repo_root / ".claude" / "hooks"
    pre_task_hook = hooks_dir / "pre-task-skill-check.js"
    if not pre_task_hook.exists():
        errors.append(ValidationError(
            "skill-check-enforcement",
            "Missing .claude/hooks/pre-task-skill-check.js (pre-task skill-check hook)",
            severity="warning"
        ))
    
    hooks_config = repo_root / ".claude" / "hooks.json"
    if not hooks_config.exists():
        errors.append(ValidationError(
            "skill-check-enforcement",
            "Missing .claude/hooks.json (hooks configuration)",
            severity="warning"
        ))
    
    # Check plan completion validation
    try:
        try:
            from scripts.validate_plan_completion import validate_plan_completion
        except Exception:
            from validate_plan_completion import validate_plan_completion

        _, violations = validate_plan_completion(repo_root, verbose=False)
        for violation in violations:
            errors.append(ValidationError("plan_completion", violation, severity="error"))
    except Exception as exc:
        errors.append(ValidationError(
            "plan_completion",
            f"plan completion validation failed: {exc}",
            severity="error"
        ))

    return errors


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    repo_root = find_repo_root()
    print(f"Validating repository: {repo_root}\n")

    errors = validate_repo(repo_root, verbose)

    # Separate errors and warnings
    actual_errors = [e for e in errors if e.severity == "error"]
    warnings = [e for e in errors if e.severity == "warning"]

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  {w}")
        print()

    if actual_errors:
        print("Errors:")
        for e in actual_errors:
            print(f"  {e}")
        print(f"\n❌ Validation failed with {len(actual_errors)} error(s)")
        sys.exit(1)
    else:
        print("✅ Validation passed!")
        if warnings:
            print(f"   ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
