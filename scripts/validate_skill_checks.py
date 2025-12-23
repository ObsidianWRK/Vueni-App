#!/usr/bin/env python3
"""
Skill Check Validator

Validates that agents check for relevant skills before responding to user messages.
Analyzes conversation logs or agent responses to detect missing skill checks.

Usage:
    python scripts/validate_skill_checks.py [--file <path>] [--verbose]
    python scripts/validate_skill_checks.py --check-response "<response text>"
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Patterns that indicate skill checking occurred
SKILL_CHECK_PATTERNS = [
    r"openskills read",
    r"I've read the .+ skill",
    r"Using .+ skill",
    r"Skill read:",
    r"Reading:",
    r"invoked.*skill",
    r"checking.*skill",
    r"relevant skill",
]

# Patterns that indicate skill checking was skipped (violations)
VIOLATION_PATTERNS = [
    # Direct tool use without skill mention
    (r"(read_file|write|search_replace|grep|codebase_search)", r"openskills|skill"),
    # Starting implementation without skill check
    (r"(I'll|I will|Let me|Starting)", r"openskills|skill|checking"),
]

# Common task triggers that should require skill checks
TASK_TRIGGERS = [
    r"implement",
    r"create",
    r"build",
    r"add",
    r"fix",
    r"update",
    r"modify",
    r"write",
    r"design",
    r"plan",
    r"debug",
    r"test",
]


class SkillCheckViolation:
    """Represents a detected skill check violation."""
    
    def __init__(self, message: str, severity: str = "warning", context: Optional[str] = None):
        self.message = message
        self.severity = severity
        self.context = context
    
    def __str__(self):
        icon = "❌" if self.severity == "error" else "⚠️"
        result = f"{icon} {self.message}"
        if self.context:
            result += f"\n   Context: {self.context[:100]}..."
        return result


def find_repo_root() -> Path:
    """Find the repository root by looking for AGENTS.md."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def extract_available_skills(agents_path: Path) -> List[str]:
    """Extract list of available skills from AGENTS.md."""
    if not agents_path.exists():
        return []
    
    content = agents_path.read_text()
    # Extract skill names from <name> tags
    pattern = r"<name>([^<]+)</name>"
    skills = re.findall(pattern, content)
    return [s.strip() for s in skills if s.strip()]


def check_skill_mention(text: str) -> bool:
    """Check if text contains evidence of skill checking."""
    text_lower = text.lower()
    
    # Check for skill check patterns
    for pattern in SKILL_CHECK_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    
    return False


def detect_violations(text: str, available_skills: List[str]) -> List[SkillCheckViolation]:
    """
    Detect potential skill check violations in agent response text.
    
    Uses conservative heuristics to avoid false positives.
    """
    violations = []
    text_lower = text.lower()
    
    # Check if response mentions any task triggers
    has_task_trigger = any(re.search(trigger, text_lower) for trigger in TASK_TRIGGERS)
    
    # Check if skill check occurred
    has_skill_check = check_skill_mention(text)
    
    # If there's a task trigger but no skill check, it's a potential violation
    if has_task_trigger and not has_skill_check:
        # Look for tool usage patterns that suggest implementation started
        if re.search(r"(read_file|write|search_replace|grep|codebase_search|run_terminal_cmd)", text):
            violations.append(SkillCheckViolation(
                "Task detected but no evidence of skill check before tool use",
                severity="warning",
                context=text[:200]
            ))
    
    # Check for direct tool calls without skill context
    tool_pattern = r"(read_file|write|search_replace|grep|codebase_search)"
    tool_matches = list(re.finditer(tool_pattern, text, re.IGNORECASE))
    
    if tool_matches and not has_skill_check:
        # Check if this looks like the start of a response (first 500 chars)
        first_part = text[:500].lower()
        if any(tool in first_part for tool in ["read_file", "write", "search_replace"]):
            violations.append(SkillCheckViolation(
                "Tool usage detected at start of response without skill check",
                severity="warning",
                context=text[:200]
            ))
    
    return violations


