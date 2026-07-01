# Dev Skeleton

## Purpose

- Provide short skills and templates that orient an AI agent before source reading.
- Preserve project intent, constraints, truth-source rules, and review preferences.
- Avoid durable implementation knowledge.

## Non-Goals

- Persistent implementation KB.
- CLI package.
- Source indexer.
- Module, class, function, API, or architecture mirror.
- Test, onboarding, release, or project-management workflow.

## Source Of Truth

- `skills/*/SKILL.md`: agent behavior constraints.
- `templates/*.md`: copyable skeleton files for target repositories.
- `README.md`: public positioning and usage.

Current repository files are authoritative for implementation facts.

## Stable Constraints

- Keep skills short and trigger descriptions precise.
- Keep templates generic and copyable.
- Prefer deletion over preserving stale detail.
- Do not record code structure or current behavior as durable knowledge.
- Review support injects priorities and red lines; source and diff still decide facts.

## Entry Hints

- Start with `README.md` for positioning.
- Use `skills/README.md` to see available skills.
- Use `templates/` for target-repository skeleton files.
- Read `REVIEW_SKELETON.md` before reviewing this repo.

## Refresh Triggers

Update this file only when purpose, non-goals, skill set, distribution model, truth-source rules, or review constraints change.
