# dev-cycle Next Design Plan

## Goal

Shape `dev-cycle` as a repo-native development lifecycle toolkit for AI-assisted engineering: context building, querying, updating, design review, code review, test review, migration planning, onboarding, changelogging, and postmortem analysis.

The knowledge base is not the source of truth. Source code, configuration, tests, release artifacts, and maintained human-facing docs remain authoritative. The Context exists to route questions, compress context, explain cross-module contracts, and expose uncertainty.

`dev-cycle` is not a project-management replacement, scheduler, database, or LLM runtime. Its scope is the repository-local development cycle and the deterministic checks that keep AI-assisted work bounded and auditable.

## Architecture

`dev-cycle` evolves in three product layers and three implementation layers.

Product layers:

| Layer | Responsibility |
|---|---|
| Context Layer | Repository understanding through Context planning, building, querying, updating, and auditing. |
| Review Layer | Design, code, and test review workflows that use fresh Context when useful and fall back to source when needed. |
| Evolution Layer | Migration planning, postmortem analysis, onboarding, and changelogging that turn project changes into reusable context. |

Implementation layers:

| Layer | Responsibility |
|---|---|
| Skill Layer | Planning, reading, synthesis, review, and maintenance performed by Agent skills. |
| Spec Layer | Stable artifacts and schemas: `.dev-cycle/context/config.yaml`, `CONTEXT_PLAN.md`, Context frontmatter, `_validation/`, and `index.json`. |
| Tool Layer | Deterministic checks such as hashing, dirty-state detection, link validation, manifest validation, and CI exit codes. |

The tool layer should stay deterministic. It should not become an LLM executor or workflow engine; it gives skills scoped inputs, checks, and policy gates.

Distribution model: deterministic tools ship through normal releases under the `dev-cycle` Python distribution and the `dev-cycle` CLI. Skills may call that released CLI directly when available; when operating inside a target repository, they may copy the released tool bundle or reference it through an external mechanism such as `vasmc`. The target repository should own lifecycle artifacts, not the dev-cycle tool implementation.

Current repository support:

- `spec/CONTEXT_SPEC.md` defines the artifact schema.
- `skills/` contains copyable Agent skill prompts grouped as Context (`context-*`), Review (`review-*`), Evolution (`cycle-*`), and thin recipes such as `cycle-init`.
- `skills/REVIEW_PROTOCOL.md` defines the common source authority and Context freshness gate for review skills.
- `templates/` provides starter artifacts for target repositories.
- `dev_cycle/templates/` packages those starter artifacts so installed `dev-cycle context scaffold` does not depend on a source checkout.
- `dev_cycle/context/` contains the released command implementations used by the installed `dev-cycle` CLI.
- `tools/context_*.py` are source-checkout wrappers around `dev_cycle.context.*` for direct `python3 tools/context_*.py` usage.
- `dev_cycle.context.scaffold` installs starter config, manifest, and reserved Context directories into a target repository without generating Context prose.
- `dev_cycle.context.manifest` selects bounded `CONTEXT_PLAN.md` tasks by status, ID/tag/path filters, and slice size; it does not execute or generate Context prose.
- `dev_cycle.context.docs` inventories existing docs from `docs.existing`, checks Manifest `Docs Comparison` coverage, and emits duplicate hints without judging prose quality.
- `dev_cycle.context.audit` audits existing artifacts and can write `.dev-cycle/context/index.json`; it does not generate Context prose.
- `dev_cycle.context.fingerprint` generates and checks dirty-aware source fingerprints used by Context frontmatter.
- `dev_cycle.context.impact` maps `--staged`, `--worktree`, `--base`, `--since`, or `--files` changes to Manifest tasks, existing docs changes, and special Context artifact changes for diff-first maintenance.
- `dev_cycle.context.update_plan` turns impact results into read-only bounded update actions, blockers, existing-docs reviews, special artifact reviews, and new Context candidates.
- `dev_cycle.context.query_lint` checks `context-query` answer drafts for required sections, source type markers, inference isolation, and citation coverage.
- `dev-cycle` is the installed CLI dispatcher for deterministic commands; source checkouts may call `python3 tools/context_*.py` directly.
- `dev-cycle self-check` is the release smoke boundary: it imports every released subcommand module and verifies that the installed dispatcher can reach each tool.

