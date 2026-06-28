# dev-cycle Agent Guide

This repository uses `dev-cycle` for AI-assisted development lifecycle context.

## Read This First

- The Context is auxiliary. Source code, configuration, tests, release artifacts, and maintained human docs are authoritative.
- Use Context documents to route questions, understand boundaries, compress context, and find source links.
- Do not present Context prose as fact when it conflicts with source, tests, config, or release outputs.
- If Context freshness is stale, dirty, missing, or unknown, say so and verify against authoritative sources.

## Root Agent Instruction

Add this short pointer to the repository's root `AGENTS.md`, `CLAUDE.md`, or equivalent AI instruction file:

```markdown
This repository uses dev-cycle. Before planning, querying, or updating repository knowledge, read `.dev-cycle/context/AGENT_GUIDE.md`. Treat Context as routing/context, not authority; verify factual claims against source, tests, config, release artifacts, or maintained docs.
```

## First-Time Setup

Install or reference the `dev-cycle` CLI, then scaffold starter artifacts into this repository:

```bash
dev-cycle context scaffold --repo . --dry-run
dev-cycle context scaffold --repo .
```

Configure `.dev-cycle/context/config.yaml` before building Context content. At minimum, review:

- `include`: paths that are meaningful for Context planning.
- `exclude`: generated files, dependencies, build output, and noisy paths.
- `releaseExcluded`: files useful for AI context but not release-facing truth.
- `docs.existing`: maintained docs that should be compared before creating Context.

## AI Operating Rules

1. Prefer bounded commands. Use `--slice 1` or `--slice 2` unless the user explicitly asks for a larger run.
2. Do not update formal Context from dirty or untracked source. Use drafts or impact notes until the source change is committed.
3. Start updates from a diff scope when possible: `--staged`, `--worktree`, `--since`, `--base`, or `--files`.
4. Every factual answer should identify its source type: Context, source fallback, existing docs, or inference.
5. Keep inference separate from facts. If inference is necessary, label it explicitly.
6. If Context and source disagree, source wins and the Context should be marked for update.
7. Do not run full-repository Context work by default. Ask before running broad or expensive operations.

## Common Commands

```bash
dev-cycle self-check --json
dev-cycle context docs --repo . --check-manifest --check-links
dev-cycle context manifest --repo . --slice 1
dev-cycle context impact --repo . --since HEAD~1 --json
dev-cycle context update-plan --repo . --since HEAD~1 --slice 1
dev-cycle context fingerprint --repo . --check .dev-cycle/context/path/to/doc.md
dev-cycle context query-lint --repo . path/to/answer.md
dev-cycle context audit --repo . --fail-on stale --fail-on dead-links --min-score B
```

## Skill Usage

Use `context-plan` to create or revise `CONTEXT_PLAN.md`.
Use `context-build` to build small slices of planned Context.
Use `context-update` after source changes.
Use `context-query` for provenance-first answers.
Use `context-audit` before relying on Context for review or planning.

Skills may be copied into the target repository or referenced from the `dev-cycle` source repository. The deterministic `dev-cycle context` command group is the stable context-tooling boundary.

## When To Stop And Ask

Ask the user before:

- Updating Context from dirty source.
- Running an unbounded build/update.
- Creating Context that duplicates maintained docs.
- Treating release-excluded files as release authority.
- Changing artifact boundary config in a way that broadens scope significantly.
