---
name: kb-build
description: "Build bounded KB slices from KB_PLAN.md with dirty-aware fingerprints and persisted validation."
---

# KB Build

Use to materialize planned KB tasks into `.agent/kb/**/*.md`.

## Hard Rules

- Default is `slice 1`.
- Do not run until complete unless the user explicitly says `until-complete`.
- Authoritative KB must be based on clean tracked source by default.
- Dirty or untracked source blocks formal writes unless `draft` or `allow-dirty` is explicit.
- Draft output goes under `.agent/kb/_draft/` and must not mark the task `built`.
- Always persist validation under `.agent/kb/_validation/<task-id>.md`.

## Invocation

- `slice N`: max tasks this turn.
- `only <id|tag|path>`: select one task/topic.
- `dry-run`: show reads/writes only.
- `plan-only`: validate manifest and boundaries only.
- `draft`: write dirty-source results as non-authoritative drafts.
- `allow-dirty`: write formal KB but mark `notAuthoritative: true`.

## Steps

1. Select tasks with `kb manifest --status planned --slice N --json` when available.
2. Stop if the selector reports legacy manifest entries; run `kb migrate-plan` first.
3. For each selected task, inspect listed `Sources`.
4. Check source state with `kb fingerprint` or Git:
   - clean tracked: formal write allowed.
   - dirty tracked: block or draft.
   - untracked: block or draft.
   - deleted: mark orphaned candidate; do not build.
5. Build a focused cognitive map:
   - Frontmatter from `templates/kb-doc.md`.
   - Cross-module contracts and design tradeoffs.
   - Mermaid only when it clarifies multi-step interaction.
   - Links instead of duplicated definitions.
6. Update `GLOSSARY.md` for formal KB only.
7. Write validation questions and answers.
8. Update `KB_PLAN.md` status only for formal successful builds.

## Output

- Built or draft KB paths.
- Validation path.
- Manifest changes.
- Dirty/orphaned blockers.
- Suggested next slice.
