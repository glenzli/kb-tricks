# dev-cycle

> Development lifecycle skills and deterministic checks for AI-assisted engineering.

`dev-cycle` is a repo-native toolkit for the software development lifecycle. It combines copyable AI skills, stable artifact contracts, and deterministic CLI checks for context building, querying, updating, design review, code review, test review, migration planning, onboarding, changelogging, and postmortem analysis.

It is not a project-management replacement, scheduler, database, or LLM runtime. Source code, configuration, tests, release artifacts, and maintained human-facing docs remain authoritative. `dev-cycle` helps AI agents and developers work around those assets in smaller, auditable steps.

## Design Direction

`dev-cycle` treats Context as one subsystem in a broader development-cycle workflow. The Context is the context layer; review and evolution skills use that layer when it is fresh, and fall back to source when it is not.

The Context is an auxiliary context layer, not the authority for a repository. Source code, configuration, tests, release artifacts, and maintained human-facing docs remain authoritative. The Context should route questions, compress context, explain cross-module contracts, and expose uncertainty.

The next-phase design is tracked in [ROADMAP.md](./ROADMAP.md). The most important operating contracts are:

- **Bounded by default**: `context-build` and `context-update` process small slices unless the user explicitly requests full execution.
- **Clean source for authoritative Context**: dirty or untracked source content is blocked from formal Context writes by default and belongs in draft or impact artifacts.
- **Artifact boundaries**: projects can declare include/exclude/release-excluded paths through `.dev-cycle/context/config.yaml`.
- **Dirty-aware fingerprints**: Context metadata records Git state and content hashes, not only commit IDs.
- **Existing docs comparison**: Context planning should compare existing docs before creating a parallel documentation island.
- **Provenance-first answers**: query results distinguish Context, source fallback, existing docs, and inference.

## Specs And Tooling

- [spec/CONTEXT_SPEC.md](./spec/CONTEXT_SPEC.md): stable artifact schema for `.dev-cycle/context/config.yaml`, `CONTEXT_PLAN.md`, Context frontmatter, validation files, glossary, and `index.json`.
- [RELEASE.md](./RELEASE.md): release boundary, install smoke, and packaging verification notes.
- [skills/](./skills): copyable Agent skill prompts; each child directory keeps the released skill name and contains `SKILL.md`.
- [templates/](./templates): starter templates for config, agent guidance, manifest, Context docs, validation artifacts, and query answers.
- [dev_cycle/context/](./dev_cycle/context): released dependency-free command implementations used by the installed `dev-cycle` CLI.
- [tools/context_scaffold.py](./tools/context_scaffold.py): source-checkout wrapper for installing starter config, AI agent guidance, manifest, and reserved Context directories into a target repository.
- [tools/context_manifest.py](./tools/context_manifest.py): source-checkout wrapper for bounded `CONTEXT_PLAN.md` task selection.
- [tools/context_build_assist.py](./tools/context_build_assist.py): source-checkout wrapper for deterministic Context skeleton, fingerprint, and validation draft generation.
- [tools/context_migrate_plan.py](./tools/context_migrate_plan.py): source-checkout wrapper for converting legacy path-only Manifest entries into explicit task fields.
- [tools/context_docs.py](./tools/context_docs.py): source-checkout wrapper for existing-docs inventory, manifest comparison coverage, dead-link reporting, severity-ranked duplicate hints, and compact summary JSON.
- [tools/context_audit.py](./tools/context_audit.py): source-checkout wrapper for setup checks, hashes, dirty-state checks, support/reserved Context classification, links, manifest coverage, validation artifacts, policy exit codes, and optional `index.json` generation.
- [tools/context_fingerprint.py](./tools/context_fingerprint.py): source-checkout wrapper for generating and checking dirty-aware source fingerprints.
- [tools/context_impact.py](./tools/context_impact.py): source-checkout wrapper for diff-first changed-file to Manifest task mapping.
- [tools/context_update_plan.py](./tools/context_update_plan.py): source-checkout wrapper for read-only bounded update actions, blockers, draft targets, setup warnings, docs reviews, and new Context candidates.
- [tools/context_query_lint.py](./tools/context_query_lint.py): source-checkout wrapper for provenance linting of `context-query` answers.
- [tools/release_smoke.py](./tools/release_smoke.py): local/CI release smoke runner for tests, CLI import checks, scaffold dry-run, query lint, and whitespace checks.
- [tools/release_rehearsal.py](./tools/release_rehearsal.py): full release rehearsal for sdist/wheel content boundaries, installed CLI checks, and packaging metadata warnings.