## Core Operating Contracts

### 1. Bounded execution by default

`context-build` and `context-update` must default to small slices. They should never run the whole repo unless the user explicitly requests an all-in execution mode.

Required invocation contracts:

- `slice N`: process at most `N` manifest tasks in this turn.
- `only <id|tag|path>`: process only matching manifest entries.
- `dry-run`: report what would be read and written, but do not change files.
- `plan-only`: produce or refine the plan without writing Context documents.
- `draft`: write dirty or untracked-source results into draft or impact artifacts instead of authoritative Context.
- `allow-dirty`: explicitly allow dirty-source authoritative writes while marking them `notAuthoritative: true`.
- `until-complete`: explicitly allow repeated slices until the manifest has no remaining eligible tasks.

Default: `slice 1`.

### 2. Authoritative Context vs draft Context

Formal Context documents under `.dev-cycle/context/**/*.md` should be based on clean, tracked source files by default.

Dirty or untracked sources must not be written into authoritative Context unless the user explicitly overrides the gate. Dirty worktree workflows are still useful, but they belong in draft and impact artifacts:

- `.dev-cycle/context/_draft/`
- `.dev-cycle/context/_impact/`
- `.dev-cycle/context/_validation/`

Draft artifacts must be labeled `notAuthoritative: true` and must not be treated as final Context by `context-query`.

### 3. Artifact boundary configuration

Projects should be able to declare which files are candidates for Context ingestion and which files are excluded from release-facing semantics.

Standard config location:

```yaml
# .dev-cycle/context/config.yaml
include:
  - src/**
  - docs/dev/**
exclude:
  - dist/**
  - out/**
  - node_modules/**
releaseExcluded:
  - docs/dev/**
  - .dev-cycle/**
docs:
  existing:
    - README.md
    - docs/**
```

`context-plan` must read this config before planning. If it does not exist, `context-plan` should propose one and pause for confirmation before deepening the plan.

### 4. Dirty-aware fingerprints

Commit hashes alone are insufficient because the Agent may read dirty worktree content. Context frontmatter must record both Git state and content hash.

```yaml
fingerprint:
  - file: src/cli/release.ts
    commit: 65db3c1
    tracked: true
    worktree: clean
    contentHash: sha256:...
```

Rules:

- Clean tracked file: record `commit`, `tracked: true`, `worktree: clean`, and `contentHash`.
- Dirty tracked file: record `commit`, `tracked: true`, `worktree: dirty`, and `contentHash`; authoritative writes are blocked by default.
- Untracked file: record `commit: null`, `tracked: false`, `worktree: untracked`, and `contentHash`; authoritative writes are blocked by default.
- Freshness checks compare `contentHash` first, then Git commit.

### 5. `CONTEXT_PLAN.md` as long-lived manifest

`CONTEXT_PLAN.md` is not only a build checklist. It is the long-lived manifest for Context lifecycle state.

Required task states:

- `planned`
- `built`
- `stale`
- `orphaned`
- `merged-into-docs`
- `deprecated`

Suggested entry shape:

```markdown
- [built] release-packaging
  - **ID**: `release-packaging`
  - **Context**: `.dev-cycle/context/release/packaging.md`
  - **Sources**: `src/cli/release.ts`
  - **Focus**: Release packaging boundary and artifact exclusion rules.
  - **Status**: `built`
  - **Tags**: `release`, `packaging`
  - **LastValidated**: `2026-06-26`
```

### 6. Existing docs comparison

Many repositories already have useful docs. `dev-cycle` should not automatically create a second documentation island.

Planning and audit flows should be able to answer:

- Which existing docs are already sufficient?
- What does the Context add beyond existing docs?
- Which Context sections should be merged back into human-facing docs?
- Which Context sections duplicate existing docs and add little retrieval value?
- Which existing docs conflict with code or Context?

### 7. Provenance-first querying

