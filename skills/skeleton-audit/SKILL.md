---
name: skeleton-audit
description: Audit project skeleton files for source-first discipline, stale KB behavior, excessive implementation detail, missing purpose or non-goals, unclear source-of-truth rules, weak review constraints, and links that encourage agents to trust skeletons over source. Use when reviewing DEV_SKELETON.md, REVIEW_SKELETON.md, AGENTS.md, or a proposed skeleton migration.
---

# Skeleton Audit

Review skeletons as orientation artifacts.

## Checks

- Does `DEV_SKELETON.md` state purpose, non-goals, source of truth, constraints, entry hints, and refresh triggers?
- Does `REVIEW_SKELETON.md` state review priorities, red lines, risk patterns, and verification expectations?
- Does `AGENTS.md` tell agents to verify facts against source?
- Does any file summarize modules, classes, functions, or behavior that should be read from source?
- Does any file imply skeleton content is authoritative?
- Are claims grounded in maintained project files?

## Output

Lead with findings. For each issue, cite the file and explain whether to delete, shorten, or reframe the content.

Do not ask the user to build deterministic tooling unless a repeated failure shows prompt-only audit is insufficient.
