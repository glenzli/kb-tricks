---
name: kb-migrate
description: "一个大规模架构迁移规划技能，分析知识库全量文档以评估迁移影响面，并生成安全的分阶段迁移蓝图。"
---

# 知识库迁移规划目标 (KB Migrate Goal)
当项目面临架构级迁移（如框架替换、单体拆分、语言迁移）时，通过分析现有知识库来评估每个模块的迁移影响等级，生成一份带有安全执行顺序的分阶段迁移蓝图 (`MIGRATION_PLAN.md`)，并在迁移完成后驱动 KB 全量刷新。

# 前置条件 (Prerequisites)
- 项目中存在由 `kb-build` 构建的知识库。
- 用户提供了明确的**迁移目标描述**（如："将 REST API 从 Express 迁移到 Fastify"、"把单体服务拆分为 3 个微服务"）。

# 操作指令 (Instructions)

### 第 1 步：迁移目标理解 (Migration Target Understanding)
1. 从用户描述中提取：
   - **当前状态 (From)**：当前使用的技术/架构（从 KB 和项目配置中验证）。
   - **目标状态 (To)**：迁移后的目标技术/架构。
   - **迁移范围 (Scope)**：是全量迁移还是渐进式共存？
2. 阅读 `KB_PLAN.md` 和 `GLOSSARY.md`，建立对整个项目模块地图的全局视野。

### 第 2 步：影响面分析 — 逐模块扫描 (Impact Analysis — Per Module Scan)
对 KB 中的**每个文档**进行以下评估（仅读取 Frontmatter + 文档概要，不精读全部正文）：

1. 根据迁移目标，判定每个模块的**迁移影响等级**：

   | 等级 | 含义 | 示例 |
   |---|---|---|
   | ⬜ **无影响 (Unaffected)** | 该模块与迁移目标无关 | 迁移 API 框架时，纯工具类函数 |
   | 🟡 **可适配 (Adaptable)** | 需要小幅调整接口或配置 | 中间件签名从 `(req, res, next)` 改为 `(request, reply)` |
   | 🟠 **需重写 (Rewrite Required)** | 核心逻辑依赖旧技术，需大幅重写 | 强依赖 Express 路由系统的控制器 |
   | 🔴 **需废弃 (Deprecate)** | 旧版专有，目标架构中不再存在 | Express 特有的错误处理中间件 |

2. **依赖关系标注**：利用 KB 文档中的 SSOT 链接，标注每个模块被哪些其他模块依赖。

### 第 3 步：安全执行顺序生成 (Safe Execution Order)
1. 基于依赖关系图，计算安全的迁移顺序。核心原则：
   - **叶子优先 (Leaves First)**：先迁移没有被其他模块依赖的"叶子"模块。
   - **核心最后 (Core Last)**：被引最多的基础模块最后迁移。
   - **可适配优先 (Adaptable First)**：先处理小幅调整，再处理需重写的模块。
2. 生成一张 Mermaid 依赖图，标注迁移顺序编号。

### 第 4 步：生成迁移蓝图 (Generate Migration Blueprint)
在项目根目录生成 `MIGRATION_PLAN.md`：

```markdown
# 🔄 迁移计划书 (Migration Blueprint)

## 📌 迁移概要
- **From**: <当前架构>
- **To**: <目标架构>
- **范围**: <全量 / 渐进>

## 📊 影响矩阵 (Impact Matrix)
| KB 文档 | 关联源码 | 影响等级 | 依赖方 |
|---|---|---|---|
| auth-flow.md | src/api/auth.ts | 🟠 需重写 | gateway.md, rbac.md |
| database.md | src/core/db.ts | ⬜ 无影响 | — |
| ... | ... | ... | ... |

## 🔀 迁移依赖图
<Mermaid 图展示安全执行顺序>

## 🏗️ 分阶段执行计划 (Phased Execution)
### 阶段 1: 叶子模块（可适配）
- [ ] <模块 A>: <具体迁移操作>
- [ ] <模块 B>: <具体迁移操作>

### 阶段 2: 中间层模块（需重写）
- [ ] <模块 C>: <具体迁移操作>

### 阶段 3: 核心模块
- [ ] <模块 D>: <具体迁移操作>

### 阶段 4: 清理与废弃
- [ ] 移除 <废弃模块>
- [ ] 运行 `kb-update` 全量刷新知识库
```

### 第 5 步：后续联动指引 (Post-Migration Guidance)
在蓝图末尾明确说明迁移完成后需要执行的技能操作：
1. 运行 `kb-update` 全量刷新所有受影响的 KB 文档指纹。
2. 运行 `kb-audit` 验证迁移后的知识库健康度。
3. 对迁移涉及的核心模块运行 `moe-test` 验证测试覆盖。
4. 更新 `GLOSSARY.md` 中的旧术语为新术语（保留旧名作为同义词）。

# 示例 (Examples)

## 示例：将 Express REST API 迁移到 Fastify
1. **目标理解**：From: Express 4.x → To: Fastify 4.x，渐进式迁移（共存期）。
2. **影响面分析**：
   - `database.md` (db.ts) → ⬜ 无影响（纯 Prisma，与框架无关）。
   - `auth-flow.md` (auth.ts, rbac.ts) → 🟠 需重写（中间件签名和装饰器模式不同）。
   - `error-handler.md` (errorMiddleware.ts) → 🔴 需废弃（Express `(err, req, res, next)` 模式，Fastify 使用 `setErrorHandler`）。
   - `rate-limiter.md` (rateLimiter.ts) → 🟡 可适配（换用 `@fastify/rate-limit` 插件）。
3. **安全执行顺序**：阶段 1: rate-limiter（叶子，可适配）→ 阶段 2: auth-flow（中间层，需重写）→ 阶段 3: error-handler（废弃旧版 + 新建 Fastify 版）→ 阶段 4: `kb-update` 全量刷新。

# 联动触发 (Cross-Skill Triggers)
> 以下建议在对应技能已安装时可选触发。调用时使用技能名称，Agent 会自动查找对应的 SKILL.md。如果技能未安装，在结果中告知用户并建议手动执行对应操作。

| 触发条件 | 建议调用技能 | 目的 |
|---|---|---|
| 迁移蓝图全部执行完毕 | `kb-update` | 全量刷新所有受影响的 KB 文档指纹 |
| `kb-update` 完成后 | `kb-audit` | 验证迁移后的知识库健康度 |
| 迁移涉及核心模块 | `moe-test` | 验证核心模块的测试覆盖未因迁移而劣化 |
| `kb-update` 完成后 | `kb-changelog` | 记录本次迁移导致的知识库变更 |

