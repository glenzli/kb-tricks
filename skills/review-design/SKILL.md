---
name: review-design
description: "Review an architecture proposal, RFC, or design note before implementation."
---

# Review Design

Use before code is written or before a design is accepted.

Follow `../REVIEW_PROTOCOL.md`.

## Hard Rules

- Review the proposal against source, config, tests, maintained docs, and fresh KB.
- If relevant KB is stale or dirty, skip KB consistency checks and say why.
- Do not turn review into implementation.
- Prefer specific risks and changes over broad advice.

## Steps

1. Identify proposal scope, target users, changed components, and constraints.
2. Detect project type from manifests and directory structure.
3. Run dimension checks:
   - Feasibility.
   - Scalability.
   - Complexity risk.
   - Security and compliance.
   - Operational cost.
4. Add one domain-specific check when useful.
5. If KB freshness passes, compare against existing architecture and contracts.
6. Aggregate findings and assign readiness.

## Output

- Readiness: `Blocked`, `Major Revisions`, `Minor Revisions`, `Ready`, or `Excellent`.
- Findings ordered by severity.
- Concrete recommendations.
- Open questions.
- KB freshness note when KB was used or skipped.

