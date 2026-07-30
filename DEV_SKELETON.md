# Dev Skeleton

## Purpose

- Provide short source-first skills and templates that orient an AI agent and preserve navigable source during changes.
- Preserve project intent, constraints, truth-source rules, and review preferences.
- Avoid durable implementation knowledge.

## Non-Goals

- Persistent implementation KB.
- CLI package.
- Source indexer.
- Module, class, function, API, or architecture mirror.
- Standalone test, onboarding, release, or project-management workflow.

## Source Of Truth

- `skills/*/SKILL.md`: agent behavior constraints.
- `templates/*.md`: copyable skeleton files for target repositories.
- `README.md`: public positioning and usage.

Current repository files are authoritative for implementation facts.

## Stable Constraints

- Keep skills short and trigger descriptions precise.
- Keep broadly triggered skill bodies concise and load stack-specific guidance only when relevant.
- Keep templates generic and copyable.
- Prefer deletion over preserving stale detail.
- Do not record code structure or current behavior as durable knowledge.
- Treat the code tree as the detailed index: preserve durable semantic-ownership expectations, not current module inventories.
- Keep entry hints at file or artifact-category level, not function level.
- Review support injects priorities and red lines; source and diff still decide facts.

## Entry Hints

- Start with `README.md` for positioning.
- Use `skills/README.md` to see available skills.
- Use `skills/maintain-source-cohesion/` for development-time ownership and navigation guidance.
- Use `templates/` for target-repository skeleton files.
- Read `REVIEW_SKELETON.md` before reviewing this repo.

## Refresh Triggers

Update this file only when purpose, non-goals, skill set, distribution model, truth-source rules, or review constraints change. Routine implementation changes should not update it.
