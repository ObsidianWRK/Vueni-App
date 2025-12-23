#!/usr/bin/env python3
"""
Plan Completion Workflow Executor

Automatically executes the plan_completion_workflow when a plan is completed.
Writes entry to WorkDone.md and deletes the plan file.

Usage:
    python scripts/execute_plan_completion.py <plan_file_path>
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


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


def verify_all_todos_completed(todos: List[Dict]) -> bool:
    """Verify that all todos are marked as completed."""
    if not todos:
        return False
    
    return all(todo.get("status") == "completed" for todo in todos)


def generate_workdone_entry(plan_path: Path, frontmatter: Dict, todos: List[Dict]) -> str:
    """Generate WorkDone.md entry for completed plan."""
    plan_name = frontmatter.get("name", plan_path.stem.replace(".plan", ""))
    overview = frontmatter.get("overview", "")
    completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Get relative path
    repo_root = find_repo_root()
    try:
        plan_file_rel = plan_path.relative_to(repo_root)
    except ValueError:
        plan_file_rel = plan_path
    
    # Generate entry
    entry = f"""---
plan_name: {plan_name}
completed_at: {completed_at}
plan_file: {plan_file_rel}
todos_count: {len(todos)}
status: completed
---

## Plan: {plan_name}

**Completed:** {completed_at}

**Overview:** {overview}

### Completed Todos
"""
    
    for todo in todos:
        entry += f"- {todo.get('id', 'Unknown')}: {todo.get('content', '')}\n"
    
    entry += f"""
### Summary
Successfully completed all {len(todos)} todos for plan: {plan_name}. {overview}
"""
    
    return entry


def write_workdone_entry(entry: str, repo_root: Path) -> bool:
    """Write entry to WorkDone.md atomically."""
    workdone_path = repo_root / "docs" / "WorkDone.md"
    
    try:
        # Read existing content
        if workdone_path.exists():
            existing_content = workdone_path.read_text(encoding="utf-8")
        else:
            existing_content = "# WorkDone - Completed Plans Archive\n\nThis file tracks completed plans and work accomplished across all agents.\n\n"
        
        # Append new entry
        new_content = existing_content + "\n" + entry
        
        # Write atomically
        workdone_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error writing to WorkDone.md: {e}", file=sys.stderr)
        return False


def delete_plan_file(plan_path: Path) -> bool:
    """Delete the plan file after successful WorkDone.md write."""
    try:
        if plan_path.exists():
            plan_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting plan file: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: execute_plan_completion.py <plan_file_path>", file=sys.stderr)
        sys.exit(1)
    
    plan_path = Path(sys.argv[1])
    if not plan_path.is_absolute():
        repo_root = find_repo_root()
        plan_path = repo_root / plan_path
    
    if not plan_path.exists():
        print(f"Error: Plan file not found: {plan_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse plan file
    content = plan_path.read_text(encoding="utf-8")
    frontmatter, body = parse_yaml_frontmatter(content)
    
    # Get todos
    todos = frontmatter.get("todos", [])
    
    # Verify all todos are completed
    if not verify_all_todos_completed(todos):
        print(f"Error: Not all todos are completed in plan: {plan_path}", file=sys.stderr)
        print(f"  Found {len(todos)} todos, but not all are marked as 'completed'", file=sys.stderr)
        sys.exit(1)
    
    # Generate WorkDone entry
    entry = generate_workdone_entry(plan_path, frontmatter, todos)
    
    # Write to WorkDone.md
    repo_root = find_repo_root()
    if not write_workdone_entry(entry, repo_root):
        print("Error: Failed to write to WorkDone.md. Plan file not deleted.", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Wrote entry to WorkDone.md")
    
    # Delete plan file
    if delete_plan_file(plan_path):
        print(f"✓ Deleted plan file: {plan_path}")
    else:
        print(f"Warning: Failed to delete plan file: {plan_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