The released Python distribution is `dev-cycle`, the import package is
`dev_cycle`, and the installed deterministic CLI is `dev-cycle`.

Installed CLI example:

```bash
dev-cycle self-check --json
dev-cycle context scaffold --repo /path/to/project --dry-run
dev-cycle context manifest --repo /path/to/project --slice 1 --json
dev-cycle context build-assist --repo /path/to/project --slice 1 --write
dev-cycle context migrate-plan --repo /path/to/project --dry-run
dev-cycle context migrate-plan --repo /path/to/project --write
dev-cycle context docs --repo /path/to/project --check-manifest --check-links
dev-cycle context docs --repo /path/to/project --summary-json
dev-cycle context impact --repo /path/to/project --staged --json
dev-cycle context impact --repo /path/to/project --worktree --json
dev-cycle context impact --repo /path/to/project --base main --json
dev-cycle context impact --repo /path/to/project --since HEAD~1 --json
dev-cycle context update-plan --repo /path/to/project --staged --json
dev-cycle context update-plan --repo /path/to/project --worktree --draft --json
dev-cycle context query-lint --repo /path/to/project templates/context-query-answer.md
dev-cycle context audit --repo /path/to/project --fail-on stale --fail-on dead-links --min-score B
dev-cycle context audit --repo /path/to/project --summary-json
dev-cycle context fingerprint --repo /path/to/project --check .dev-cycle/context/release/packaging.md
```

After scaffolding a target repository, point its root `AGENTS.md`, `CLAUDE.md`,
or equivalent AI instruction file at `.dev-cycle/context/AGENT_GUIDE.md` so agents know
how to use Context as auxiliary context rather than authority.

`dev-cycle context docs` and `dev-cycle context impact/update-plan` apply `.dev-cycle/context/config.yaml` `exclude` rules when collecting existing docs, so broad patterns such as `docs.existing: ["*.md"]` can safely pair with exclusions like `.dev-cycle/**` and `CONTEXT_PLAN.md`.

`dev-cycle context docs --json` and `dev-cycle context audit --json` keep the full payload for detailed automation; `--summary-json` returns a compact top-issues view for agents and CI logs.

Source checkout fallback:

```bash
python3 tools/context_audit.py --repo /path/to/project --write-index .dev-cycle/context/index.json
python3 tools/context_build_assist.py --repo /path/to/project --slice 1 --write
python3 tools/context_migrate_plan.py --repo /path/to/project --dry-run
python3 tools/context_impact.py --repo /path/to/project --files src/cli/release.ts --json
python3 tools/context_update_plan.py --repo /path/to/project --since HEAD~1 --json
python3 tools/context_query_lint.py templates/context-query-answer.md
```

Minimal CI smoke chain:

```bash
python3 -B tools/release_smoke.py
```

Full release rehearsal before publishing:

```bash
python3 -B tools/release_rehearsal.py
```

## Skills

The complete catalog is summarized in [skills/README.md](./skills/README.md). Review skills share [skills/REVIEW_PROTOCOL.md](./skills/REVIEW_PROTOCOL.md).

### Recipes

#### [cycle-init](./skills/cycle-init/SKILL.md) — Initialization Recipe

A thin orchestration recipe for scaffold, `context-plan`, user confirmation, and the first bounded `context-build` slice.

### Context Layer

#### [context-plan](./skills/context-plan/SKILL.md) — Context Manifest Planning

Scans the repository to identify high-signal boundaries and generates a structured long-lived `CONTEXT_PLAN.md` manifest.

- **Macro Discovery**: Reads manifest files and directory trees without deep-diving into code
- **Artifact Boundary Config**: Respects `.dev-cycle/context/config.yaml` include/exclude/releaseExcluded rules
- **Existing Docs Comparison**: Compares existing docs before creating a parallel Context topic
- **Signal-to-Noise Isolation**: Explicitly filters out boilerplate, tests, and dependencies
- **Task Chunking**: Breaks down the documentation process into manageable, file-by-file tasks

