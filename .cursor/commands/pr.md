Generate a high-quality PR title + description.

Ask me (briefly) if anything critical is missing, otherwise proceed.

Include:
- **Title**: Imperative mood, concise, max 72 chars
- **Summary**: What changed and why (2-3 sentences)
- **Changes**: Bulleted list grouped by area
- **Testing**: What was tested and how to reproduce
- **Risk**: Potential issues and rollback plan
- **Checklist**: Docs, tests, monitoring considerations

Format with GitHub markdown:
- Use `code blocks` for file/function names
- Use **bold** for section headers
- Link to related issues with #number

Example structure:
```
## Summary
Brief description of the change and motivation.

## Changes
- **Area 1**: Description of changes
- **Area 2**: Description of changes

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- How to test: `npm run test`

## Risk Assessment
Low/Medium/High - explanation

## Checklist
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Error handling added
```

Context:
(include links, tickets, or paste diff summary)
