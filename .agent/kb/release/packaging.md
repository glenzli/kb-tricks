---
id: "release-packaging"
title: "Release Packaging"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "pyproject.toml"
    commit: "deffe8781f912ab49c08903da4bfffb1e3ba6555"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:23fd65b3922618ab85ec41ab95423632f2543b687a1adc7a4cc7eed5845e49f7"
  - file: "MANIFEST.in"
    commit: "deffe8781f912ab49c08903da4bfffb1e3ba6555"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:71b939f80c2f079c4be90f98545a611c941ea097b6eda1756af512c7e4130e42"
  - file: "kb_tricks/templates/KB_PLAN.md"
    commit: "91c9b39bf8d8b1052632e9e139c0b3635cae1bcc"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:183ec6fceeec7fdc3c6dd761dd0b9048c751a5ae2bc3ffc14699449894951e6f"
  - file: "kb_tricks/templates/config.yaml"
    commit: "91c9b39bf8d8b1052632e9e139c0b3635cae1bcc"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:6456dbb37bb7aa17bbdef213c741b584f5c4dc2b5fa266bf3dd46a914b4234c7"
  - file: "kb_tricks/templates/kb-doc.md"
    commit: "91c9b39bf8d8b1052632e9e139c0b3635cae1bcc"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:be097b1994431ae793e212eef9c38f4bdd7718f6ce3b72175aa7bb5191d20765"
  - file: "kb_tricks/templates/query-answer.md"
    commit: "91c9b39bf8d8b1052632e9e139c0b3635cae1bcc"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:70c6e1cf1a01dec841d491bef6c07ed4fb30c660b9f108d9a4b2b566e959c7c3"
  - file: "kb_tricks/templates/validation.md"
    commit: "91c9b39bf8d8b1052632e9e139c0b3635cae1bcc"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:3f11169b1c453b30b559d7b3c826bca12c25a981b883de65f66f50d2f8252533"
  - file: "tools/release_smoke.py"
    commit: "95653ed4add23dcd17e68fd77148b694f0144c47"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:2a3ce16cd0ca1e923c6ef13b8443c8ab46996b6baa113f2bde608d7c02e14727"
  - file: "tests/test_packaging.py"
    commit: "a5b8df6a7a4061ae42d09146264884edbaa09d4c"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:a89a91e5997caf0053799683f5ded073919cdf71b8f14d148634dffd56ae87ce"
  - file: ".github/workflows/ci.yml"
    commit: "95653ed4add23dcd17e68fd77148b694f0144c47"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:6a42e1b9c8a575d8a67080adb5743355c02678380dca6af0ed77c42fef112c65"
  - file: "README.md"
    commit: "deffe8781f912ab49c08903da4bfffb1e3ba6555"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:a9039d42138230425cab3b2f7f3ed0c5e13afe4dcdc3d692563766ac68251e1b"
  - file: "RELEASE.md"
    commit: "a5b8df6a7a4061ae42d09146264884edbaa09d4c"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:ce34440199bce3e45ae2ca6abd5f8e91609d9cc255b3c0721993c47b686b29da"
  - file: "ROADMAP.md"
    commit: "deffe8781f912ab49c08903da4bfffb1e3ba6555"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:f116b1a96f40c871843cc1cc12e3a06d6a1409acf410f08efb1cc5197d915af4"
tags: ["release", "packaging", "ci", "templates"]
---

# Release Packaging

## Role

Release packaging turns the deterministic tools into an installable `kb` CLI.
It also packages scaffold templates so `kb scaffold` works outside a source
checkout.

## Contracts

- [pyproject.toml](../../../pyproject.toml) defines the `kb` console script and
  includes `kb_tricks.commands` and `kb_tricks/templates/*` in the installed
  package.
- [MANIFEST.in](../../../MANIFEST.in) keeps templates, specs, skills, and
  source-checkout wrappers in source distributions.
- [release_smoke.py](../../../tools/release_smoke.py) runs the shared release
  smoke sequence for source checkouts and installed CLIs.
- Manual scaffold smoke commands must create the target directory first because
  `kb scaffold --repo` targets an existing repository.
- [ci.yml](../../../.github/workflows/ci.yml) verifies source smoke, package
  installation, and installed CLI smoke.
- [test_packaging.py](../../../tests/test_packaging.py) checks package template
  availability, scaffold fallback behavior, and release smoke command coverage.

## Release Boundary

`.agent/**` and `KB_PLAN.md` are dogfood artifacts, not release authority. They
can explain packaging decisions, but changing them must not be treated as a
release behavior change unless paired with source, test, or packaging metadata
updates.

## SSOT Links

- User quickstart: [README.md](../../../README.md)
- Release checklist: [RELEASE.md](../../../RELEASE.md)
- Roadmap status: [ROADMAP.md](../../../ROADMAP.md)

## Blindspots

- The project has a local `.venv`, but release smoke should not rely on it in CI.
- Setuptools 82 warns that `project.license` as a TOML table is deprecated and
  must move to current license metadata before 2027-02-18.
- The first real tag/release still needs a decision on versioning and publish
  destination.
