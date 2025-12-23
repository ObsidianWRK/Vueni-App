# Plan: Test XML Tag Usage in plan-mode Skill

<goal>

Verify that the `plan-mode` skill's SKILL.md file correctly uses XML tags as structural delimiters per the Agent Skills prompt engineering best practices.

</goal><context>

The `plan-mode` skill states it "uses XML tags for prompt engineering best practices." These tags serve as delimiters that help Claude parse and understand different sections of the skill instructions.

</context><test_cases>

### Test 1: Required XML Tags Present

Verify these XML tags exist in `.claude/skills/plan-mode/SKILL.md`:| Tag | Purpose | Expected |

|-----|---------|----------|

| `<purpose>` | Skill purpose statement | Present |

| `<workflow>` | Planning workflow wrapper | Present |

| `<understand>` | Phase 1 instructions | Present |

| `<research>` | Phase 2 instructions | Present |

| `<structure>` | Phase 3 instructions | Present |

| `<output_format>` | Phase 4 template | Present |

| `<best_practices>` | Prompt engineering tips | Present |

| `<chain_of_thought>` | Reasoning markers | Present |

| `<output_modes>` | Output format options | Present |

| `<clarifying_questions>` | Question guidelines | Present |

| `<examples>` | Example plans | Present |

| `<integration>` | Platform-specific notes | Present |

### Test 2: Tags Are Properly Closed

Every opening tag should have a matching closing tag.

### Test 3: Tags Are Not Nested Incorrectly

Verify tags don't overlap improperly (e.g., `<a><b></a></b>` is invalid).

### Test 4: Content Exists Between Tags

Tags should not be empty — each should contain meaningful content.</test_cases><verification>

```bash
# Test 1: Check all required tags exist
grep -E "<purpose>|<workflow>|<understand>|<research>|<structure>|<output_format>|<best_practices>|<chain_of_thought>|<output_modes>|<clarifying_questions>|<examples>|<integration>" .claude/skills/plan-mode/SKILL.md

# Test 2: Count opening vs closing tags (should match)
for tag in purpose workflow understand research structure output_format best_practices chain_of_thought output_modes clarifying_questions examples integration; do
  open=$(grep -c "<$tag>" .claude/skills/plan-mode/SKILL.md)
  close=$(grep -c "</$tag>" .claude/skills/plan-mode/SKILL.md)
  echo "<$tag>: open=$open, close=$close"
done

# Test 3: Check tag nesting order
grep -n -E "^</?[a-z_]+>$" .claude/skills/plan-mode/SKILL.md

# Test 4: Validate no empty tags (same line open/close)
grep -E "<[a-z_]+></[a-z_]+>" .claude/skills/plan-mode/SKILL.md
```

</verification><success_criteria>

- All required XML tags are present
- Each opening tag has exactly one matching closing tag
- No empty tags exist
- Tags are properly nested (no overlapping)

</success_criteria><todos>| ID | Task | Depends On | Status |

|----|------|------------|--------|

| T1 | Run Test 1: Verify all required XML tags present | – | pending |

| T2 | Run Test 2: Verify opening/closing tags match | T1 | pending |

| T3 | Run Test 3: Verify proper tag nesting | T2 | pending |

| T4 | Run Test 4: Verify no empty tags | T3 | pending |</todos>