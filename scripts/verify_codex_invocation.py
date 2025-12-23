#!/usr/bin/env python3
"""
Codex Skill Triple Verification Harness

Checks three standards for each skill under a given skills root:
1) Keyword invocation prompt -> expects INVOCATION_OK:<skill>
2) Explicit invocation prompt -> expects INVOCATION_OK:<skill>
3) Runtime self-test -> validates SKILL.md frontmatter and emits SELFTEST_OK:<skill>

Outputs a JSON report and can append a markdown summary.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


MARKER_INVOCATION = "INVOCATION_OK"
MARKER_SELFTEST = "SELFTEST_OK"


@dataclass
class CheckResult:
    status: str  # "pass", "fail", "skip"
    detail: str


@dataclass
class SkillResult:
    skill: str
    keyword: CheckResult
    explicit: CheckResult
    selftest: CheckResult

    def failed(self) -> bool:
        return any(r.status == "fail" for r in (self.keyword, self.explicit, self.selftest))


def read_frontmatter(skill_md: Path) -> Dict[str, str]:
    content = skill_md.read_text(encoding="utf-8", errors="ignore")
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    fm_lines = content[4:end].splitlines()
    fm: Dict[str, str] = {}
    for line in fm_lines:
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def run_codex(prompt: str) -> Tuple[str, Optional[str]]:
    """
    Run Codex CLI with the provided prompt.
    Returns (stdout, error_message). error_message is None on success.
    """
    try:
        proc = subprocess.run(
            ["codex", "exec", prompt],
            check=False,
            capture_output=True,
            text=True,
        )
        return proc.stdout + proc.stderr, None
    except FileNotFoundError:
        return "", "codex CLI not found"
    except Exception as exc:  # pragma: no cover - safety net
        return "", f"codex CLI error: {exc}"


def check_invocation(skill: str, prompt: str) -> CheckResult:
    output, err = run_codex(prompt)
    marker = f"{MARKER_INVOCATION}:{skill}"
    if err:
        return CheckResult("skip", err)
    if marker in output:
        return CheckResult("pass", f"Marker found: {marker}")
    return CheckResult("fail", f"Missing marker {marker}; output: {output[:200]}...")


def check_selftest(skill_dir: Path) -> CheckResult:
    skill_md = skill_dir / "SKILL.md"
    license_txt = skill_dir / "LICENSE.txt"
    if not skill_md.exists():
        return CheckResult("fail", "SKILL.md missing")
    if not license_txt.exists():
        return CheckResult("fail", "LICENSE.txt missing")

    fm = read_frontmatter(skill_md)
    name = fm.get("name", "")
    description = fm.get("description", "")

    missing = []
    if name != skill_dir.name:
        missing.append(f"name mismatch (found '{name}')")
    if not description:
        missing.append("description missing")
    # license is optional per minimal frontmatter spec

    if missing:
        return CheckResult("fail", "; ".join(missing))

    return CheckResult("pass", f"{MARKER_SELFTEST}:{skill_dir.name}")


def append_markdown(md_path: Path, results: List[SkillResult]) -> None:
    lines = [
        "\n## Codex Triple Verification Results",
        "",
        "| Skill | Keyword | Explicit | Self-test | Notes |",
        "|-------|---------|----------|-----------|-------|",
    ]
    for r in results:
        def icon(res: CheckResult) -> str:
            return {"pass": "✅", "fail": "❌", "skip": "⏭️"}.get(res.status, res.status)

        note = r.keyword.detail if r.keyword.status != "pass" else ""
        if r.explicit.status != "pass":
            note = f"{note} | explicit: {r.explicit.detail}".strip(" |")
        if r.selftest.status != "pass":
            note = f"{note} | selftest: {r.selftest.detail}".strip(" |")
        lines.append(
            f"| {r.skill} | {icon(r.keyword)} | {icon(r.explicit)} | {icon(r.selftest)} | {note or '—'} |"
        )

    with md_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex skill triple verification harness")
    parser.add_argument("--skills-root", default=".codex/skills", help="Root directory of Codex skills")
    parser.add_argument("--report-json", default="reports/codex_invocation_report.json", help="Path to JSON report")
    parser.add_argument("--append-md", help="Optional markdown file to append a summary table")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of skills (for quick checks)")
    args = parser.parse_args()

    skills_root = Path(args.skills_root)
    if not skills_root.exists():
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return 1

    skill_dirs = sorted([d for d in skills_root.iterdir() if d.is_dir()])
    if args.limit:
        skill_dirs = skill_dirs[: args.limit]

    results: List[SkillResult] = []

    for skill_dir in skill_dirs:
        skill = skill_dir.name
        keyword_prompt = (
            f"Use the {skill} skill to help with its intended task. "
            f"Respond with {MARKER_INVOCATION}:{skill} once loaded."
        )
        explicit_prompt = (
            f"Invoke skill {skill} now. Respond with {MARKER_INVOCATION}:{skill} once loaded."
        )

        keyword_res = check_invocation(skill, keyword_prompt)
        explicit_res = check_invocation(skill, explicit_prompt)
        selftest_res = check_selftest(skill_dir)

        results.append(SkillResult(skill, keyword_res, explicit_res, selftest_res))

    report_path = Path(args.report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "skills_root": str(skills_root),
        "markers": {"invocation": MARKER_INVOCATION, "selftest": MARKER_SELFTEST},
        "results": [asdict(r) for r in results],
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"JSON report written to {report_path}")

    if args.append_md:
        append_markdown(Path(args.append_md), results)
        print(f"Markdown summary appended to {args.append_md}")

    failures = [r for r in results if r.failed()]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
