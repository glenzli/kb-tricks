---
name: context-update
description: "Maintain existing Context from diff-first scopes, dirty-aware fingerprints, and bounded rewrite actions."
---

# Context Update

Use after source, docs, config, or Context-related changes.

## Hard Rules

- Diff-first when a scope exists.
- Default slice is 1 affected Context task.
- Do not widen beyond `dev-cycle context update-plan` actions.
- Dirty or untracked source blocks formal writes unless `draft` or `allow-dirty` is explicit.
- Do not delete orphaned Context silently; mark or propose.
- Refresh validation and fingerprints for every formal update.

## Scope Options

Prefer one:

- `--staged`
- `--worktree`
- `--base <commitish>`
- `--since <commitish>`
- `--files <path...>`

If no scope is provided, use full fingerprint audit as a fallback.

## Steps

1. Run `dev-cycle context update-plan --json` with the requested scope when available.
2. Treat `actions` as the maximum formal work set.
3. Report `blocked`, `docsActions`, `newContextCandidates`, `specialActions`, and `releaseExcludedChanges`.
4. If `dry-run`, stop after the plan.
5. For each selected action:
   - Re-read only relevant sources and existing Context.
   - Update the focused sections.
   - Refresh frontmatter fingerprint.
   - Refresh `.dev-cycle/context/_validation/<task-id>.md`.
   - Sync `CONTEXT_PLAN.md` lifecycle status.
6. Keep draft updates in `_draft/`.
7. Run or recommend `context-audit` after updates.

## Output

- Updated Context and validation paths.
- Blockers and draft paths.
- Manifest state changes.
- New Context candidates.
- Existing docs review candidates.
- Suggested `cycle-changelog` when update work is complete.
