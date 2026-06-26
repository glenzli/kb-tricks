# Validation: release-packaging

- **KB**: `.agent/kb/release/packaging.md`
- **Source Mode**: `clean`
- **Validated At**: `2026-06-26`

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

## Blindspots

- This validation does not publish or install from a built wheel artifact.
