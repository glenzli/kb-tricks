---
id: "context-cli-toolchain"
title: "Context CLI Toolchain"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "dev_cycle/cli.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:1b7fa476e1223e4521bf97f7454f89f355ddad2a6c6b5109880fbdb4dfa13386"
  - file: "dev_cycle/context/scaffold.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:072b37bc9e632283243935531430c16262072d4375e9f6ecebe68d48a5878145"
  - file: "dev_cycle/context/manifest.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:f1f5508d525b2fb20ec2dd5adc4b0f1e059a50512533ca716c939b62187ef25f"
  - file: "dev_cycle/context/audit.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:fe2dcecdecfd06ec652d841ba7fa55b465230e6b67e40611d4cdd6218dfa266c"
  - file: "dev_cycle/context/docs.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:25801dfa6619e5a2d23e955287d5bbb29164234b5e8b7e2c68af5faa83308ab4"
  - file: "dev_cycle/context/fingerprint.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:9566f14b5fc5e107f209a7648e42c744f713e9c6b7fa475f42916f019e7137a7"
  - file: "dev_cycle/context/impact.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:2f6f3cf612de139bab059fbf553f53611433e17dc73272827dbc226ffa03ac56"
  - file: "dev_cycle/context/update_plan.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:4c92f854752fb3c495d8c5558b419afc99f592653f204dfb5f1b88618c6a9985"
  - file: "dev_cycle/context/query_lint.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:a588cfbe4d885ec928b27f5a0b5b57ad22012d2eeeafa75c5fdd20c0b764dbe0"
  - file: "dev_cycle/context/migrate_plan.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:18f3c830bcf6ff6885c47dce12dfed47ab5c53d0763b80396e1f569be3f7f2e9"
  - file: "tools/context_scaffold.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:16221f864aa1f0dc6a5c929bf9312fca655596fc277418ae1a4c8471e5ea90d0"
  - file: "tools/context_manifest.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:2000762e5734e3386d8ca1c231c9dead0cafd9140bf77f11f4dc4f237b998ae5"
  - file: "tools/context_audit.py"
    commit: "f920dea31b07d216ea766a88b9b6fbe9c0d22cf8"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:e971ef328fc8e28b009a8cdafa5379bb45ffef9673a39b8913971111a5c546f1"
tags: ["context", "cli", "toolchain", "audit", "fingerprint"]
---

# Context CLI Toolchain

## Role

The installed command is `dev-cycle`, implemented by `dev_cycle.cli`. It is a thin dispatcher over deterministic context helpers. The dispatcher owns command group parsing and `self-check`; each context command module owns its own argument parsing, data model, text output, JSON output, and exit-code policy.

The source-checkout scripts in `tools/context_*.py` are wrappers for local development. They add the repository root to `sys.path`, import the matching `dev_cycle.context.*` module, and delegate to that module's `main()` function. Release checks verify that installed CLI behavior does not depend on the `tools` package.

## Contracts

- Public CLI boundary: `dev-cycle self-check` and `dev-cycle context <command>`.
- Source wrapper boundary: `python3 tools/context_<command>.py` should behave like `dev-cycle context <command>` for source checkouts.
- Context commands are deterministic helpers. They may parse manifests, inspect Git state, classify files, emit JSON, or scaffold templates, but they do not synthesize Context prose.
- Write behavior is explicit. `scaffold` writes only starter artifacts unless `--dry-run` is used; `migrate-plan` requires `--write`; `audit` writes `index.json` only when `--write-index` is supplied. Manifest selection, docs inventory, impact, update-plan, fingerprint checks, and query lint are read-only except for their normal stdout/stderr.
- Exit codes are part of the contract: `0` means success/pass, `1` means policy or lint failures where applicable, and `2` means invalid input or unreadable required files.

## Command Map

| Command | Runtime module | Primary responsibility |
|---|---|---|
| `self-check` | `dev_cycle.cli` | Import every released context command and verify a callable `main()`. |
| `context scaffold` | `dev_cycle.context.scaffold` | Install config, agent guide, manifest template, and reserved directories. |
| `context manifest` | `dev_cycle.context.manifest` | Select bounded manifest tasks by status, tag, ID, source, or context path. |
| `context migrate-plan` | `dev_cycle.context.migrate_plan` | Convert legacy path-only manifest entries into explicit task fields. |
| `context docs` | `dev_cycle.context.docs` | Inventory existing Markdown docs, dead links, manifest comparison coverage, and duplicate hints. |
| `context audit` | `dev_cycle.context.audit` | Validate setup, Context frontmatter, fingerprints, links, manifest coverage, validation files, and optional index generation. |
| `context fingerprint` | `dev_cycle.context.fingerprint` | Generate or check dirty-aware source fingerprints. |
| `context impact` | `dev_cycle.context.impact` | Map a diff or explicit file list to manifest tasks and special Context changes. |
| `context update-plan` | `dev_cycle.context.update_plan` | Turn impact data plus dirty-source gates into bounded update actions. |
| `context query-lint` | `dev_cycle.context.query_lint` | Check provenance-first answer structure and source markers. |

## Interactions

```mermaid
flowchart TD
  CLI["dev-cycle CLI"] --> SelfCheck["self-check"]
  CLI --> ContextGroup["context command group"]
  ContextGroup --> Scaffold["scaffold writes starter artifacts"]
  ContextGroup --> Manifest["manifest selects bounded tasks"]
  ContextGroup --> Docs["docs inventories existing Markdown"]
  ContextGroup --> Audit["audit validates Context and can write index.json"]
  ContextGroup --> Fingerprint["fingerprint gates clean/dirty source"]
  ContextGroup --> Impact["impact maps changed files to tasks"]
  Impact --> UpdatePlan["update-plan emits allowed, blocked, or draft actions"]
  ContextGroup --> QueryLint["query-lint validates answer provenance"]
  Tools["tools/context_*.py wrappers"] --> ContextGroup
```

## Design Notes

- `dev_cycle.cli` intentionally avoids command implementation details. The command table is the release boundary between the installed script and context modules.
- `manifest` depends on manifest parsing from `audit` and legacy detection from `migrate_plan`; this keeps status normalization consistent across selection and health checks.
- `impact` maps changed files by manifest sources, context paths, and existing Context fingerprints. This allows updates to start from a diff instead of a full repository scan.
- `update_plan` consumes impact data and re-checks source state before allowing writes. This is the main dirty-source gate for incremental maintenance.
- `audit` is the central schema validator. It also provides shared helpers for path normalization, frontmatter parsing, config parsing, Git state, link checks, and index generation.
- `docs` is intentionally advisory. It reports existing docs coverage and duplicate hints, but the skill layer decides whether existing prose is sufficient.

## SSOT Links

- CLI dispatcher: [dev_cycle/cli.py](../../../dev_cycle/cli.py)
- Context command modules: [dev_cycle/context](../../../dev_cycle/context)
- Source wrappers: [tools](../../../tools)
- Artifact schema: [spec/CONTEXT_SPEC.md](../../../spec/CONTEXT_SPEC.md)
- Release verification: [RELEASE.md](../../../RELEASE.md)

## Blindspots

- This Context does not document every parser edge case in each command module. Use the source and tests for exact error strings and JSON shapes.
- Wrapper files are mechanically similar; Git rename detection may pair them oddly in diffs, but their runtime contract is the imported module name.
