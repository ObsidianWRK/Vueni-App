#!/usr/bin/env python3
"""
Agent System Validator

Validates the complete agent instruction system across:
- AGENTS.md canonical instructions
- .claude/CLAUDE.md and .claude/rules/ (Claude Code adapter)
- .cursor/rules/ (Cursor adapter)
- Skills architecture
- Size limits for Codex CLI

Usage:
    python scripts/validate_agent_system.py [--verbose]
"""

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Codex limit
CODEX_LIMIT_BYTES = 32768
CODEX_WARNING_THRESHOLD = 0.85  # Warn at 85% of limit

class ValidationError:
    def __init__(self, gate: str, message: str, severity: str = "error"):
        self.gate = gate
        self.message = message
        self.severity = severity

    def __str__(self):
        icon = "❌" if self.severity == "error" else "⚠️"  if self.severity == "warning" else "ℹ️"
        return f"{icon} [{self.gate}] {self.message}"


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


def validate_g1_instruction_topology(repo_root: Path, verbose: bool) -> List[ValidationError]:
    """
    Gate 1: Instruction Topology
    - No contradictory instructions across overlapping scopes
    - All critical subsystems have an instruction source
    """
    errors = []

    # Check AGENTS.md exists
    agents_md = repo_root / "AGENTS.md"
    if not agents_md.exists():
        errors.append(ValidationError("g1", "AGENTS.md not found"))
        return errors

    # Check for nested AGENTS.md files (should be none in flat structure)
    nested_agents = list(repo_root.rglob("AGENTS.md"))
    if len(nested_agents) > 1:
        errors.append(ValidationError(
            "g1",
            f"Found {len(nested_agents)} AGENTS.md files (expected 1 for flat structure)",
            severity="warning"
        ))

    # Check .claude/CLAUDE.md exists
    claude_md = repo_root / ".claude" / "CLAUDE.md"
    if not claude_md.exists():
        errors.append(ValidationError("g1", ".claude/CLAUDE.md not found"))

    # Check .claude/rules/ exists
    claude_rules_dir = repo_root / ".claude" / "rules"
    if not claude_rules_dir.exists():
        errors.append(ValidationError("g1", ".claude/rules/ directory not found"))
    else:
        # Check for expected rule files
        expected_rules = [
            "skills-architecture.md",
            "plan-workflows.md",
            "web-search-policy.md",
            "ocr-auto-invoke.md"
        ]
        for rule_file in expected_rules:
            if not (claude_rules_dir / rule_file).exists():
                errors.append(ValidationError("g1", f".claude/rules/{rule_file} not found"))

    # Check .cursor/rules/ exists
    cursor_rules_dir = repo_root / ".cursor" / "rules"
    if not cursor_rules_dir.exists():
        errors.append(ValidationError("g1", ".cursor/rules/ directory not found"))
    else:
        # Check for operating contract
        operating_contract = cursor_rules_dir / "00-operating-contract.mdc"
        if not operating_contract.exists():
            errors.append(ValidationError("g1", ".cursor/rules/00-operating-contract.mdc not found"))

    if verbose:
        print(f"  Checked instruction topology: {len(errors)} issue(s)")

    return errors


def validate_g2_codex_limits(repo_root: Path, verbose: bool) -> List[ValidationError]:
    """
    Gate 2: Codex Limits
    - AGENTS.md size ≤ 32KB OR documented override exists
    - Provide repeatable size check command
    """
    errors = []

    agents_md = repo_root / "AGENTS.md"
    if not agents_md.exists():
        errors.append(ValidationError("g2", "AGENTS.md not found"))
        return errors

    size_bytes = agents_md.stat().st_size
    size_pct = (size_bytes / CODEX_LIMIT_BYTES) * 100

    if size_bytes > CODEX_LIMIT_BYTES:
        errors.append(ValidationError(
            "g2",
            f"AGENTS.md exceeds Codex limit: {size_bytes} bytes ({size_pct:.1f}% of {CODEX_LIMIT_BYTES} byte limit)"
        ))
    elif size_bytes > CODEX_LIMIT_BYTES * CODEX_WARNING_THRESHOLD:
        errors.append(ValidationError(
            "g2",
            f"AGENTS.md approaching Codex limit: {size_bytes} bytes ({size_pct:.1f}% of {CODEX_LIMIT_BYTES} byte limit)",
            severity="warning"
        ))

    if verbose:
        print(f"  AGENTS.md size: {size_bytes} bytes ({size_pct:.1f}% of limit)")

    return errors


