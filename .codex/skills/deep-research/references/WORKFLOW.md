# Deep Research Workflow Reference

This document provides detailed instructions for each phase of the deep research workflow.

## Phase 1: Query Analysis (Detailed)

### Classification Algorithm

```
1. Parse query for key indicators:
   - Single entity/concept → Focused
   - "vs", "compared to", "or" → Comparative  
   - Multiple distinct topics/domains → Multi-faceted
   - "trends", "emerging", "future of" → Exploratory

2. Check for complexity markers:
   - Time constraints ("in 2024", "recently") → Add temporal filter
   - Domain specificity ("in healthcare", "for startups") → Add domain filter
   - Depth indicators ("deep dive", "comprehensive") → Increase iteration limit

3. Output classification:
   > **Query Type**: [Focused/Comparative/Multi-faceted/Exploratory]
   > **Research Mode**: [Deep Iterative/Wide Parallel]
   > **Filters**: [temporal, domain, depth as applicable]
```

### Query Decomposition (Wide Parallel Mode)

For multi-faceted queries, decompose systematically:

```
Original: "Impact of AI on healthcare, education, and employment"

Subtasks:
1. "AI applications and impact in healthcare sector 2024"
2. "AI transformation of education and learning"
3. "AI effects on employment and job market"
4. "Cross-sector AI trends and common patterns"
```

## Phase 2: Research Execution (Detailed)

### Deep Iterative Mode Protocol

```
ITERATION 1 (Broad):
├── Search: [main topic + context]
├── Extract: Key facts, definitions, major themes
├── Identify: 2-3 gaps or deeper questions
└── Note: Sources with credibility indicators

ITERATION 2 (Focused):
├── Search: [gap #1 specific query]
├── Search: [gap #2 specific query]  
├── Synthesize: Connect new findings to iteration 1
└── Identify: Remaining gaps (if any)

ITERATION 3 (Deep):
├── Search: [remaining critical gaps]
├── Validate: Cross-reference key claims
└── Finalize: Complete synthesis
```

### Wide Parallel Mode Protocol

```
DECOMPOSITION:
├── Break query into 3-5 independent subtasks
├── Ensure subtasks cover all dimensions
└── Add cross-reference subtask if needed

PARALLEL EXECUTION:
├── Execute searches for all subtasks
├── Track sources per subtask
└── Note overlapping findings

MERGE PROTOCOL:
├── Identify common themes across subtasks
├── Flag contradictions for explicit mention
├── Build unified narrative with clear sections
└── Cross-reference findings between sections
```

## Phase 3: Synthesis (Detailed)

### Source Quality Assessment

Rate each source on:
- **Authority**: Official source, academic, established media, blog, forum
- **Recency**: Publication date relative to topic relevance
- **Corroboration**: Claim appears in multiple independent sources

```
Quality Tiers:
- High: Official/academic + recent + corroborated
- Medium: Established media OR corroborated
- Low: Single source, blog, or outdated
```

### Claim Attribution Format

Every factual claim must include attribution:

```markdown
According to [Source Name](URL), [claim]. This is corroborated by 
[Second Source](URL) which adds that [additional detail].

However, [Contrasting Source](URL) suggests [alternative view], 
indicating some debate in this area.
```

### Handling Uncertainty

```markdown
**High Confidence**: Multiple authoritative sources agree
**Medium Confidence**: Single authoritative source or multiple secondary sources
**Low Confidence**: Limited sources, potential bias, or conflicting information
**Unknown**: Insufficient evidence found—noted as research gap
```

## Phase 4: Output Generation (Detailed)

### Report Assembly Order

1. **Executive Summary**: 2-3 sentences, key takeaway, confidence level
2. **Key Findings**: Bulleted highlights with source count
3. **Detailed Sections**: Organized by theme/subtask
4. **Methodology Note**: Research mode used, search count, date
5. **Source List**: All URLs with brief descriptions
6. **Appendix** (if applicable): JSON export, raw data

### Progressive Summarization

To manage context window:

```
After each search:
1. Extract key facts (max 5 bullet points)
2. Note source URL and quality tier
3. Discard raw search content
4. Keep running synthesis document

Final assembly uses synthesis, not raw results
```

### Visualization Decision Tree

```
Include Mermaid diagram when:
├── Comparing 3+ entities → Use comparison table or flowchart
├── Showing process/timeline → Use sequence or timeline diagram
├── Displaying relationships → Use entity relationship diagram
├── Showing hierarchy → Use tree or mindmap
└── Otherwise → Skip visualization
```
