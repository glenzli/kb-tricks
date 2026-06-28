---
name: review-code
description: "Review code diffs with focused expert dimensions, source authority, and optional Context cross-checks."
---

# Review Code

Use for PRs, commits, working-tree diffs, or scoped file changes.

Follow `../REVIEW_PROTOCOL.md`.

## Hard Rules

- Findings first, ordered by severity.
- Cite file and line where possible.
- Do not comment on unrelated code.
- Skip Context cross-check if relevant Context is stale, dirty, draft-only, or not authoritative.
- Treat tests and source as stronger evidence than Context.

## Triage

Classify changed files:

- `trivial`: comments, docs, formatting, small copy changes.
- `standard`: normal product or tool changes.
- `critical`: auth, crypto, data loss, migrations, public API, release boundary, security-sensitive code.

Review `standard` and `critical`; summarize skipped trivial files.

## Dimensions

Check:

- Architecture and boundaries.
- Logic and edge cases.
- Security.
- Performance.
- Testability.
- Maintainability.
- Domain-specific risks.
- Context direct or indirect impact, only after freshness passes.

## Output

- Findings with severity, file/line, issue, and fix suggestion.
- Triage summary.
- Test gaps.
- Context action items:
  - `Context-Action: UPDATE <path>` for direct contract drift.
  - `Context-Action: REVIEW <path>` for possible indirect impact.
- Residual risks and open questions.

