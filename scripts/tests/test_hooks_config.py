import json
from pathlib import Path


def test_hooks_config_enforces_plan_completion():
    config_path = Path(".claude/hooks.json")
    assert config_path.exists()

    config = json.loads(config_path.read_text())
    hooks = config.get("hooks", {})

    post_tool = hooks.get("PostToolUse", [])
    todo_hooks = [h for h in post_tool if h.get("matcher") == "^todo_write$"]
    assert todo_hooks
    hook = todo_hooks[0]["hooks"][0]
    assert hook.get("continueOnError") is False
    assert hook.get("async") is False

    session_start = hooks.get("SessionStart", [])
    assert session_start
    scripts = [h["script"] for block in session_start for h in block.get("hooks", [])]
    assert ".claude/hooks/pre-session-plan-check.js" in scripts
