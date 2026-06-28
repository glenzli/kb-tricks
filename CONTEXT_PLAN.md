# dev-cycle Context Manifest

## Overall Approach

This repository is a development-cycle toolkit with two different artifact types:
copyable AI skills and deterministic Python CLI helpers. Context should explain
the contracts between those layers and route future agents to the right source
files. It should not duplicate the full skill prompts, spec, tests, or README.

## Artifact Boundary

- Config: `.dev-cycle/context/config.yaml`
- Include: `dev_cycle/**`, `tools/**`, `skills/**`, `templates/**`, `spec/**`, `tests/**`, root release docs and packaging metadata.
- Exclude: VCS data, virtualenvs, caches, build outputs, vendored dependencies, and generated release artifacts.
- Release Excluded: `.dev-cycle/**`, `skills/**`, `tests/**`, `templates/**`, `spec/**`, and `tools/**` are useful to agents but are not the installed runtime package.

## Existing Docs Comparison

- `README.md`: Good product-level overview, command catalog, and layer map. Context should add cross-module routing and source ownership.
- `ROADMAP.md`: Captures design direction and gaps. Context should link to it for future priorities instead of restating the roadmap.
- `RELEASE.md`: Covers release verification. Context should only explain how release checks relate to packaging boundaries.
- `spec/CONTEXT_SPEC.md`: Authoritative artifact schema. Context should summarize how code modules implement the schema, not redefine it.
- `skills/README.md` and `skills/REVIEW_PROTOCOL.md`: Human-facing catalog and shared review rules. Context should describe skill grouping and handoff paths.

## Ignored Targets

- `.dev-cycle/context/_draft/`, `_impact/`, `_validation/`: Non-authoritative support artifacts.
- `.venv/`, `dist/`, `build/`, `*.egg-info/`, `__pycache__/`: Generated or local environment output.

## Task Manifest

- [built] context-cli-toolchain
  - **ID**: `context-cli-toolchain`
  - **Context**: `.dev-cycle/context/context/cli-toolchain.md`
  - **Sources**: `dev_cycle/cli.py`, `dev_cycle/context/build_assist.py`, `dev_cycle/context/scaffold.py`, `dev_cycle/context/manifest.py`, `dev_cycle/context/audit.py`, `dev_cycle/context/docs.py`, `dev_cycle/context/fingerprint.py`, `dev_cycle/context/impact.py`, `dev_cycle/context/update_plan.py`, `dev_cycle/context/query_lint.py`, `dev_cycle/context/migrate_plan.py`, `tools/context_build_assist.py`, `tools/context_scaffold.py`, `tools/context_manifest.py`, `tools/context_audit.py`
  - **Focus**: Installed CLI dispatch, deterministic helper boundaries, read/write behavior, and dogfood-safe execution order.
  - **Tags**: `context`, `cli`, `toolchain`, `audit`, `fingerprint`
  - **Docs Comparison**: README lists commands and examples; spec defines schemas. Context should connect commands to source modules and operating boundaries.
  - **Status**: `built`
  - **LastValidated**: `2026-06-29`

- [planned] context-artifact-contract
  - **ID**: `context-artifact-contract`
  - **Context**: `.dev-cycle/context/context/artifact-contract.md`
  - **Sources**: `AGENTS.md`, `spec/CONTEXT_SPEC.md`, `templates/config.yaml`, `templates/CONTEXT_PLAN.md`, `templates/context-doc.md`, `templates/context-validation.md`, `templates/context-query-answer.md`, `templates/AGENT_GUIDE.md`, `dev_cycle/templates/config.yaml`, `dev_cycle/templates/CONTEXT_PLAN.md`, `dev_cycle/templates/context-doc.md`, `dev_cycle/templates/context-validation.md`, `dev_cycle/templates/context-query-answer.md`, `dev_cycle/templates/AGENT_GUIDE.md`
  - **Focus**: Stable artifact schema, package template duplication, reserved directories, and provenance/validation contracts.
  - **Tags**: `context`, `spec`, `templates`, `contract`
  - **Docs Comparison**: `spec/CONTEXT_SPEC.md` is authoritative. Context should be a routing map and maintenance note for implementers.
  - **Status**: `planned`
  - **LastValidated**: ``

- [planned] skill-catalog-and-flow
  - **ID**: `skill-catalog-and-flow`
  - **Context**: `.dev-cycle/context/skills/catalog-and-flow.md`
  - **Sources**: `skills/README.md`, `skills/REVIEW_PROTOCOL.md`, `skills/context-plan/SKILL.md`, `skills/context-build/SKILL.md`, `skills/context-update/SKILL.md`, `skills/context-query/SKILL.md`, `skills/context-audit/SKILL.md`, `skills/cycle-init/SKILL.md`, `skills/cycle-migrate/SKILL.md`, `skills/cycle-onboard/SKILL.md`, `skills/cycle-changelog/SKILL.md`, `skills/cycle-postmortem/SKILL.md`, `skills/review-code/SKILL.md`, `skills/review-design/SKILL.md`, `skills/review-test/SKILL.md`
  - **Focus**: Skill grouping, lifecycle handoffs, review-layer freshness gate, and boundaries between prompt recipes and deterministic CLI.
  - **Tags**: `skills`, `context`, `review`, `cycle`
  - **Docs Comparison**: Skills are source prompts and `skills/README.md` is a catalog. Context should explain selection and composition, not restate prompt bodies.
  - **Status**: `planned`
  - **LastValidated**: ``

- [planned] release-and-packaging-boundary
  - **ID**: `release-and-packaging-boundary`
  - **Context**: `.dev-cycle/context/release/packaging-boundary.md`
  - **Sources**: `pyproject.toml`, `MANIFEST.in`, `RELEASE.md`, `tools/release_smoke.py`, `tools/release_rehearsal.py`, `README.md`
  - **Focus**: Distribution name/import package/entrypoint, sdist versus wheel boundary, license metadata, and install smoke chain.
  - **Tags**: `release`, `packaging`, `ci`
  - **Docs Comparison**: RELEASE documents commands. Context should explain why each check exists and which files affect package contents.
  - **Status**: `planned`
  - **LastValidated**: ``

- [planned] deterministic-test-coverage
  - **ID**: `deterministic-test-coverage`
  - **Context**: `.dev-cycle/context/tests/deterministic-coverage.md`
  - **Sources**: `tests/test_dev_cycle_cli.py`, `tests/test_context_build_assist.py`, `tests/test_context_scaffold.py`, `tests/test_context_manifest.py`, `tests/test_context_audit.py`, `tests/test_context_docs.py`, `tests/test_context_fingerprint.py`, `tests/test_context_impact.py`, `tests/test_context_update_plan.py`, `tests/test_context_query_lint.py`, `tests/test_context_migrate_plan.py`, `tests/test_packaging.py`, `tests/fixtures/valid-context/CONTEXT_PLAN.md`, `tests/fixtures/broken-context/CONTEXT_PLAN.md`
  - **Focus**: What behavior is covered by deterministic tests, how fixtures encode healthy/broken Context, and where release smoke extends unit coverage.
  - **Tags**: `tests`, `fixtures`, `quality`
  - **Docs Comparison**: README only names the smoke command. Context should map test files to product contracts and remaining risk.
  - **Status**: `planned`
  - **LastValidated**: ``
