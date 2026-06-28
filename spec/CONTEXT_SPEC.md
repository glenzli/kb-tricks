# dev-cycle Context Artifact Spec

This document defines the stable Context artifacts used by `dev-cycle`. Skills may synthesize and maintain the Context, but deterministic tools should validate only the structures described here.

## Authority Model

The Context is not the repository authority. Source code, configuration, tests, release artifacts, and maintained human-facing docs remain authoritative. Context artifacts provide routing, context compression, cross-module explanation, and uncertainty reporting.

## Paths

| Path | Purpose |
|---|---|
| `.dev-cycle/context/config.yaml` | Project-specific artifact boundaries and existing docs hints. |
| `.dev-cycle/context/AGENT_GUIDE.md` | Copyable AI-agent operating instructions for this repository's Context. |
| `CONTEXT_PLAN.md` | Long-lived Context manifest and lifecycle state. |
| `.dev-cycle/context/**/*.md` | Authoritative Context documents, excluding reserved directories. |
| `.dev-cycle/context/_draft/` | Non-authoritative draft Context based on dirty or exploratory work. |
| `.dev-cycle/context/_impact/` | Non-authoritative impact notes and dry-run outputs. |
| `.dev-cycle/context/_validation/` | Persisted context-cleared validation artifacts. |
| `.dev-cycle/context/GLOSSARY.md` | Term routing table. |
| `.dev-cycle/context/index.json` | Machine-readable index generated from manifest, Context docs, glossary, and links. |

Reserved directories under `.dev-cycle/context/` are `_draft/`, `_impact/`, and `_validation/`. Documents in reserved directories must not be treated as authoritative Context. Auxiliary files such as `AGENT_GUIDE.md`, `GLOSSARY.md`, `CHANGELOG.md`, and `ONBOARDING.md` support routing or agent behavior and do not need Manifest entries.

Audit/index tooling classifies Context Markdown as `kind: authoritative`, `kind: support`, or `kind: reserved`. Only authoritative documents participate in Manifest coverage, stale/dirty/orphaned health scoring, and untracked-Context checks.

## Scaffolding

`tools/context_scaffold.py` installs the starter artifacts defined by this spec into a target repository:

```text
python3 tools/context_scaffold.py --repo /path/to/project --dry-run
python3 tools/context_scaffold.py --repo /path/to/project
python3 tools/context_scaffold.py --repo /path/to/project --force
```

It creates `.dev-cycle/context/config.yaml`, `.dev-cycle/context/AGENT_GUIDE.md`, `CONTEXT_PLAN.md`, and reserved directories for `_draft/`, `_impact/`, and `_validation/`. It does not generate Context prose, run repository analysis, or overwrite existing scaffold files unless `--force` is supplied. `--dry-run` prints the planned writes without touching the target repository.

## `.dev-cycle/context/config.yaml`

Minimal schema:

```yaml
include:
  - src/**
exclude:
  - dist/**
  - node_modules/**
releaseExcluded:
  - docs/dev/**
  - .dev-cycle/**
docs:
  existing:
    - README.md
    - docs/**
```

Rules:

- `include` defines candidate source/doc paths for Context planning.
- `exclude` always removes paths from Context planning.
- `releaseExcluded` may be useful for Agent context but must not be described as release-facing truth.
- `docs.existing` tells planning/query flows where human-facing docs already exist.
- Missing config is allowed, but `context-plan` should propose one before creating detailed manifest entries.

## Existing Docs Inventory

`tools/context_docs.py` is the deterministic helper for existing human-facing docs:

```text
python3 tools/context_docs.py --repo /path/to/project --json
python3 tools/context_docs.py --repo /path/to/project --summary-json
python3 tools/context_docs.py --repo /path/to/project --full-json
python3 tools/context_docs.py --repo /path/to/project --check-manifest
python3 tools/context_docs.py --repo /path/to/project --check-links
python3 tools/context_docs.py --repo /path/to/project --duplicate-limit 5
```

It reads `.dev-cycle/context/config.yaml` `docs.existing`, expands matching Markdown documents, extracts headings, content hashes, local links, unmatched patterns, Manifest `Docs Comparison` coverage, dead local links, and low-cost duplicate hints. Duplicate hints include `severity` (`high`, `medium`, `low`), `score`, `sourceMentionKind` (`source`, `docs`, or `null`), and `overlapKind` (`content`, `source-reference`, or `term`). Shared title/slug plus source mentions are high severity; shared title/slug alone or source-reference overlap alone is medium; tag-only matches are low. Generic tags such as `api`, `cli`, `docs`, `preview`, `release`, and `test` are ignored when they are the only match signal.

