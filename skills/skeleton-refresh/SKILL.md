---
name: skeleton-refresh
description: Refresh existing SKELETON.md, REVIEW_SKELETON.md, or AGENTS.md when durable project intent, boundaries, source authority, stable ownership, navigation, architectural priors, invariants, runtime or release constraints, or review preferences changed. Also use to migrate legacy DEV_SKELETON.md. Do not use for first-time initialization or routine implementation edits.
---

# Skeleton Refresh

Update only durable orientation.

If no canonical or legacy skeleton files exist, use `skeleton-init` rather than inventing an update
target.

## Refresh For

- Project purpose or non-goals.
- Runtime, platform, or release boundaries.
- Source-of-truth files or artifact categories.
- Stable domain assumptions.
- Durable semantic ownership, subsystem entries, or navigation expectations.
- Review priorities or red lines.
- Stable entries that route common work to an owner.

Skip routine refactors, renamed helpers, internal implementation movement, and test churn when the
stable owner and navigation path did not change.
If only current implementation details changed, leave skeletons unchanged.

1. Prefer `SKELETON.md`. If only `DEV_SKELETON.md` exists and modernization is in scope, migrate its
   durable content and remove the legacy file rather than maintaining both indefinitely.
2. Inspect the source-of-truth files relevant to the claimed change.
3. Remove stale detail before adding new detail.
4. Keep semantic maps bounded and stable; a map should route to owners, not enumerate implementations.
5. Add a nested `SKELETON.md` only when a large subsystem cannot be navigated locally in one or two hops.
6. Keep the result source-first and compact enough to remain useful.
7. Mark uncertainty instead of hard-coding guesses.

## Finish Check

Prefer a smaller skeleton that points to source over a larger skeleton that competes with source.