#### [context-build](./skills/context-build/SKILL.md) — Manifest Execution & Context Construction

Executes the `CONTEXT_PLAN.md` manifest in bounded slices to build high-signal Context.

- **Bounded Execution**: Defaults to `slice 1`; full execution requires explicit `until-complete`
- **Manifest Execution**: Iteratively processes tasks from the manifest ensuring no loss of context
- **Cognitive Mapping**: Captures cross-module contracts and design trade-offs, not boilerplate
- **Mermaid Diagrams**: Mandatory for complex API interaction chains
- **Semantic Glossary**: Terms + synonyms as retrieval anchors for RAG
- **Context-Cleared Validation**: 3-D adversarial questions scored against Context-only access to prevent hallucination
- **Dirty-Aware Fingerprinting**: Git state + content hashes for rot detection

#### [context-update](./skills/context-update/SKILL.md) — Incremental Knowledge Maintenance

Keeps an existing Context fresh via fingerprint diffing and chunked scoped rewrites.

- **Diff-First Scope**: Starts from staged, worktree, base, since, or files scopes when provided, then falls back to full fingerprint scan
- **Fingerprint Diff**: Detects stale/orphaned Context files by comparing recorded Git state and content hashes
- **Impact Analysis**: Classifies changes as Patch / Breaking / New Module
- **Cascade Check**: Traces SSOT links to find ripple effects
- **Chunked Execution**: Processes 1-2 stale docs per iteration to prevent context overflow
- **Manifest Sync**: Keeps `CONTEXT_PLAN.md` lifecycle state in sync when files are added, updated, merged, or deprecated
- **Context-Cleared Validation**: Reduced-scope self-evaluation (1-2 questions per changed doc)

#### [context-query](./skills/context-query/SKILL.md) — Context Query & Source Fallback

Anti-hallucination knowledge retrieval with automatic source code verification.

- **Glossary-Driven Lookup**: Semantic trigger matching via `GLOSSARY.md` for precise document routing
- **Graph Walk**: Traverses SSOT links to collect full context — never scans the entire Context
- **Source Code Fallback**: When Context lacks concrete API signatures or logic details, automatically reads source code to verify — never fabricates
- **Provenance Contract**: Every factual answer line marks Context, source fallback, or existing docs; inference is isolated and lintable
- **Blindspot Reporting**: Honestly reports gaps instead of hallucinating

#### [context-audit](./skills/context-audit/SKILL.md) — Context Health Check

Token-efficient Context health dashboard using metadata-only scanning.

- **Coverage Check**: Cross-references `CONTEXT_PLAN.md` tasks against actual Context files
- **Freshness Check**: Batch dirty-aware fingerprint validation via Frontmatter, Git state, and content hashes
- **Link Integrity**: Validates all SSOT internal links for dead references
- **Glossary Coverage**: Checks glossary entries point to existing files
- **Health Report**: A/B/C/D/F scoring with actionable recommendations

### Review Layer

Review skills are source-first. They may use Context only after the shared freshness gate passes.

#### [review-design](./skills/review-design/SKILL.md) — Design Review

Shift-left architecture review before any code is written.

- **Layer 1** (5 Design Experts, parallel): Feasibility · Scalability · Complexity Risk · Security & Compliance · Operational Cost
- **Layer 2** (Domain Expert): Dynamically generated per project paradigm
- **Layer 3** (Context Consistency Expert, conditional): Cross-checks design proposals against existing architectural patterns in Context
- **Aggregator**: Design Readiness Rating (Blocked -> Major Revisions -> Minor Revisions -> Ready -> Excellent)

#### [review-code](./skills/review-code/SKILL.md) — Code Review

Multi-dimensional code review using specialized expert prompts.

- **Diff Triage Filter**: Pre-classifies files as Trivial / Standard / Critical to skip noise and boost critical findings
- **Layer 1** (6 Base Experts, parallel): Architecture · Logic Boundary · Security · Performance · Testability · Maintainability
- **Layer 2** (Domain Expert): Dynamically generated per project paradigm (REST API, compiler, data pipeline, etc.)
- **Layer 3** (Context Expert, conditional): Cross-checks diffs against Context knowledge chains with **Freshness Hard Gate** — skips if Context is stale
  - **Direct Impact** → `Context-Action: UPDATE` (auto)
  - **Indirect Impact** → `Context-Action: REVIEW` (user decision)
