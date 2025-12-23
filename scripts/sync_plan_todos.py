#!/usr/bin/env python3
"""
Plan File Todo Sync

Syncs todos from todo_write operations to plan file frontmatter.
This ensures plan files have accurate todo state for completion detection.

Usage:
    python scripts/sync_plan_todos.py <plan_file_path> [--todos-json <json>]
    python scripts/sync_plan_todos.py --find-active
"""

import json
import re
import sys
from datetime import datetime
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
    
    # Find closing ---
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
    
    # Simple YAML parsing for todos array
    frontmatter = {}
    todos = []
    in_todos = False
    current_todo = {}
    
    for line in frontmatter_str.split("\n"):
        raw_line = line
        stripped = line.strip()
        if not stripped:
            continue
        
        # Check for todos: array start
        if stripped.startswith("todos:"):
            in_todos = True
            continue
        
        if in_todos:
            # Check for todo item
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
                # Parse todo item: - id: T1\n  content: ...\n  status: ...
                continue
            elif ":" in stripped and not raw_line.startswith("  "):
                # End of todos array
                if current_todo:
                    todos.append(current_todo)
                in_todos = False
                current_todo = {}
            
            if in_todos and current_todo is not None:
                # Parse todo fields
                if "id:" in stripped:
                    current_todo["id"] = stripped.split("id:")[1].strip()
                elif "content:" in stripped:
                    current_todo["content"] = stripped.split("content:")[1].strip()
                elif "status:" in stripped:
                    current_todo["status"] = stripped.split("status:")[1].strip()
        else:
            # Regular frontmatter field
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    
    if current_todo and in_todos:
        todos.append(current_todo)
    
    if todos:
        frontmatter["todos"] = todos
    
    return frontmatter, body


def format_todos_yaml(todos: List[Dict]) -> str:
    """Format todos array as YAML."""
    if not todos:
        return "todos: []"
    
    lines = ["todos:"]
    for todo in todos:
        lines.append(f"  - id: {todo.get('id', '')}")
        lines.append(f"    content: {todo.get('content', '')}")
        lines.append(f"    status: {todo.get('status', 'pending')}")
        if todo.get("dependencies"):
            deps = todo["dependencies"]
            if isinstance(deps, list):
                lines.append(f"    dependencies: {deps}")
            else:
                lines.append(f"    dependencies: [{deps}]")
    
    return "\n".join(lines)


def update_plan_file(plan_path: Path, todos: List[Dict]) -> bool:
    """Update plan file with new todos."""
    try:
        content = plan_path.read_text(encoding="utf-8")
        frontmatter, body = parse_yaml_frontmatter(content)
        
        # Update todos in frontmatter
        frontmatter["todos"] = todos
        
        # Reconstruct file
        frontmatter_lines = ["---"]
        for key, value in frontmatter.items():
            if key == "todos":
                frontmatter_lines.append(format_todos_yaml(value))
            else:
                frontmatter_lines.append(f"{key}: {value}")
        frontmatter_lines.append("---")
        
        new_content = "\n".join(frontmatter_lines) + "\n\n" + body
        plan_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error updating plan file: {e}", file=sys.stderr)
        return False


def find_active_plan_files(repo_root: Path) -> List[Path]:
    """Find all active plan files in .cursor/plans/ directory."""
    plans_dir = repo_root / ".cursor" / "plans"
    if not plans_dir.exists():
        return []
    
    plan_files = []
    for plan_file in plans_dir.glob("*.plan.md"):
        try:
            content = plan_file.read_text(encoding="utf-8")
            frontmatter, _ = parse_yaml_frontmatter(content)
            # Only include files with todos
            if frontmatter.get("todos"):
                plan_files.append(plan_file)
        except Exception:
            continue
    
    return plan_files


def main():
    """Main entry point."""
    repo_root = find_repo_root()
    
    if "--find-active" in sys.argv:
        # Find and list active plan files
        plan_files = find_active_plan_files(repo_root)
        for plan_file in plan_files:
            print(str(plan_file.relative_to(repo_root)))
        return
    
    if len(sys.argv) < 2:
        print("Usage: sync_plan_todos.py <plan_file> [--todos-json <json>]", file=sys.stderr)
        print("       sync_plan_todos.py --find-active", file=sys.stderr)
        sys.exit(1)
    
    plan_file_path = Path(sys.argv[1])
    if not plan_file_path.is_absolute():
        plan_file_path = repo_root / plan_file_path
    
    if not plan_file_path.exists():
        print(f"Error: Plan file not found: {plan_file_path}", file=sys.stderr)
        sys.exit(1)
    
    # Get todos from JSON if provided
    todos = []
    if "--todos-json" in sys.argv:
        idx = sys.argv.index("--todos-json")
        if idx + 1 < len(sys.argv):
            try:
                todos = json.loads(sys.argv[idx + 1])
            except json.JSONDecodeError as e:
                print(f"Error parsing todos JSON: {e}", file=sys.stderr)
                sys.exit(1)
    
    # If no todos provided, read from plan file
    if not todos:
        content = plan_file_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_yaml_frontmatter(content)
        todos = frontmatter.get("todos", [])
    
    # Update plan file
    if update_plan_file(plan_file_path, todos):
        print(f"✓ Updated plan file: {plan_file_path}")
    else:
        print(f"✗ Failed to update plan file: {plan_file_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
