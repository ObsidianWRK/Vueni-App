# Web Search Policy

**Priority:** High
**Applies to:** All web search operations

## Policy

No `web_search` unless the `deep-research` skill is explicitly invoked and its workflow followed.

If external sources are needed, invoke `deep-research` and perform all searches inside that workflow.

## Rationale

The `deep-research` skill provides:
- Structured research methodology
- Proper citation management
- Multi-phase iterative search
- Comprehensive analysis and reporting

Using web_search outside this workflow leads to:
- Inconsistent research quality
- Missing citations
- Fragmented information gathering
- No structured output

## Compliance

**Correct:**
```
User: "Research the latest trends in AI agents"
Agent: Invokes deep-research skill
Agent: Follows deep-research workflow with web_search
```

**Incorrect:**
```
User: "What's the latest on AI agents?"
Agent: Uses web_search directly
```

**Enforcement:**
- This policy is enforced through agent instruction priority
- Violations indicate missing skill-checking workflow
- See AGENTS.md skill checking requirement
