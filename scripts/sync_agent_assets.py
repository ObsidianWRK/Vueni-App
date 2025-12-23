#!/usr/bin/env python3
"""
Agent Assets Mirror Generator

Generates real-file mirrors of canonical agent assets to ensure cross-platform
portability without relying on symlink traversal.

Features:
- Copies .claude/skills/ to .codex/skills/ and skills/ as real files
- Generates manifests with SHA256 checksums for validation
- Atomic updates (write to temp, then move)
- Selective sync (skip if unchanged based on manifest)

Usage:
    python scripts/sync_agent_assets.py [--verbose] [--force]
"""

import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SyncError(Exception):
    """Raised when sync operations fail."""
    pass


def find_repo_root() -> Path:
    """Find the repository root by looking for AGENTS.md."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def sha256_file(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_manifest(manifest_path: Path) -> Optional[Dict]:
    """Load manifest JSON if it exists."""
    if not manifest_path.exists():
        return None
    try:
        with open(manifest_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️  Warning: Failed to load manifest {manifest_path}: {e}")
        return None


def save_manifest(manifest_path: Path, manifest: Dict) -> None:
    """Save manifest JSON atomically."""
    # Write to temp file first
    temp_fd, temp_path = tempfile.mkstemp(
        dir=manifest_path.parent,
        prefix=".manifest.tmp.",
        suffix=".json"
    )
    try:
        with open(temp_fd, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write('\n')  # Add trailing newline
        # Atomic move
        shutil.move(temp_path, manifest_path)
    except Exception as e:
        # Clean up temp file on error
        try:
            Path(temp_path).unlink()
        except:
            pass
        raise SyncError(f"Failed to save manifest {manifest_path}: {e}")


def collect_source_files(source_dir: Path, verbose: bool) -> Dict[str, Dict]:
    """Collect all files from source directory with metadata."""
    files = {}

    if not source_dir.exists():
        raise SyncError(f"Source directory not found: {source_dir}")

    if not source_dir.is_dir():
        raise SyncError(f"Source is not a directory: {source_dir}")

    # Walk source directory
    for item in source_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(source_dir)
            rel_path_str = str(rel_path)

            # Skip hidden files and manifests
            if rel_path_str.startswith('.') or '.manifest.json' in rel_path_str:
                continue

            # Calculate metadata
            sha256 = sha256_file(item)
            size = item.stat().st_size
            mtime = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc)

            files[rel_path_str] = {
                "sha256": sha256,
                "size": size,
                "mtime": mtime.isoformat()
            }

            if verbose:
                print(f"  Collected: {rel_path_str} ({size} bytes, sha256: {sha256[:8]}...)")

    return files


def sync_to_mirror(
    source_dir: Path,
    mirror_dir: Path,
    source_files: Dict[str, Dict],
    verbose: bool,
    force: bool
) -> Tuple[int, int, int]:
    """
    Sync source files to mirror directory.

    Returns: (copied, skipped, deleted)
    """
    copied = 0
    skipped = 0
    deleted = 0

    # Load existing manifest
    manifest_path = mirror_dir / ".manifest.json"
    old_manifest = load_manifest(manifest_path)
    old_files = old_manifest.get("files", {}) if old_manifest else {}

    # Ensure mirror directory exists
    mirror_dir.mkdir(parents=True, exist_ok=True)

    # Copy new/changed files
    for rel_path, metadata in source_files.items():
        source_file = source_dir / rel_path
        mirror_file = mirror_dir / rel_path

        # Check if file needs update
        needs_update = force or (
            rel_path not in old_files or
            old_files[rel_path].get("sha256") != metadata["sha256"]
        )

        if needs_update:
            # Ensure parent directory exists
            mirror_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_file, mirror_file)
            copied += 1

            if verbose:
                status = "Updated" if rel_path in old_files else "Copied"
                print(f"  ✅ {status}: {rel_path}")
        else:
            skipped += 1
            if verbose:
                print(f"  ⏭️  Skipped (unchanged): {rel_path}")

    # Delete files that no longer exist in source
    for rel_path in old_files:
        if rel_path not in source_files:
            mirror_file = mirror_dir / rel_path
            if mirror_file.exists():
                mirror_file.unlink()
                deleted += 1
                if verbose:
                    print(f"  🗑️  Deleted: {rel_path}")

    # Clean up empty directories
    for dirpath in sorted(mirror_dir.rglob("*"), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            dirpath.rmdir()
            if verbose:
                print(f"  🗑️  Removed empty dir: {dirpath.relative_to(mirror_dir)}")

    return copied, skipped, deleted


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    force = "--force" in sys.argv or "-f" in sys.argv

    try:
        repo_root = find_repo_root()
        print(f"Syncing agent assets: {repo_root}\n")

        # Define paths
        source_dir = repo_root / ".claude" / "skills"
        mirror_dirs = [
            repo_root / ".codex" / "skills",
            repo_root / "skills"
        ]

        # Collect source files
        if verbose:
            print(f"Collecting source files from {source_dir}...")
        source_files = collect_source_files(source_dir, verbose)
        print(f"✅ Collected {len(source_files)} files from canonical source\n")

        # Sync to each mirror
        for mirror_dir in mirror_dirs:
            print(f"Syncing to {mirror_dir.relative_to(repo_root)}...")

            # Remove symlink if exists
            if mirror_dir.is_symlink():
                if verbose:
                    print(f"  🔗 Removing symlink: {mirror_dir}")
                mirror_dir.unlink()

            # Sync files
            copied, skipped, deleted = sync_to_mirror(
                source_dir,
                mirror_dir,
                source_files,
                verbose,
                force
            )

            # Generate manifest
            manifest = {
                "source": ".claude/skills",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator": "scripts/sync_agent_assets.py",
                "files": source_files
            }

            manifest_path = mirror_dir / ".manifest.json"
            save_manifest(manifest_path, manifest)

            print(f"✅ Synced to {mirror_dir.relative_to(repo_root)}: "
                  f"{copied} copied, {skipped} skipped, {deleted} deleted")
            print(f"   Manifest: {manifest_path.relative_to(repo_root)}\n")

        print("✅ Agent assets sync completed successfully!")
        sys.exit(0)

    except SyncError as e:
        print(f"\n❌ Sync failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
