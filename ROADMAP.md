# kb-tricks Next Design Plan

## Goal

Move `kb-tricks` from a set of KB-generating skills into a controllable, auditable, incrementally maintainable AI development context system.

The knowledge base is not the source of truth. Source code, configuration, tests, release artifacts, and maintained human-facing docs remain authoritative. The KB exists to route questions, compress context, explain cross-module contracts, and expose uncertainty.

## Architecture

`kb-tricks` should evolve in three layers:

| Layer | Responsibility |
|---|---|
| Skill Layer | Planning, reading, synthesis, review, and maintenance performed by Agent skills. |
| Spec Layer | Stable artifacts and schemas: `.agent/kb/config.yaml`, `KB_PLAN.md`, KB frontmatter, `_validation/`, and `index.json`. |
| Tool Layer | Deterministic checks such as hashing, dirty-state detection, link validation, manifest validation, and CI exit codes. |

The first implementation stage should strengthen the Skill and Spec layers without pretending that a full CLI already exists. CLI-shaped options such as `slice 2` or `dry-run` are interpreted as skill invocation contracts until a real tool layer is added.

Distribution model: deterministic tools should ship through normal releases and the stable `kb` CLI. Skills may call that released CLI directly when available; when operating inside a target repository, they may copy the released tool bundle or reference it through an external mechanism such as `vasmc`. The target repository should own KB artifacts, not the kb-tricks tool implementation.

Current repository support:

- `spec/KB_SPEC.md` defines the artifact schema.
- `templates/` provides starter artifacts for target repositories.
- `kb_tricks/templates/` packages those starter artifacts so installed `kb scaffold` does not depend on a source checkout.
- `tools/kb_scaffold.py` installs starter config, manifest, and reserved KB directories into a target repository without generating KB prose.
- `tools/kb_manifest.py` selects bounded `KB_PLAN.md` tasks by status, ID/tag/path filters, and slice size; it does not execute or generate KB prose.
- `tools/kb_docs.py` inventories existing docs from `docs.existing`, checks Manifest `Docs Comparison` coverage, and emits duplicate hints without judging prose quality.
- `tools/kb_audit.py` provides the first deterministic Tool Layer helper. It audits existing artifacts and can write `.agent/kb/index.json`; it does not generate KB prose.
- `tools/kb_fingerprint.py` generates and checks dirty-aware source fingerprints used by KB frontmatter.
- `tools/kb_impact.py` maps `--staged`, `--worktree`, `--base`, `--since`, or `--files` changes to Manifest tasks, existing docs changes, and special KB artifact changes for diff-first maintenance.
- `tools/kb_update_plan.py` turns impact results into read-only bounded update actions, blockers, existing-docs reviews, special artifact reviews, and new KB candidates.
- `tools/kb_query_lint.py` checks `kb-query` answer drafts for required sections, source type markers, inference isolation, and citation coverage.
- `kb` is the installed CLI dispatcher for the deterministic tools; source checkouts may still call `python3 tools/kb_*.py` directly.
- `kb self-check` is the release smoke boundary: it imports every released subcommand module and verifies that the installed dispatcher can reach each tool.

## Core Operating Contracts

### 1. Bounded execution by default

`kb-build` and `kb-update` must default to small slices. They should never run the whole repo unless the user explicitly requests an all-in execution mode.

Required invocation contracts:

- `slice N`: process at most `N` manifest tasks in this turn.
- `only <id|tag|path>`: process only matching manifest entries.
- `dry-run`: report what would be read and written, but do not change files.
- `plan-only`: produce or refine the plan without writing KB documents.
- `draft`: write dirty or untracked-source results into draft or impact artifacts instead of authoritative KB.
- `allow-dirty`: explicitly allow dirty-source authoritative writes while marking them `notAuthoritative: true`.
- `until-complete`: explicitly allow repeated slices until the manifest has no remaining eligible tasks.

Default: `slice 1`.

### 2. Authoritative KB vs draft KB

Formal KB documents under `.agent/kb/**/*.md` should be based on clean, tracked source files by default.

Dirty or untracked sources must not be written into authoritative KB unless the user explicitly overrides the gate. Dirty worktree workflows are still useful, but they belong in draft and impact artifacts:

- `.agent/kb/_draft/`
- `.agent/kb/_impact/`
- `.agent/kb/_validation/`

