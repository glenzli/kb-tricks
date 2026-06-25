---
name: kb-plan
description: "一个用于探索代码库并生成长期知识库 Manifest (KB_PLAN.md) 的规划阶段技能。"
---

# 知识库规划目标 (KB Plan Goal)
通过宏观扫描代码库，区分“高信噪比 (High Signal)”逻辑与“样板干扰 (High Noise)”，并生成一份结构化、可长期维护的知识库 Manifest (`KB_PLAN.md`)。`KB_PLAN.md` 不只是一次性施工计划，也承担 KB 生命周期状态索引：planned / built / stale / orphaned / merged-into-docs / deprecated。

# 核心原则 (Core Principles)
- **KB 是辅助上下文，不是权威来源**：源码、配置、测试、发布产物和现有维护文档仍然是事实来源。
- **先定义边界再规划**：规划前必须识别 `.agent/kb/config.yaml` 中的 include / exclude / releaseExcluded / docs.existing。
- **先比较现有文档**：仓库已有文档足够表达的内容，不应机械复制到 `.agent/kb/` 形成第二套文档孤岛。
- **宏观扫描，不深读源码**：本技能只建立边界和任务，不做源码级实现归纳。

# 操作指令 (Instructions)

### 第 0 步：边界配置读取或生成 (Artifact Boundary Config)
1. 检查是否存在 `.agent/kb/config.yaml`。
2. 如果存在，先读取并遵守其边界：
   ```yaml
   include:
     - src/**
     - docs/dev/**
   exclude:
     - dist/**
     - out/**
     - node_modules/**
   releaseExcluded:
     - docs/dev/**
     - .agent/**
   docs:
     existing:
       - README.md
       - docs/**
   ```
3. 如果不存在，基于仓库结构在 `KB_PLAN.md` 中生成一个 **Proposed Artifact Boundary** 区块，列出建议的 include / exclude / releaseExcluded / docs.existing，并暂停要求用户确认或调整。不要在边界未确认时继续生成细粒度任务。
4. 如果当前环境可访问 `kb-tricks/tools/kb_scaffold.py`，可以先用 `python3 tools/kb_scaffold.py --repo <target> --dry-run` 展示 starter artifact 写入计划；只有用户确认后才真正 scaffold。该工具只安装初始 config、Manifest 和保留目录，不替代本技能的规划判断。
5. 可参考 `templates/config.yaml` 的结构生成建议配置；稳定字段定义见 `spec/KB_SPEC.md`。
6. `releaseExcluded` 表示不应被发布产物语义吸收的上下文资产。规划时可以读取，但在报告中必须标注其不属于 release-facing docs。

### 第 1 步：宏观探索 (Macro Discovery)
1. **禁止深入阅读具体代码。**
2. 首先阅读 `README.md`，核心配置文件（例如 `package.json`, `go.mod`, `pom.xml`, `docker-compose.yml` ）。
3. 按 `.agent/kb/config.yaml` 的 include / exclude 边界浏览项目的根目录树及主要子目录的骨架文件（如入口 `main` 文件或暴露公共接口的 `index` 文件）。
4. 对项目的架构范式和主要边界建立初步直觉（如：这是一个包含 Auth, Pricing, Order 模块的微服务 API）。

### 第 2 步：信噪比隔离 (Signal-to-Noise Isolation)
1. **识别应当包含的模块 (High Signal)**：包含业务核心逻辑、跨模块调用契约、隐式状态转换、稳定的公共 API。
2. **识别应当排除的目录 (High Noise)**：明确指出哪些目录是“高噪音”的，并记录在计划书中以备忽略。例如：单测/集成测试（除非测试框架是项目核心）、样板代码、构建脚本、依赖库 `vendor`/`node_modules`。
3. 对 `releaseExcluded` 中的路径单独标注：它们可以帮助 Agent 理解开发上下文，但不应被描述为面向用户或发布产物的事实来源。

### 第 3 步：已有文档对比 (Existing Docs Comparison)
1. 如果仓库中存在 `tools/kb_docs.py`，先运行 `python3 tools/kb_docs.py --repo . --json` 获取现有文档清单、标题、目录、hash、链接和疑似重复线索；否则按 `.agent/kb/config.yaml` 的 `docs.existing` 手动读取现有文档的标题、目录和高层摘要。不要深度重写现有文档。
2. 对每个候选 KB 主题判断：
   - **已有文档已充分覆盖**：标记为 `merged-into-docs` 或不创建 KB 任务。
   - **KB 有新增价值**：例如跨模块契约、设计权衡、隐式边界、Agent 检索锚点。
   - **应回写现有文档**：面向人类维护者更有价值的内容，标记为 `merged-into-docs` 候选。
   - **潜在冲突**：现有 docs、源码入口和计划中的 KB 焦点互相矛盾时，记录为风险项。
3. 在 `KB_PLAN.md` 中输出 **Existing Docs Comparison** 区块，回答：
   - 现有 docs 已覆盖什么。
   - KB 相比现有 docs 多了什么。
   - 哪些 KB 主题应合并回 docs。
   - 哪些候选 KB 是重复噪音。
