# Context Manifest

## Overall Approach

Describe the repository architecture and why the Context is divided into the task groups below. Keep this short; detailed prose belongs in Context documents after bounded build slices.

## Artifact Boundary

- Config: `.dev-cycle/context/config.yaml`
- Include: `<source-or-doc-patterns>`
- Exclude: `<generated-or-noisy-patterns>`
- Release Excluded: `.dev-cycle/**`, `<agent-only-or-internal-patterns>`

## Existing Docs Comparison

- `README.md`: Covers install and quickstart; do not duplicate.
- `<docs/path.md>`: Add concrete comparison notes before creating parallel Context.

## Ignored Targets

- `tests/`: Test suites, unless test architecture is itself the target.
- `dist/`: Build output.

## Task Manifest

- [planned] <task-id>
  - **ID**: `<task-id>`
  - **Context**: `.dev-cycle/context/<area>/<topic>.md`
  - **Sources**: `<source/path.ext>`
  - **Focus**: Cross-module contract, design trade-offs, and edge behavior.
  - **Tags**: `<tag>`
  - **Docs Comparison**: Existing docs have overview only; Context should capture agent retrieval anchors.
  - **Status**: `planned`
  - **LastValidated**: ``
