# Dev Skeleton

## Purpose

- Provide compact, source-first orientation for AI-assisted development.
- Keep project navigation and semantic ownership legible as repositories grow.
- Supply durable constraints and architectural priors without replacing engineering judgment.

## Non-Goals

- Persistent implementation knowledge bases or generated code inventories.
- CLI, indexing, project-management, onboarding, test, or release systems.
- Prescriptive decomposition rules that substitute a workflow for local reasoning.

## Source Authority

- `.codex-plugin/plugin.json`: installable plugin identity and bundle entry point.
- `skills/*/SKILL.md`: reusable agent guidance.
- `skills/*/references/*.md`: conditional guidance for specialized boundaries.
- `skills/*/agents/openai.yaml`: user-facing skill metadata and invocation policy.
- `templates/*.md`: copyable project skeletons.
- `README.md`: public positioning and usage, not the required internal navigation entry.

Current source, tests, configuration, schemas, and release artifacts remain authoritative for
implementation facts.

## Repository Map

| Concern | Stable entry | Ownership boundary |
| --- | --- | --- |
| Distribute the complete skill bundle | `.codex-plugin/plugin.json` | Plugin identity and bundle-level discovery |
| Create or evolve project orientation | `skills/skeleton-*/` | Skeleton lifecycle and source-first discipline |
| Maintain production structure | `skills/maintain-source-cohesion/` | Semantic ownership, extraction judgment, and boundary validation |
| Review changes | `skills/review-skeleton/` | Review priorities and source-grounded findings |
| Copy files into another repository | `templates/` | Generic project-facing skeleton contracts |

## Architectural Priors

- A skeleton is a bounded semantic map and a set of durable priors, not a mirror of today's code.
- This repository is the plugin root; skills and bundle-level templates remain one maintained unit.
- Root `SKELETON.md` should route an unfamiliar maintainer to a subsystem or stable entry in one or
  two hops. Add a nested `SKELETON.md` only when a large subsystem cannot meet that standard locally.
- README files may serve product, installation, public documentation, or package-specific needs;
  internal navigation must not depend on overloading them.
- Source entries, module declarations, schemas, build files, and tests describe current mechanics.
- Skills should improve the model's judgment with missing context. They should not require ceremony
  where the task is already clear and low risk.
- Large cohesive owners are acceptable. Mixed lifecycle, policy, or failure ownership is the actual
  reason to reconsider a boundary.

## Stable Constraints

- Keep broadly triggered skill bodies concise without deleting guidance needed for complex projects.
- Load stack-specific material only when the current change touches that boundary.
- Keep templates project-agnostic and easy to remove or adapt.
- Prefer stable responsibility names and navigation edges over volatile file inventories.
- Mark uncertainty rather than converting inference into durable project intent.
- Prefer deleting stale guidance to preserving it for completeness.

## Refresh Boundary

Update this file when purpose, non-goals, stable owners, navigation strategy, distribution model,
truth-source rules, or architectural priors change. Routine implementation movement, helper renames,
and current behavior belong in source and should not trigger an update.
