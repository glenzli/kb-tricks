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
  "manifest": [],
  "terms": [],
  "links": [],
  "summary": {}
}
```

`tools/kb_audit.py --write-index .agent/kb/index.json` may generate this file from existing artifacts. Skills may read it as a fast routing index, but should fall back to source KB/docs when the index is missing or stale.

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
