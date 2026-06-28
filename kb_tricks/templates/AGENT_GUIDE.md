# kb-tricks Agent Guide

This repository uses `kb-tricks` for AI-maintained development context.

## Read This First

- The KB is auxiliary. Source code, configuration, tests, release artifacts, and maintained human docs are authoritative.
- Use KB documents to route questions, understand boundaries, compress context, and find source links.
- Do not present KB prose as fact when it conflicts with source, tests, config, or release outputs.
- If KB freshness is stale, dirty, missing, or unknown, say so and verify against authoritative sources.

## Root Agent Instruction

Add this short pointer to the repository's root `AGENTS.md`, `CLAUDE.md`, or equivalent AI instruction file:

```markdown
This repository uses kb-tricks. Before planning, querying, or updating repository knowledge, read `.agent/kb/AGENT_GUIDE.md`. Treat KB as routing/context, not authority; verify factual claims against source, tests, config, release artifacts, or maintained docs.
```

## First-Time Setup

Install or reference the `kb` CLI, then scaffold starter artifacts into this repository:

```bash
kb scaffold --repo . --dry-run
kb scaffold --repo .
```

Configure `.agent/kb/config.yaml` before building KB content. At minimum, review:

- `include`: paths that are meaningful for KB planning.
- `exclude`: generated files, dependencies, build output, and noisy paths.
- `releaseExcluded`: files useful for AI context but not release-facing truth.
- `docs.existing`: maintained docs that should be compared before creating KB.

## AI Operating Rules

1. Prefer bounded commands. Use `--slice 1` or `--slice 2` unless the user explicitly asks for a larger run.
2. Do not update formal KB from dirty or untracked source. Use drafts or impact notes until the source change is committed.
3. Start updates from a diff scope when possible: `--staged`, `--worktree`, `--since`, `--base`, or `--files`.
4. Every factual answer should identify its source type: KB, source fallback, existing docs, or inference.
5. Keep inference separate from facts. If inference is necessary, label it explicitly.
6. If KB and source disagree, source wins and the KB should be marked for update.
7. Do not run full-repository KB work by default. Ask before running broad or expensive operations.

## Common Commands

```bash
kb self-check --json
kb docs --repo . --check-manifest --check-links
kb manifest --repo . --slice 1
kb impact --repo . --since HEAD~1 --json
kb update-plan --repo . --since HEAD~1 --slice 1
kb fingerprint --repo . --check .agent/kb/path/to/doc.md
kb query-lint --repo . path/to/answer.md
kb audit --repo . --fail-on stale --fail-on dead-links --min-score B
```

## Skill Usage

Use `kb-plan` to create or revise `KB_PLAN.md`.
Use `kb-build` to build small slices of planned KB.
Use `kb-update` after source changes.
Use `kb-query` for provenance-first answers.
Use `kb-audit` before relying on KB for review or planning.

Skills may be copied into the target repository or referenced from the `kb-tricks` source repository. The deterministic `kb` CLI is the stable implementation boundary.

## When To Stop And Ask

Ask the user before:

- Updating KB from dirty source.
- Running an unbounded build/update.
- Creating KB that duplicates maintained docs.
- Treating release-excluded files as release authority.
- Changing artifact boundary config in a way that broadens scope significantly.
