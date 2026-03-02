# kb-tricks

> Agent-native skill suite for building, maintaining, querying, reviewing, testing, migrating, and onboarding codebases with AI.

A collection of composable AI skills designed around **Cognitive Mapping**, **Adversarial Validation**, and **Mixture-of-Experts** patterns. These skills cover the full knowledge lifecycle: plan → build → maintain → query → audit → review design → review code → review tests → incident postmortem → migrate → changelog → onboard.

## Skills

### 🚀 [kb-init](./kb-init/SKILL.md) — One-Click Orchestration Pipeline

An orchestrator meta-skill that autonomously drives the `kb-plan` -> `Human Confirmation` -> `kb-build` pipeline, providing a seamless "Plan & Execute" experience.

### 🗺️ [kb-plan](./kb-plan/SKILL.md) — Knowledge Base Blueprinting

Scans the repository to identify high-signal boundaries and generates a structured `KB_PLAN.md` blueprint.

- **Macro Discovery**: Reads manifest files and directory trees without deep-diving into code
- **Signal-to-Noise Isolation**: Explicitly filters out boilerplate, tests, and dependencies
- **Task Chunking**: Breaks down the documentation process into manageable, file-by-file tasks

### 🧠 [kb-build](./kb-build/SKILL.md) — Blueprint Execution & KB Construction

Executes the `KB_PLAN.md` blueprint chunk by chunk to build a high-signal knowledge base.

- **Plan Execution**: Iteratively processes tasks from the blueprint ensuring no loss of context
- **Cognitive Mapping**: Captures cross-module contracts and design trade-offs, not boilerplate
- **Mermaid Diagrams**: Mandatory for complex API interaction chains
- **Semantic Glossary**: Terms + synonyms as retrieval anchors for RAG
- **Context-Cleared Validation**: 3-D adversarial questions scored against KB-only access to prevent hallucination
- **Source Fingerprinting**: Git Commit IDs for rot detection

### 🔄 [kb-update](./kb-update/SKILL.md) — Incremental Knowledge Maintenance

Keeps an existing KB fresh via fingerprint diffing and chunked scoped rewrites.

- **Fingerprint Diff**: Detects stale/orphaned KB files by comparing recorded Commit IDs
- **Impact Analysis**: Classifies changes as Patch / Breaking / New Module
- **Cascade Check**: Traces SSOT links to find ripple effects
- **Chunked Execution**: Processes 1-2 stale docs per iteration to prevent context overflow
- **Blueprint Sync**: Keeps `KB_PLAN.md` in sync when files are added or removed
- **Context-Cleared Validation**: Reduced-scope self-evaluation (1-2 questions per changed doc)

### 🔎 [kb-query](./kb-query/SKILL.md) — Knowledge Base Query & Source Fallback

Anti-hallucination knowledge retrieval with automatic source code verification.

- **Glossary-Driven Lookup**: Semantic trigger matching via `GLOSSARY.md` for precise document routing
- **Graph Walk**: Traverses SSOT links to collect full context — never scans the entire KB
- **Source Code Fallback**: When KB lacks concrete API signatures or logic details, automatically reads source code to verify — never fabricates
- **Structured Citations**: Every answer marks sources as 📚 KB or 📄 Source Fallback
- **Blindspot Reporting**: Honestly reports gaps instead of hallucinating

### 🩺 [kb-audit](./kb-audit/SKILL.md) — Knowledge Base Health Check

Token-efficient KB health dashboard using metadata-only scanning.

- **Coverage Check**: Cross-references `KB_PLAN.md` tasks against actual KB files
- **Freshness Check**: Batch fingerprint validation via `git log` — reads only Frontmatter, never body
- **Link Integrity**: Validates all SSOT internal links for dead references
- **Glossary Coverage**: Checks glossary entries point to existing files
- **Health Report**: A/B/C/D/F scoring with actionable recommendations

### 📐 [moe-design](./moe-design/SKILL.md) — Mixture-of-Experts Design Review

Shift-left architecture review before any code is written.

- **Layer 1** (5 Design Experts, parallel): Feasibility · Scalability · Complexity Risk · Security & Compliance · Operational Cost
- **Layer 2** (Domain Expert): Dynamically generated per project paradigm
- **Layer 3** (KB Consistency Expert, conditional): Cross-checks design proposals against existing architectural patterns in KB
- **Aggregator**: Design Readiness Rating (🔴 Blocked → 🟠 Major Revisions → 🟡 Minor Revisions → 🟢 Ready → ✅ Excellent)

### 🔍 [moe-cr](./moe-cr/SKILL.md) — Mixture-of-Experts Code Review

