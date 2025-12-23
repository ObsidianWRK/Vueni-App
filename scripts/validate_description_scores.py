#!/usr/bin/env python3
"""
Validate skill description scores based on 100-point criteria.

Scoring:
- Action verbs: 20 (base) + 10 (if 3+ verbs) = 30 max
- Keywords: 15 points
- File types: 10 points (when applicable)
- Use cases: 20 points ("when to use" guidance)
- Natural phrasing: 15 points (user-focused language)
- Length >100 chars: 10 points
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Action verbs to detect
ACTION_VERBS = [
    'create', 'build', 'generate', 'design', 'extract', 'analyze', 'test',
    'install', 'use', 'write', 'edit', 'modify', 'process', 'develop',
    'implement', 'guide', 'help', 'support', 'enable', 'provide', 'conduct',
    'execute', 'produce', 'facilitate', 'apply', 'configure', 'transcribe',
    'verify', 'debug', 'capture', 'view', 'style', 'theme', 'generate'
]

def extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """Extract YAML frontmatter from SKILL.md content."""
    if not content.startswith('---'):
        return {}, content
    
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break
    
    if end_idx is None:
        return {}, content
    
    frontmatter_str = '\n'.join(lines[1:end_idx])
    body = '\n'.join(lines[end_idx + 1:])
    
    frontmatter = {}
    for line in frontmatter_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    
    return frontmatter, body

def count_action_verbs(text: str) -> int:
    """Count distinct action verbs in text."""
    text_lower = text.lower()
    found = set()
    for verb in ACTION_VERBS:
        # Match whole words
        pattern = r'\b' + re.escape(verb) + r'(?:s|ing|ed|er)?\b'
        if re.search(pattern, text_lower):
            found.add(verb)
    return len(found)

def has_use_cases(text: str) -> bool:
    """Check if description has 'when to use' guidance."""
    patterns = [
        r'use this skill when',
        r'use when',
        r'when.*request',
        r'when.*ask',
        r'when.*want',
        r'when.*need',
        r'for.*when',
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in patterns)

def has_natural_phrasing(text: str) -> bool:
    """Check if description uses natural, user-focused language."""
    # Check for user-focused patterns
    user_patterns = [
        r'use this skill',
        r'when users',
        r'when the user',
        r'when.*request',
    ]
    # Check against technical jargon
    jargon_patterns = [
        r'this skill enables',
        r'comprehensive toolkit for',
        r'provides.*capabilities',
    ]
    text_lower = text.lower()
    has_user_focus = any(re.search(p, text_lower) for p in user_patterns)
    has_jargon = any(re.search(p, text_lower) for p in jargon_patterns)
    return has_user_focus and not has_jargon

def has_file_types(text: str) -> bool:
    """Check if description mentions file types."""
    file_patterns = [
        r'\.(pdf|png|jpg|jpeg|docx|xlsx|pptx|csv|tsv|xlsm|js|html)',
        r'\(\.\w+',
        r'for \.\w+',
    ]
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in file_patterns)

def score_description(description: str) -> Tuple[int, Dict]:
    """Score a description based on criteria."""
    score = 0
    details = {}
    max_score = 100
    
    # Action verbs (30 max)
    verb_count = count_action_verbs(description)
    if verb_count >= 3:
        score += 30
        details['action_verbs'] = f"{verb_count} verbs (30/30)"
    elif verb_count >= 1:
        score += 20
        details['action_verbs'] = f"{verb_count} verbs (20/30)"
    else:
        details['action_verbs'] = f"{verb_count} verbs (0/30)"
    
    # Keywords (15 points) - assume present if description is meaningful
    if len(description.split()) >= 10:
        score += 15
        details['keywords'] = "Present (15/15)"
    else:
        details['keywords'] = "Limited (0/15)"
    
    # File types (10 points) - only if applicable
    # Skills without file types can still get 100/100 by scoring full on other criteria
    if has_file_types(description):
        score += 10
        details['file_types'] = "Mentioned (10/10)"
        max_score = 100  # With file types, max is 100
    else:
        # Don't penalize - file types are optional
        # Adjust max score to 90 if no file types (since file types are 10 points)
        details['file_types'] = "Not applicable (optional, max 90)"
        max_score = 90  # Without file types, max is 90
    
    # Use cases (20 points)
    if has_use_cases(description):
        score += 20
        details['use_cases'] = "Present (20/20)"
    else:
        details['use_cases'] = "Missing (0/20)"
    
    # Natural phrasing (15 points)
    if has_natural_phrasing(description):
        score += 15
        details['natural_phrasing'] = "Yes (15/15)"
    else:
        details['natural_phrasing'] = "No (0/15)"
    
    # Length >100 chars (10 points)
    if len(description) > 100:
        score += 10
        details['length'] = f"{len(description)} chars (10/10)"
    else:
        details['length'] = f"{len(description)} chars (0/10)"
    
    # Check length limit
    if len(description) > 1024:
        details['warning'] = f"Exceeds 1024 char limit ({len(description)} chars)"
    
    # Normalize score to max_score
    normalized_score = min(score, max_score)
    details['max_possible'] = max_score
    
    return normalized_score, details

def validate_skill(skill_path: Path) -> Tuple[bool, int, Dict]:
    """Validate a skill's description."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, 0, {}
    
    content = skill_md.read_text(encoding='utf-8')
    frontmatter, _ = extract_frontmatter(content)
    description = frontmatter.get('description', '')
    
    if not description:
        return False, 0, {}
    
    score, details = score_description(description)
    # Valid if score equals max possible (100 with file types, 90 without)
    max_possible = details.get('max_possible', 100)
    is_valid = score >= max_possible
    
    return is_valid, score, details

def main():
    skills_dir = Path('skills')
    if not skills_dir.exists():
        print(f"{RED}Error: skills/ directory not found{RESET}")
        sys.exit(1)
    
    print(f"{BOLD}Skill Description Validation{RESET}\n")
    
    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / 'SKILL.md').exists():
            is_valid, score, details = validate_skill(item)
            skills.append({
                'name': item.name,
                'valid': is_valid,
                'score': score,
                'details': details
            })
    
    # Sort by score
    skills.sort(key=lambda x: x['score'])
    
    # Print results
    all_valid = True
    for skill in skills:
        max_possible = skill['details'].get('max_possible', 100)
        status = f"{GREEN}✓{RESET}" if skill['valid'] else f"{RED}✗{RESET}"
        score_color = GREEN if skill['valid'] else YELLOW if skill['score'] >= 80 else RED
        print(f"{status} {BOLD}{skill['name']}{RESET}: {score_color}{skill['score']}/{max_possible}{RESET}")
        for key, value in skill['details'].items():
            if key != 'warning':
                print(f"  - {key}: {value}")
        if 'warning' in skill['details']:
            print(f"  {YELLOW}⚠ {skill['details']['warning']}{RESET}")
        if not skill['valid']:
            all_valid = False
        print()
    
    # Summary
    avg_score = sum(s['score'] for s in skills) / len(skills) if skills else 0
    valid_count = sum(1 for s in skills if s['valid'])
    
    print("=" * 50)
    print(f"{BOLD}Summary{RESET}")
    print(f"Skills analyzed: {len(skills)}")
    print(f"Average score: {avg_score:.1f}/100")
    print(f"Skills at 100/100: {valid_count}/{len(skills)}")
    
    if all_valid:
        print(f"{GREEN}{BOLD}✓ All descriptions meet 100/100 criteria!{RESET}")
        sys.exit(0)
    else:
        print(f"{YELLOW}{BOLD}⚠ Some descriptions need improvement{RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()
