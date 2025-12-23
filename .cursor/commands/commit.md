Propose 3 conventional-commit messages for the changes.

Format:
- type(scope): subject
- optional body (why)
- optional footer (BREAKING CHANGE / refs)

Constraints:
- Subject <= 72 chars, no trailing period.
- Prefer a specific scope (package/module) if obvious.
- Use imperative mood ("add" not "added").

Types:
- feat: new feature
- fix: bug fix
- docs: documentation only
- style: formatting, no code change
- refactor: restructure without behavior change
- perf: performance improvement
- test: adding/updating tests
- build: build system or dependencies
- ci: CI configuration
- chore: maintenance tasks

Examples:
- feat(auth): add OAuth2 login flow
- fix(api): handle null response from payment gateway
- refactor(ui): extract Button into shared component
- docs(readme): add deployment instructions

Context:
(paste what changed or the PR summary)