Multi-dimensional code review using specialized expert prompts.

- **Diff Triage Filter**: Pre-classifies files as 🟢 Trivial / 🟡 Standard / 🔴 Critical to skip noise and boost critical findings
- **Layer 1** (6 Base Experts, parallel): Architecture · Logic Boundary · Security · Performance · Testability · Maintainability
- **Layer 2** (Domain Expert): Dynamically generated per project paradigm (REST API, compiler, data pipeline, etc.)
- **Layer 3** (KB Expert, conditional): Cross-checks diffs against KB knowledge chains with **Freshness Hard Gate** — skips if KB is stale
  - **Direct Impact** → `KB-Action: UPDATE` (auto)
  - **Indirect Impact** → `KB-Action: REVIEW` (user decision)
- **Aggregator**: Dedup → Critical File Boost → Conflict Resolution → Risk Rating (🔴🟠🟡🟢✅)

### 🎓 [kb-onboard](./kb-onboard/SKILL.md) — Knowledge-Driven Onboarding

Generates guided learning paths for new team members from existing KB.

- **Topology-Sorted Reading Path**: Orders KB docs by dependency graph (foundations first)
- **Core Concept Summaries**: 2-3 sentence "What You Need to Know" per module
- **Comprehension Quizzes**: Architecture / Design Intent / Boundary questions with reference answers
- **Personalization**: Optional focus on specific modules for targeted roles

### 🧪 [moe-test](./moe-test/SKILL.md) — Mixture-of-Experts Test Review

Multi-dimensional test quality review with KB contract cross-check.

- **Layer 1** (4 Test Experts, parallel): Coverage Gaps · Assertion Quality · Test Maintainability · Boundary Conditions
- **Layer 2** (Framework Expert): Dynamically generated per test framework (Jest, pytest, Go testing, etc.)
- **Layer 3** (KB Contract Coverage, conditional): Cross-checks KB-documented contracts against actual test coverage
- **Aggregator**: Test Health Rating (🔴 Unsafe → 🟠 Weak → 🟡 Adequate → 🟢 Good → ✅ Excellent)

### 🚑 [moe-postmortem](./moe-postmortem/SKILL.md) — Mixture-of-Experts Incident Postmortem

Structured incident analysis with root cause tracing and KB fault propagation mapping.

- **Layer 1** (5 Postmortem Experts, parallel): Root Cause (5 Whys) · Blast Radius · Timeline Reconstruction · Defense Gap Analysis · Systemic Fix Recommendations
- **Layer 2** (KB Fault Propagation, conditional): Traces fault path through KB knowledge chains with Mermaid visualization
- **Report**: Standardized postmortem with MTTD/MTTR, 5 Whys, action items, and propagation diagram

### 🔀 [kb-migrate](./kb-migrate/SKILL.md) — Large-Scale Migration Planning

KB-driven architecture migration planning with safe execution ordering.

- **Impact Matrix**: Classifies each module as ⬜ Unaffected / 🟡 Adaptable / 🟠 Rewrite / 🔴 Deprecate
- **Dependency-Sorted Execution**: Leaves-first, core-last migration sequence
- **Migration Blueprint**: `MIGRATION_PLAN.md` with phased execution plan
- **Post-Migration Guidance**: Auto-triggers `kb-update` + `kb-audit` + `moe-test`

### 📝 [kb-changelog](./kb-changelog/SKILL.md) — Knowledge Base Changelog

Auto-generates human-readable KB change summaries after updates.

- **Diff-First Strategy**: Reads only `git diff` output, never full file content
- **Semantic Summarization**: 1-2 sentence per-file change descriptions
- **Incremental Append**: Appends new entries to `CHANGELOG.md` (newest first)

## How They Connect

```
                      ┌──── moe-design ◄── RFC / 设计文档
                      │
kb-init (Orchestrator) ──drives──┐
                                 ▼
kb-plan ──blueprint──→ kb-build ──fingerprints──→ kb-update ──→ kb-changelog
                           │                          ↑
                           ├──── KB ────→ moe-cr ─────┘ (KB-Action: UPDATE)
                           ├──── KB ────→ moe-test (契约 ↔ 测试交叉验证)
                           ├──── KB ────→ moe-postmortem (故障传播追踪)
                           ├──── KB ────→ kb-migrate (迁移影响分析)
                           ├──── KB ────→ kb-query (查询 + 源码回退)
                           ├──── KB ────→ kb-audit (健康体检)
                           └──── KB ────→ kb-onboard (新人引导)
```

## License

[MIT](./LICENSE) © Glen Li

---

# kb-tricks

