# dev-cycle Skill Catalog

`dev-cycle` skills are grouped by development-cycle role. Keep one skill per
directory so they remain easy to copy, install, and reference from target
repositories.

## Context Layer

The context layer builds and maintains repository understanding. These skills
own KB planning, construction, maintenance, querying, and health checks.

| Skill | Purpose |
|---|---|
| `kb-plan` | Plan long-lived KB manifest entries and artifact boundaries. |
| `kb-build` | Build bounded KB slices from clean source. |
| `kb-update` | Refresh KB from diff-first impact scopes. |
| `kb-query` | Answer with KB/docs/source provenance. |
| `kb-audit` | Check KB health with metadata-first scans. |

## Review Layer

The review layer checks proposed or actual work. Review skills run fixed
dimension checks internally, while public names describe the development-cycle
action.

| Skill | Purpose |
|---|---|
| `review-design` | Review architecture proposals before implementation. |
| `review-code` | Review code diffs with dimension-specific checks. |
| `review-test` | Review tests and compare coverage against KB contracts. |

Review skills must follow [`REVIEW_PROTOCOL.md`](./REVIEW_PROTOCOL.md).

## Evolution Layer

The evolution layer handles project changes that extend beyond one local diff.
These skills may use KB as context, but source, tests, release artifacts, and
maintained docs remain authoritative.

| Skill | Purpose |
|---|---|
| `cycle-migrate` | Plan large architectural or platform migrations. |
| `cycle-postmortem` | Analyze incidents and produce action-oriented postmortems. |
| `cycle-onboard` | Generate onboarding paths from fresh project context. |
| `cycle-changelog` | Summarize KB/context changes after updates. |

## Recipes

Recipes orchestrate other skills and should stay thin.

| Skill | Purpose |
|---|---|
| `cycle-init` | Run scaffold, planning, user confirmation, and first bounded build slice. |
