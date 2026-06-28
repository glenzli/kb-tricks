---
id: "<task-id>"
title: "<Task Title>"
status: "planned"
notAuthoritative: true
fingerprint:
  - file: "<source/path.ext>"
    commit: "current-git-commit-hash-or-null"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:..."
tags: ["<tag>"]
---

# <Task Title>

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

- Replace template placeholders before marking this document authoritative.
