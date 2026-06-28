---
name: kb-audit
description: "Audit KB health with metadata-first checks: coverage, freshness, links, boundaries, validation, and index output."
---

# KB Audit

Use before relying on KB for review, migration, onboarding, or query answers.

## Hard Rules

- Metadata-first. Do not deep-read KB prose or source files.
- Source and tests remain authoritative.
- Treat dirty, stale, draft, and `notAuthoritative` KB as unsafe for decisions.
- Prefer deterministic tooling when present.

## Fast Path

Run:

```bash
kb audit --repo . --summary-json
kb audit --repo . --write-index .agent/kb/index.json
kb docs --repo . --check-manifest --check-links
```

Use `tools/kb_audit.py` / `tools/kb_docs.py` wrappers when the installed CLI is unavailable.

## Checks

- Setup: config, manifest, reserved dirs.
- Manifest coverage: tasks vs actual authoritative KB docs.
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
  - `kb-plan` for missing/duplicate manifest work.
  - `kb-build` for planned missing docs.
  - `kb-update` for stale/dirty/orphaned docs.
  - `cycle-changelog` after completed updates.
