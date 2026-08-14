---
name: skeleton-init
description: Initialize source-first SKELETON.md, REVIEW_SKELETON.md, and AGENTS.md files in a repository that does not yet have the canonical dev-skeleton contracts, or replace an explicitly selected KB/context setup. Capture durable project boundaries, source authority, a bounded semantic map, architectural priors, invariants, and review preferences without implementation summaries. Use skeleton-refresh for existing canonical files or legacy migration.
---

# Skeleton Init

Create three compact orientation files, not a knowledge base or workflow system.

## Boundary

- If `SKELETON.md` already exists, use `skeleton-refresh` unless the user explicitly requests a full
  reinitialization.
- If only `DEV_SKELETON.md` exists, use `skeleton-refresh` to migrate its durable content.
- Preserve an existing `REVIEW_SKELETON.md` or `AGENTS.md` unless replacing it is explicitly in scope.

## Use Maintained Templates

Read the maintained [SKELETON.md template](../../templates/SKELETON.md),
[REVIEW_SKELETON.md template](../../templates/REVIEW_SKELETON.md), and
[AGENTS.md template](../../templates/AGENTS.md) before writing. Treat them as adaptable output
assets, not project facts. If these bundle-level templates are unavailable, report an incomplete
dev-skeleton distribution instead of synthesizing a competing template contract.

## Do

1. Read enough authoritative source, manifests, configuration, tests, schemas, release artifacts, and
   maintained documentation to distinguish project intent from current mechanics.
2. Capture durable orientation: purpose and boundaries, source authority, architectural priors,
   invariants, review priorities, and core red lines.
3. Add a bounded semantic map when it materially shortens navigation. Map stable concerns to entry
   points and ownership boundaries; do not inventory the tree.
4. Create the missing canonical files:
   - `SKELETON.md`
   - `REVIEW_SKELETON.md`
   - `AGENTS.md`
5. Keep README independent. It may be a useful source, but it is not required to own internal navigation.
6. Mark uncertainty instead of inventing intent.

## Never Include

- Function, class, method, API, or module summaries.
- Architecture mirrors, call graphs, generated or exhaustive source indexes, or test inventories.
- Function-level entry hints.
- Behavior that should be read from current source.

## Finish Check

Every durable claim must be grounded in an authoritative file or marked as uncertain.
Routine implementation changes should not require skeleton updates.
