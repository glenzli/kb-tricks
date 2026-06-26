# Validation: skill-template-contract

- **KB**: `.agent/kb/skills/templates-and-skills.md`
- **Source Mode**: `clean`
- **Validated At**: `2026-06-26`

## Questions

### Q1 Responsibility Split

- **Question**: What should skills own, and what should deterministic CLI tools own?
- **KB-only Answer**: Skills own reading, synthesis, and prose quality. CLI tools own deterministic validation, path boundaries, link checks, freshness, impact, selection, and release smoke verification.
- **Citations**: `.agent/kb/skills/templates-and-skills.md`
- **Result**: pass

### Q2 Provenance

- **Question**: What provenance must query answers expose?
- **KB-only Answer**: Query answers must distinguish KB, source fallback, existing docs, and inference.
- **Citations**: `.agent/kb/skills/templates-and-skills.md`
- **Result**: pass

## Blindspots

- This validation does not inspect every MoE skill.
