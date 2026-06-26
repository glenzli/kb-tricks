---
id: "skill-template-contract"
title: "Skill Template Contract"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "kb-build/SKILL.md"
    commit: "7dce569328f5dff8a073cc9dd15ba2baba6e40b8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:2ff76531e4659305de1fbd73db5664f1948f645f426fd054ddca9c99ea721b1f"
  - file: "kb-audit/SKILL.md"
    commit: "63ec70532cbc23787518ad3d92896fe3de00e4df"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:99d35511886a8cdbd391297ea785ba034c36b4e327bc30452e228f73f4af1da9"
  - file: "kb-query/SKILL.md"
    commit: "e33e8ed2a2bd4b04de971df5d19816abf869e827"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:d97bd24382492a32a29fe576dc9abefb2975ce6012720f7b57257a42dbdd3c70"
  - file: "kb-update/SKILL.md"
    commit: "704c01f14d1650d59d24ef01a7e3a68ff2be9e95"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:743dda6ab8723f1ba08f1a1c82ee8cd2f33125ae3110a6bf19d446f4a0d5db4a"
  - file: "kb-plan/SKILL.md"
    commit: "63ec70532cbc23787518ad3d92896fe3de00e4df"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:899189353ff76d30893891d7da379dc53321e97b752581a9a5162f387a79cba5"
  - file: "kb-init/SKILL.md"
    commit: "2d2ced5a833a4d57d84ee0452da7c3c98cbe7ace"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:121bd94dde9d71d98b0133bdec186dd91f7af8f4789de6ee1e144536ced3fa6d"
  - file: "templates/KB_PLAN.md"
    commit: "6e5713c139884c1233ac88a64c4305c3dd3f7ee0"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:183ec6fceeec7fdc3c6dd761dd0b9048c751a5ae2bc3ffc14699449894951e6f"
  - file: "templates/config.yaml"
    commit: "6e5713c139884c1233ac88a64c4305c3dd3f7ee0"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:6456dbb37bb7aa17bbdef213c741b584f5c4dc2b5fa266bf3dd46a914b4234c7"
  - file: "templates/kb-doc.md"
    commit: "6e5713c139884c1233ac88a64c4305c3dd3f7ee0"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:be097b1994431ae793e212eef9c38f4bdd7718f6ce3b72175aa7bb5191d20765"
  - file: "templates/query-answer.md"
    commit: "e33e8ed2a2bd4b04de971df5d19816abf869e827"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:70c6e1cf1a01dec841d491bef6c07ed4fb30c660b9f108d9a4b2b566e959c7c3"
  - file: "templates/validation.md"
    commit: "6e5713c139884c1233ac88a64c4305c3dd3f7ee0"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:3f11169b1c453b30b559d7b3c826bca12c25a981b883de65f66f50d2f8252533"
  - file: "spec/KB_SPEC.md"
    commit: "06623c6dc07f1e33e041f8138b36d35328bafd9e"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:0b2396d68a0f7ae2e4ce9ee2e0d666b6ae2f22c47be2ec9db50700f0b655f16e"
tags: ["skills", "templates", "spec", "provenance"]
---

# Skill Template Contract

## Role

The `kb-*` skills define agent workflows. The templates define the files those
workflows should create. The deterministic CLI validates the resulting
artifacts but does not replace skill judgment.

## Contracts

- Skills should use bounded execution and select small slices from the manifest.
- Generated KB documents should carry dirty-aware fingerprints in frontmatter.
- Query answers must distinguish KB, source fallback, existing docs, and
  inference.
- Validation questions should be written to `.agent/kb/_validation/` so audit
  can check whether built tasks were actually self-tested.
- Existing docs comparison is required for active manifest tasks so KB does not
  duplicate README, release, or spec content.

## Boundary Between Skill and CLI

Skills own reading, synthesis, and prose quality. CLI tools own deterministic
checks: path boundaries, link checks, freshness, impact, selection, and release
smoke verification. This split keeps the package usable in normal repositories:
users can install the CLI, while skills can be copied or referenced separately.

## SSOT Links

- Build workflow: [kb-build/SKILL.md](../../../kb-build/SKILL.md)
- Audit workflow: [kb-audit/SKILL.md](../../../kb-audit/SKILL.md)
- Query workflow: [kb-query/SKILL.md](../../../kb-query/SKILL.md)
- Artifact spec: [KB_SPEC.md](../../../spec/KB_SPEC.md)

## Blindspots

- The scaffolded templates are intentionally generic and need per-repository
  boundary tuning.
- Template duplication between `templates/` and `kb_tricks/templates/` needs
  tests to keep source and package copies in sync.