Every factual answer from `context-query` must label its source type:

- `Context`
- `Source fallback`
- `Existing docs`
- `Inference`

Inference must be isolated in an uncertainty section and must not be presented as fact. `templates/context-query-answer.md` and `dev-cycle context query-lint` make this contract checkable before an answer is delivered or reused.

### 8. Diff-first maintenance

`context-update` should start from the change scope whenever possible:

- `staged`: use changed files from the Git index.
- `worktree`: use unstaged tracked changes plus untracked files.
- `base <commitish>`: use changed files from `base...HEAD`.
- `since <commitish>`: use changed files from the diff.
- `files <path...>`: update only Context entries related to those files.
- No scope: fall back to full manifest and fingerprint scan.

`dev-cycle context impact --staged`, `dev-cycle context impact --worktree`, `dev-cycle context impact --base <commitish>`, `dev-cycle context impact --since <commitish>`, and `dev-cycle context impact --files <path...>` provide the deterministic changed-file to Manifest mapping for this workflow. `dev-cycle context update-plan` uses the same mutually exclusive scope options and adds dirty-source gates plus bounded update actions before any skill reads source or writes Context prose.

### 9. Validation artifacts

Context-cleared validation must be persisted, not only performed mentally.

Standard path:

```text
.dev-cycle/context/_validation/<task-id>.md
```

Each validation file should record questions, Context-only answers, citations, pass/fail status, blindspots, and validation date.

### 10. Machine-readable index and CI

`dev-cycle` can generate `.dev-cycle/context/index.json` with document paths, terms, source files, fingerprints, links, tags, status, and staleness through `dev-cycle context audit --write-index`.

The deterministic tool layer supports CI-friendly checks such as:

```text
python3 tools/context_audit.py --fail-on stale
python3 tools/context_audit.py --fail-on dead-links
python3 tools/context_audit.py --min-score B
python3 tools/release_smoke.py
```

## Implementation Status

### Completed

- Bounded Manifest selection through `dev-cycle context manifest`.
- Authoritative vs draft Context contracts in specs and skills.
- Artifact boundary config through `.dev-cycle/context/config.yaml`.
- Dirty-aware fingerprints through `dev-cycle context fingerprint` and `dev-cycle context audit`.
- Existing docs inventory and Manifest comparison through `dev-cycle context docs`.
- Long-lived `CONTEXT_PLAN.md` lifecycle states.
- Persisted validation artifact schema and audit checks.
- Machine-readable `.dev-cycle/context/index.json` generation through `dev-cycle context audit --write-index`.
- CI-friendly audit exit codes through `--fail-on` and `--min-score`.
- Diff-first maintenance scope through `dev-cycle context impact`.
- Read-only update planning through `dev-cycle context update-plan`.
- Deterministic Context skeleton and validation draft preparation through `dev-cycle context build-assist`.
- Audit health/completeness split so bounded Context coverage does not masquerade as freshness failure.
- Context support/reserved artifact classification in impact and update planning.
- Hard provenance for `context-query` through `templates/context-query-answer.md` and `dev-cycle context query-lint`.
- Installed CLI dispatcher, package templates, release smoke script, and GitHub Actions CI workflow.
- First bounded dogfood slice for this repository.

### In Progress

- Release packaging polish around local venv workflows, source distributions, and installed CLI smoke.
- Keeping root templates and packaged templates synchronized through tests.
- Aligning skill instructions with the deterministic tool layer as the CLI surface stabilizes.

### Next

- Continue dogfood slices after source changes are committed, starting with `context-artifact-contract`.
- Add a concise `CONTRIBUTING.md` or developer quickstart that points contributors to `tools/release_smoke.py`.
- Decide whether to publish a first tagged release or keep iterating as source-only package installs.

### Deferred

- Automated Context prose generation as a deterministic tool. Context synthesis should remain a skill/Agent responsibility for now.
- Deeper natural-language quality scoring for existing docs; current tools intentionally limit themselves to deterministic inventory and coverage signals.
- Stronger review expert integration through `Context-Action` outputs without letting review skills directly rewrite Context.
