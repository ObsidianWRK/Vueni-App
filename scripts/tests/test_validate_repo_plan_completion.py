from pathlib import Path

from scripts.validate_repo import validate_repo


def write_plan(plan_path: Path, name: str):
    content = "\n".join(
        [
            "---",
            f"name: {name}",
            "todos:",
            "  - id: T1",
            "    content: Done",
            "    status: completed",
            "---",
            "",
            "# Plan",
        ]
    )
    plan_path.write_text(content, encoding="utf-8")


def test_validate_repo_flags_plan_completion_missing_workdone(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "AGENTS.md").write_text("<name>test-skill</name>", encoding="utf-8")
    skills_dir = repo_root / ".claude" / "skills" / "test-skill"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: test\n---\n", encoding="utf-8"
    )
    (skills_dir / "LICENSE.txt").write_text("MIT", encoding="utf-8")

    plans_dir = repo_root / ".cursor" / "plans"
    plans_dir.mkdir(parents=True)
    write_plan(plans_dir / "plan.plan.md", "missing-workdone")

    errors = validate_repo(repo_root, verbose=False)
    error_messages = [str(err) for err in errors]
    assert any("WorkDone" in msg or "plan completion" in msg for msg in error_messages)
