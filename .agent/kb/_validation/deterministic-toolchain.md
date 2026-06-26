# Validation: deterministic-toolchain

- **KB**: `.agent/kb/toolchain/deterministic-tools.md`
- **Source Mode**: `clean`
- **Validated At**: `2026-06-26`

## Questions

### Q1 Bounded Execution

- **Question**: Which tool decides a small manifest slice, and what options constrain it?
- **KB-only Answer**: `kb manifest` selects manifest tasks and supports `--slice`, `--only`, and status filters.
- **Citations**: `.agent/kb/toolchain/deterministic-tools.md`
- **Result**: pass

### Q2 Dirty Source Gate

- **Question**: Which tool blocks updates when impacted sources are dirty or untracked?
- **KB-only Answer**: `kb update-plan` starts from impact data and blocks dirty or untracked sources unless draft or allow flags are used.
- **Citations**: `.agent/kb/toolchain/deterministic-tools.md`
- **Result**: pass

## Blindspots

- The validation confirms routing knowledge, not implementation correctness.