def validate_response(response_text: str, available_skills: List[str], verbose: bool = False) -> Tuple[bool, List[SkillCheckViolation]]:
    """
    Validate a single agent response for skill checking compliance.
    
    Returns: (is_valid, violations)
    """
    violations = detect_violations(response_text, available_skills)
    
    if verbose:
        has_check = check_skill_mention(response_text)
        print(f"  Skill check detected: {GREEN if has_check else YELLOW}{has_check}{RESET}")
        if available_skills:
            print(f"  Available skills: {len(available_skills)}")
    
    is_valid = len([v for v in violations if v.severity == "error"]) == 0
    return is_valid, violations


def validate_file(file_path: Path, available_skills: List[str], verbose: bool = False) -> Tuple[bool, List[SkillCheckViolation]]:
    """Validate a file containing agent responses."""
    if not file_path.exists():
        print(f"{RED}Error: File not found: {file_path}{RESET}")
        return False, []
    
    content = file_path.read_text()
    
    # Try to parse as JSON (conversation log format)
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "messages" in data:
            # Extract agent messages
            agent_messages = [
                msg.get("content", "") 
                for msg in data["messages"] 
                if msg.get("role") == "assistant"
            ]
            content = "\n".join(agent_messages)
        elif isinstance(data, list):
            # List of messages
            agent_messages = [
                msg.get("content", "") if isinstance(msg, dict) else str(msg)
                for msg in data
                if isinstance(msg, dict) and msg.get("role") == "assistant"
            ]
            content = "\n".join(agent_messages)
    except json.JSONDecodeError:
        # Not JSON, treat as plain text
        pass
    
    return validate_response(content, available_skills, verbose)


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    check_response = None
    
    # Check for --check-response flag
    if "--check-response" in sys.argv:
        idx = sys.argv.index("--check-response")
        if idx + 1 < len(sys.argv):
            check_response = sys.argv[idx + 1]
        else:
            print(f"{RED}Error: --check-response requires a response text argument{RESET}")
            sys.exit(1)
    
    # Find repo root
    repo_root = find_repo_root()
    agents_path = repo_root / "AGENTS.md"
    available_skills = extract_available_skills(agents_path)
    
    if verbose:
        print(f"{BOLD}Skill Check Validator{RESET}")
        print(f"Repository: {repo_root}")
        print(f"Available skills: {len(available_skills)}")
        if available_skills:
            print(f"  Sample: {', '.join(available_skills[:5])}...")
        print()
    
    violations = []
    
    if check_response:
        # Validate provided response text
        is_valid, violations = validate_response(check_response, available_skills, verbose)
    elif "--file" in sys.argv:
        # Validate file
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            file_path = Path(sys.argv[idx + 1])
            is_valid, violations = validate_file(file_path, available_skills, verbose)
        else:
            print(f"{RED}Error: --file requires a file path{RESET}")
            sys.exit(1)
    else:
        # Interactive mode or help
        print(f"{BOLD}Skill Check Validator{RESET}")
        print("\nUsage:")
        print(f"  {sys.argv[0]} --check-response \"<response text>\"")
        print(f"  {sys.argv[0]} --file <path>")
        print(f"  {sys.argv[0]} --verbose")
        print("\nThis validator checks for evidence of skill checking in agent responses.")
        print("It uses conservative heuristics to avoid false positives.")
        sys.exit(0)
    
    # Report results
    if violations:
        print(f"\n{BOLD}Violations detected:{RESET}")
        for violation in violations:
            print(f"  {violation}")
        
        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]
        
        print(f"\n{RED}✗ Validation failed: {len(errors)} error(s), {len(warnings)} warning(s){RESET}")
        sys.exit(1 if errors else 0)
    else:
        print(f"\n{GREEN}✓ No violations detected{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
