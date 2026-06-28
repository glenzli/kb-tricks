# Validation: deterministic-toolchain

- **KB**: `.agent/kb/toolchain/deterministic-tools.md`
- **Source Mode**: `clean`
- **Validated At**: `2026-06-28`

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

### Q3 Reporting Shape

- **Question**: Which tools now expose compact summary JSON, and what kind of data is kept out of that compact view?
- **KB-only Answer**: `kb docs` and `kb audit` expose `--summary-json`; the compact view keeps counts and top issues, while full heading inventories and complete payload details stay in `--json`/`--full-json`.
- **Citations**: `.agent/kb/toolchain/deterministic-tools.md`
- **Result**: pass

### Q4 Legacy Migration

- **Question**: Which command migrates legacy path-only Manifest entries, and does it write by default?
- **KB-only Answer**: `kb migrate-plan` converts legacy path-only Manifest entries into explicit task fields. It previews by default and only writes when `--write` is supplied.
- **Citations**: `.agent/kb/toolchain/deterministic-tools.md`
- **Result**: pass

## Blindspots

- The validation confirms routing knowledge, not implementation correctness.
