# kb-tricks Artifact Spec

This document defines the stable artifacts used by `kb-tricks`. Skills may synthesize and maintain the KB, but deterministic tools should validate only the structures described here.

## Authority Model

The KB is not the repository authority. Source code, configuration, tests, release artifacts, and maintained human-facing docs remain authoritative. KB artifacts provide routing, context compression, cross-module explanation, and uncertainty reporting.

## Paths

| Path | Purpose |
|---|---|
| `.agent/kb/config.yaml` | Project-specific artifact boundaries and existing docs hints. |
| `KB_PLAN.md` | Long-lived KB manifest and lifecycle state. |
| `.agent/kb/**/*.md` | Authoritative KB documents, excluding reserved directories. |
| `.agent/kb/_draft/` | Non-authoritative draft KB based on dirty or exploratory work. |
| `.agent/kb/_impact/` | Non-authoritative impact notes and dry-run outputs. |
| `.agent/kb/_validation/` | Persisted context-cleared validation artifacts. |
| `.agent/kb/GLOSSARY.md` | Term routing table. |
| `.agent/kb/index.json` | Machine-readable index generated from manifest, KB docs, glossary, and links. |

Reserved directories under `.agent/kb/` are `_draft/`, `_impact/`, and `_validation/`. Documents in reserved directories must not be treated as authoritative KB.

## Scaffolding

`tools/kb_scaffold.py` installs the starter artifacts defined by this spec into a target repository:

```text
python3 tools/kb_scaffold.py --repo /path/to/project --dry-run
python3 tools/kb_scaffold.py --repo /path/to/project
python3 tools/kb_scaffold.py --repo /path/to/project --force
```

It creates `.agent/kb/config.yaml`, `KB_PLAN.md`, and reserved directories for `_draft/`, `_impact/`, and `_validation/`. It does not generate KB prose, run repository analysis, or overwrite existing scaffold files unless `--force` is supplied. `--dry-run` prints the planned writes without touching the target repository.

## `.agent/kb/config.yaml`

Minimal schema:

```yaml
include:
  - src/**
exclude:
  - dist/**
  - node_modules/**
releaseExcluded:
  - docs/dev/**
  - .agent/**
docs:
  existing:
    - README.md
    - docs/**
```

Rules:

- `include` defines candidate source/doc paths for KB planning.
- `exclude` always removes paths from KB planning.
- `releaseExcluded` may be useful for Agent context but must not be described as release-facing truth.
- `docs.existing` tells planning/query flows where human-facing docs already exist.
- Missing config is allowed, but `kb-plan` should propose one before creating detailed manifest entries.

## Existing Docs Inventory

`tools/kb_docs.py` is the deterministic helper for existing human-facing docs:

```text
python3 tools/kb_docs.py --repo /path/to/project --json
python3 tools/kb_docs.py --repo /path/to/project --check-manifest
```

It reads `.agent/kb/config.yaml` `docs.existing`, expands matching Markdown documents, extracts headings, content hashes, local links, unmatched patterns, Manifest `Docs Comparison` coverage, and low-cost duplicate hints. It does not decide whether prose is sufficient; that remains a skill-layer judgment. `--check-manifest` exits `1` when active Manifest tasks lack `Docs Comparison`, and exits `2` when the requested check cannot run.

## `KB_PLAN.md` Manifest

Manifest entries use a status marker and stable task ID:

```markdown
- [planned] release-packaging
  - **ID**: `release-packaging`
  - **KB**: `.agent/kb/release/packaging.md`
  - **Sources**: `src/cli/release.ts`, `src/release/config.ts`
  - **Focus**: Release packaging boundaries and artifact exclusion rules.
  - **Tags**: `release`, `packaging`
  - **Status**: `planned`
  - **LastValidated**: `2026-06-26`
```

Allowed states:

- `planned`: should be built.
- `built`: authoritative KB exists and validation passed.
- `stale`: source changed and KB needs refresh.
- `orphaned`: referenced source no longer exists.
- `merged-into-docs`: content belongs in existing human-facing docs instead of standalone KB.
- `deprecated`: topic is intentionally retired.

Compatibility:

- Old `[ ]` entries are interpreted as `planned`.
- Old `[x]` entries are interpreted as `built`.

### Manifest Selection

`tools/kb_manifest.py` is the deterministic selector for bounded Manifest execution:

```text
python3 tools/kb_manifest.py --repo /path/to/project --slice 1 --json
python3 tools/kb_manifest.py --repo /path/to/project --slice 2
python3 tools/kb_manifest.py --repo /path/to/project --only release-packaging
python3 tools/kb_manifest.py --repo /path/to/project --status planned --json
python3 tools/kb_manifest.py --repo /path/to/project --status any --slice 10
```

Default selection is `status planned, stale` with `slice 1`. `--only` may match task ID, task name, tag, KB path, or source path. The tool is read-only: it never reads source content, writes KB prose, mutates `KB_PLAN.md`, or updates status. Skills must treat the JSON `selected` array as the maximum task set they are allowed to process in the current bounded turn.