- **Aggregator**: Dedup -> Critical File Boost -> Conflict Resolution -> Risk Rating

#### [review-test](./skills/review-test/SKILL.md) — Test Review

Multi-dimensional test quality review with Context contract cross-check.

- **Layer 1** (4 Test Experts, parallel): Coverage Gaps · Assertion Quality · Test Maintainability · Boundary Conditions
- **Layer 2** (Framework Expert): Dynamically generated per test framework (Jest, pytest, Go testing, etc.)
- **Layer 3** (Context Contract Coverage, conditional): Cross-checks Context-documented contracts against actual test coverage
- **Aggregator**: Test Health Rating (Unsafe -> Weak -> Adequate -> Good -> Excellent)

### Evolution Layer

#### [cycle-migrate](./skills/cycle-migrate/SKILL.md) — Large-Scale Migration Planning

Architecture migration planning with safe execution ordering.

- **Impact Matrix**: Classifies each module as unaffected, adaptable, rewrite required, or deprecated
- **Dependency-Sorted Execution**: Leaves-first, core-last migration sequence
- **Migration Blueprint**: `MIGRATION_PLAN.md` with phased execution plan
- **Post-Migration Guidance**: Auto-triggers `context-update` + `context-audit` + `review-test`

#### [cycle-postmortem](./skills/cycle-postmortem/SKILL.md) — Incident Postmortem

Structured incident analysis with root cause tracing and optional Context fault propagation mapping.

- **Layer 1** (5 Postmortem Experts, parallel): Root Cause (5 Whys) · Blast Radius · Timeline Reconstruction · Defense Gap Analysis · Systemic Fix Recommendations
- **Layer 2** (Context Fault Propagation, conditional): Traces fault path through Context knowledge chains with Mermaid visualization
- **Report**: Standardized postmortem with MTTD/MTTR, 5 Whys, action items, and propagation diagram

#### [cycle-onboard](./skills/cycle-onboard/SKILL.md) — Onboarding

Generates guided learning paths for new developers or agents from fresh project context.

- **Topology-Sorted Reading Path**: Orders Context docs by dependency graph (foundations first)
- **Core Concept Summaries**: 2-3 sentence "What You Need to Know" per module
- **Comprehension Quizzes**: Architecture / Design Intent / Boundary questions with reference answers
- **Personalization**: Optional focus on specific modules for targeted roles

#### [cycle-changelog](./skills/cycle-changelog/SKILL.md) — Context Changelog

Auto-generates human-readable Context change summaries after updates.

- **Diff-First Strategy**: Reads only `git diff` output, never full file content
- **Semantic Summarization**: 1-2 sentence per-file change descriptions
- **Incremental Append**: Appends new entries to `CHANGELOG.md` (newest first)

## How They Connect

```
                      ┌──── review-design ◄── RFC / 设计文档
                      │
cycle-init (Orchestrator) ──drives──┐
                                 ▼
context-plan ──manifest──→ context-build ──fingerprints──→ context-update ──→ cycle-changelog
                           │                          ↑
                           ├──── Context ────→ review-code ─────┘ (Context-Action: UPDATE)
                           ├──── Context ────→ review-test (契约 ↔ 测试交叉验证)
                           ├──── Context ────→ cycle-postmortem (故障传播追踪)
                           ├──── Context ────→ cycle-migrate (迁移影响分析)
                           ├──── Context ────→ context-query (查询 + 源码回退)
                           ├──── Context ────→ context-audit (健康体检)
                           └──── Context ────→ cycle-onboard (新人引导)
```

## License

[MIT](./LICENSE) © Glen Li

---

# dev-cycle

> 面向 AI 辅助研发的开发周期技能与确定性检查工具。

`dev-cycle` 是一套面向代码仓库的软件开发周期辅助工具。它把可复制的 AI 技能、稳定的产物契约和确定性的 CLI 检查组合在一起，覆盖上下文构建、查询、更新、设计评审、代码评审、测试评审、迁移规划、入门引导、变更记录和事故复盘。

