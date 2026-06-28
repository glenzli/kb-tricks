---
name: cycle-migrate
description: "Plan large architectural, platform, framework, or language migrations with source-first impact analysis and KB-assisted context."
---

# Cycle Migrate

Use when the user has a concrete migration target, such as framework replacement,
service split, runtime upgrade, language migration, or storage backend change.

## Hard Rules

- Source, config, tests, release artifacts, and maintained docs are authoritative.
- Use KB for routing and dependency context only when fresh.
- Produce a plan, not implementation, unless the user explicitly asks to execute.
- Keep migration order safe: leaves first, core last.

## Inputs

Extract:

- From: current architecture or technology.
- To: target architecture or technology.
- Scope: full migration, phased migration, or coexistence.
- Constraints: compatibility, release window, data migration, rollback.

## Steps

1. Read `KB_PLAN.md`, relevant fresh KB docs, existing docs, and key config files.
2. Identify affected modules and source paths.
3. Classify each module:
   - `unaffected`
   - `adaptable`
   - `rewrite`
   - `deprecate`
4. Build a dependency order from imports, references, KB links, and known runtime paths.
5. Split into phases with validation gates.
6. List follow-up context work after migration.

## Output

Create or propose `MIGRATION_PLAN.md`:

- Summary: From / To / Scope / Constraints.
- Impact matrix.
- Dependency order.
- Phased execution plan.
- Risk and rollback notes.
- Follow-ups: `kb-update`, `kb-audit`, `review-test`, `cycle-changelog`.

