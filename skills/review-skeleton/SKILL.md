---
name: review-skeleton
description: Perform source-first code, design, or documentation review using project-specific review priorities from REVIEW_SKELETON.md and orientation from DEV_SKELETON.md. Use when Codex is asked for a review, CR, PR review, design review, or change assessment in a repository that uses dev-skeleton.
---

# Review Skeleton

Use skeletons to bias review, not to prove facts.

## Workflow

1. Read `REVIEW_SKELETON.md`.
2. Read `DEV_SKELETON.md` if the review depends on project purpose or constraints.
3. Inspect the actual diff, source files, config, tests, and release artifacts needed for the review.
4. Lead with findings ordered by severity.
5. Cite concrete files and lines when possible.
6. Separate skeleton-preference concerns from source-grounded correctness issues.

## Review Focus

Use the repository's review skeleton to prioritize:

- project purpose fit
- source-of-truth violations
- release, runtime, or compatibility boundaries
- over-engineering and scope creep
- stale documentation or skeleton risk
- missing verification for risky changes

## Guardrails

Do not let skeleton files replace reading source. If the skeleton conflicts with source, report the mismatch and trust source for implementation facts.
