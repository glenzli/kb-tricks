---
name: kb-update
description: "Maintain existing KB from diff-first scopes, dirty-aware fingerprints, and bounded rewrite actions."
---

# KB Update

Use after source, docs, config, or KB-related changes.

## Hard Rules

- Diff-first when a scope exists.
- Default slice is 1 affected KB task.
- Do not widen beyond `kb update-plan` actions.
- Dirty or untracked source blocks formal writes unless `draft` or `allow-dirty` is explicit.
- Do not delete orphaned KB silently; mark or propose.
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

1. Run `kb update-plan --json` with the requested scope when available.
2. Treat `actions` as the maximum formal work set.
3. Report `blocked`, `docsActions`, `newKbCandidates`, `specialActions`, and `releaseExcludedChanges`.
4. If `dry-run`, stop after the plan.
5. For each selected action:
   - Re-read only relevant sources and existing KB.
   - Update the focused sections.
   - Refresh frontmatter fingerprint.
   - Refresh `.agent/kb/_validation/<task-id>.md`.
   - Sync `KB_PLAN.md` lifecycle status.
6. Keep draft updates in `_draft/`.
7. Run or recommend `kb-audit` after updates.

## Output

- Updated KB and validation paths.
- Blockers and draft paths.
- Manifest state changes.
- New KB candidates.
- Existing docs review candidates.
- Suggested `cycle-changelog` when update work is complete.
