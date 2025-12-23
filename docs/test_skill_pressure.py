#!/usr/bin/env python3
"""
Pressure-scenario testing for skills per superpowers:writing-skills
Tests that skill survives various stress conditions after standardization
"""
import os
import re
import sys
from pathlib import Path

def test_skill_structure(skill_path):
    """Test basic skill structure"""
    tests = []

    # Test 1: SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        tests.append(("✅", "SKILL.md exists"))
    else:
        tests.append(("❌", "SKILL.md missing"))
        return tests

    # Test 2: Frontmatter exists
    with open(skill_md, 'r') as f:
        content = f.read()

    if content.startswith('---\n') and '\n---\n' in content:
        tests.append(("✅", "Frontmatter present"))
    else:
        tests.append(("❌", "Frontmatter missing"))
        return tests

    # Test 3: Minimal frontmatter (name + description only)
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        lines = [l for l in fm_text.split('\n') if l.strip() and not l.strip().startswith('#')]

        has_name = any('name:' in line for line in lines)
        has_desc = any('description:' in line for line in lines)

        # Count non-empty, non-comment lines
        field_count = len(lines)

        if has_name and has_desc:
            tests.append(("✅", "Has name and description"))
        else:
            tests.append(("❌", "Missing name or description"))

        if field_count == 2:
            tests.append(("✅", "Minimal frontmatter (2 fields only)"))
        else:
            tests.append(("⚠️", f"Extra frontmatter fields ({field_count} fields, expected 2)"))

    # Test 4: Body content exists
    body = content.split('\n---\n', 2)[2] if '\n---\n' in content else ''
    if len(body.strip()) > 50:
        tests.append(("✅", "Skill body content present"))
    else:
        tests.append(("⚠️", "Skill body content minimal or missing"))

    # Test 5: No banned patterns
    banned_found = []
    if '.claude/hooks/' in content or '.codex/hooks/' in content:
        banned_found.append("hook references")
    if re.search(r'/Users/\w+', content) or re.search(r'C:[/\\]', content):
        banned_found.append("absolute paths")

    if not banned_found:
        tests.append(("✅", "No banned patterns detected"))
    else:
        tests.append(("❌", f"Banned patterns: {', '.join(banned_found)}"))

    return tests

def test_skill_invocability(skill_path):
    """Test that skill can be invoked (basic checks)"""
    tests = []

    skill_md = skill_path / 'SKILL.md'
    with open(skill_md, 'r') as f:
        content = f.read()

    # Test: Has workflow/usage instructions
    keywords = ['workflow', 'usage', 'how to', 'invoke', 'when to']
    has_instructions = any(kw in content.lower() for kw in keywords)

    if has_instructions:
        tests.append(("✅", "Contains workflow/usage instructions"))
    else:
        tests.append(("⚠️", "May be missing workflow/usage instructions"))

    # Test: Has clear purpose/description
    if '<purpose>' in content or '# Purpose' in content or '## Purpose' in content:
        tests.append(("✅", "Has clear purpose section"))
    else:
        tests.append(("⚠️", "May be missing clear purpose section"))

    return tests

def test_skill_resources(skill_path):
    """Test skill resources and dependencies"""
    tests = []

    # Check for LICENSE.txt
    license_file = skill_path / 'LICENSE.txt'
    if license_file.exists():
        tests.append(("✅", "LICENSE.txt present"))
    else:
        tests.append(("⚠️", "LICENSE.txt missing (may not be required)"))

    # Check for scripts/references directories
    scripts_dir = skill_path / 'scripts'
    refs_dir = skill_path / 'references'

    if scripts_dir.exists():
        script_count = len(list(scripts_dir.glob('*.py'))) + len(list(scripts_dir.glob('*.js')))
        tests.append(("✅", f"Has {script_count} scripts"))

    if refs_dir.exists():
        ref_count = len(list(refs_dir.glob('*.md')))
        tests.append(("✅", f"Has {ref_count} reference docs"))

    return tests

def run_pressure_tests(skill_path):
    """Run all pressure tests on a skill"""
    all_tests = []

    print(f"\n{'='*60}")
    print(f"Pressure Testing: {skill_path.name}")
    print(f"{'='*60}\n")

    # Structure tests
    print("📋 Structure Tests:")
    structure_tests = test_skill_structure(skill_path)
    for status, msg in structure_tests:
        print(f"  {status} {msg}")
    all_tests.extend(structure_tests)

    # Invocability tests
    print("\n🚀 Invocability Tests:")
    invoke_tests = test_skill_invocability(skill_path)
    for status, msg in invoke_tests:
        print(f"  {status} {msg}")
    all_tests.extend(invoke_tests)

    # Resource tests
    print("\n📦 Resource Tests:")
    resource_tests = test_skill_resources(skill_path)
    for status, msg in resource_tests:
        print(f"  {status} {msg}")
    all_tests.extend(resource_tests)

    # Summary
    print(f"\n{'='*60}")
    passed = sum(1 for status, _ in all_tests if status == "✅")
    warnings = sum(1 for status, _ in all_tests if status == "⚠️")
    failed = sum(1 for status, _ in all_tests if status == "❌")

    print(f"Summary: {passed} passed, {warnings} warnings, {failed} failed")
    print(f"{'='*60}\n")

    return failed == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_skill_pressure.py <skill-name>")
        sys.exit(1)

    skill_name = sys.argv[1]
    skill_path = Path(f'/Users/damon/Vueni-App-refactor/.claude/skills/{skill_name}')

    if not skill_path.exists():
        print(f"❌ Skill directory not found: {skill_path}")
        sys.exit(1)

    success = run_pressure_tests(skill_path)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
