---
name: kb-changelog
description: "一个知识库变更日志技能，在 kb-update 执行后自动对比 KB 差异并生成人类可读的变更摘要。"
---

# 知识库变更日志目标 (KB Changelog Goal)
在每次 `kb-update` 执行完毕后，自动对比知识库的 Git 差异，生成一份**人类可读的变更摘要**，让团队成员无需逐文件 diff 就能快速了解"知识库最近更新了什么"。

# 前置条件 (Prerequisites)
- 项目使用 Git 进行版本管理。
- 知识库中的 KB 文件已被 Git 跟踪。
- 最近一次 `kb-update` 的变更已经被暂存 (staged) 或提交 (committed)。

# 操作指令 (Instructions)

### 第 1 步：获取 KB 差异范围 (Get KB Diff Scope)
1. 确定要对比的范围：
   - **默认**：最近一次 commit 与当前工作区之间的差异 (`git diff HEAD -- .agent/kb/`)。
   - **可选参数**：用户可以指定两个 commit ID 进行对比 (`git diff <from>..<to> -- .agent/kb/`)。
2. 获取所有被修改、新增或删除的 KB 文件列表。

### 第 2 步：分类变更 (Classify Changes)
对每个变更的 KB 文件进行分类：

| 变更类型 | 判定条件 |
|---|---|
| 📝 **内容更新 (Updated)** | 文件已存在且内容被修改 |
| 🆕 **新增文档 (Added)** | 文件为新创建 |
| 🗑️ **废弃/删除 (Removed)** | 文件被删除或标记为废弃 |
| 📖 **词汇表变更 (Glossary)** | `GLOSSARY.md` 被修改 |
| 📋 **蓝图变更 (Blueprint)** | `KB_PLAN.md` 被修改 |

### 第 3 步：生成语义摘要 (Generate Semantic Summary)
对每个 📝 **内容更新**的文件（最消耗 Token 的部分），采用**差异优先**策略：

1. **仅读取 diff 输出**（`git diff` 的 `+/-` 行），不读取文件全文。
2. 从 diff 中提炼**本次更新的核心变更**，用 1-2 句话概括：
   - 哪个组件/契约被修改了？
   - 修改的性质是什么？（签名变更 / 行为变更 / 新增功能 / 修复错误描述）
3. 如果 diff 中包含 Mermaid 图变更，标注"图表已更新"。

### 第 4 步：生成变更日志 (Generate Changelog)
输出或追加到 `.agent/kb/CHANGELOG.md`：

```markdown
# 📋 知识库变更日志 (KB Changelog)

## [YYYY-MM-DD] — <可选的变更主题标题>

### 📝 内容更新
- **[auth-flow.md](./api/auth-flow.md)**：`sign()` 函数从 HS256 迁移到 RS256，新增 `privateKey` 参数。图表已更新。
- **[database.md](./core/database.md)**：连接池超时配置从 30s 调整为 10s。

### 🆕 新增文档
- **[rate-limiter.md](./api/rate-limiter.md)**：新增限流中间件的认知地图，覆盖 Redis 配置和降级策略。

### 🗑️ 废弃/删除
- **[legacy-auth.md](./api/legacy-auth.md)**：旧版 Session 认证文档已标记为废弃。

### 📖 词汇表变更
- 新增: `RS256`, `非对称签名`
- 废弃: `HS256` (保留为同义词)

### 📋 蓝图变更
- `KB_PLAN.md`: 新增 `rate-limiter.md` 条目 [x]
```

### 第 5 步：增量追加策略 (Incremental Append)
1. 如果 `CHANGELOG.md` 已存在，将新条目**追加到文件顶部**（最新的在最前面）。
2. 如果不存在，创建新文件。
3. 保持历史记录不被覆盖——每次更新都是一个新的日期区块。

# 示例 (Examples)

## 示例：记录一次 JWT 算法迁移的 KB 更新
1. **差异范围**：`git diff HEAD~1 -- .agent/kb/` 显示 3 个文件变更。
2. **分类**：`auth-flow.md` → 📝 更新，`GLOSSARY.md` → 📖 词汇表变更，`CHANGELOG.md` → 跳过（不记录自身的变更）。
3. **语义摘要**：读取 `auth-flow.md` 的 diff，提炼："`sign()` 从 HS256 迁移到 RS256，新增 privateKey 参数，Mermaid 时序图已同步更新。"
4. **输出**：在 `CHANGELOG.md` 顶部追加一个新的日期区块。
