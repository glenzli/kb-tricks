# dev-skeleton

Source-first project intent and review skeleton skills for LLM-assisted development.

`dev-skeleton` is not a knowledge base system, code indexer, CLI package, or project-management framework. It provides copyable skills and templates that help an AI agent start from the right intent, constraints, source-of-truth rules, and review preferences before reading the actual code.

The source remains authoritative. Skeleton files only tell the agent how to orient itself and what to protect.

## Principles

- **Source first**: code, configuration, tests, release artifacts, and maintained docs are authoritative.
- **Skeleton, not archive**: record project purpose, non-goals, stable constraints, source-of-truth rules, and review preferences.
- **No source mirror**: do not maintain module summaries, class maps, function behavior, call graphs, or API signatures as long-lived knowledge.
- **Dynamic reading**: let the LLM inspect source on demand for the task at hand.
- **Light updates**: refresh skeletons only when intent, constraints, tech stack, runtime/release boundaries, or review preferences change.
- **Review preference injection**: review skeletons tell the LLM what this project cares about; the LLM still performs the review from source and diff.

## Repository Layout

```text
skills/
  skeleton-init/      Create a source-first project skeleton.
  skeleton-refresh/   Update skeletons only for stable intent or constraint changes.
  skeleton-audit/     Check skeletons for source-first discipline and over-detail.
  review-skeleton/    Use project review preferences during source-first review.

templates/
  DEV_SKELETON.md
  REVIEW_SKELETON.md
  AGENTS.md

docs/
  DESIGN.md
```

Root `DEV_SKELETON.md` and `REVIEW_SKELETON.md` describe this repository itself.

## Usage

Copy or adapt the templates into a target repository:

```text
DEV_SKELETON.md
REVIEW_SKELETON.md
AGENTS.md
```

Then ask an AI agent to use the relevant skill:

- `skeleton-init`: create initial skeletons from source, README, manifests, and release/runtime files.
- `skeleton-refresh`: update existing skeletons after stable project intent or constraints change.
- `skeleton-audit`: check whether skeletons are too detailed, stale, or not source-first.
- `review-skeleton`: perform source-first review using project-specific review preferences.

There is no install step and no released CLI. Skill distribution is intentionally left to the user or an external skill distributor.

## Out Of Scope

- Persistent KBs that try to answer implementation details.
- Long-lived architecture mirrors.
- Static class/function/method indexes.
- Context build/update/audit CLI workflows.
- Test/onboarding/release automation.
- Multi-agent review frameworks that replace ordinary source-first review.

## Maintenance Rule

When in doubt, delete detail from skeletons and point the agent back to source.
