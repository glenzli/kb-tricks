# Dev Skeleton

## Purpose

`dev-skeleton` provides lightweight, source-first skills and templates that help an AI agent orient to a project before reading source code.

The project exists to preserve intent, constraints, and review preferences, not implementation knowledge.

## Non-Goals

- No persistent implementation knowledge base.
- No Python CLI package.
- No source code indexer.
- No class/function/module mirror.
- No test, onboarding, release, or project-management workflow.
- No compatibility with the old `dev-cycle` CLI or `.dev-cycle/context` artifacts.

## Source Of Truth

- `skills/*/SKILL.md`: executable agent workflows.
- `templates/*.md`: copyable skeleton files for target repositories.
- `README.md`: public positioning and usage.
- `docs/DESIGN.md`: design rationale.

Skeleton files are not authority for implementation facts. Source files remain authoritative.

## Stable Constraints

- Prefer deletion over preserving stale detail.
- Keep skills short; assume the LLM can read source.
- Record project purpose, non-goals, source-of-truth rules, stable constraints, and review preferences.
- Do not record function-level behavior, current module internals, or generated code structure as long-lived knowledge.
- Review support should inject project priorities and red lines; it should not replace source-first review.

## Entry Hints

- Start with `README.md` for positioning.
- Use `skills/README.md` to see available skills.
- Use `templates/` for target-repository skeleton files.
- Use `REVIEW_SKELETON.md` before reviewing this repository.

## Refresh Triggers

Update this skeleton only when project purpose, non-goals, skill set, distribution model, or review constraints change.

Do not update it for ordinary wording edits or implementation details.
