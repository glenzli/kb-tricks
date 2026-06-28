---
name: context-build
description: "Build bounded Context slices from CONTEXT_PLAN.md with dirty-aware fingerprints and persisted validation."
---

# Context Build

Use to materialize planned Context tasks into `.dev-cycle/context/**/*.md`.

## Hard Rules

- Default is `slice 1`.
- Do not run until complete unless the user explicitly says `until-complete`.
- Authoritative Context must be based on clean tracked source by default.
- Dirty or untracked source blocks formal writes unless `draft` or `allow-dirty` is explicit.
- Draft output goes under `.dev-cycle/context/_draft/` and must not mark the task `built`.
- Always persist validation under `.dev-cycle/context/_validation/<task-id>.md`.

## Invocation

- `slice N`: max tasks this turn.
- `only <id|tag|path>`: select one task/topic.
- `dry-run`: show reads/writes only.
- `plan-only`: validate manifest and boundaries only.
- `draft`: write dirty-source results as non-authoritative drafts.
- `allow-dirty`: write formal Context but mark `notAuthoritative: true`.

## Steps

1. Select tasks with `dev-cycle context manifest --status planned --slice N --json` when available.
2. Stop if the selector reports legacy manifest entries; run `dev-cycle context migrate-plan` first.
3. Optionally run `dev-cycle context build-assist --slice N` to generate deterministic skeletons and fingerprints; use `--write` only when the user wants the skeleton files.
4. For each selected task, inspect listed `Sources`.
5. Check source state with `dev-cycle context fingerprint` or Git:
   - clean tracked: formal write allowed.
   - dirty tracked: block or draft.
   - untracked: block or draft.
   - deleted: mark orphaned candidate; do not build.
6. Build a focused cognitive map:
   - Frontmatter from `templates/context-doc.md`.
   - Cross-module contracts and design tradeoffs.
   - Mermaid only when it clarifies multi-step interaction.
   - Links instead of duplicated definitions.
7. Update `GLOSSARY.md` for formal Context only.
8. Write validation questions and answers.
9. Update `CONTEXT_PLAN.md` status only for formal successful builds.

## Output

- Built or draft Context paths.
- Validation path.
- Manifest changes.
- Dirty/orphaned blockers.
- Suggested next slice.
