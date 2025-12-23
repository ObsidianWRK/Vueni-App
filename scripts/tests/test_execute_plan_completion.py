from pathlib import Path

from scripts.execute_plan_completion import parse_yaml_frontmatter


def test_parse_yaml_frontmatter_reads_inline_todos(tmp_path: Path):
    plan_path = tmp_path / "plan.plan.md"
    content = "\n".join(
        [
            "---",
            "name: sample",
            "todos:",
            "  - id: T1",
            "    content: Test",
            "    status: completed",
            "---",
            "",
            "# Plan",
        ]
    )
    plan_path.write_text(content, encoding="utf-8")

    frontmatter, _ = parse_yaml_frontmatter(plan_path.read_text(encoding="utf-8"))
    todos = frontmatter.get("todos", [])

    assert len(todos) == 1
    assert todos[0]["id"] == "T1"
    assert todos[0]["status"] == "completed"
