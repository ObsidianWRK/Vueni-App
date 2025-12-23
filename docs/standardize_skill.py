#!/usr/bin/env python3
"""
Standardize a skill's frontmatter to minimal format (name + description only)
Per superpowers:writing-skills specification
"""
import os
import re
import sys
from pathlib import Path

def extract_frontmatter_and_body(content):
    """Extract YAML frontmatter and body from SKILL.md content"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return None, content

    frontmatter = match.group(1)
    body = match.group(2)
    return frontmatter, body

def parse_frontmatter(frontmatter_text):
    """Parse YAML frontmatter into dict"""
    result = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    return result

def create_minimal_frontmatter(name, description):
    """Create minimal frontmatter with only name and description"""
    # Clean description - remove quotes if present
    desc = description.strip()
    if (desc.startswith('"') and desc.endswith('"')) or \
       (desc.startswith("'") and desc.endswith("'")):
        desc = desc[1:-1]

    return f"""---
name: {name}
description: {desc}
---"""

def check_banned_patterns(content, skill_name):
    """Check for banned patterns in skill content"""
    issues = []

    # Check for hook references
    if '.claude/hooks/' in content or '.codex/hooks/' in content:
        issues.append("❌ Contains hook path references (.claude/hooks/ or .codex/hooks/)")

    # Check for hardcoded absolute paths (simple check)
    if re.search(r'[/\\]Users[/\\]', content) or re.search(r'[Cc]:[/\\]', content):
        issues.append("❌ Contains hardcoded absolute paths")

    # Check for hard model requirements
    must_patterns = [
        r'MUST use \w+',
        r'requires? [A-Z][a-z]+ \d+',
        r'only works with \w+',
    ]
    for pattern in must_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"⚠️ May contain hard model requirement: {pattern}")

    return issues

def standardize_skill(skill_path):
    """Standardize a single skill's frontmatter"""
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        return False, f"❌ SKILL.md not found in {skill_path}"

    # Read current content
    with open(skill_md, 'r') as f:
        content = f.read()

    # Extract frontmatter and body
    frontmatter_text, body = extract_frontmatter_and_body(content)
    if frontmatter_text is None:
        return False, "❌ No frontmatter found"

    # Parse frontmatter
    fm = parse_frontmatter(frontmatter_text)

    if 'name' not in fm or 'description' not in fm:
        return False, "❌ Missing required name or description"

    # Create minimal frontmatter
    new_frontmatter = create_minimal_frontmatter(fm['name'], fm['description'])
    new_content = new_frontmatter + '\n' + body

    # Check banned patterns
    issues = check_banned_patterns(new_content, fm['name'])

    # Write standardized content
    with open(skill_md, 'w') as f:
        f.write(new_content)

    # Report
    report = f"✅ Standardized {fm['name']}\n"
    report += f"  - Removed fields: {', '.join([k for k in fm.keys() if k not in ['name', 'description']])}\n"

    if issues:
        report += "  - Issues found:\n"
        for issue in issues:
            report += f"    {issue}\n"
    else:
        report += "  - ✅ No banned patterns detected\n"

    return True, report

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 standardize_skill.py <skill-name>")
        sys.exit(1)

    skill_name = sys.argv[1]
    skill_path = Path(f'/Users/damon/Vueni-App-refactor/.claude/skills/{skill_name}')

    if not skill_path.exists():
        print(f"❌ Skill directory not found: {skill_path}")
        sys.exit(1)

    success, report = standardize_skill(skill_path)
    print(report)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
