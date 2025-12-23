#!/usr/bin/env python3
"""
Skills Installation Script

Installs skill zip files to the repository, making them available across:
- Claude Code (via .claude/skills/)
- Cursor (via .claude/skills/ + AGENTS.md registration)
- Codex (via .codex/skills/ sync)

Usage:
    python scripts/install_skills.py [zip_files...] [--dry-run] [--verbose] [--skip-validation] [--skip-codex-sync]
"""

import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def find_repo_root() -> Path:
    """Find the repository root by looking for AGENTS.md."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def parse_yaml_value(value: str):
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


def parse_simple_yaml(yaml_str: str) -> Dict:
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


def extract_zip_skill(zip_path: Path, temp_dir: Path) -> Optional[Path]:
    """Extract zip file to temporary directory and return skill directory path."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all to temp directory
            zip_ref.extractall(temp_dir)
            
            # Find the root skill directory (should match zip name without .zip)
            zip_name = zip_path.stem
            extracted_root = temp_dir / zip_name
            
            # If direct match doesn't exist, look for SKILL.md to find root
            if not extracted_root.exists():
                # Search for SKILL.md in extracted files
                for item in temp_dir.rglob("SKILL.md"):
                    extracted_root = item.parent
                    break
                else:
                    # If still not found, use first directory
                    dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
                    if dirs:
                        extracted_root = dirs[0]
                    else:
                        return None
            
            return extracted_root
    except zipfile.BadZipFile:
        return None
    except Exception as e:
        print_status("fail", f"Error extracting {zip_path.name}: {e}")
        return None


def validate_skill_structure(skill_dir: Path) -> Tuple[bool, Optional[Dict], List[str]]:
    """Validate skill structure and return (is_valid, frontmatter, warnings)."""
    warnings = []
    
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, None, ["SKILL.md not found"]
    
    # Read and parse frontmatter
    content = skill_md.read_text()
    frontmatter, _ = extract_frontmatter(content)
    
    if not frontmatter:
        return False, None, ["SKILL.md missing YAML frontmatter"]
    
    # Check required fields
    if "name" not in frontmatter:
        return False, None, ["Frontmatter missing 'name' field"]
    
    if "description" not in frontmatter:
        return False, None, ["Frontmatter missing 'description' field"]
    
    # Check for LICENSE.txt (optional)
    license_txt = skill_dir / "LICENSE.txt"
    if not license_txt.exists():
        warnings.append("LICENSE.txt not found (optional)")
    
    return True, frontmatter, warnings


def extract_agents_skills(agents_path: Path) -> set[str]:
    """Extract skill names from AGENTS.md."""
    if not agents_path.exists():
        return set()
    
    content = agents_path.read_text()
    pattern = r"<name>([^<]+)</name>"
    return set(re.findall(pattern, content))


def check_conflicts(skill_name: str, repo_root: Path, agents_skills: set[str]) -> Tuple[bool, List[str]]:
    """Check for conflicts with existing skills. Returns (has_conflicts, conflict_messages)."""
    conflicts = []
    
    # Check AGENTS.md
    if skill_name in agents_skills:
        conflicts.append(f"Skill '{skill_name}' already registered in AGENTS.md")
    
    # Check .claude/skills/ directory
    skill_dir = repo_root / ".claude" / "skills" / skill_name
    if skill_dir.exists():
        conflicts.append(f"Skill directory already exists: .claude/skills/{skill_name}/")
    
    return len(conflicts) > 0, conflicts


def update_agents_md(agents_path: Path, skill_name: str, description: str, dry_run: bool = False) -> bool:
    """Insert new skill entry before </available_skills> tag in AGENTS.md."""
    if not agents_path.exists():
        print_status("fail", "AGENTS.md not found")
        return False
    
    content = agents_path.read_text()
    
    # Find the insertion point (before </available_skills>)
    closing_tag = "</available_skills>"
    if closing_tag not in content:
        print_status("fail", "AGENTS.md missing </available_skills> closing tag")
        return False
    
    # Create new skill entry
    # Find indentation by looking at previous skill entry
    indent_match = re.search(r'(\s*)</available_skills>', content)
    indent = indent_match.group(1) if indent_match else "    "
    
    skill_entry = f"""{indent}<skill>
{indent}<name>{skill_name}</name>
{indent}<description>{description}</description>
{indent}<location>project</location>
{indent}</skill>

"""
    
    # Insert before closing tag
    insertion_point = content.find(closing_tag)
    new_content = content[:insertion_point] + skill_entry + content[insertion_point:]
    
    if not dry_run:
        agents_path.write_text(new_content)
        print_status("pass", f"Registered '{skill_name}' in AGENTS.md")
    else:
        print_status("info", f"Would register '{skill_name}' in AGENTS.md")
    
    return True


