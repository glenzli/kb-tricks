---
name: review-test
description: "Review test quality, coverage gaps, assertions, maintainability, and optional Context contract coverage."
---

# Review Test

Use when evaluating test files, test strategy, or test changes in a diff.

Follow `../REVIEW_PROTOCOL.md`.

## Hard Rules

- Source and actual tests are authoritative.
- Do not require coverage for implementation details that should stay private.
- If Context is stale or dirty, skip Context contract coverage and report that.
- Suggest concrete test cases, not generic encouragement.

## Steps

1. Identify test framework, target source, and changed test files.
2. Check dimensions:
   - Coverage gaps.
   - Assertion quality.
   - Boundary conditions.
   - Test maintainability.
   - Framework-specific correctness.
3. If Context freshness passes, compare tests against documented contracts.
4. Distinguish between missing tests and stale Context.
5. Rate overall test health.

## Output

- Test health: `Unsafe`, `Weak`, `Adequate`, `Good`, or `Excellent`.
- Findings with file/line or test name.
- Suggested test cases.
- Contract coverage notes.
- Follow-ups: `context-update` when Context appears stale, `review-code` when source issues are found.