It does not decide whether prose is sufficient; that remains a skill-layer judgment. Text output limits duplicate hints by default so dead links and missing comparison work stay visible. `--json` and `--full-json` keep the complete `duplicateHints` list; `--summary-json` emits counts, global top duplicate hints, `topDuplicateHintsByTask`, dead-link counts, and Docs Comparison status without the full heading inventory. `--check-manifest` exits `1` when active Manifest tasks lack `Docs Comparison`, `--check-links` exits `1` when existing docs contain dead local links, and both exit `2` when the requested check cannot run.

## `CONTEXT_PLAN.md` Manifest

Manifest entries use a status marker and stable task ID:

```markdown
- [planned] release-packaging
  - **ID**: `release-packaging`
  - **Context**: `.dev-cycle/context/release/packaging.md`
  - **Sources**: `src/cli/release.ts`, `src/release/config.ts`
  - **Focus**: Release packaging boundaries and artifact exclusion rules.
  - **Tags**: `release`, `packaging`
  - **Status**: `planned`
  - **LastValidated**: `2026-06-26`
```

Allowed states:

- `planned`: should be built.
- `built`: authoritative Context exists and validation passed.
- `stale`: source changed and Context needs refresh.
- `orphaned`: referenced source no longer exists.
- `merged-into-docs`: content belongs in existing human-facing docs instead of standalone Context.
- `deprecated`: topic is intentionally retired.

Legacy cleanup:

- Old `[ ]` entries are interpreted as `planned`.
- Old `[x]` entries are interpreted as `built`.
- Path-only legacy entries such as `- [x] .dev-cycle/context/core/scanner-state.md` should be migrated before relying on bounded selection IDs.

### Manifest Migration

`tools/context_migrate_plan.py` rewrites legacy path-only Manifest entries into explicit task fields:

```text
dev-cycle context migrate-plan --repo /path/to/project --dry-run
dev-cycle context migrate-plan --repo /path/to/project --write
python3 tools/context_migrate_plan.py --repo /path/to/project --json
```

The migration is deterministic. It preserves existing legacy task fields when they are already present: `ID`, `Sources`, `Focus`, `Tags`, `Docs Comparison`, `Status`, and `LastValidated`. Missing fields are inferred from the Context path and existing Context frontmatter when possible: `id`, `status`, `tags`, `title`, and fingerprint `Sources`. Unknown required values such as absent `Sources` or `Docs Comparison` are marked as `TBD`. JSON output includes `preservedFields`, `missingFields`, and `inferredFields` so callers can tell whether migration retained human-written metadata or filled gaps mechanically. `--dry-run` is the default; `--write` is required to modify `CONTEXT_PLAN.md`.

### Manifest Selection

`tools/context_manifest.py` is the deterministic selector for bounded Manifest execution:

```text
python3 tools/context_manifest.py --repo /path/to/project --slice 1 --json
python3 tools/context_manifest.py --repo /path/to/project --slice 2
python3 tools/context_manifest.py --repo /path/to/project --only release-packaging
python3 tools/context_manifest.py --repo /path/to/project --status planned --json
python3 tools/context_manifest.py --repo /path/to/project --status any --slice 10
```

Default selection is `status planned, stale` with `slice 1`. `--only` may match task ID, task name, tag, Context path, or source path. The tool is read-only: it never reads source content, writes Context prose, mutates `CONTEXT_PLAN.md`, or updates status. When legacy path-only entries are present, it emits a warning to run `dev-cycle context migrate-plan`. Skills must treat the JSON `selected` array as the maximum task set they are allowed to process in the current bounded turn.

### Build Assist

`tools/context_build_assist.py` is the deterministic skeleton helper for bounded Context builds:

```text
dev-cycle context build-assist --repo /path/to/project --slice 1
dev-cycle context build-assist --repo /path/to/project --slice 1 --write
dev-cycle context build-assist --repo /path/to/project --only release-packaging --write
dev-cycle context build-assist --repo /path/to/project --draft --write
python3 tools/context_build_assist.py --repo /path/to/project --slice 1 --json
```

It selects Manifest tasks with the same status and `--only` semantics as `context manifest`, computes dirty-aware fingerprints for listed sources, and prepares a Context document skeleton plus `_validation/<task-id>.md` skeleton. It does not synthesize Context prose, update `GLOSSARY.md`, or mark Manifest tasks `built`. Generated skeletons are `notAuthoritative: true` and validation answers are `pending` until a skill or human replaces the placeholders. `--write` is required to touch the target repository; without it the command is a dry run. Dirty or untracked source blocks formal skeleton writes unless `--draft`, `--allow-dirty`, or `--allow-untracked` is explicit.