def sync_to_codex(repo_root: Path, skill_name: str, dry_run: bool = False) -> bool:
    """Sync a single skill to .codex/skills/."""
    source_dir = repo_root / ".claude" / "skills" / skill_name
    codex_dir = repo_root / ".codex" / "skills" / skill_name
    
    if not source_dir.exists():
        print_status("fail", f"Source directory not found: {source_dir}")
        return False
    
    if not dry_run:
        # Ensure .codex/skills/ exists
        codex_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing if present
        if codex_dir.exists():
            shutil.rmtree(codex_dir)
        
        # Copy skill directory
        shutil.copytree(source_dir, codex_dir)
        print_status("pass", f"Synced '{skill_name}' to .codex/skills/")
    else:
        print_status("info", f"Would sync '{skill_name}' to .codex/skills/")
    
    return True


def sync_all_to_codex(repo_root: Path, dry_run: bool = False) -> bool:
    """Sync all skills from .claude/skills/ to .codex/skills/."""
    source_dir = repo_root / ".claude" / "skills"
    codex_dir = repo_root / ".codex" / "skills"
    
    if not source_dir.exists():
        print_status("fail", f"Source directory not found: {source_dir}")
        return False
    
    skills = [d.name for d in source_dir.iterdir() if d.is_dir()]
    
    if not skills:
        print_status("warn", "No skills found to sync")
        return True
    
    if not dry_run:
        # Remove existing .codex/skills/ and recreate
        if codex_dir.exists():
            shutil.rmtree(codex_dir)
        
        codex_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy each skill
        for skill in sorted(skills):
            src = source_dir / skill
            dst = codex_dir / skill
            shutil.copytree(src, dst)
        
        print_status("pass", f"Synced {len(skills)} skill(s) to .codex/skills/")
    else:
        print_status("info", f"Would sync {len(skills)} skill(s) to .codex/skills/")
    
    return True


def install_skill(
    zip_path: Path,
    repo_root: Path,
    temp_dir: Path,
    agents_skills: set[str],
    dry_run: bool = False,
    skip_validation: bool = False,
    skip_codex_sync: bool = False
) -> Tuple[bool, str]:
    """
    Install a single skill from zip file.
    Returns (success, message).
    """
    zip_name = zip_path.name
    
    print(f"\n{BOLD}Processing: {zip_name}{RESET}")
    print("-" * 60)
    
    # Extract zip
    print_status("info", f"Extracting {zip_name}...")
    skill_dir = extract_zip_skill(zip_path, temp_dir)
    
    if not skill_dir:
        return False, f"Failed to extract {zip_name}"
    
    print_status("pass", f"Extracted to temporary directory")
    
    # Validate structure
    if not skip_validation:
        print_status("info", "Validating skill structure...")
        is_valid, frontmatter, warnings = validate_skill_structure(skill_dir)
        
        if not is_valid:
            return False, f"Validation failed: {', '.join(warnings)}"
        
        for warning in warnings:
            print_status("warn", warning)
        
        skill_name = frontmatter["name"]
        description = frontmatter["description"]
        
        # Check if name matches directory
        dir_name = skill_dir.name
        if skill_name != dir_name:
            print_status("warn", f"Skill name '{skill_name}' doesn't match directory name '{dir_name}'")
    else:
        # Read frontmatter without validation
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return False, "SKILL.md not found"
        
        content = skill_md.read_text()
        frontmatter, _ = extract_frontmatter(content)
        
        if not frontmatter or "name" not in frontmatter or "description" not in frontmatter:
            return False, "Invalid frontmatter"
        
        skill_name = frontmatter["name"]
        description = frontmatter["description"]
    
    # Check conflicts
    print_status("info", "Checking for conflicts...")
    has_conflicts, conflict_messages = check_conflicts(skill_name, repo_root, agents_skills)
    
    if has_conflicts:
        return False, f"Conflicts detected: {', '.join(conflict_messages)}"
    
    print_status("pass", "No conflicts detected")
    
    # Install to .claude/skills/
    target_dir = repo_root / ".claude" / "skills" / skill_name
    
    if not dry_run:
        print_status("info", f"Installing to .claude/skills/{skill_name}/...")
        
        # Remove existing if present
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Copy skill directory
        shutil.copytree(skill_dir, target_dir)
        print_status("pass", f"Installed to .claude/skills/{skill_name}/")
    else:
        print_status("info", f"Would install to .claude/skills/{skill_name}/")
    
    # Update AGENTS.md
    print_status("info", "Updating AGENTS.md...")
    agents_path = repo_root / "AGENTS.md"
    if not update_agents_md(agents_path, skill_name, description, dry_run):
        return False, "Failed to update AGENTS.md"
    
    # Sync to Codex (only if not dry-run, since we'll do final sync at end)
    if not skip_codex_sync and not dry_run:
        print_status("info", "Syncing to Codex...")
        if not sync_to_codex(repo_root, skill_name, dry_run=False):
            print_status("warn", "Codex sync failed, but installation succeeded")
    elif not skip_codex_sync and dry_run:
        print_status("info", "Would sync to Codex (after installation)")
    
    return True, f"Successfully installed '{skill_name}'"


