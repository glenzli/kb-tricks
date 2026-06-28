# dev-cycle Knowledge Base Manifest

## Overall Approach

This repository is both the implementation of deterministic `kb` context tooling
and the source of the dev-cycle skills/templates. The KB is intentionally small:
it routes agents to the right source files, explains cross-file contracts, and
records validation questions. It is not authoritative. Source code, tests,
packaging metadata, and release outputs remain the source of truth.

## Artifact Boundary

- Config: `.agent/kb/config.yaml`
- Include: `kb_tricks/**`, `tools/**`, `templates/**`, `skills/kb-*/SKILL.md`, `skills/moe-*/SKILL.md`, `spec/**`, `tests/**`, `.github/workflows/**`, `pyproject.toml`, `MANIFEST.in`, `README.md`, `RELEASE.md`, `ROADMAP.md`
- Exclude: `dist/**`, `out/**`, `node_modules/**`, `vendor/**`, `build/**`, `*.egg-info/**`, `.venv/**`
- Release Excluded: `.agent/**`, `KB_PLAN.md`

## Existing Docs Comparison

- `README.md`: User-facing install, command list, quickstart, and release checks.
- `RELEASE.md`: Release packaging and verification procedure.
- `ROADMAP.md`: Product direction and implementation status.
- `spec/KB_SPEC.md`: Structural contract for KB artifacts.
- KB docs should add retrieval routing, source boundaries, and validation results
  that are too operational or agent-specific for the public docs.

## Ignored Targets

- `dist/`, `build/`, `*.egg-info/`, `.venv/`: Build or local environment output.
- `.agent/`: Dogfood KB artifacts. They must not define release semantics.
- Tests are included only when they define released behavior or release gates.

## Task Manifest

- [built] deterministic-toolchain
  - **ID**: `deterministic-toolchain`
  - **KB**: `.agent/kb/toolchain/deterministic-tools.md`
  - **Sources**: `kb_tricks/cli.py`, `kb_tricks/commands/__init__.py`, `kb_tricks/commands/audit.py`, `kb_tricks/commands/manifest.py`, `kb_tricks/commands/migrate_plan.py`, `kb_tricks/commands/update_plan.py`, `kb_tricks/commands/impact.py`, `kb_tricks/commands/fingerprint.py`, `kb_tricks/commands/docs.py`, `kb_tricks/commands/query_lint.py`, `kb_tricks/commands/scaffold.py`, `tools/__init__.py`, `tools/kb_audit.py`, `tools/kb_manifest.py`, `tools/kb_migrate_plan.py`, `tools/kb_update_plan.py`, `tools/kb_impact.py`, `tools/kb_fingerprint.py`, `tools/kb_docs.py`, `tools/kb_query_lint.py`, `tools/kb_scaffold.py`, `tests/test_kb_cli.py`, `tests/test_kb_docs.py`, `tests/test_kb_impact.py`, `tests/test_kb_manifest.py`, `tests/test_kb_migrate_plan.py`, `tests/test_kb_scaffold.py`, `tests/test_kb_update_plan.py`
  - **Focus**: CLI dispatch, package command implementations, source-checkout wrappers, deterministic audit/manifest/migration/update planning, dirty-aware fingerprints, docs inventory, query provenance linting, scaffold boundaries, context-doc noise control, and toolchain regression coverage.
  - **Tags**: `cli`, `audit`, `bounded`, `fingerprint`, `impact`
  - **Docs Comparison**: README lists commands, but the KB records how the tools compose and where source authority lives.
  - **Status**: `built`
  - **LastValidated**: `2026-06-28`

- [built] skill-template-contract
  - **ID**: `skill-template-contract`
  - **KB**: `.agent/kb/skills/templates-and-skills.md`
  - **Sources**: `skills/kb-build/SKILL.md`, `skills/kb-audit/SKILL.md`, `skills/kb-query/SKILL.md`, `skills/kb-update/SKILL.md`, `skills/kb-plan/SKILL.md`, `skills/kb-init/SKILL.md`, `skills/kb-changelog/SKILL.md`, `skills/kb-migrate/SKILL.md`, `skills/kb-onboard/SKILL.md`, `skills/moe-cr/SKILL.md`, `skills/moe-design/SKILL.md`, `skills/moe-postmortem/SKILL.md`, `skills/moe-test/SKILL.md`, `templates/AGENT_GUIDE.md`, `templates/KB_PLAN.md`, `templates/config.yaml`, `templates/kb-doc.md`, `templates/query-answer.md`, `templates/validation.md`, `spec/KB_SPEC.md`
  - **Focus**: Skill catalog responsibilities, target-repository agent guidance, template shape, provenance requirements, and the boundary between generated KB prose and deterministic CLI checks.
  - **Tags**: `skills`, `templates`, `spec`, `provenance`
  - **Docs Comparison**: spec/KB_SPEC.md defines structure; KB adds agent routing and practical maintenance guidance.
  - **Status**: `built`
  - **LastValidated**: `2026-06-28`

- [built] release-packaging
  - **ID**: `release-packaging`
  - **KB**: `.agent/kb/release/packaging.md`
  - **Sources**: `pyproject.toml`, `MANIFEST.in`, `kb_tricks/templates/AGENT_GUIDE.md`, `kb_tricks/templates/KB_PLAN.md`, `kb_tricks/templates/config.yaml`, `kb_tricks/templates/kb-doc.md`, `kb_tricks/templates/query-answer.md`, `kb_tricks/templates/validation.md`, `tools/release_smoke.py`, `tools/release_rehearsal.py`, `tests/test_packaging.py`, `.github/workflows/ci.yml`, `README.md`, `RELEASE.md`, `ROADMAP.md`
  - **Focus**: Package data, installed CLI smoke testing, full release rehearsal, CI release checks, and which dogfood artifacts stay out of release semantics.
  - **Tags**: `release`, `packaging`, `ci`, `templates`
  - **Docs Comparison**: README and RELEASE document commands; KB explains why package resources, source templates, and CI smoke checks must move together.
  - **Status**: `built`
  - **LastValidated**: `2026-06-28`