它不是项目管理系统、调度器、数据库或 LLM runtime。源码、配置、测试、发布产物和面向人的维护文档仍然是权威。`dev-cycle` 的目标是帮助 AI agent 和开发者围绕这些权威资产进行更小步、更可审计的工作。

## 设计方向

`dev-cycle` 把 Context 视为更大开发周期工作流里的一个子系统。Context 是上下文层；review 和 evolution 技能可以在 Context 新鲜时使用它，在 Context 过期时回退到源码。

Context 不是代码仓库的权威来源。源码、配置、测试、发布产物和面向人的维护文档仍然是权威。Context 的职责是路由问题、压缩上下文、解释跨模块契约，并显式暴露不确定性。

下一阶段设计记录在 [ROADMAP.md](./ROADMAP.md)。最重要的运行契约是：

- **默认小步执行**：`context-build` 和 `context-update` 只处理小切片，除非用户明确要求全量执行。
- **正式 Context 只基于干净源码**：dirty 或 untracked 源码默认不能写入正式 Context，只能进入草稿或影响分析产物。
- **产物边界配置**：项目可以通过 `.dev-cycle/context/config.yaml` 声明 include、exclude 和 releaseExcluded 路径。
- **dirty-aware 指纹**：Context 元数据记录 Git 状态和内容哈希，而不只是 commit ID。
- **已有文档对比**：规划 Context 前先比较现有文档，避免制造第二套文档孤岛。
- **来源优先回答**：查询结果必须区分 Context、源码回退、现有文档和推断。

## 规范与工具

- [spec/CONTEXT_SPEC.md](./spec/CONTEXT_SPEC.md)：定义 `.dev-cycle/context/config.yaml`、`CONTEXT_PLAN.md`、Context frontmatter、验证文件、词汇表和 `index.json` 的稳定结构。
- [RELEASE.md](./RELEASE.md)：记录 release 边界、安装 smoke 和打包验证流程。
- [skills/](./skills)：可复制的 Agent skill prompt；每个子目录保留发布后的 skill 名称，并包含 `SKILL.md`。
- [templates/](./templates)：提供 config、AI agent 指引、Manifest、Context 文档、验证产物和查询回答模板。
- [dev_cycle/context/](./dev_cycle/context)：安装后的 `dev-cycle` CLI 使用的无依赖命令实现。
- [tools/context_scaffold.py](./tools/context_scaffold.py)：源码 checkout wrapper，用于把 starter config、AI agent 指引、Manifest 和 Context 保留目录安装到目标仓库。
- [tools/context_manifest.py](./tools/context_manifest.py)：源码 checkout wrapper，用于 `CONTEXT_PLAN.md` 小步任务选择。
- [tools/context_build_assist.py](./tools/context_build_assist.py)：源码 checkout wrapper，用于生成确定性的 Context skeleton、fingerprint 和 validation 草稿。
- [tools/context_migrate_plan.py](./tools/context_migrate_plan.py)：源码 checkout wrapper，用于把旧的纯路径 Manifest 条目迁移为显式任务字段。
- [tools/context_docs.py](./tools/context_docs.py)：源码 checkout wrapper，用于现有文档清单、Manifest Docs Comparison 覆盖率、死链报告、按严重级别排序的重复提示和紧凑 summary JSON。
- [tools/context_audit.py](./tools/context_audit.py)：源码 checkout wrapper，用于 setup 检查、hash、dirty 状态、support/reserved Context 分类、链接、Manifest 覆盖、验证产物、策略 exit code 和可选 `index.json` 生成。
- [tools/context_fingerprint.py](./tools/context_fingerprint.py)：源码 checkout wrapper，用于 dirty-aware source fingerprint 生成与检查。
- [tools/context_impact.py](./tools/context_impact.py)：源码 checkout wrapper，用于 diff-first changed files 到 Manifest 任务影响面映射。
- [tools/context_update_plan.py](./tools/context_update_plan.py)：源码 checkout wrapper，用于只读 bounded actions、阻塞项、draft target、setup warning、docs review 和新 Context 候选规划。
- [tools/context_query_lint.py](./tools/context_query_lint.py)：源码 checkout wrapper，用于 `context-query` 回答来源类型与推断隔离检查。
- [tools/release_smoke.py](./tools/release_smoke.py)：本地/CI release smoke 入口，统一运行测试、CLI import 检查、scaffold dry-run、query lint 和 whitespace 检查。
- [tools/release_rehearsal.py](./tools/release_rehearsal.py)：完整 release 预演入口，用于验证 sdist/wheel 内容边界、安装态 CLI 和 packaging metadata 警告。

