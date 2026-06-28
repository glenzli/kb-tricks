# Validation: release-packaging

- **KB**: `.agent/kb/release/packaging.md`
- **Source Mode**: `clean`
- **Validated At**: `2026-06-28`

## Questions

### Q1 Installed CLI

- **Question**: Which files make installed `kb scaffold` work without a source checkout?
- **KB-only Answer**: `pyproject.toml` packages `kb_tricks/templates/*`, `MANIFEST.in` keeps those files in source distributions, and packaged copies live under `kb_tricks/templates/`.
- **Citations**: `.agent/kb/release/packaging.md`
- **Result**: pass

### Q2 CI Gate

- **Question**: What does CI verify for release smoke?
- **KB-only Answer**: CI runs source checkout smoke, installs the package, then runs installed CLI smoke.
- **Citations**: `.agent/kb/release/packaging.md`
- **Result**: pass

### Q3 Public CLI Surface

- **Question**: Where should installed users discover compact JSON entry points?
- **KB-only Answer**: `README.md` is the public command surface and shows compact `--summary-json` entry points for `docs` and `audit`, plus `migrate-plan` dry-run/write examples.
- **Citations**: `.agent/kb/release/packaging.md`
- **Result**: pass

### Q4 Package Boundary

- **Question**: How does release rehearsal treat `migrate-plan`?
- **KB-only Answer**: The `migrate-plan` command module is required in wheels, while the source-checkout wrapper is kept in sdists and forbidden from wheels.
- **Citations**: `.agent/kb/release/packaging.md`
- **Result**: pass

## Blindspots

- This validation does not publish or install from a built wheel artifact.