> 面向 Agent 原生设计的技能套件：用 AI 构建、维护、查询、审查、测试、迁移知识库并引导新人入门。

一组可组合的 AI 技能，围绕**认知地图（Cognitive Mapping）**、**对抗性验证（Adversarial Validation）**和**混合专家（Mixture-of-Experts）**模式设计。覆盖知识全生命周期：规划 → 构建 → 维护 → 查询 → 体检 → 设计审查 → 代码审查 → 测试审查 → 事故复盘 → 迁移规划 → 变更日志 → 新人入门。

## 技能一览

### 🚀 [kb-init](./kb-init/SKILL.md) — 一键编排流水线

一个"元技能 (Meta-Skill)"，它负责自主编排 `kb-plan` -> `人类确认` -> `kb-build` 这一完整的"规划与执行 (Plan & Execute)"流水线，提供顺滑的交互体验。

### 🗺️ [kb-plan](./kb-plan/SKILL.md) — 知识库蓝图规划

通过宏观扫描代码库，区分高信噪比边界，并生成结构化的 `KB_PLAN.md` 施工计划书。

- **宏观探索**：阅读配置和目录树，不深陷具体代码细节
- **信噪比隔离**：显式过滤样板代码、测试文件和外部依赖
- **任务分块**：将文档化过程拆解为可管理、防上下文溢出的逐文件任务

### 🧠 [kb-build](./kb-build/SKILL.md) — 蓝图执行与知识库构建

按块执行 `KB_PLAN.md` 计划书，构建高信噪比、低维护成本的知识库。

- **计划执行**：迭代式处理蓝图中的任务，确保不丢失上下文
- **认知地图**：记录跨模块契约和设计权衡，而非样板代码
- **Mermaid 图谱**：复杂 API 交互链路强制要求可视化
- **语义触发词典**：术语 + 同义词，作为 RAG 检索锚点
- **清空上下文验证**：架构/设计意图/边界三维提问，仅允许基于 KB 作答以防幻觉
- **源码指纹**：Git Commit ID 用于知识腐烂检测

### 🔄 [kb-update](./kb-update/SKILL.md) — 增量知识维护

通过指纹比对和分块范围性重写，保持知识库的时效性。

- **指纹比对**：通过 Commit ID 检测过期/孤立的 KB 文件
- **影响分析**：将变更分类为 补丁型 / 破坏型 / 新模块
- **级联检查**：追踪 SSOT 链接发现连锁影响
- **分块执行**：每次仅处理 1~2 个过期文档，防止上下文溢出
- **蓝图同步**：新增/删除文件时同步更新 `KB_PLAN.md` 索引
- **清空上下文验证**：缩小范围的自我评估（每个变更文档 1-2 个问题）

### 🔎 [kb-query](./kb-query/SKILL.md) — 知识库查询与源码回退

带有反幻觉机制的知识库检索，不完整时自动回退到源码验证。

- **词汇表驱动检索**：通过 `GLOSSARY.md` 语义触发匹配精准定位文档
- **图谱遍历**：沿 SSOT 链接按需展开上下文——从不全量扫描 KB
- **源码回退**：当 KB 缺乏具体 API 签名或逻辑细节时，自动读取源码验证——绝不捏造
- **结构化引用**：每条回答标注来源为 📚 KB 或 📄 源码回退
- **盲区上报**：诚实报告知识空白，而非幻觉填充

### 🩺 [kb-audit](./kb-audit/SKILL.md) — 知识库健康体检

省 Token 的元数据扫描式健康仪表盘。

- **覆盖率检查**：交叉对比 `KB_PLAN.md` 任务与实际 KB 文件
- **新鲜度检查**：仅读取 Frontmatter 的批量指纹校验——从不精读正文
- **链接完整性**：验证所有 SSOT 内部链接是否存在死链
- **词汇表覆盖**：检查词汇表条目是否指向存在的文件
- **健康报告**：A/B/C/D/F 评级 + 可操作的改进建议

### 📐 [moe-design](./moe-design/SKILL.md) — 混合专家设计审查

在代码编写之前对架构提案进行"左移 (Shift-Left)"审查。

- **Layer 1**（5 个设计专家，并行）：可行性 · 可扩展性 · 复杂度风险 · 安全与合规 · 运维成本
- **Layer 2**（领域专家）：根据项目范式动态生成
- **Layer 3**（KB 一致性专家，条件触发）：将设计提案与 KB 中现有的架构模式进行交叉验证
- **聚合器**：设计就绪度评级（🔴 返工 → 🟠 重大修改 → 🟡 小幅修改 → 🟢 就绪 → ✅ 优秀）

