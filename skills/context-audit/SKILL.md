---
name: context-audit
description: "Audit Context health with metadata-first checks: coverage, freshness, links, boundaries, validation, and index output."
---

# Context Audit

Use before relying on Context for review, migration, onboarding, or query answers.

## Hard Rules

- Metadata-first. Do not deep-read Context prose or source files.
- Source and tests remain authoritative.
- Treat dirty, stale, draft, and `notAuthoritative` Context as unsafe for decisions.
- Prefer deterministic tooling when present.

## Fast Path

Run:

```bash
dev-cycle context audit --repo . --summary-json
dev-cycle context audit --repo . --write-index .dev-cycle/context/index.json
dev-cycle context docs --repo . --check-manifest --check-links
```

Use `tools/context_audit.py` / `tools/context_docs.py` wrappers when the installed CLI is unavailable.

## Checks

- Setup: config, manifest, reserved dirs.
- Manifest coverage: tasks vs actual authoritative Context docs.
- Freshness: fingerprint commit, content hash, tracked, worktree, source existence.
- Dirty/draft authority: `notAuthoritative`, `_draft/`, `_impact/`.
- Links: local Markdown links and glossary targets.
- Validation: matching `_validation/<task-id>.md`.
- Existing docs: `Docs Comparison`, dead links, duplicate hints.
- Release boundary: `releaseExcluded` usage.

## Scoring

Report:

- Coverage.
- Freshness.
- Links.
- Glossary.
- Validation.
- Setup.
- Overall grade.

## Output

- Health summary.
- Top issues by category.
- Recommended next actions:
  - `context-plan` for missing/duplicate manifest work.
  - `context-build` for planned missing docs.
  - `context-update` for stale/dirty/orphaned docs.
  - `cycle-changelog` after completed updates.