4. 生成或更新 Manifest 后，如果可用，运行 `python3 tools/kb_docs.py --repo . --check-manifest`；若失败，补齐缺失任务的 `Docs Comparison` 字段或明确解释为什么该任务不需要独立比较。

### 第 4 步：生成长期 Manifest (Generate Long-Lived Manifest)
在**项目的根目录**（与 `README.md` 同级）生成或更新 `KB_PLAN.md`。`KB_PLAN.md` 不应放入 `.agent/kb/` 知识库内容目录中。知识库正文内容统一存放在 `.agent/kb/` 目录下。

可参考 `templates/KB_PLAN.md` 的结构；稳定字段定义见 `spec/KB_SPEC.md`。

**必须使用如下格式规范：**

1. **整体规划 (Overall Approach)**：简述项目架构和为什么采取下述模块划分。
2. **边界配置 (Artifact Boundary)**：记录 `.agent/kb/config.yaml` 的 include / exclude / releaseExcluded 摘要；如果配置缺失，则记录 Proposed Artifact Boundary 并要求确认。
3. **已有文档对比 (Existing Docs Comparison)**：记录 docs 覆盖、KB 新增价值、回写建议和重复噪音。
4. **过滤声明 (Exclusion List)**：列出明确决定跳过不写的目录（如：`Ignored: /tests/ - Test fixtures and suites`）。
5. **Manifest 任务清单 (Task Manifest)**：
   使用状态标签 `[planned]` / `[built]` / `[stale]` / `[orphaned]` / `[merged-into-docs]` / `[deprecated]` 的 Markdown 列表。每个条目代表一个长期可追踪的 KB 主题，粒度为 1 个文档对应 1~3 个核心源码文件。
   列表项必须包含：
   - 稳定任务 ID（如 `api-auth-flow`）。
   - 预期的 KB 文件相对路径名称（如 `.agent/kb/api/auth.md`）。
   - 该文档要覆盖的**核心源码文件路径**。
   - 该文档的**核心关注点**（如：重点记录 JWT 签名和中间件校验逻辑）。
   - 标签、状态和是否建议合并回现有 docs。

**兼容性规则**：如果读取旧版 `KB_PLAN.md`，将 `[ ]` 视为 `[planned]`，将 `[x]` 视为 `[built]`。

**`KB_PLAN.md` 示例结构：**
```markdown
# 知识库 Manifest (Knowledge Base Manifest)

## 📌 整体规划
该项目是一个基于 Express 的 REST API。我们将知识库划分为 `api/`, `models/`, 和 `core/` 三个子系统。

## 🧭 边界配置 (Artifact Boundary)
- Config: `.agent/kb/config.yaml`
- Include: `src/**`, `docs/dev/**`
- Exclude: `dist/**`, `node_modules/**`
- Release Excluded: `.agent/**`, `docs/dev/**`

## 📚 已有文档对比 (Existing Docs Comparison)
- `README.md` 已覆盖启动和部署入口，不重复写入 KB。
- `docs/auth.md` 缺少鉴权中间件与 RBAC 的跨模块契约，保留 KB 任务。
- `docs/api-errors.md` 与源码错误码可能冲突，标记为风险项。

## 🗑️ 过滤声明 (Ignored Targets)
- `tests/`：单元测试。
- `scripts/`：数据库迁移的样板脚本。

## 🏗️ Manifest 任务清单 (Task Manifest)
- [planned] api-auth-flow
  - **ID**: `api-auth-flow`
  - **KB**: `.agent/kb/api/auth-flow.md`
  - **Sources**: `src/api/auth.ts`, `src/middleware/rbac.ts`
  - **Focus**: JWT 令牌的分发、校验机制以及基于角色的访问控制验证链路。
  - **Tags**: `auth`, `rbac`, `api`
  - **Docs Comparison**: `docs/auth.md` 有概览，但缺少跨模块契约。
  - **Status**: `planned`
- [merged-into-docs] core-database
  - **ID**: `core-database`
  - **KB**: `.agent/kb/core/database.md`
  - **Sources**: `src/core/db.ts`
  - **Focus**: 连接池配置与 Prisma ORM 初始化生命周期。
  - **Docs Comparison**: 已由 `docs/database.md` 充分覆盖，暂不生成独立 KB。
  - **Status**: `merged-into-docs`
```

### 第 5 步：人工确认提示 (Human-in-the-Loop Check)
1. 生成完 `KB_PLAN.md` 后，立即停止执行。
2. 通过对话框或 Agent 提示词提醒用户：“KB_PLAN.md Manifest 已生成，请检查边界配置、已有文档对比和任务状态。你可以调整 include/exclude/releaseExcluded、补充遗漏模块，或把重复 KB 标记为 merged-into-docs。确认无误后，我们将使用 kb-build 技能按小切片正式执行沉淀。”
