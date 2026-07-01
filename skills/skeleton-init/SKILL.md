---
name: skeleton-init
description: Create source-first project skeleton files such as DEV_SKELETON.md, REVIEW_SKELETON.md, and AGENTS.md. Use when initializing dev-skeleton in a repository, replacing a heavy KB/context setup, or asking Codex to capture project purpose, non-goals, source-of-truth rules, stable constraints, entry hints, and review preferences without documenting implementation details.
---

# Skeleton Init

Create a small project skeleton, not a knowledge base.

## Workflow

1. Read existing source-of-truth files: README, package/build manifests, config, release notes, tests, schemas, and obvious entrypoints.
2. Infer only stable orientation: purpose, non-goals, source-of-truth rules, constraints, domain assumptions, entry hints, and review priorities.
3. Write or update:
   - `DEV_SKELETON.md`
   - `REVIEW_SKELETON.md`
   - `AGENTS.md`
4. Mark uncertainty as an open question instead of inventing intent.
5. Keep each file short enough that an agent will actually read it.

## Do Not Include

- Function, class, or method summaries.
- Current module-by-module architecture mirrors.
- API signatures or parameter behavior.
- Call graphs.
- Test inventories.
- Generated source indexes.

## Validation

Before finishing, check that every skeleton claim is grounded in an authoritative file or explicitly marked as an assumption.
