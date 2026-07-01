# Design

`dev-skeleton` is a deliberate retreat from long-lived project knowledge bases.

Modern LLMs can read source, search repositories, follow diffs, and inspect tests directly. A durable project artifact should therefore avoid duplicating code facts. Its job is to preserve the few stable ideas that are hard to infer reliably from a local diff:

- why the project exists
- what it refuses to do
- which files are authoritative
- what constraints should shape decisions
- what review preferences are project-specific

## What A Skeleton Is

A skeleton is an orientation artifact. It helps an agent decide where to look and how to judge trade-offs.

It may include:

- purpose
- non-goals
- source-of-truth rules
- stable runtime or release constraints
- domain assumptions
- entrypoint hints
- review red lines

It should not include:

- module-by-module summaries
- class or function inventories
- call graphs
- API signatures
- behavior that should be read from source
- stale architecture narratives

## Update Model

Skeletons should change rarely. Update them when stable project intent or constraints change.

Do not update them because an implementation detail moved. Let the LLM read the current source for that.

## Review Model

Review skeletons do not perform code review. They bias the LLM toward the right project-specific concerns before it reviews the actual diff and source.
