---
name: deep-research
description: Deep research skill combining Perplexity-style iterative depth with Manus-style parallel breadth. Analyzes queries, executes multi-phase research, and produces comprehensive reports with citations, structured data, and visualizations.
license: MIT
compatibility: Designed for Cursor, Claude, and Codex
metadata:
  version: 1.0.0
  author: Agent Skills
allowed-tools: web_search read_file write grep list_dir codebase_search
---

# Deep Research Skill

<purpose>
Execute comprehensive research by intelligently selecting between deep iterative (Perplexity-style) and wide parallel (Manus-style) approaches based on query complexity. Produce rich Markdown reports with inline citations, structured JSON exports, and Mermaid visualizations.
</purpose>

## When to Invoke

Trigger this skill when:
- User requests "deep research", "research this", or "investigate"
- Query requires multiple sources or perspectives
- User needs comprehensive analysis with citations
- Topic is complex, comparative, or multi-faceted

## Research Workflow

<workflow>

### Phase 1: Query Analysis

<query_analysis>
Classify the research query into one of four types:

| Type | Pattern | Example | Mode |
|------|---------|---------|------|
| **Focused** | Single topic, specific question | "How does CRISPR gene editing work?" | Deep Iterative |
| **Comparative** | A vs B, pros/cons | "React vs Vue for enterprise apps" | Wide Parallel |
| **Multi-faceted** | Multiple dimensions | "AI impact on healthcare, education, and jobs" | Wide Parallel |
| **Exploratory** | Open-ended discovery | "Emerging trends in sustainable energy" | Deep Iterative |

Output the classification before proceeding.
</query_analysis>

### Phase 2: Research Execution

<deep_iterative_mode>
**For Focused/Exploratory queries:**
1. Execute initial broad search on main topic
2. Analyze results, identify 2-3 knowledge gaps or deeper questions
3. Execute follow-up searches (max 3 iterations)
4. Progressively synthesize findings, building on previous context
5. Stop when gaps are filled or iteration limit reached
</deep_iterative_mode>

<wide_parallel_mode>
**For Comparative/Multi-faceted queries:**
1. Decompose query into 3-5 distinct subtasks/dimensions
2. Execute searches for each subtask (can be parallel)
3. Collect findings per subtask with source tracking
4. Cross-reference findings for patterns and contradictions
5. Merge into unified synthesis
</wide_parallel_mode>

### Phase 3: Synthesis

<synthesis>
For all findings:
1. **Deduplicate**: Remove redundant information across sources
2. **Validate**: Cross-check claims appearing in multiple sources
3. **Organize**: Group by theme, chronology, or relevance
4. **Attribute**: Link every claim to its source URL
5. **Identify gaps**: Note areas where evidence is weak or conflicting
</synthesis>

### Phase 4: Output Generation

<output_generation>
Generate three outputs:

1. **Markdown Report** (always): See `references/OUTPUT_FORMATS.md`
2. **JSON Export** (on request or for complex queries): Structured data with metadata
3. **Visualizations** (when relationships exist): Mermaid diagrams

Always include:
- Search date/time for temporal context
- Source count and quality assessment
- Confidence levels for key findings
</output_generation>

</workflow>

## Constraints

<constraints>
- Maximum 10 web searches per research session
- Summarize progressively to manage context window
- Never fabricate citations—only cite sources from search results
- Include "[Source: URL]" inline for every factual claim
- Note when information may be outdated (check publication dates)
</constraints>

## Quick Reference

Load `references/WORKFLOW.md` for detailed phase instructions.
Load `references/OUTPUT_FORMATS.md` for report templates and JSON schema.
Load `references/EXAMPLES.md` for example queries and outputs.
