---
name: cycle-changelog
description: "Summarize Context/context changes after context-update or related lifecycle work."
---

# Cycle Changelog

Use after `context-update`, context refreshes, migration work, or manual Context edits.

## Hard Rules

- Diff-first only. Prefer `git diff` output over reading full files.
- Do not include generated churn or unrelated source changes.
- Append a new entry; do not rewrite history.

## Scope

Default:

```bash
git diff HEAD -- .dev-cycle/context CONTEXT_PLAN.md
```

If the user provides commits, compare that range instead.

## Classify

- Updated Context docs.
- New Context docs.
- Removed or deprecated Context docs.
- `GLOSSARY.md` changes.
- `CONTEXT_PLAN.md` lifecycle changes.
- Validation or index changes.

## Output

Write or propose a new top entry in `.dev-cycle/context/CHANGELOG.md`:

```markdown
## YYYY-MM-DD - <short theme>

### Updated
- `<path>`: <one sentence summary>

### Added
- `<path>`: <one sentence summary>

### Manifest
- <state changes>
```

