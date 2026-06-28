---
id: "example-task"
title: "Example Task"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "src/example.ts"
    commit: "current-git-commit-hash-or-null"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:..."
tags: ["example"]
---

# Example Task

## Role

Describe what this module owns in the system.

## Contracts

- Public API or cross-module contract:
- Inputs and outputs:
- Error and boundary behavior:

## Design Notes

Capture non-obvious trade-offs and why the current shape exists.

## Interactions

```mermaid
sequenceDiagram
  participant Caller
  participant Module
  Caller->>Module: request
  Module-->>Caller: response
```

## SSOT Links

- Related module: [other.md](../other.md)

## Blindspots

- Record known gaps instead of filling them with guesses.
