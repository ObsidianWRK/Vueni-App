from pathlib import Path

from scripts.validate_plan_completion import validate_plan_completion


def write_plan(plan_path: Path, name: str, completed: bool = True):
    status = "completed" if completed else "pending"
    content = "\n".join(
        [
            "---",
            f"name: {name}",
            "todos:",
            "  - id: T1",
            "    content: Test",
            f"    status: {status}",
            "---",
            "",
            "# Plan",
        ]
    )
    plan_path.write_text(content, encoding="utf-8")


def test_validate_plan_completion_checks_home_dir(tmp_path: Path, monkeypatch):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "AGENTS.md").write_text("# Agents", encoding="utf-8")

    home_root = tmp_path / "home"
    home_root.mkdir()
    monkeypatch.setenv("HOME", str(home_root))
    home_plans = home_root / ".cursor" / "plans"
    home_plans.mkdir(parents=True)

    plan_path = home_plans / "home.plan.md"
    write_plan(plan_path, "home-plan", completed=True)

    is_valid, violations = validate_plan_completion(repo_root, verbose=False)
    assert not is_valid
    assert any("home-plan" in v for v in violations)
