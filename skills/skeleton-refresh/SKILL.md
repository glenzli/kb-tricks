---
name: skeleton-refresh
description: Refresh DEV_SKELETON.md, REVIEW_SKELETON.md, or AGENTS.md only when stable project intent, non-goals, source-of-truth rules, runtime or release constraints, domain assumptions, source-navigation expectations, entry hints, or review preferences changed. Use after meaningful project direction changes, not routine implementation edits.
---

# Skeleton Refresh

Update only durable orientation.

## Refresh For

- Project purpose or non-goals.
- Runtime, platform, or release boundaries.
- Source-of-truth files or artifact categories.
- Stable domain assumptions.
- Durable semantic-ownership or source-navigation expectations.
- Review priorities or red lines.
- Recommended entrypoints for common work.

Skip routine refactors, renamed helpers, implementation movement, and test churn.
If only current implementation details changed, leave skeletons unchanged.

1. Read the existing skeleton files.
2. Inspect the source-of-truth files relevant to the claimed change.
3. Remove stale detail before adding new detail.
4. Keep the result source-first and short.
5. Mark uncertainty instead of hard-coding guesses.

## Finish Check

Prefer a smaller skeleton that points to source over a larger skeleton that competes with source.