def main():
    """Main entry point."""
    # Parse arguments
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    verbose = "--verbose" in args or "-v" in args
    skip_validation = "--skip-validation" in args
    skip_codex_sync = "--skip-codex-sync" in args
    
    # Filter out flags
    zip_files = [arg for arg in args if not arg.startswith("--") and not arg.startswith("-")]
    
    # If no zip files specified, find all zip files in repo root
    repo_root = find_repo_root()
    
    if not zip_files:
        zip_files = sorted(repo_root.glob("*.zip"))
        if not zip_files:
            print(f"{RED}Error: No zip files found in repository root{RESET}")
            sys.exit(1)
        print(f"{BOLD}Found {len(zip_files)} zip file(s) to install{RESET}\n")
    else:
        zip_files = [repo_root / f for f in zip_files]
    
    # Validate zip files exist
    valid_zips = []
    for zip_path in zip_files:
        if not zip_path.exists():
            print_status("fail", f"Zip file not found: {zip_path}")
        else:
            valid_zips.append(zip_path)
    
    if not valid_zips:
        print(f"{RED}Error: No valid zip files to install{RESET}")
        sys.exit(1)
    
    print(f"{BOLD}Skills Installation{RESET}")
    print(f"Repository: {repo_root}")
    print(f"Zip files: {len(valid_zips)}")
    if dry_run:
        print(f"{YELLOW}(dry-run mode - no changes will be made){RESET}")
    if skip_validation:
        print(f"{YELLOW}(validation skipped){RESET}")
    if skip_codex_sync:
        print(f"{YELLOW}(Codex sync skipped){RESET}")
    print()
    
    # Load existing skills from AGENTS.md
    agents_path = repo_root / "AGENTS.md"
    agents_skills = extract_agents_skills(agents_path)
    
    if verbose:
        print(f"Found {len(agents_skills)} existing skills in AGENTS.md")
        print()
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Process each zip file
        results = []
        for zip_path in valid_zips:
            success, message = install_skill(
                zip_path,
                repo_root,
                temp_path,
                agents_skills,
                dry_run=dry_run,
                skip_validation=skip_validation,
                skip_codex_sync=skip_codex_sync
            )
            
            results.append((zip_path.name, success, message))
            
            if success:
                # Update agents_skills set for conflict checking
                # Extract skill name from message or re-read AGENTS.md
                agents_skills = extract_agents_skills(agents_path)
        
        # Summary
        print(f"\n{BOLD}Installation Summary{RESET}")
        print("-" * 60)
        
        successful = [r for r in results if r[1]]
        failed = [r for r in results if not r[1]]
        
        for zip_name, success, message in results:
            if success:
                print_status("pass", f"{zip_name}: {message}")
            else:
                print_status("fail", f"{zip_name}: {message}")
        
        print()
        print(f"Successful: {len(successful)}/{len(results)}")
        if failed:
            print(f"Failed: {len(failed)}/{len(results)}")
        
        # Final Codex sync (if not skipped and not dry-run)
        if not skip_codex_sync and not dry_run and successful:
            print(f"\n{BOLD}Final Codex Sync{RESET}")
            print("-" * 60)
            sync_all_to_codex(repo_root, dry_run=False)
        
        # Exit with error code if any failed
        if failed:
            sys.exit(1)
        else:
            print(f"\n{GREEN}✓ All skills installed successfully!{RESET}")


if __name__ == "__main__":
    main()
