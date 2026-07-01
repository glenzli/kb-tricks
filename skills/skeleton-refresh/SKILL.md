---
name: skeleton-refresh
description: Refresh existing DEV_SKELETON.md, REVIEW_SKELETON.md, or AGENTS.md only when stable project intent, non-goals, source-of-truth rules, runtime or release constraints, domain assumptions, entry hints, or review preferences changed. Use when Codex is asked to update skeletons after meaningful project direction changes, not routine implementation edits.
---

# Skeleton Refresh

Update skeletons only for durable changes.

## Refresh Triggers

Refresh when one of these changed:

- project purpose or non-goals
- supported runtime, platform, or release boundary
- source-of-truth files or artifact categories
- stable domain assumptions
- review priorities or red lines
- recommended entrypoints for common work

Do not refresh for ordinary implementation movement, refactors, renamed helper functions, or test churn.

## Workflow

1. Read the existing skeleton files.
2. Inspect the source-of-truth files relevant to the claimed change.
3. Remove stale detail before adding new detail.
4. Keep the result source-first and short.
5. State any uncertainty rather than hard-coding guesses.

## Output Discipline

Prefer a smaller skeleton that points to source over a larger skeleton that competes with source.
