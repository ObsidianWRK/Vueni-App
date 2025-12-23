#!/usr/bin/env python3
"""
Skills Sync Script

Synchronizes skills from the canonical source (.claude/skills/) to:
- .codex/skills/ (for OpenAI Codex)

The `skills/` directory is a curated subset maintained manually for Cursor.

Usage:
    python scripts/sync_skills.py [--dry-run] [--verbose]
"""

import shutil
import sys
from pathlib import Path


# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def find_repo_root() -> Path:
    """Find the repository root by looking for AGENTS.md."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def sync_skills(repo_root: Path, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Sync skills from .claude/skills/ to .codex/skills/.
    
    Returns True if sync was successful (or would be successful in dry-run mode).
    """
    source_dir = repo_root / ".claude" / "skills"
    codex_dir = repo_root / ".codex" / "skills"
    
    if not source_dir.exists():
        print(f"{RED}Error: Source directory not found: {source_dir}{RESET}")
        return False
    
    print(f"{BOLD}Skills Sync{RESET}")
    print(f"Source: {source_dir}")
    print(f"Target: {codex_dir}")
    if dry_run:
        print(f"{YELLOW}(dry-run mode - no changes will be made){RESET}")
    print()
    
    # Get list of skills to sync
    skills = [d.name for d in source_dir.iterdir() if d.is_dir()]
    
    if not skills:
        print(f"{YELLOW}No skills found to sync{RESET}")
        return True
    
    print(f"Found {len(skills)} skill(s) to sync:")
    for skill in sorted(skills):
        print(f"  - {skill}")
    print()
    
    if not dry_run:
        # Remove existing .codex/skills/ and recreate
        if codex_dir.exists():
            if verbose:
                print(f"Removing existing {codex_dir}...")
            shutil.rmtree(codex_dir)
        
        codex_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy each skill
        for skill in sorted(skills):
            src = source_dir / skill
            dst = codex_dir / skill
            if verbose:
                print(f"Copying {skill}...")
            shutil.copytree(src, dst)
        
        print(f"{GREEN}✓ Synced {len(skills)} skill(s) to .codex/skills/{RESET}")
    else:
        print(f"{BLUE}Would sync {len(skills)} skill(s) to .codex/skills/{RESET}")
    
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    repo_root = find_repo_root()
    
    success = sync_skills(repo_root, dry_run=dry_run, verbose=verbose)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