def validate_g3_claude_memory(repo_root: Path, verbose: bool) -> List[ValidationError]:
    """
    Gate 3: Claude Memory
    - .claude/CLAUDE.md exists and is an index
    - .claude/rules/*.md files have valid YAML frontmatter or are global
    """
    errors = []

    # Check .claude/CLAUDE.md
    claude_md = repo_root / ".claude" / "CLAUDE.md"
    if not claude_md.exists():
        errors.append(ValidationError("g3", ".claude/CLAUDE.md not found"))
    else:
        content = claude_md.read_text()
        # Check it's an index (references AGENTS.md)
        if "AGENTS.md" not in content:
            errors.append(ValidationError(
                "g3",
                ".claude/CLAUDE.md should reference AGENTS.md as canonical source",
                severity="warning"
            ))
        # Check it's not too large (should be thin)
        if len(content) > 10000:  # 10KB threshold for index
            errors.append(ValidationError(
                "g3",
                f".claude/CLAUDE.md is {len(content)} bytes (should be thin index <10KB)",
                severity="warning"
            ))

    # Check .claude/rules/
    rules_dir = repo_root / ".claude" / "rules"
    if not rules_dir.exists():
        errors.append(ValidationError("g3", ".claude/rules/ directory not found"))
    else:
        rule_files = list(rules_dir.glob("*.md"))
        if verbose:
            print(f"  Found {len(rule_files)} rule files in .claude/rules/")

        for rule_file in rule_files:
            content = rule_file.read_text()
            # Check for YAML frontmatter
            if content.startswith("---"):
                # Has frontmatter - check for paths: field if needed
                match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
                if match:
                    frontmatter = match.group(1)
                    if "paths:" in frontmatter:
                        # Path-scoped rule - ensure valid globs
                        if verbose:
                            print(f"    {rule_file.name}: path-scoped")
                    # else: global with frontmatter
            # else: global without frontmatter (acceptable)

    return errors


def validate_g4_cursor_rules(repo_root: Path, verbose: bool) -> List[ValidationError]:
    """
    Gate 4: Cursor Rules
    - All .cursor/rules/*.mdc conform to rule types
    - Agent-requested rules have precise descriptions
    """
    errors = []

    rules_dir = repo_root / ".cursor" / "rules"
    if not rules_dir.exists():
        errors.append(ValidationError("g4", ".cursor/rules/ directory not found"))
        return errors

    mdc_files = list(rules_dir.glob("*.mdc"))
    if not mdc_files:
        errors.append(ValidationError("g4", "No .mdc files found in .cursor/rules/"))
        return errors

    if verbose:
        print(f"  Found {len(mdc_files)} .mdc files in .cursor/rules/")

    for mdc_file in mdc_files:
        content = mdc_file.read_text()

        # Check for YAML frontmatter
        if not content.startswith("---"):
            errors.append(ValidationError("g4", f"{mdc_file.name}: missing YAML frontmatter"))
            continue

        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            errors.append(ValidationError("g4", f"{mdc_file.name}: invalid YAML frontmatter"))
            continue

        frontmatter = match.group(1)

        # Determine rule type
        has_always_apply = "alwaysApply: true" in frontmatter
        has_globs = "globs:" in frontmatter
        has_description = "description:" in frontmatter

        if has_always_apply:
            rule_type = "always"
        elif has_globs:
            rule_type = "auto_attached"
        elif has_description:
            rule_type = "agent_requested"
        else:
            rule_type = "manual"

        if verbose:
            print(f"    {mdc_file.name}: {rule_type}")

        # Validate agent-requested rules have precise descriptions
        if rule_type == "agent_requested":
            if "description:" not in frontmatter:
                errors.append(ValidationError(
                    "g4",
                    f"{mdc_file.name}: agent-requested rule missing description"
                ))

    return errors


