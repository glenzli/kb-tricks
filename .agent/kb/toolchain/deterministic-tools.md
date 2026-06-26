---
id: "deterministic-toolchain"
title: "Deterministic Toolchain"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "kb_tricks/cli.py"
    commit: "e33e8ed2a2bd4b04de971df5d19816abf869e827"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:d6979644467e123da2532ba315f0b6256d2ec18f7c116379fd723917398226c2"
  - file: "tools/kb_audit.py"
    commit: "63ec70532cbc23787518ad3d92896fe3de00e4df"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:9086bf4f4e36a9486dd70781df3d1399d0e369a99b431d0b61ba4f044b696c8a"
  - file: "tools/kb_manifest.py"
    commit: "7dce569328f5dff8a073cc9dd15ba2baba6e40b8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:121287a785ebadf36d0019b1722e50c96b1f45d25b77552fa2b0a4563355ac1e"
  - file: "tools/kb_update_plan.py"
    commit: "704c01f14d1650d59d24ef01a7e3a68ff2be9e95"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:dd555a5db8675b3dc87b48eacb2b62caec04c06684a64abff77652f676c7a0d7"
  - file: "tools/kb_impact.py"
    commit: "704c01f14d1650d59d24ef01a7e3a68ff2be9e95"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:5d2ff5d51fe9cae349e233cf944a12d4e1af03f5998e9304ebe45f2a130f8ec1"
  - file: "tools/kb_fingerprint.py"
    commit: "2d2ced5a833a4d57d84ee0452da7c3c98cbe7ace"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:c008a9837e5d87f96b5f6b4d2816b896c9b3f4b65b1ebbc96cd6ad1452ad20db"
  - file: "tools/kb_docs.py"
    commit: "63ec70532cbc23787518ad3d92896fe3de00e4df"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:f3c797951a8d8f7e9db1330ca9ae6632d8890d9fd4a6dd41a2f002c339b50e07"
  - file: "tools/kb_query_lint.py"
    commit: "e33e8ed2a2bd4b04de971df5d19816abf869e827"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:ff8fb857fdd780391f8f60ff5d0568c218aa399045f1d1269ffbe7e4819576c6"
  - file: "tools/kb_scaffold.py"
    commit: "91c9b39bf8d8b1052632e9e139c0b3635cae1bcc"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:cbf1a7829ec8e8e276b87b98095d6927c140903d4b6f7ed631edc7f27a76916d"
tags: ["cli", "audit", "bounded", "fingerprint", "impact"]
---

# Deterministic Toolchain

## Role

The released `kb` entry point in [cli.py](../../../kb_tricks/cli.py) is a thin
dispatcher over deterministic tools in [tools/](../../../tools). The tools
validate, select, fingerprint, inventory, and plan KB work. They do not generate
authoritative KB prose; skills and humans write or update the prose.

## Contracts

- `kb manifest` reads `KB_PLAN.md` and enforces bounded selection with
  `--slice`, `--only`, and status filters.
- `kb fingerprint` records commit, tracked state, worktree state, and SHA-256
  content hashes for source files.
- `kb impact` maps changed files to manifest tasks by sources, KB paths, and
  KB fingerprints.
- `kb update-plan` starts from diff impact and blocks dirty or untracked sources
  unless the user explicitly opts into draft or allow modes.
- `kb docs` inventories existing Markdown docs declared in boundary config and
  compares them with manifest tasks.
- `kb audit` checks manifest coverage, KB freshness, links, validation files,
  boundary config, release-excluded hits, and optional CI failure policies.
- `kb query-lint` checks answer templates for explicit source provenance labels.
- `kb scaffold` creates the starter manifest/config and validation directories.

## Operating Boundaries

KB docs route agents to the right files and compress cross-file context. They
are not the authority for behavior. For a behavior change, inspect the relevant
source, tests, and release smoke checks before trusting the KB.

## Dogfood Notes

The first self-dogfood run found three UX issues:

- `query-lint` lacks the common `--repo` option accepted by most other tools.
- `audit` can report grade A for a repository with no config or manifest unless
  `--fail-on missing-config --fail-on missing-manifest` is supplied.
- `docs` keeps duplicate hints and existing-doc link checks in JSON, but text
  output needs stronger prioritization so dead links and missing comparisons are
  visible.

The follow-up fix adds `query-lint --repo`, adds an audit `setup` metric that
drops missing manifest/config repositories to grade F, skips links inside fenced
code blocks, exposes existing-doc `deadLinks`, supports `docs --check-links`,
and limits text duplicate hints by default.

## SSOT Links

- CLI dispatcher: [cli.py](../../../kb_tricks/cli.py)
- Audit implementation: [kb_audit.py](../../../tools/kb_audit.py)
- Update planner: [kb_update_plan.py](../../../tools/kb_update_plan.py)
- Impact mapper: [kb_impact.py](../../../tools/kb_impact.py)

## Blindspots

- The toolchain still relies on simple Markdown/YAML-like parsing rather than a
  full Markdown or YAML parser.
- No tool currently generates final KB prose deterministically.
