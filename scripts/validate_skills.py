#!/usr/bin/env python3
"""
Agent Skills Validator
Based on the Agent Skills Specification: https://agentskills.io/specification

This script validates skills against the official specification.
Uses only Python standard library.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_status(status: str, message: str, indent: int = 0):
    """Print a status message with color coding."""
    prefix = "  " * indent
    if status == "pass":
        print(f"{prefix}{GREEN}✓{RESET} {message}")
    elif status == "fail":
        print(f"{prefix}{RED}✗{RESET} {message}")
    elif status == "warn":
        print(f"{prefix}{YELLOW}⚠{RESET} {message}")
    elif status == "info":
        print(f"{prefix}{BLUE}ℹ{RESET} {message}")


def parse_yaml_value(value: str) -> Any:
    """Parse a YAML value (simple implementation for frontmatter)."""
    value = value.strip()
    
    # Remove quotes
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    
    # Boolean
    if value.lower() in ('true', 'yes'):
        return True
    if value.lower() in ('false', 'no'):
        return False
    
    # Numbers
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    return value


def parse_simple_yaml(yaml_str: str) -> Dict[str, Any]:
    """
    Simple YAML parser for frontmatter.
    Handles basic key: value pairs, lists, and nested dicts.
    """
    result = {}
    lines = yaml_str.split('\n')
    
    current_key = None
    current_list = None
    current_dict = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        
        # Count leading spaces to determine nesting
        indent = len(line) - len(line.lstrip())
        
        # List item
        if stripped.startswith('- '):
            if current_key and current_list is not None:
                current_list.append(parse_yaml_value(stripped[2:]))
            i += 1
            continue
        
        # Key: value pair
        if ':' in stripped:
            colon_idx = stripped.index(':')
            key = stripped[:colon_idx].strip()
            value = stripped[colon_idx + 1:].strip()
            
            if indent == 0:
                # Top-level key
                current_key = key
                current_list = None
                current_dict = None
                
                if value:
                    # Simple key: value
                    result[key] = parse_yaml_value(value)
                else:
                    # Could be list or dict, peek at next line
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('- '):
                            current_list = []
                            result[key] = current_list
                        else:
                            current_dict = {}
                            result[key] = current_dict
                    else:
                        result[key] = None
            elif current_dict is not None:
                # Nested key in dict
                if value:
                    current_dict[key] = parse_yaml_value(value)
                else:
                    current_dict[key] = None
        
        i += 1
    
    return result


def validate_name(name: str) -> Tuple[bool, List[str]]:
    """Validate the name field according to spec."""
    errors = []
    
    if not name:
        errors.append("name is required and cannot be empty")
        return False, errors
    
    if len(name) > 64:
        errors.append(f"name must be max 64 characters (got {len(name)})")
    
    if not re.match(r'^[a-z0-9-]+$', name):
        errors.append("name may only contain lowercase letters, numbers, and hyphens")
    
    if name.startswith('-') or name.endswith('-'):
        errors.append("name must not start or end with a hyphen")
    
    if '--' in name:
        errors.append("name must not contain consecutive hyphens")
    
    return len(errors) == 0, errors


def validate_description(description: str) -> Tuple[bool, List[str]]:
    """Validate the description field according to spec."""
    errors = []
    
    if not description:
        errors.append("description is required and cannot be empty")
        return False, errors
    
    if len(description) > 1024:
        errors.append(f"description must be max 1024 characters (got {len(description)})")
    
    return len(errors) == 0, errors


def validate_compatibility(compatibility) -> Tuple[bool, List[str]]:
    """Validate the compatibility field according to spec."""
    warnings = []
    
    if compatibility is None:
        return True, []
    
    # Spec says it should be a string
    if not isinstance(compatibility, str):
        warnings.append(f"compatibility should be a string (max 500 chars), got {type(compatibility).__name__}")
        # Try to convert if it's a list
        if isinstance(compatibility, list):
            suggested = ", ".join(str(x) for x in compatibility)
            warnings.append(f"  Suggestion: compatibility: {suggested}")
        return False, warnings
    
    if len(compatibility) > 500:
        warnings.append(f"compatibility must be max 500 characters (got {len(compatibility)})")
        return False, warnings
    
    return True, warnings


def validate_allowed_tools(allowed_tools) -> Tuple[bool, List[str]]:
    """Validate the allowed-tools field according to spec."""
    warnings = []
    
    if allowed_tools is None:
        return True, []
    
    # Spec says it should be a space-delimited string
    if not isinstance(allowed_tools, str):
        warnings.append(f"allowed-tools should be a space-delimited string, got {type(allowed_tools).__name__}")
        # Try to convert if it's a list
        if isinstance(allowed_tools, list):
            suggested = " ".join(str(x) for x in allowed_tools)
            warnings.append(f"  Suggestion: allowed-tools: {suggested}")
        return False, warnings
    
    return True, warnings


def validate_metadata(metadata) -> Tuple[bool, List[str]]:
    """Validate the metadata field according to spec."""
    warnings = []
    
    if metadata is None:
        return True, []
    
    if not isinstance(metadata, dict):
        warnings.append(f"metadata should be a key-value mapping, got {type(metadata).__name__}")
        return False, warnings
    
    return True, warnings


def extract_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """Extract YAML frontmatter from SKILL.md content."""
    if not content.startswith('---'):
        return None, content
    
    # Find the closing ---
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break
    
    if end_idx is None:
        return None, content
    
    frontmatter_str = '\n'.join(lines[1:end_idx])
    body = '\n'.join(lines[end_idx + 1:])
    
    try:
        frontmatter = parse_simple_yaml(frontmatter_str)
        return frontmatter, body
    except Exception as e:
        return None, content


def validate_skill(skill_path: Path, codex_invoke_ready: bool = False) -> Tuple[bool, int, int]:
    """
    Validate a skill directory.
    Returns: (is_valid, error_count, warning_count)
    """
    errors = 0
    warnings = 0
    
    print(f"\n{BOLD}Validating: {skill_path}{RESET}")
    print("-" * 50)
    
    # Check directory structure
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print_status("fail", "SKILL.md not found (required)")
        return False, 1, 0
    
    print_status("pass", "SKILL.md exists")
    
    # Read and parse SKILL.md
    content = skill_md.read_text(encoding='utf-8')
    frontmatter, body = extract_frontmatter(content)
    
    if frontmatter is None:
        print_status("fail", "Could not parse YAML frontmatter")
        return False, 1, 0
    
    print_status("pass", "YAML frontmatter parsed successfully")
    
    # Validate required fields
    # Name
    name = frontmatter.get('name', '')
    name_valid, name_errors = validate_name(name)
    if name_valid:
        print_status("pass", f"name: '{name}'")
        # Check if name matches directory
        if name != skill_path.name:
            if codex_invoke_ready:
                print_status("fail", f"name '{name}' must match directory '{skill_path.name}' for invocation readiness", indent=1)
                errors += 1
            else:
                print_status("warn", f"name '{name}' does not match directory name '{skill_path.name}'", indent=1)
                warnings += 1
    else:
        for err in name_errors:
            print_status("fail", f"name: {err}")
            errors += 1
    
    # Description
    description = frontmatter.get('description', '')
    desc_valid, desc_errors = validate_description(description)
    if desc_valid:
        desc_preview = description[:60] + "..." if len(description) > 60 else description
        print_status("pass", f"description: '{desc_preview}'")
    else:
        for err in desc_errors:
            print_status("fail", f"description: {err}")
            errors += 1
    
    # Validate optional fields (per superpowers:writing-skills, only name + description are required)
    # Warn about extra frontmatter fields beyond minimal standard
    extra_fields = set(frontmatter.keys()) - {'name', 'description'}
    if extra_fields:
        print_status("warn", f"Extra frontmatter fields (minimal standard is name + description only): {', '.join(sorted(extra_fields))}")
        warnings += 1

    # License (optional, legacy)
    license_val = frontmatter.get('license')
    if license_val:
        print_status("info", f"license: '{license_val}' (legacy field, not required)")
    
    # Note: compatibility, metadata, and allowed-tools are now considered legacy fields
    # Per superpowers:writing-skills, only name + description should be in frontmatter
    
    # Validate body content
    body_lines = body.strip().split('\n')
    if len(body_lines) > 500:
        print_status("warn", f"SKILL.md body is {len(body_lines)} lines (recommended < 500 lines)")
        warnings += 1
    else:
        print_status("pass", f"Body content: {len(body_lines)} lines")

    if codex_invoke_ready:
        # Minimal readiness: name/description/license validated above; ensure frontmatter existed
        if not frontmatter:
            print_status("fail", "frontmatter missing — required for invocation readiness")
            errors += 1
        else:
            print_status("pass", "Invocation readiness: frontmatter present")
    
    # Check optional directories
    for opt_dir in ['scripts', 'references', 'assets']:
        dir_path = skill_path / opt_dir
        if dir_path.exists():
            files = list(dir_path.rglob('*'))
            file_count = len([f for f in files if f.is_file()])
            print_status("info", f"{opt_dir}/: {file_count} file(s)")
    
    # Check for reference directory (note: plural vs singular)
    ref_dir = skill_path / "reference"
    if ref_dir.exists():
        files = list(ref_dir.rglob('*'))
        file_count = len([f for f in files if f.is_file()])
        print_status("warn", f"reference/: {file_count} file(s) (spec uses 'references/' not 'reference/')")
        warnings += 1
    
    # Summary
    print()
    is_valid = errors == 0
    if is_valid and warnings == 0:
        print(f"{GREEN}{BOLD}✓ Skill is valid!{RESET}")
    elif is_valid:
        print(f"{YELLOW}{BOLD}⚠ Skill is valid with {warnings} warning(s){RESET}")
    else:
        print(f"{RED}{BOLD}✗ Skill has {errors} error(s) and {warnings} warning(s){RESET}")
    
    return is_valid, errors, warnings


def main():
    codex_invoke_ready = "--codex-invoke-ready" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--codex-invoke-ready"]

    if len(args) < 1:
        print(f"{BOLD}Agent Skills Validator{RESET}")
        print("Based on: https://agentskills.io/specification\n")
        print(f"Usage: {sys.argv[0]} <skill-path> [skill-path2 ...]")
        print(f"       {sys.argv[0]} --all     # Validate all skills in .claude/skills/")
        print(f"       {sys.argv[0]} --codex   # Validate all skills in .codex/skills/")
        print(f"       {sys.argv[0]} --cursor  # Validate all skills in skills/")
        print(f"Options:")
        print(f"       --minimal-frontmatter   # Strict mode: warn about any fields beyond name + description (superpowers:writing-skills standard)")
        sys.exit(1)
    
    skills_to_validate = []
    
    if args[0] == '--all':
        # Find all skills in .claude/skills directory (canonical source)
        skills_dir = Path('.claude/skills')
        if skills_dir.exists():
            for item in skills_dir.iterdir():
                if item.is_dir() and (item / 'SKILL.md').exists():
                    skills_to_validate.append(item)
        else:
            print(f"{RED}Error: .claude/skills directory not found{RESET}")
            sys.exit(1)
    elif args[0] == '--codex':
        # Find all skills in .codex/skills directory
        skills_dir = Path('.codex/skills')
        if skills_dir.exists():
            for item in skills_dir.iterdir():
                if item.is_dir() and (item / 'SKILL.md').exists():
                    skills_to_validate.append(item)
        else:
            print(f"{RED}Error: .codex/skills directory not found{RESET}")
            sys.exit(1)
    elif args[0] == '--cursor':
        # Find all skills in skills/ directory (Cursor subset)
        skills_dir = Path('skills')
        if skills_dir.exists():
            for item in skills_dir.iterdir():
                if item.is_dir() and (item / 'SKILL.md').exists():
                    skills_to_validate.append(item)
        else:
            print(f"{RED}Error: skills/ directory not found{RESET}")
            sys.exit(1)
    else:
        for path_str in args:
            path = Path(path_str)
            if path.exists():
                skills_to_validate.append(path)
            else:
                print(f"{RED}Error: Path not found: {path_str}{RESET}")
    
    if not skills_to_validate:
        print(f"{YELLOW}No skills found to validate{RESET}")
        sys.exit(1)
    
    print(f"{BOLD}Agent Skills Validator{RESET}")
    print("Based on: https://agentskills.io/specification")
    print(f"Validating {len(skills_to_validate)} skill(s)...")
    
    total_errors = 0
    total_warnings = 0
    valid_count = 0
    
    for skill_path in skills_to_validate:
        is_valid, errors, warnings = validate_skill(skill_path, codex_invoke_ready=codex_invoke_ready)
        total_errors += errors
        total_warnings += warnings
        if is_valid:
            valid_count += 1
    
    # Final summary
    print("\n" + "=" * 50)
    print(f"{BOLD}Summary{RESET}")
    print(f"Skills validated: {len(skills_to_validate)}")
    print(f"Valid: {valid_count}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")
    
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == '__main__':
    main()