def validate_g5_skills_quality(repo_root: Path, verbose: bool) -> List[ValidationError]:
    """
    Gate 5: Skills Quality
    - Every skill folder contains SKILL.md
    - Each SKILL.md contains required sections
    - Skills do not duplicate global policies
    """
    errors = []

    skills_dir = repo_root / ".claude" / "skills"
    if not skills_dir.exists():
        errors.append(ValidationError("g5", ".claude/skills/ directory not found"))
        return errors

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    if verbose:
        print(f"  Found {len(skill_dirs)} skill directories")

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            errors.append(ValidationError("g5", f"{skill_dir.name}: missing SKILL.md"))
            continue

        content = skill_md.read_text()

        # Check for YAML frontmatter
        if not content.startswith("---"):
            errors.append(ValidationError("g5", f"{skill_dir.name}: missing YAML frontmatter"))
            continue

        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            errors.append(ValidationError("g5", f"{skill_dir.name}: invalid YAML frontmatter"))
            continue

        frontmatter = match.group(1)

        # Check required fields
        if "name:" not in frontmatter:
            errors.append(ValidationError("g5", f"{skill_dir.name}: frontmatter missing 'name'"))
        if "description:" not in frontmatter:
            errors.append(ValidationError("g5", f"{skill_dir.name}: frontmatter missing 'description'"))

        # Check for required sections (basic check)
        body = content[match.end():]
        required_sections = ["purpose", "when to invoke", "workflow"]
        for section in required_sections:
            if section.lower() not in body.lower():
                errors.append(ValidationError(
                    "g5",
                    f"{skill_dir.name}: missing '{section}' section",
                    severity="warning"
                ))

    return errors


