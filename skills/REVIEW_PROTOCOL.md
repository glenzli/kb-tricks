# Review Protocol

This protocol applies to `review-design`, `review-code`, and `review-test`.

## Authority

Source code, configuration, tests, release artifacts, and maintained docs are
authoritative. Context is routing and context. A review skill may use Context only when
the relevant Context documents are fresh and authoritative.

## Freshness Gate

Before using Context evidence, review skills must check relevant Context frontmatter:

- `fingerprint.contentHash`
- `fingerprint.commit`
- `fingerprint.worktree`
- `tracked`
- `notAuthoritative`

If any relevant Context document is stale, dirty, draft-only, untracked, or
`notAuthoritative: true`, skip the Context-specific review layer and report the
reason. Continue the source-first review.

## Review Pattern

Review skills may use dimension-specific reviewers internally:

1. Route the request and identify the project paradigm.
2. Run fixed dimension checks for the review type.
3. Add one focused domain check when useful.
4. Add the Context cross-check layer only after the freshness gate passes.
5. Aggregate, deduplicate, rate severity, and produce actionable findings.

The public skill names are `review-design`, `review-code`, and `review-test`.

## Output

Findings must include:

- Severity or risk level.
- File, line, function, proposal section, or evidence location when available.
- Concrete finding.
- Actionable recommendation.
- Source type: source/config/test/docs/Context/inference.

Inference must be isolated from factual findings.