### Impact Mapping

`tools/context_impact.py` is the deterministic helper for diff-first maintenance:

```text
dev-cycle context impact --repo /path/to/project --staged --json
dev-cycle context impact --repo /path/to/project --worktree --json
dev-cycle context impact --repo /path/to/project --base main --json
dev-cycle context impact --repo /path/to/project --since HEAD~1 --json
dev-cycle context impact --repo /path/to/project --files src/cli/release.ts --json
python3 tools/context_impact.py --repo /path/to/project --files src/cli/release.ts --json
```

Exactly one scope option must be provided: `--staged`, `--worktree`, `--base`, `--since`, or `--files`. JSON output includes top-level `scopeMode` plus a `scope` object so automation can distinguish index changes, dirty worktree changes, branch-base changes, explicit commitish diffs, and manually supplied file lists.

It maps changed files to Manifest tasks through `Sources`, Context paths, and Context frontmatter fingerprints. It also reports existing docs changes from `docs.existing`, special artifact changes such as `CONTEXT_PLAN.md` and `.dev-cycle/context/config.yaml`, `possibleContextDocs` for development-doc paths such as `docs/dev/**` when config is missing, `contextSupportChanges` for support/reserved Context artifacts such as `.dev-cycle/context/AGENT_GUIDE.md` and `_validation/**`, `setupWarnings` when config is missing, unmatched files, and a bounded `selectedTasks` slice. Context support artifacts are removed from `unmatchedFiles` so they do not look like source candidates. It does not read changed file contents or rewrite Context prose.

### Update Planning

`tools/context_update_plan.py` is the deterministic dry-run planner for `context-update`:

```text
dev-cycle context update-plan --repo /path/to/project --staged --json
dev-cycle context update-plan --repo /path/to/project --worktree --draft --json
dev-cycle context update-plan --repo /path/to/project --base main --slice 2 --json
python3 tools/context_update_plan.py --repo /path/to/project --since HEAD~1 --json
```

It reuses the same mutually exclusive scope options as `dev-cycle context impact`, then adds dirty-source gates and bounded update actions. JSON output includes `actions`, `blocked`, `docsActions`, `contextSupportActions`, `newContextCandidates`, `specialActions`, `releaseExcludedChanges`, `setupWarnings`, and `policy`. Task actions include `targetContext`; draft task actions also include `draftTarget` under `.dev-cycle/context/_draft/`. Draft new-context candidates include `draftTarget` derived from the changed file stem.

When `.dev-cycle/context/config.yaml` is missing and changed `.dev-cycle/context/**` support files would otherwise appear as unmatched source candidates, impact analysis emits a `setupWarnings` entry with code `missing-config-context-support-files`; the planner preserves those warnings and removes the files from `newContextCandidates`. Development-doc paths such as `docs/dev/**` are reported as `possibleContextDocs` instead of ordinary new context candidates until config declares whether they are existing docs, release-excluded context, or source inputs. It is read-only: it does not read changed file contents, rewrite context prose, mutate `CONTEXT_PLAN.md`, or refresh fingerprints.

### Query Answer Schema

`context-query` answers must be provenance-first Markdown documents. Every factual line in the answer section must use one or more source markers:

- `[Context]`
- `[源码回退]` or `[Source Fallback]`
- `[现有 docs]` or `[Existing Docs]`

Inference must not appear in the factual answer section. If inference is unavoidable, isolate it under `## 不确定性与推断 (Uncertainty & Inference)` and mark it with `⚠️ [推断]` or `[Inference]`.

Required sections:

```markdown
## 回答 (Answer)

<factual answer lines with source markers>

## 不确定性与推断 (Uncertainty & Inference)

无

## 引用出处 (Citations)

- Context: `.dev-cycle/context/...`
- 源码: `src/file.ts:42`
- 现有 docs: `docs/file.md`
- 推断: 无

## 知识库状态 (Context Status)

- ✅ 新鲜 / ⚠️ 部分过期 / ⚠️ dirty 或 draft / ❌ 未覆盖
```

`templates/context-query-answer.md` provides the starter structure. `tools/context_query_lint.py` checks required sections, factual source markers, inference isolation, and citation coverage:

```text
dev-cycle context query-lint answer.md
dev-cycle context query-lint --repo /path/to/project docs/answer.md
dev-cycle context query-lint --json answer.md
python3 tools/context_query_lint.py templates/context-query-answer.md
```

