---
name: cycle-changelog
description: "Summarize KB/context changes after kb-update or related lifecycle work."
---

# Cycle Changelog

Use after `kb-update`, context refreshes, migration work, or manual KB edits.

## Hard Rules

- Diff-first only. Prefer `git diff` output over reading full files.
- Do not include generated churn or unrelated source changes.
- Append a new entry; do not rewrite history.

## Scope

Default:

```bash
git diff HEAD -- .agent/kb KB_PLAN.md
```

If the user provides commits, compare that range instead.

## Classify

- Updated KB docs.
- New KB docs.
- Removed or deprecated KB docs.
- `GLOSSARY.md` changes.
- `KB_PLAN.md` lifecycle changes.
- Validation or index changes.

## Output

Write or propose a new top entry in `.agent/kb/CHANGELOG.md`:

```markdown
## YYYY-MM-DD - <short theme>

### Updated
- `<path>`: <one sentence summary>

### Added
- `<path>`: <one sentence summary>

### Manifest
- <state changes>
```

