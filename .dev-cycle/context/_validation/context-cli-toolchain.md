# Validation: context-cli-toolchain

- **Context**: `.dev-cycle/context/context/cli-toolchain.md`
- **Source Mode**: `clean`
- **Validated At**: `2026-06-29`

## Questions

### Q1 Architecture

- **Question**: Which module owns installed command dispatch, and which modules own context command behavior?
- **Context-only Answer**: Installed command dispatch is owned by `dev_cycle.cli`. Each `dev_cycle.context.*` command module owns its own argument parsing, data model, output, and exit-code policy. Source-checkout wrappers in `tools/context_*.py` delegate to those modules.
- **Citations**: `.dev-cycle/context/context/cli-toolchain.md`
- **Result**: pass

### Q2 Boundary

- **Question**: Which deterministic commands are allowed to write repository files?
- **Context-only Answer**: `scaffold` writes starter artifacts unless run with `--dry-run`; `migrate-plan` writes only with `--write`; `audit` writes `index.json` only with `--write-index`. The other listed helpers are read-only except for stdout/stderr.
- **Citations**: `.dev-cycle/context/context/cli-toolchain.md`
- **Result**: pass

### Q3 Maintenance Flow

- **Question**: How should an incremental Context update start from a diff instead of scanning the whole repository?
- **Context-only Answer**: Use `context impact` to map changed files to manifest tasks, then let `context update-plan` apply source-state gates and emit allowed, blocked, or draft actions.
- **Citations**: `.dev-cycle/context/context/cli-toolchain.md`
- **Result**: pass

## Blindspots

- Exact JSON fields and failure text still require source or tests.