### 🔍 [moe-cr](./moe-cr/SKILL.md) — 混合专家代码审查

使用专业化的专家提示词进行多维度代码审查。

- **差异分级过滤器**：预先将文件分为 🟢 琐碎 / 🟡 标准 / 🔴 关键，跳过噪音并提升关键发现的严重级别
- **Layer 1**（6 个基础专家，并行）：架构 · 逻辑边界 · 安全性 · 性能 · 可测试性 · 可维护性
- **Layer 2**（领域专家）：根据项目范式动态生成（REST API、编译器、数据管道等）
- **Layer 3**（KB 专家，条件触发）：将 diff 与 KB 知识链路交叉检查，并带有**新鲜度硬性门控** — KB 过期则直接跳过
  - **直接影响** → `KB-Action: UPDATE`（自动更新）
  - **间接影响** → `KB-Action: REVIEW`（由用户决定）
- **聚合器**：去重 → 关键文件提升 → 冲突仲裁 → 风险评级（🔴🟠🟡🟢✅）

### 🎓 [kb-onboard](./kb-onboard/SKILL.md) — 知识库驱动新人引导

利用现有知识库为新团队成员生成有引导性的学习路径。

- **拓扑排序阅读路径**：按知识依赖图排序（基础优先）
- **核心概念速览**：每个模块 2-3 句"你需要知道什么"摘要
- **理解检验测验**：架构 / 设计意图 / 边界条件问题 + 参考答案
- **个性化扩展**：可选针对特定角色聚焦相关模块

### 🧪 [moe-test](./moe-test/SKILL.md) — 混合专家测试审查

多维度测试质量审查，与 KB 契约交叉验证。

- **Layer 1**（4 个测试专家，并行）：覆盖率缺口 · 断言质量 · 测试可维护性 · 边界条件
- **Layer 2**（框架专家）：根据测试框架动态生成（Jest、pytest、Go testing 等）
- **Layer 3**（KB 契约覆盖，条件触发）：将 KB 记录的契约与实际测试交叉比对
- **聚合器**：测试健康度评级（🔴 不安全 → 🟠 薄弱 → 🟡 合格 → 🟢 良好 → ✅ 优秀）

### 🚑 [moe-postmortem](./moe-postmortem/SKILL.md) — 混合专家事故复盘

结构化事故分析：根因追踪 + KB 故障传播路径映射。

- **Layer 1**（5 个复盘专家，并行）：根因分析 (5 Why) · 影响面评估 · 时间线重建 · 防御缺失分析 · 系统性修复建议
- **Layer 2**（KB 故障传播，条件触发）：沿 KB 知识链追踪故障传播路径 + Mermaid 可视化
- **报告**：标准化复盘文档，含 MTTD/MTTR、5 Why、行动项和传播图

### 🔀 [kb-migrate](./kb-migrate/SKILL.md) — 大规模迁移规划

基于 KB 的架构迁移规划，安全排序执行。

- **影响矩阵**：将每个模块分类为 ⬜ 无影响 / 🟡 可适配 / 🟠 需重写 / 🔴 需废弃
- **依赖排序执行**：叶子优先、核心最后的迁移顺序
- **迁移蓝图**：`MIGRATION_PLAN.md` 分阶段执行计划
- **迁移后联动**：自动触发 `kb-update` + `kb-audit` + `moe-test`

### 📝 [kb-changelog](./kb-changelog/SKILL.md) — 知识库变更日志

更新后自动生成人类可读的 KB 变更摘要。

- **差异优先策略**：仅读取 `git diff` 输出，从不精读全文
- **语义摘要**：每个文件 1-2 句变更描述
- **增量追加**：新条目追加到 `CHANGELOG.md` 顶部（最新在前）

## 技能之间的关联

```
                    ┌──── moe-design ◄── RFC / 设计文档
                    │
kb-init (编排器) ──驱动──┐
                        ▼
kb-plan ──蓝图──→ kb-build ──指纹──→ kb-update ──→ kb-changelog
                      │                    ↑
                      ├──── KB ────→ moe-cr ─┘ (KB-Action: UPDATE)
                      ├──── KB ────→ moe-test (契约 ↔ 测试交叉验证)
                      ├──── KB ────→ moe-postmortem (故障传播追踪)
                      ├──── KB ────→ kb-migrate (迁移影响分析)
                      ├──── KB ────→ kb-query (查询 + 源码回退)
                      ├──── KB ────→ kb-audit (健康体检)
                      └──── KB ────→ kb-onboard (新人引导)
```

## 许可证

[MIT](./LICENSE) © Glen Li