发布到 Python 生态的 distribution 名称是 `dev-cycle`，import package 是 `dev_cycle`，安装后的确定性 CLI 是 `dev-cycle`。

安装后的 CLI 示例：

```bash
dev-cycle self-check --json
dev-cycle context scaffold --repo /path/to/project --dry-run
dev-cycle context manifest --repo /path/to/project --slice 1 --json
dev-cycle context build-assist --repo /path/to/project --slice 1 --write
dev-cycle context migrate-plan --repo /path/to/project --dry-run
dev-cycle context migrate-plan --repo /path/to/project --write
dev-cycle context docs --repo /path/to/project --check-manifest --check-links
dev-cycle context docs --repo /path/to/project --summary-json
dev-cycle context impact --repo /path/to/project --staged --json
dev-cycle context impact --repo /path/to/project --worktree --json
dev-cycle context impact --repo /path/to/project --base main --json
dev-cycle context impact --repo /path/to/project --since HEAD~1 --json
dev-cycle context update-plan --repo /path/to/project --staged --json
dev-cycle context update-plan --repo /path/to/project --worktree --draft --json
dev-cycle context query-lint --repo /path/to/project templates/context-query-answer.md
dev-cycle context audit --repo /path/to/project --fail-on stale --fail-on dead-links --min-score B
dev-cycle context audit --repo /path/to/project --summary-json
dev-cycle context fingerprint --repo /path/to/project --check .dev-cycle/context/release/packaging.md
```

对目标仓库执行 scaffold 后，建议在该仓库根目录的 `AGENTS.md`、`CLAUDE.md`
或同类 AI 指令文件里指向 `.dev-cycle/context/AGENT_GUIDE.md`，让 agent 明确 Context 只是辅助上下文，不是权威来源。

`dev-cycle context docs` 和 `dev-cycle context impact/update-plan` 收集现有文档时会应用 `.dev-cycle/context/config.yaml` 的 `exclude` 规则，所以文档型仓库可以用 `docs.existing: ["*.md"]`，再排除 `.dev-cycle/**` 和 `CONTEXT_PLAN.md`。

`dev-cycle context docs --json` 和 `dev-cycle context audit --json` 保留完整 payload，适合细粒度自动化；`--summary-json` 返回紧凑的 top issues 视图，更适合 agent 和 CI 日志。

源码 checkout fallback：

```bash
python3 tools/context_audit.py --repo /path/to/project --write-index .dev-cycle/context/index.json
python3 tools/context_build_assist.py --repo /path/to/project --slice 1 --write
python3 tools/context_migrate_plan.py --repo /path/to/project --dry-run
python3 tools/context_impact.py --repo /path/to/project --files src/cli/release.ts --json
python3 tools/context_update_plan.py --repo /path/to/project --since HEAD~1 --json
python3 tools/context_query_lint.py templates/context-query-answer.md
```

最小 CI smoke chain：

```bash
python3 -B tools/release_smoke.py
```

发布前完整 release 预演：

```bash
python3 -B tools/release_rehearsal.py
```

## 技能一览

完整目录见 [skills/README.md](./skills/README.md)。Review 技能共同遵守 [skills/REVIEW_PROTOCOL.md](./skills/REVIEW_PROTOCOL.md)。

### Recipes

#### [cycle-init](./skills/cycle-init/SKILL.md) — 初始化 recipe

一个薄编排 recipe，负责 scaffold、`context-plan`、用户确认和第一个 bounded `context-build` 切片。

### Context Layer

#### [context-plan](./skills/context-plan/SKILL.md) — 知识库 Manifest 规划

通过宏观扫描代码库，区分高信噪比边界，并生成结构化、可长期维护的 `CONTEXT_PLAN.md` Manifest。

