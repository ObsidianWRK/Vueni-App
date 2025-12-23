#!/bin/bash
# Batch standardize all skills with TDD
# Per superpowers:writing-skills workflow

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="/Users/damon/Vueni-App-refactor/.claude/skills"

# List of all skills (already standardized: algorithmic-art)
SKILLS=(
    "brand-guidelines"
    "canvas-design"
    "deep-research"
    "doc-coauthoring"
    "docx"
    "expo-ios-designer"
    "frontend-design"
    "internal-comms"
    "mcp-builder"
    "ocr"
    "pdf"
    "plan-mode"
    "pptx"
    "shadcn-ui"
    "skill-creator"
    "slack-gif-creator"
    "template"
    "theme-factory"
    "web-artifacts-builder"
    "webapp-testing"
    "xlsx"
)

echo "=========================================="
echo "Batch Standardization with TDD"
echo "=========================================="
echo ""

TOTAL=${#SKILLS[@]}
COUNT=0
FAILED=()

for skill in "${SKILLS[@]}"; do
    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL] Processing: $skill"
    echo "------------------------------------------"

    # Run pre-standardization test
    echo "  Running pre-standardization pressure test..."
    python3 "$SCRIPT_DIR/test_skill_pressure.py" "$skill" > "/tmp/pre_${skill}.txt" 2>&1

    # Standardize
    echo "  Standardizing frontmatter..."
    if python3 "$SCRIPT_DIR/standardize_skill.py" "$skill"; then
        # Run post-standardization test
        echo "  Running post-standardization pressure test..."
        python3 "$SCRIPT_DIR/test_skill_pressure.py" "$skill" > "/tmp/post_${skill}.txt" 2>&1

        # Check if tests passed
        if [ $? -eq 0 ]; then
            echo "  ✅ $skill standardized and tested successfully"

            # Commit individual skill
            cd "$SKILLS_DIR/.." && git add ".claude/skills/$skill/SKILL.md"
            git commit -m "Standardize $skill: minimal frontmatter (name + description)

TDD evidence:
- Pre-standardization: $(grep "Summary:" /tmp/pre_${skill}.txt | tail -1)
- Post-standardization: $(grep "Summary:" /tmp/post_${skill}.txt | tail -1)
- No banned patterns detected

Per superpowers:writing-skills."

        else
            echo "  ⚠️ $skill: Pressure tests found issues"
            FAILED+=("$skill")
        fi
    else
        echo "  ❌ Failed to standardize $skill"
        FAILED+=("$skill")
    fi

    echo ""
done

echo "=========================================="
echo "Batch Standardization Complete"
echo "=========================================="
echo "Total processed: $TOTAL"
echo "Failed: ${#FAILED[@]}"
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "Failed skills:"
    for skill in "${FAILED[@]}"; do
        echo "  - $skill"
    done
fi
