#!/usr/bin/env python3
"""
Plan Completion Validation

Validates that completed plans have corresponding WorkDone.md entries.
Detects when the completion workflow was skipped.

Usage:
    python scripts/validate_plan_completion.py [--verbose]
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set


def find_repo_root() -> Path:
    """Find the repository root by looking for AGENTS.md."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def parse_yaml_frontmatter(content: str) -> tuple[Dict, str]:
    """Parse YAML frontmatter from plan file."""
    if not content.startswith("---"):
        return {}, content
    
    lines = content.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break
    
    if end_idx is None:
        return {}, content
    
    frontmatter_str = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1:])
    
    frontmatter = {}
    todos = []
    in_todos = False
    current_todo = {}
    
    for line in frontmatter_str.split("\n"):
        raw_line = line
        stripped = line.strip()
        if not stripped:
            continue
        
        if stripped.startswith("todos:"):
            in_todos = True
            continue
        
        if in_todos:
            if stripped.startswith("- "):
                if current_todo:
                    todos.append(current_todo)
                current_todo = {}
                inline = stripped[2:].strip()
                if inline:
                    key, _, value = inline.partition(":")
                    if key and value:
                        key = key.strip()
                        value = value.strip()
                        if key == "id":
                            current_todo["id"] = value
                        elif key == "content":
                            current_todo["content"] = value
                        elif key == "status":
                            current_todo["status"] = value
                continue
            elif ":" in stripped and not raw_line.startswith("  "):
                if current_todo:
                    todos.append(current_todo)
                in_todos = False
                current_todo = {}
            
            if in_todos and current_todo is not None:
                if "id:" in stripped:
                    current_todo["id"] = stripped.split("id:")[1].strip()
                elif "content:" in stripped:
                    current_todo["content"] = stripped.split("content:")[1].strip()
                elif "status:" in stripped:
                    current_todo["status"] = stripped.split("status:")[1].strip()
        else:
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    
    if current_todo and in_todos:
        todos.append(current_todo)
    
    if todos:
        frontmatter["todos"] = todos
    
    return frontmatter, body


def get_plan_dirs(repo_root: Path) -> List[Path]:
    """Return plan directories to check (workspace + home)."""
    return [
        repo_root / ".cursor" / "plans",
        Path.home() / ".cursor" / "plans",
    ]


def get_completed_plan_files(repo_root: Path) -> List[Dict]:
    """Get all plan files with completed todos."""
    completed_plans = []

    for plans_dir in get_plan_dirs(repo_root):
        if not plans_dir.exists():
            continue

        for plan_file in plans_dir.glob("*.plan.md"):
            try:
                content = plan_file.read_text(encoding="utf-8")
                frontmatter, _ = parse_yaml_frontmatter(content)
                todos = frontmatter.get("todos", [])

                if todos and all(todo.get("status") == "completed" for todo in todos):
                    completed_plans.append({
                        "path": plan_file,
                        "name": frontmatter.get("name", plan_file.stem),
                        "todos_count": len(todos)
                    })
            except Exception:
                continue

    return completed_plans


def get_workdone_plan_names(repo_root: Path) -> Set[str]:
    """Extract plan names from WorkDone.md."""
    workdone_path = repo_root / "docs" / "WorkDone.md"
    if not workdone_path.exists():
        return set()
    
    content = workdone_path.read_text(encoding="utf-8")
    plan_names = set()
    
    # Extract plan names from frontmatter
    pattern = r"plan_name:\s*([^\n]+)"
    matches = re.findall(pattern, content)
    for match in matches:
        plan_names.add(match.strip())
    
    return plan_names


def validate_plan_completion(repo_root: Path, verbose: bool = False) -> tuple[bool, List[str]]:
    """Validate that all completed plans have WorkDone.md entries."""
    completed_plans = get_completed_plan_files(repo_root)
    workdone_plans = get_workdone_plan_names(repo_root)
    
    violations = []
    
    for plan in completed_plans:
        plan_name = plan["name"]
        if plan_name not in workdone_plans:
            violations.append(
                f"Completed plan '{plan_name}' ({plan['path'].name}) has no WorkDone.md entry"
            )
            if verbose:
                print(f"  Missing entry for: {plan_name}")
                print(f"    Plan file: {plan['path']}")
                print(f"    Todos completed: {plan['todos_count']}")
    
    is_valid = len(violations) == 0
    return is_valid, violations


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    repo_root = find_repo_root()
    print(f"Validating plan completion: {repo_root}\n")
    
    is_valid, violations = validate_plan_completion(repo_root, verbose)
    
    if violations:
        print("Violations found:")
        for violation in violations:
            print(f"  ⚠️  {violation}")
        print(f"\n✗ Validation failed: {len(violations)} violation(s)")
        sys.exit(1)
    else:
        print("✓ All completed plans have WorkDone.md entries")
        sys.exit(0)


if __name__ == "__main__":
    main()
