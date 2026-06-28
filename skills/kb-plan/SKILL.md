---
name: kb-plan
description: "Plan the repository KB manifest, artifact boundaries, and existing-docs comparison without deep source reading."
---

# KB Plan

Use when a repository needs or needs to refresh `KB_PLAN.md`.

## Hard Rules

- Plan only. Do not build KB prose.
- Macro-scan first; avoid deep source reading.
- Define artifact boundaries before detailed tasks.
- Compare existing docs before proposing new KB topics.
- Stop for user review after writing or proposing the manifest.

## Inputs

Read:

- Repo tree and manifest files.
- `.agent/kb/config.yaml` if present.
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
  - .agent/**
docs:
  existing:
    - README.md
    - docs/**
```

## Steps

1. Identify source, docs, tests, generated output, build output, and local-only context.
2. Run `kb docs --summary-json` or `tools/kb_docs.py --json` when available.
3. Decide which existing docs are sufficient, stale, duplicate, or worth linking.
4. Create or update `KB_PLAN.md` with:
   - Overall approach.
   - Artifact boundary.
   - Existing docs comparison.
   - Ignored targets.
   - Task manifest.
5. For each task include `ID`, `KB`, `Sources`, `Focus`, `Tags`, `Docs Comparison`, `Status`.
6. Mark states as `planned`, `built`, `stale`, `orphaned`, `merged-into-docs`, or `deprecated`.

## Output

- `KB_PLAN.md` proposal or update.
- Summary of new, changed, duplicate, and docs-merge candidates.
- Clear next step: usually `kb-build slice 1`.