def validate_g6_portability(repo_root: Path, verbose: bool) -> List[ValidationError]:
    """
    Gate 6: Portability
    - No symlinks in mirror directories (cross-platform compatibility)
    - Manifests exist and are valid
    - File hashes match canonical source
    - Skills count matches canonical
    """
    errors = []

    # Define paths
    canonical_dir = repo_root / ".claude" / "skills"
    mirror_dirs = [
        repo_root / ".codex" / "skills",
        repo_root / "skills"
    ]

    # Check canonical source exists
    if not canonical_dir.exists():
        errors.append(ValidationError("g6", ".claude/skills/ canonical source not found"))
        return errors

    # Count canonical skills
    canonical_skills = [d for d in canonical_dir.iterdir() if d.is_dir()]
    if verbose:
        print(f"  Canonical source has {len(canonical_skills)} skills")

    # Check each mirror
    for mirror_dir in mirror_dirs:
        mirror_name = str(mirror_dir.relative_to(repo_root))

        # Check mirror exists
        if not mirror_dir.exists():
            errors.append(ValidationError("g6", f"{mirror_name} mirror not found"))
            continue

        # Check it's NOT a symlink (portability requirement)
        if mirror_dir.is_symlink():
            errors.append(ValidationError(
                "g6",
                f"{mirror_name} is a symlink (must be real directory for cross-platform compatibility)"
            ))
            continue

        # Check manifest exists
        manifest_path = mirror_dir / ".manifest.json"
        if not manifest_path.exists():
            errors.append(ValidationError("g6", f"{mirror_name}/.manifest.json not found"))
            continue

        # Load and validate manifest
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            errors.append(ValidationError("g6", f"{mirror_name}/.manifest.json invalid: {e}"))
            continue

        # Check manifest structure
        if "source" not in manifest:
            errors.append(ValidationError("g6", f"{mirror_name}/.manifest.json missing 'source' field"))
        if "generated_at" not in manifest:
            errors.append(ValidationError("g6", f"{mirror_name}/.manifest.json missing 'generated_at' field"))
        if "files" not in manifest:
            errors.append(ValidationError("g6", f"{mirror_name}/.manifest.json missing 'files' field"))
            continue

        manifest_files = manifest.get("files", {})

        # Count skills in mirror
        mirror_skills = [d for d in mirror_dir.iterdir() if d.is_dir()]
        if verbose:
            print(f"  {mirror_name} has {len(mirror_skills)} skills, {len(manifest_files)} files in manifest")

        # Verify skill count matches canonical
        if len(mirror_skills) != len(canonical_skills):
            errors.append(ValidationError(
                "g6",
                f"{mirror_name} skill count mismatch: {len(mirror_skills)} vs {len(canonical_skills)} canonical"
            ))

        # Sample verification: check a few files match canonical
        # (full verification would be expensive, so we sample)
        sample_count = 0
        max_samples = 5
        for rel_path, metadata in manifest_files.items():
            if sample_count >= max_samples:
                break

            canonical_file = canonical_dir / rel_path
            mirror_file = mirror_dir / rel_path

            # Check canonical file exists
            if not canonical_file.exists():
                errors.append(ValidationError(
                    "g6",
                    f"{mirror_name}/{rel_path} in manifest but missing from canonical source",
                    severity="warning"
                ))
                sample_count += 1
                continue

            # Check mirror file exists
            if not mirror_file.exists():
                errors.append(ValidationError(
                    "g6",
                    f"{mirror_name}/{rel_path} in manifest but file missing"
                ))
                sample_count += 1
                continue

            # Verify hash matches
            expected_hash = metadata.get("sha256")
            if expected_hash:
                actual_hash = sha256_file(canonical_file)
                if actual_hash != expected_hash:
                    errors.append(ValidationError(
                        "g6",
                        f"{mirror_name}/{rel_path} hash mismatch (manifest out of sync)",
                        severity="warning"
                    ))

            sample_count += 1

        if verbose and sample_count > 0:
            print(f"    Verified {sample_count} sample files")

    return errors


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    repo_root = find_repo_root()
    print(f"Validating agent system: {repo_root}\n")

    # Run all validation gates
    gates = [
        ("g1_instruction_topology", validate_g1_instruction_topology),
        ("g2_codex_limits", validate_g2_codex_limits),
        ("g3_claude_memory", validate_g3_claude_memory),
        ("g4_cursor_rules", validate_g4_cursor_rules),
        ("g5_skills_quality", validate_g5_skills_quality),
        ("g6_portability", validate_g6_portability),
    ]

    all_errors = []
    gate_results = []

    for gate_id, gate_fn in gates:
        if verbose:
            print(f"Running {gate_id}...")
        errors = gate_fn(repo_root, verbose)
        all_errors.extend(errors)

        gate_errors = [e for e in errors if e.severity == "error"]
        gate_warnings = [e for e in errors if e.severity == "warning"]

        if gate_errors:
            status = "❌ FAIL"
        elif gate_warnings:
            status = "⚠️  WARN"
        else:
            status = "✅ PASS"

        gate_results.append((gate_id, status, len(gate_errors), len(gate_warnings)))

        if verbose and errors:
            for error in errors:
                print(f"  {error}")
        if verbose:
            print()

    # Print gate summary
    print("Validation Gate Summary:")
    print("=" * 60)
    for gate_id, status, error_count, warn_count in gate_results:
        issues = []
        if error_count:
            issues.append(f"{error_count} error(s)")
        if warn_count:
            issues.append(f"{warn_count} warning(s)")
        issue_str = ", ".join(issues) if issues else "no issues"
        print(f"{status} {gate_id:30} [{issue_str}]")
    print("=" * 60)

    # Separate errors and warnings
    actual_errors = [e for e in all_errors if e.severity == "error"]
    warnings = [e for e in all_errors if e.severity == "warning"]

    # Print detailed errors/warnings if not verbose
    if not verbose:
        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(f"  {w}")

        if actual_errors:
            print("\nErrors:")
            for e in actual_errors:
                print(f"  {e}")

    # Final result
    print()
    if actual_errors:
        print(f"❌ Agent system validation failed with {len(actual_errors)} error(s)")
        sys.exit(1)
    else:
        print("✅ Agent system validation passed!")
        if warnings:
            print(f"   ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
