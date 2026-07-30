---
name: skeleton-audit
description: Audit DEV_SKELETON.md, REVIEW_SKELETON.md, and AGENTS.md for source-first discipline, stale KB behavior, excessive implementation detail, missing purpose or non-goals, unclear source-of-truth rules, weak review constraints, and language that makes skeletons compete with source.
---

# Skeleton Audit

Audit skeletons as orientation, not source documentation.

## Check

- Does `DEV_SKELETON.md` state purpose, non-goals, source of truth, constraints, entry hints, and refresh triggers?
- Does `REVIEW_SKELETON.md` state review priorities, red lines, risk patterns, and verification expectations?
- Does `AGENTS.md` tell agents to verify facts against source?
- Are project-defining red lines visible in `Block`, not only risk patterns?
- Are entry hints file or artifact-category level rather than function level?
- Are source-navigation expectations durable ownership rules rather than a current module inventory?
- Do refresh triggers exclude routine implementation changes?
- Does any file summarize modules, classes, functions, or behavior that should be read from source?
- Does any file imply skeleton content is authoritative?
- Are claims grounded in maintained project files?

## Output

Lead with findings. For each issue, cite the file and say whether to delete, shorten, or reframe.

Do not ask the user to build deterministic tooling unless a repeated failure shows prompt-only audit is insufficient.