### Impact Mapping

`tools/kb_impact.py` is the deterministic helper for diff-first maintenance:

```text
kb impact --repo /path/to/project --staged --json
kb impact --repo /path/to/project --worktree --json
kb impact --repo /path/to/project --base main --json
kb impact --repo /path/to/project --since HEAD~1 --json
kb impact --repo /path/to/project --files src/cli/release.ts --json
python3 tools/kb_impact.py --repo /path/to/project --files src/cli/release.ts --json
```

Exactly one scope option must be provided: `--staged`, `--worktree`, `--base`, `--since`, or `--files`. JSON output includes top-level `scopeMode` plus a `scope` object so automation can distinguish index changes, dirty worktree changes, branch-base changes, explicit commitish diffs, and manually supplied file lists.

It maps changed files to Manifest tasks through `Sources`, KB paths, and KB frontmatter fingerprints. It also reports existing docs changes from `docs.existing`, special artifact changes such as `KB_PLAN.md` and `.agent/kb/config.yaml`, unmatched files, and a bounded `selectedTasks` slice. It does not read changed file contents or rewrite KB prose.

### Update Planning

`tools/kb_update_plan.py` is the deterministic dry-run planner for `kb-update`:

```text
kb update-plan --repo /path/to/project --staged --json
kb update-plan --repo /path/to/project --worktree --draft --json
kb update-plan --repo /path/to/project --base main --slice 2 --json
python3 tools/kb_update_plan.py --repo /path/to/project --since HEAD~1 --json
```

It reuses the same mutually exclusive scope options as `kb impact`, then adds dirty-source gates and bounded update actions. JSON output includes `actions`, `blocked`, `docsActions`, `newKbCandidates`, `specialActions`, `releaseExcludedChanges`, and `policy`. It is read-only: it does not read changed file contents, rewrite KB prose, mutate `KB_PLAN.md`, or refresh fingerprints.

### Query Answer Schema

`kb-query` answers must be provenance-first Markdown documents. Every factual line in the answer section must use one or more source markers:

- `[KB]`
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

- KB: `.agent/kb/...`
- 源码: `src/file.ts:42`
- 现有 docs: `docs/file.md`
- 推断: 无

## 知识库状态 (KB Status)

- ✅ 新鲜 / ⚠️ 部分过期 / ⚠️ dirty 或 draft / ❌ 未覆盖
```

`templates/query-answer.md` provides the starter structure. `tools/kb_query_lint.py` checks required sections, factual source markers, inference isolation, and citation coverage:

```text
kb query-lint answer.md
kb query-lint --json answer.md
python3 tools/kb_query_lint.py templates/query-answer.md
```

Exit code `0` means the answer contract passed. Exit code `1` means the linter found provenance or structure failures. Exit code `2` means the linter could not read the requested input.

## KB Frontmatter

Every authoritative KB document must start with YAML-like frontmatter:

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

`tools/kb_fingerprint.py` is the deterministic helper for this section:

```text
python3 tools/kb_fingerprint.py src/cli/release.ts
python3 tools/kb_fingerprint.py --json src/cli/release.ts
python3 tools/kb_fingerprint.py --allow-dirty src/cli/release.ts
python3 tools/kb_fingerprint.py --check .agent/kb/release/packaging.md
```

Exit code `0` means generation/check passed. Exit code `1` means a policy or fingerprint check failed, such as dirty source without override or stale recorded metadata. Exit code `2` means the tool could not run the requested operation, such as a missing source file.

## Validation Artifacts

Each built manifest task should have:

```text
.agent/kb/_validation/<task-id>.md
```

Required sections:

```markdown
# Validation: <task-id>

- **KB**: `.agent/kb/...`
- **Source Mode**: `clean`
- **Validated At**: `YYYY-MM-DD`

## Questions
### Q1 Architecture
- **Question**: ...
- **KB-only Answer**: ...
- **Citations**: ...
- **Result**: pass

### Q2 Boundary
- **Question**: ...
- **KB-only Answer**: ...
- **Citations**: ...
- **Result**: pass

## Blindspots
- None
```

## Glossary

`GLOSSARY.md` should contain a Markdown table:

```markdown
| Term / Keyword | Synonyms | Target KB Document Link |
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

`tools/kb_audit.py --write-index .agent/kb/index.json` may generate this file from existing artifacts and enrich it with `tools/kb_docs.py` inventory data. Skills may read it as a fast routing index, but should fall back to source KB/docs when the index is missing or stale.

## Audit Exit Semantics

Deterministic audit tools should support:

```text
--fail-on stale
--fail-on dead-links
--fail-on missing-manifest
--fail-on missing-config
--fail-on dirty
--fail-on draft
--fail-on missing-validation
--min-score B
```

Exit code `0` means policy passed. Exit code `1` means the audit completed but policy failed. Exit code `2` means the audit itself could not run.
