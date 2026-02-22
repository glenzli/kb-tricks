# kb-tricks

> Agent-native skill suite for building, maintaining, and reviewing codebases with AI.

A collection of composable AI skills designed around **Cognitive Mapping**, **Adversarial Validation**, and **Mixture-of-Experts** patterns. These skills work together as a pipeline: build knowledge → maintain knowledge → review code with knowledge.

## Skills

### 🧠 [kb-build](./kb-build/SKILL.md) — Full Knowledge Base Construction

Builds a high-signal, low-maintenance knowledge base from scratch.

- **Cognitive Mapping**: Captures cross-module contracts and design trade-offs, not boilerplate
- **Mermaid Diagrams**: Mandatory for complex API interaction chains
- **Semantic Glossary**: Terms + synonyms as retrieval anchors for RAG
- **3-D Adversarial Validation**: Architecture / Design Intent / Boundary questions, scored against KB-only access
- **Source Fingerprinting**: Git Commit IDs for rot detection

### 🔄 [kb-update](./kb-update/SKILL.md) — Incremental Knowledge Maintenance

Keeps an existing KB fresh via fingerprint diffing and scoped rewrites.

- **Fingerprint Diff**: Detects stale/orphaned KB files by comparing recorded Commit IDs
- **Impact Analysis**: Classifies changes as Patch / Breaking / New Module
- **Cascade Check**: Traces SSOT links to find ripple effects
- **Orchestrator Pattern**: References `kb-build` steps for creation tasks — no logic duplication
- **Targeted Validation**: Reduced-scope audit (1-2 questions per changed doc)

### 🔍 [moe-cr](./moe-cr/SKILL.md) — Mixture-of-Experts Code Review

Multi-dimensional code review using specialized expert prompts.

- **Layer 1** (6 Base Experts, parallel): Architecture · Logic Boundary · Security · Performance · Testability · Maintainability
- **Layer 2** (Domain Expert): Dynamically generated per project paradigm (REST API, compiler, data pipeline, etc.)
- **Layer 3** (KB Expert, conditional): Cross-checks diffs against KB knowledge chains
  - **Direct Impact** → `KB-Action: UPDATE` (auto)
  - **Indirect Impact** → `KB-Action: REVIEW` (user decision)
- **Aggregator**: Dedup → Conflict Resolution (Security > Correctness > Perf > Maintain) → Risk Rating (🔴🟠🟡🟢✅)

## How They Connect

```
kb-build ──fingerprints──→ kb-update ──stale detection──→ kb-update
    │                                                        ↑
    └──────── KB ──────────→ moe-cr ──KB-Action: UPDATE──────┘
```

## License

[MIT](./LICENSE) © Glen Li

---

# kb-tricks

> 面向 Agent 原生设计的技能套件：用 AI 构建、维护知识库并进行代码审查。

一组可组合的 AI 技能，围绕**认知地图（Cognitive Mapping）**、**对抗性验证（Adversarial Validation）**和**混合专家（Mixture-of-Experts）**模式设计。三个技能构成完整流水线：构建知识 → 维护知识 → 用知识审查代码。

## 技能一览

### 🧠 [kb-build](./kb-build/SKILL.md) — 全量知识库构建

从零构建高信噪比、低维护成本的知识库。

- **认知地图**：记录跨模块契约和设计权衡，而非样板代码
- **Mermaid 图谱**：复杂 API 交互链路强制要求可视化
- **语义触发词典**：术语 + 同义词，作为 RAG 检索锚点
- **三维对抗验证**：架构 / 设计意图 / 边界条件三个维度提问，仅允许基于 KB 作答
- **源码指纹**：Git Commit ID 用于知识腐烂检测

### 🔄 [kb-update](./kb-update/SKILL.md) — 增量知识维护

通过指纹比对和限定范围的重写，保持知识库的时效性。

- **指纹比对**：通过 Commit ID 检测过期/孤立的 KB 文件
- **影响分析**：将变更分类为 补丁型 / 破坏型 / 新模块
- **级联检查**：追踪 SSOT 链接发现连锁影响
- **编排器模式**：引用 `kb-build` 的步骤处理创建任务——不重复逻辑
- **定向验证**：缩小范围的审计（每个变更文档 1-2 个问题）

### 🔍 [moe-cr](./moe-cr/SKILL.md) — 混合专家代码审查

使用专业化的专家提示词进行多维度代码审查。

- **Layer 1**（6 个基础专家，并行）：架构 · 逻辑边界 · 安全性 · 性能 · 可测试性 · 可维护性
- **Layer 2**（领域专家）：根据项目范式动态生成（REST API、编译器、数据管道等）
- **Layer 3**（KB 专家，条件触发）：将 diff 与 KB 知识链路交叉检查
  - **直接影响** → `KB-Action: UPDATE`（自动更新）
  - **间接影响** → `KB-Action: REVIEW`（由用户决定）
- **聚合器**：去重 → 冲突仲裁（安全 > 正确性 > 性能 > 可维护性）→ 风险评级（🔴🟠🟡🟢✅）

## 技能之间的关联

```
kb-build ──指纹──→ kb-update ──过期检测──→ kb-update
    │                                        ↑
    └──── KB ────→ moe-cr ──KB-Action: UPDATE─┘
```

## 许可证

[MIT](./LICENSE) © Glen Li
