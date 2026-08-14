---
name: review-skeleton
description: Perform source-first code, design, or documentation review using REVIEW_SKELETON.md priorities and SKELETON.md orientation. Use for review, CR, PR review, design review, or change assessment in a repository that uses dev-skeleton. Fall back to legacy DEV_SKELETON.md only when SKELETON.md is absent.
---

# Review Skeleton

Use skeletons to bias review, not to prove facts.

## Do

1. Read `REVIEW_SKELETON.md`.
2. Read `SKELETON.md` if the review depends on project purpose, ownership, or constraints. Use
   `DEV_SKELETON.md` only as a legacy fallback.
3. Inspect the actual diff, source files, config, tests, and release artifacts needed for the review.
4. Lead with findings ordered by severity.
5. Cite concrete files and lines when possible.
6. Separate skeleton-preference concerns from source-grounded correctness issues.

## Focus

- Purpose fit.
- Project-defining red lines from `Block`.
- Source-of-truth violations.
- Release, runtime, or compatibility boundaries.
- Semantic ownership and false modularity when a change grows or moves a responsibility.
- Over-engineering and scope creep.
- Stale documentation or skeleton risk.
- Missing verification for risky changes.

## Guardrail

If skeletons conflict with source, trust source for facts and report skeleton drift.