- **宏观探索**：阅读配置和目录树，不深陷具体代码细节
- **产物边界配置**：遵守 `.dev-cycle/context/config.yaml` 的 include/exclude/releaseExcluded 规则
- **已有文档对比**：创建 Context 主题前先比较现有 docs，避免文档孤岛
- **信噪比隔离**：显式过滤样板代码、测试文件和外部依赖
- **任务分块**：将文档化过程拆解为可管理、防上下文溢出的逐文件任务

#### [context-build](./skills/context-build/SKILL.md) — Manifest 执行与知识库构建

按小切片执行 `CONTEXT_PLAN.md` Manifest，构建高信噪比、低维护成本的知识库。

- **默认小步执行**：默认 `slice 1`；全量执行必须显式声明 `until-complete`
- **Manifest 执行**：迭代式处理 Manifest 中的任务，确保不丢失上下文
- **认知地图**：记录跨模块契约和设计权衡，而非样板代码
- **Mermaid 图谱**：复杂 API 交互链路强制要求可视化
- **语义触发词典**：术语 + 同义词，作为 RAG 检索锚点
- **清空上下文验证**：架构/设计意图/边界三维提问，仅允许基于 Context 作答以防幻觉
- **dirty-aware 源码指纹**：Git 状态 + 内容哈希用于知识腐烂检测

#### [context-update](./skills/context-update/SKILL.md) — 增量知识维护

通过指纹比对和分块范围性重写，保持知识库的时效性。

- **差异优先范围**：优先从 staged、worktree、base、since 或 files 范围入口计算影响面，再回退到全量指纹扫描
- **指纹比对**：通过 Git 状态和内容哈希检测过期/孤立的 Context 文件
- **影响分析**：将变更分类为 补丁型 / 破坏型 / 新模块
- **级联检查**：追踪 SSOT 链接发现连锁影响
- **分块执行**：每次仅处理 1~2 个过期文档，防止上下文溢出
- **Manifest 同步**：新增、更新、合并或废弃文件时同步更新 `CONTEXT_PLAN.md` 生命周期状态
- **清空上下文验证**：缩小范围的自我评估（每个变更文档 1-2 个问题）

#### [context-query](./skills/context-query/SKILL.md) — 知识库查询与源码回退

带有反幻觉机制的知识库检索，不完整时自动回退到源码验证。

- **词汇表驱动检索**：通过 `GLOSSARY.md` 语义触发匹配精准定位文档
- **图谱遍历**：沿 SSOT 链接按需展开上下文——从不全量扫描 Context
- **源码回退**：当 Context 缺乏具体 API 签名或逻辑细节时，自动读取源码验证——绝不捏造
- **来源契约**：每条事实回答标注 Context、源码回退或现有 docs；推断隔离并可被 lint
- **盲区上报**：诚实报告知识空白，而非幻觉填充

#### [context-audit](./skills/context-audit/SKILL.md) — 知识库健康体检

省 Token 的元数据扫描式健康仪表盘。

- **覆盖率检查**：交叉对比 `CONTEXT_PLAN.md` 任务与实际 Context 文件
- **新鲜度检查**：基于 Frontmatter、Git 状态和内容哈希的 dirty-aware 批量指纹校验
- **链接完整性**：验证所有 SSOT 内部链接是否存在死链
- **词汇表覆盖**：检查词汇表条目是否指向存在的文件
- **健康报告**：A/B/C/D/F 评级 + 可操作的改进建议

### Review Layer

Review 技能以源码为权威。只有相关 Context 通过共同的新鲜度门控后，才允许使用 Context 交叉检查。

#### [review-design](./skills/review-design/SKILL.md) — 设计审查

在代码编写之前对架构提案进行"左移 (Shift-Left)"审查。

- **Layer 1**（5 个设计专家，并行）：可行性 · 可扩展性 · 复杂度风险 · 安全与合规 · 运维成本
- **Layer 2**（领域专家）：根据项目范式动态生成
- **Layer 3**（Context 一致性专家，条件触发）：将设计提案与 Context 中现有的架构模式进行交叉验证
- **聚合器**：设计就绪度评级（返工 -> 重大修改 -> 小幅修改 -> 就绪 -> 优秀）

#### [review-code](./skills/review-code/SKILL.md) — 代码审查

使用专业化的专家提示词进行多维度代码审查。