`--repo` resolves relative answer paths against a target repository and reports paths relative to that repository. Exit code `0` means the answer contract passed. Exit code `1` means the linter found provenance or structure failures. Exit code `2` means the linter could not read the requested input.

## Context Frontmatter

Every authoritative Context document must start with YAML-like frontmatter:

```yaml
---
id: "release-packaging"
title: "Release Packaging"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "src/cli/release.ts"
    commit: "65db3c1"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:..."
tags: ["release", "packaging"]
---
```

Required fields:

- `id`
- `title`
- `status`
- `notAuthoritative`
- `fingerprint`
- `tags`

Fingerprint rules:

- Clean tracked source: record `commit`, `tracked: true`, `worktree: clean`, and `contentHash`.
- Dirty tracked source: record `commit`, `tracked: true`, `worktree: dirty`, and `contentHash`; authoritative writes are blocked by default.
- Untracked source: record `commit: null`, `tracked: false`, `worktree: untracked`, and `contentHash`; authoritative writes are blocked by default.
- Freshness checks compare `contentHash` first, then Git commit.

`notAuthoritative: true` means query and review skills must warn before using the document for decisions.

`tools/context_fingerprint.py` is the deterministic helper for this section:

```text
python3 tools/context_fingerprint.py src/cli/release.ts
python3 tools/context_fingerprint.py --json src/cli/release.ts
python3 tools/context_fingerprint.py --allow-dirty src/cli/release.ts
python3 tools/context_fingerprint.py --check .dev-cycle/context/release/packaging.md
```

Exit code `0` means generation/check passed. Exit code `1` means a policy or fingerprint check failed, such as dirty source without override or stale recorded metadata. Exit code `2` means the tool could not run the requested operation, such as a missing source file.

## Validation Artifacts

Each built manifest task should have:

```text
.dev-cycle/context/_validation/<task-id>.md
```

Required sections:

```markdown
# Validation: <task-id>

- **Context**: `.dev-cycle/context/...`
- **Source Mode**: `clean`
- **Validated At**: `YYYY-MM-DD`

## Questions
### Q1 Architecture
- **Question**: ...
- **Context-only Answer**: ...
- **Citations**: ...
- **Result**: pass

### Q2 Boundary
- **Question**: ...
- **Context-only Answer**: ...
- **Citations**: ...
- **Result**: pass

## Blindspots
- None
```

## Glossary

`GLOSSARY.md` should contain a Markdown table:

```markdown
| Term / Keyword | Synonyms | Target Context Document Link |
|---|---|---|
| Release packaging | build artifact, publish bundle | [packaging.md](./release/packaging.md) |
```

Draft-only terms should not be added to the authoritative glossary unless explicitly promoted.

## `index.json`

The generated index should be deterministic JSON:

```json
{
  "schemaVersion": 1,
  "generatedAt": "2026-06-26T00:00:00Z",
  "documents": [],
  "existingDocs": [],
  "docsComparison": {},
  "docsDuplicateHints": [],
  "manifest": [],
  "terms": [],
  "links": [],
  "summary": {}
}
```

Document records include `kind`, `support`, `reserved`, freshness fields, fingerprint metadata, and link checks. Existing-docs duplicate hints keep their severity fields. `tools/context_audit.py --write-index .dev-cycle/context/index.json` may generate this file from existing artifacts and enrich it with `tools/context_docs.py` inventory data. Skills may read it as a fast routing index, but should fall back to source Context/docs when the index is missing or stale.

## Audit Exit Semantics

Deterministic audit tools should support:

```text
--fail-on stale
--fail-on dead-links
--fail-on missing-manifest
--fail-on missing-config
--fail-on dirty
--fail-on draft
--fail-on missing
--fail-on missing-validation
--fail-on failed-validation
--fail-on boundary
--fail-on orphaned
--fail-on untracked
--fail-on not-authoritative
--summary-json
--full-json
--min-score B
```

Missing `CONTEXT_PLAN.md` or `.dev-cycle/context/config.yaml` must affect the audit grade even when the caller does not pass `--fail-on`: the `setup` metric is `0` until both files exist. Policy exit codes remain explicit through `--fail-on` and `--min-score`.

`--json` and `--full-json` emit the full index-shaped payload plus audit-only fields. `--summary-json` emits compact counts, top issues, support document links, and `releaseExcludedUses`. A release-excluded reference is reported with severity `context` and is not a health concern by itself; the review question is whether the prose wrongly treats that path as release authority.

Exit code `0` means policy passed. Exit code `1` means the audit completed but policy failed. Exit code `2` means the audit itself could not run.