Draft artifacts must be labeled `notAuthoritative: true` and must not be treated as final KB by `kb-query`.

### 3. Artifact boundary configuration

Projects should be able to declare which files are candidates for KB ingestion and which files are excluded from release-facing semantics.

Standard config location:

```yaml
# .agent/kb/config.yaml
include:
  - src/**
  - docs/dev/**
exclude:
  - dist/**
  - out/**
  - node_modules/**
releaseExcluded:
  - docs/dev/**
  - .agent/**
docs:
  existing:
    - README.md
    - docs/**
```

`kb-plan` must read this config before planning. If it does not exist, `kb-plan` should propose one and pause for confirmation before deepening the plan.

### 4. Dirty-aware fingerprints

Commit hashes alone are insufficient because the Agent may read dirty worktree content. KB frontmatter must record both Git state and content hash.

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

### 5. `KB_PLAN.md` as long-lived manifest

`KB_PLAN.md` is not only a build checklist. It is the long-lived manifest for KB lifecycle state.

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
  - **KB**: `.agent/kb/release/packaging.md`
  - **Sources**: `src/cli/release.ts`
  - **Focus**: Release packaging boundary and artifact exclusion rules.
  - **Status**: `built`
  - **Tags**: `release`, `packaging`
  - **LastValidated**: `2026-06-26`
```

### 6. Existing docs comparison

Many repositories already have useful docs. `kb-tricks` should not automatically create a second documentation island.

Planning and audit flows should be able to answer:

- Which existing docs are already sufficient?
- What does the KB add beyond existing docs?
- Which KB sections should be merged back into human-facing docs?
- Which KB sections duplicate existing docs and add little retrieval value?
- Which existing docs conflict with code or KB?

### 7. Provenance-first querying

Every factual answer from `kb-query` must label its source type:

- `KB`
- `Source fallback`
- `Existing docs`
- `Inference`

Inference must be isolated in an uncertainty section and must not be presented as fact. `templates/query-answer.md` and `kb query-lint` make this contract checkable before an answer is delivered or reused.

### 8. Diff-first maintenance

`kb-update` should start from the change scope whenever possible:

- `staged`: use changed files from the Git index.
- `worktree`: use unstaged tracked changes plus untracked files.
- `base <commitish>`: use changed files from `base...HEAD`.
- `since <commitish>`: use changed files from the diff.
- `files <path...>`: update only KB entries related to those files.
- No scope: fall back to full manifest and fingerprint scan.

`kb impact --staged`, `kb impact --worktree`, `kb impact --base <commitish>`, `kb impact --since <commitish>`, and `kb impact --files <path...>` provide the deterministic changed-file to Manifest mapping for this workflow. `kb update-plan` uses the same mutually exclusive scope options and adds dirty-source gates plus bounded update actions before any skill reads source or writes KB prose.

### 9. Validation artifacts

Context-cleared validation must be persisted, not only performed mentally.

Standard path:

```text
.agent/kb/_validation/<task-id>.md
```

Each validation file should record questions, KB-only answers, citations, pass/fail status, blindspots, and validation date.

### 10. Machine-readable index and CI

After the core schemas stabilize, `kb-tricks` should generate `.agent/kb/index.json` with document paths, terms, source files, fingerprints, links, tags, status, and staleness.

The deterministic tool layer should support CI-friendly checks such as:

```text
python3 tools/kb_audit.py --fail-on stale
python3 tools/kb_audit.py --fail-on dead-links
python3 tools/kb_audit.py --min-score B
```

## Delivery Phases

### P0: Make it controllable and trustworthy

- Bounded execution defaults.
- Authoritative vs draft KB split.
- Artifact boundary config.
- Dirty-aware fingerprints.
- Existing docs comparison in planning.

### P1: Make it maintainable

- Long-lived `KB_PLAN.md` manifest states.
- Hard provenance in `kb-query` with lintable answer drafts.
- Diff-first `kb-update`.
- Persisted validation artifacts.
- Audit awareness of draft, dirty, stale, orphaned, merged, and deprecated states.

### P2: Make it an engineering component

- `.agent/kb/index.json`.
- Deterministic audit tool with exit codes.
- CI policies.
- Stronger MoE review integration through `KB-Action` outputs without letting review skills directly rewrite KB.
