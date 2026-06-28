# Knowledge Base Manifest

## Overall Approach

Describe the repository architecture and why the Context is divided into the task groups below.

## Artifact Boundary

- Config: `.dev-cycle/context/config.yaml`
- Include: `src/**`, `docs/dev/**`
- Exclude: `dist/**`, `out/**`, `node_modules/**`
- Release Excluded: `.dev-cycle/**`, `docs/dev/**`

## Existing Docs Comparison

- `README.md`: Covers install and quickstart; do not duplicate.
- `docs/example.md`: Add concrete comparison notes here.

## Ignored Targets

- `tests/`: Test suites, unless test architecture is itself the target.
- `dist/`: Build output.

## Task Manifest

- [planned] example-task
  - **ID**: `example-task`
  - **Context**: `.dev-cycle/context/example/task.md`
  - **Sources**: `src/example.ts`
  - **Focus**: Cross-module contract, design trade-offs, and edge behavior.
  - **Tags**: `example`
  - **Docs Comparison**: Existing docs have overview only; Context should capture Agent retrieval anchors.
  - **Status**: `planned`
  - **LastValidated**: ``