- **差异分级过滤器**：预先将文件分为琐碎 / 标准 / 关键，跳过噪音并提升关键发现的严重级别
- **Layer 1**（6 个基础专家，并行）：架构 · 逻辑边界 · 安全性 · 性能 · 可测试性 · 可维护性
- **Layer 2**（领域专家）：根据项目范式动态生成（REST API、编译器、数据管道等）
- **Layer 3**（Context 专家，条件触发）：将 diff 与 Context 知识链路交叉检查，并带有**新鲜度硬性门控** — Context 过期则直接跳过
  - **直接影响** → `Context-Action: UPDATE`（自动更新）
  - **间接影响** → `Context-Action: REVIEW`（由用户决定）
- **聚合器**：去重 -> 关键文件提升 -> 冲突仲裁 -> 风险评级

#### [review-test](./skills/review-test/SKILL.md) — 测试审查

多维度测试质量审查，与 Context 契约交叉验证。

- **Layer 1**（4 个测试专家，并行）：覆盖率缺口 · 断言质量 · 测试可维护性 · 边界条件
- **Layer 2**（框架专家）：根据测试框架动态生成（Jest、pytest、Go testing 等）
- **Layer 3**（Context 契约覆盖，条件触发）：将 Context 记录的契约与实际测试交叉比对
- **聚合器**：测试健康度评级（不安全 -> 薄弱 -> 合格 -> 良好 -> 优秀）

### Evolution Layer

#### [cycle-migrate](./skills/cycle-migrate/SKILL.md) — 大规模迁移规划

架构迁移规划，安全排序执行。

- **影响矩阵**：将每个模块分类为无影响、可适配、需重写或需废弃
- **依赖排序执行**：叶子优先、核心最后的迁移顺序
- **迁移蓝图**：`MIGRATION_PLAN.md` 分阶段执行计划
- **迁移后联动**：自动触发 `context-update` + `context-audit` + `review-test`

#### [cycle-postmortem](./skills/cycle-postmortem/SKILL.md) — 事故复盘

结构化事故分析：根因追踪 + 可选 Context 故障传播路径映射。

- **Layer 1**（5 个复盘专家，并行）：根因分析 (5 Why) · 影响面评估 · 时间线重建 · 防御缺失分析 · 系统性修复建议
- **Layer 2**（Context 故障传播，条件触发）：沿 Context 知识链追踪故障传播路径 + Mermaid 可视化
- **报告**：标准化复盘文档，含 MTTD/MTTR、5 Why、行动项和传播图

#### [cycle-onboard](./skills/cycle-onboard/SKILL.md) — 入门引导

利用新鲜项目上下文为新开发者或新 Agent 生成有引导性的学习路径。

- **拓扑排序阅读路径**：按知识依赖图排序（基础优先）
- **核心概念速览**：每个模块 2-3 句"你需要知道什么"摘要
- **理解检验测验**：架构 / 设计意图 / 边界条件问题 + 参考答案
- **个性化扩展**：可选针对特定角色聚焦相关模块

#### [cycle-changelog](./skills/cycle-changelog/SKILL.md) — 上下文变更日志

更新后自动生成人类可读的 Context 变更摘要。

- **差异优先策略**：仅读取 `git diff` 输出，从不精读全文
- **语义摘要**：每个文件 1-2 句变更描述
- **增量追加**：新条目追加到 `CHANGELOG.md` 顶部（最新在前）

## 技能之间的关联

```
                    ┌──── review-design ◄── RFC / 设计文档
                    │
cycle-init (编排器) ──驱动──┐
                        ▼
context-plan ──Manifest──→ context-build ──指纹──→ context-update ──→ cycle-changelog
                      │                    ↑
                      ├──── Context ────→ review-code ─┘ (Context-Action: UPDATE)
                      ├──── Context ────→ review-test (契约 ↔ 测试交叉验证)
                      ├──── Context ────→ cycle-postmortem (故障传播追踪)
                      ├──── Context ────→ cycle-migrate (迁移影响分析)
                      ├──── Context ────→ context-query (查询 + 源码回退)
                      ├──── Context ────→ context-audit (健康体检)
                      └──── Context ────→ cycle-onboard (新人引导)
```

## 许可证

[MIT](./LICENSE) © Glen Li
