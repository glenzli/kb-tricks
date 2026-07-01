---
name: skeleton-init
description: Create source-first DEV_SKELETON.md, REVIEW_SKELETON.md, and AGENTS.md files. Use when initializing dev-skeleton in a repository or replacing a KB/context setup with purpose, non-goals, source-of-truth rules, stable constraints, entry hints, and review preferences without implementation summaries.
---

# Skeleton Init

Create three short orientation files, not a knowledge base.

## Do

1. Read authoritative files: README, manifests, config, release notes, tests, schemas, and obvious entrypoints.
2. Capture only durable orientation: purpose, non-goals, truth sources, constraints, domain assumptions, entry hints, review priorities, and core red lines.
3. Create or update:
   - `DEV_SKELETON.md`
   - `REVIEW_SKELETON.md`
   - `AGENTS.md`
4. Mark uncertainty instead of inventing intent.

## Never Include

- Function, class, method, API, or module summaries.
- Architecture mirrors, call graphs, source indexes, or test inventories.
- Function-level entry hints.
- Behavior that should be read from current source.

## Finish Check

Every durable claim must be grounded in an authoritative file or marked as uncertain.
Routine implementation changes should not require skeleton updates.
