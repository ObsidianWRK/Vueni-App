# Plan: Test Cursor Plan XML Tag Generation

<goal>Verify whether Cursor's built-in plan creation generates plans with XML tags per the plan-mode skill specification.</goal><context>The plan-mode skill specifies that plans should use XML tags as structural delimiters. However, Cursor's native `create_plan` tool may output standard Markdown headers instead. This test determines if manual intervention or post-processing is required.</context><test_cases>

### Test 1: Create a Plan via Cursor

1. Enter plan mode in Cursor
2. Request a simple plan (e.g., "Plan how to add a button")
3. Observe the generated plan file

### Test 2: Check for XML Tags in Output

Examine the generated plan file for:

- `<goal>` tag (vs `## Goal` header)
- `<context>` tag (vs `## Context` header)
- `<steps>` tag (vs `## Steps` header)
- `<assumptions>` tag (vs `## Assumptions` header)
- `<risks>` tag (vs `## Risks` header)
- `<todos>` tag (vs `## Implementation Todos` header)

### Test 3: Compare Against plan-mode Skill Spec

Check if the output matches the format specified in `.claude/skills/plan-mode/SKILL.md`:

- Does it use XML structural delimiters?
- Does it follow the recommended section order?

</test_cases><verification>

```bash
# After Cursor creates a plan, check for XML tags
PLAN_FILE="path/to/new/plan.md"

# Check for XML tags (should find matches if compliant)
echo "=== Checking for XML tags ==="
grep -E "^<(goal|context|steps|assumptions|risks|todos)>" "$PLAN_FILE"

# Check for Markdown headers (should NOT find these if XML-compliant)
echo "=== Checking for Markdown headers ==="
grep -E "^## (Goal|Context|Steps|Assumptions|Risks)" "$PLAN_FILE"

# Summary
echo "=== Result ==="
if grep -q "^<goal>" "$PLAN_FILE"; then
  echo "✓ Plan uses XML tags"
else
  echo "✗ Plan uses Markdown headers (needs conversion)"
fi
```

</verification><expected_results>| Scenario | XML Tags Found | Markdown Headers Found | Result ||----------|---------------|------------------------|--------|| Cursor native output | No | Yes | **Needs conversion** || After `convert_plan_to_xml.py` | Yes | No | **Compliant** || Manual XML formatting | Yes | No | **Compliant** |</expected_results><success_criteria>

- Determine definitively whether Cursor's `create_plan` tool outputs XML tags
- If not, confirm the `convert_plan_to_xml.py` script can fix it
- Document the workflow for creating XML-compliant plans

</success_criteria><todos>| ID | Task | Depends On | Status ||----|------|------------|--------|| T1 | Trigger Cursor to create a new plan | – | pending || T2 | Examine raw output for XML vs Markdown | T1 | pending || T3 | If Markdown, run conversion script | T2 | pending || T4 | Document findings and workflow | T3 | pending |</todos>