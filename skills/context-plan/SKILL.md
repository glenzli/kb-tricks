---
name: context-plan
description: "Plan the repository Context manifest, artifact boundaries, and existing-docs comparison without deep source reading."
---

# Context Plan

Use when a repository needs or needs to refresh `CONTEXT_PLAN.md`.

## Hard Rules

- Plan only. Do not build Context prose.
- Macro-scan first; avoid deep source reading.
- Define artifact boundaries before detailed tasks.
- Compare existing docs before proposing new Context topics.
- Stop for user review after writing or proposing the manifest.

## Inputs

Read:

- Repo tree and manifest files.
- `.dev-cycle/context/config.yaml` if present.
- Existing docs from `docs.existing`.
- README, release docs, specs, and package/config files.

If config is missing, propose:

```yaml
include:
  - src/**
exclude:
  - dist/**
  - node_modules/**
releaseExcluded:
  - .dev-cycle/**
docs:
  existing:
    - README.md
    - docs/**
```

## Steps

1. Identify source, docs, tests, generated output, build output, and local-only context.
2. Run `dev-cycle context docs --summary-json` or `tools/context_docs.py --json` when available.
3. Decide which existing docs are sufficient, stale, duplicate, or worth linking.
4. Create or update `CONTEXT_PLAN.md` with:
   - Overall approach.
   - Artifact boundary.
   - Existing docs comparison.
   - Ignored targets.
   - Task manifest.
5. For each task include `ID`, `Context`, `Sources`, `Focus`, `Tags`, `Docs Comparison`, `Status`.
6. Mark states as `planned`, `built`, `stale`, `orphaned`, `merged-into-docs`, or `deprecated`.

## Output

- `CONTEXT_PLAN.md` proposal or update.
- Summary of new, changed, duplicate, and docs-merge candidates.
- Clear next step: usually `context-build slice 1`.
