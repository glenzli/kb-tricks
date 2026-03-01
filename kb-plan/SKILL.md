---
name: kb-plan
description: "一个用于探索代码库并生成知识库构建蓝图 (KB_PLAN.md) 的规划阶段技能。"
---

# 知识库规划目标 (KB Plan Goal)
通过宏观扫描代码库，区分“高信噪比 (High Signal)”逻辑与“样板干扰 (High Noise)”，并生成一份结构化的知识库构建施工计划书 (`KB_PLAN.md`)，以此指导后续的文档沉淀工作。

# 操作指令 (Instructions)

### 第 1 步：宏观探索 (Macro Discovery)
1. **禁止深入阅读具体代码。**
2. 首先阅读 `README.md`，核心配置文件（例如 `package.json`, `go.mod`, `pom.xml`, `docker-compose.yml` ）。
3. 浏览项目的根目录树及主要子目录的骨架文件（如入口 `main` 文件或暴露公共接口的 `index` 文件）。
4. 对项目的架构范式和主要边界建立初步直觉（如：这是一个包含 Auth, Pricing, Order 模块的微服务 API）。

### 第 2 步：信噪比隔离 (Signal-to-Noise Isolation)
1. **识别应当包含的模块 (High Signal)**：包含业务核心逻辑、跨模块调用契约、隐式状态转换、稳定的公共 API。
2. **识别应当排除的目录 (High Noise)**：明确指出哪些目录是“高噪音”的，并记录在计划书中以备忽略。例如：单测/集成测试（除非测试框架是项目核心）、样板代码、构建脚本、依赖库 `vendor`/`node_modules`。

### 第 3 步：生成施工蓝图 (Generate Blueprint)
在项目的根目录（或指定的例如 `.agent/kb/` 目录中）生成一个名为 `KB_PLAN.md` 的文件。该文件是后续构建技能的输入，要求具备极高的可执行性。

**必须使用如下格式规范：**

1. **整体规划 (Overall Approach)**：简述项目架构和为什么采取下述模块划分。
2. **过滤声明 (Exclusion List)**：列出明确决定跳过不写的目录（如：`Ignored: /tests/ - Test fixtures and suites`）。
3. **施工任务清单 (Task List)**：
   使用带有复选框 `[ ]` 的 Markdown 列表。每个复选框代表一个待生成的独立知识库文档，粒度为 1 个文档对应 1~3 个核心源码文件。
   列表项必须包含：
   - 预期的 KB 文件相对路径名称（如 `.agent/kb/api/auth.md`）。
   - 该文档要覆盖的**核心源码文件路径**。
   - 该文档的**核心关注点**（如：重点记录 JWT 签名和中间件校验逻辑）。

**`KB_PLAN.md` 示例结构：**
```markdown
# 知识库构建计划书 (Knowledge Base Blueprint)

## 📌 整体规划
该项目是一个基于 Express 的 REST API。我们将知识库划分为 `api/`, `models/`, 和 `core/` 三个子系统。

## 🗑️ 过滤声明 (Ignored Targets)
- `tests/`：单元测试。
- `scripts/`：数据库迁移的样板脚本。

## 🏗️ 施工任务清单 (Task List)
- [ ] `.agent/kb/api/auth-flow.md`
  - **Sources**: `src/api/auth.ts`, `src/middleware/rbac.ts`
  - **Focus**: JWT 令牌的分发、校验机制以及基于角色的访问控制验证链路。
- [ ] `.agent/kb/core/database.md`
  - **Sources**: `src/core/db.ts`
  - **Focus**: 连接池配置与 Prisma ORM 初始化生命周期。
```

### 第 4 步：人工确认提示 (Human-in-the-Loop Check)
1. 生成完 `KB_PLAN.md` 后，立即停止执行。
2. 通过对话框或 Agent 提示词提醒用户：“KB_PLAN.md 计划书已生成，请检查任务清单。你可以在其中调整焦点或添加遗漏的模块。确认无误后，我们将使用 kb-build 技能来正式执行沉淀。”
