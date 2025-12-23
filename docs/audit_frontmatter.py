#!/usr/bin/env python3
"""Audit frontmatter across all skills"""
import os
import re
from pathlib import Path

def extract_frontmatter(skill_path):
    """Extract YAML frontmatter from SKILL.md"""
    try:
        with open(skill_path, 'r') as f:
            content = f.read()

        # Match YAML frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter
    except Exception as e:
        return {"error": str(e)}

def main():
    base_dir = Path('/Users/damon/Vueni-App-refactor/.claude/skills')

    print("# Frontmatter Audit Report\n")
    print("## Skills in .claude/skills/\n")

    skills = sorted([d for d in base_dir.iterdir() if d.is_dir()])

    for skill_dir in skills:
        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            print(f"### {skill_dir.name} - ❌ NO SKILL.md\n")
            continue

        fm = extract_frontmatter(skill_md)
        if fm is None:
            print(f"### {skill_dir.name} - ❌ NO FRONTMATTER\n")
            continue

        if "error" in fm:
            print(f"### {skill_dir.name} - ❌ ERROR: {fm['error']}\n")
            continue

        print(f"### {skill_dir.name}\n")
        for key in ['name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools']:
            if key in fm:
                value = fm[key]
                if len(value) > 80:
                    value = value[:77] + '...'
                print(f"- **{key}**: {value}")
            else:
                print(f"- **{key}**: ❌ MISSING")
        print()

if __name__ == '__main__':
    main()
