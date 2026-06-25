---
name: kb-audit
description: "一个轻量级、低 Token 消耗的知识库健康体检技能，通过元数据扫描而非内容精读来快速生成健康报告。"
---

# 知识库健康体检目标 (KB Audit Goal)
以最低 Token 成本快速诊断整个知识库的健康状况。通过扫描**元数据 (Frontmatter)、Manifest 状态、链接结构、词汇表和验证产物**（而非精读文档正文），输出一份结构化的健康报告和改进建议。

# 前置条件 (Prerequisites)
- 项目中存在由 `kb-build` 技能构建的知识库。
- 项目中存在 `KB_PLAN.md` Manifest。

# 核心设计原则：省 Token 策略 (Token-Efficient Design)

> **关键约束**：本技能的全部操作都围绕"元数据优先"展开。严禁精读 KB 文档正文或源码文件。所有检查仅依赖以下低成本数据源：
> - YAML Frontmatter（约 5-10 行/文件）
> - `GLOSSARY.md` 表格
> - `KB_PLAN.md` Manifest 任务状态
> - `.agent/kb/_validation/` 文件存在性和摘要字段
> - 文件系统目录树
> - `git log`、Git 跟踪状态和内容哈希命令输出

# 操作指令 (Instructions)

### 第 1 步：Manifest 覆盖率检查 (Manifest Coverage Check)
1. 读取 `KB_PLAN.md`，统计 Manifest 任务状态：
   - `planned`
   - `built`
   - `stale`
   - `orphaned`
   - `merged-into-docs`
   - `deprecated`
2. 兼容旧版格式：`[ ]` 视为 `planned`，`[x]` 视为 `built`。
3. 扫描知识库目录下实际存在的 `.md` 文件列表。
4. 交叉对比：
   - **计划中有但文件不存在**：→ 标记为 ⛔ 缺失 (Missing)。
   - **文件存在但计划中没有**：→ 标记为 ❓ 未索引 (Untracked)。
   - **标记为 merged-into-docs 但仍有正式 KB 文件**：→ 标记为 🔁 待清理或确认。
   - **标记为 deprecated 但仍被链接引用**：→ 标记为 🔗 废弃引用风险。
5. 计算覆盖率：`built 数 / (planned + built + stale 数) × 100%`。`merged-into-docs` 和 `deprecated` 不计为缺失。

### 第 2 步：dirty-aware 新鲜度检查 (Dirty-Aware Freshness Check)
1. 对每个 KB 文件，**仅读取 YAML Frontmatter 区块**（到第二个 `---` 为止即可停止读取）。
2. 提取 `fingerprint` 中的每个 `file`、`commit`、`tracked`、`worktree`、`contentHash`。
3. 对每个源码文件检查：
   - 文件是否存在。
   - 当前 Git 跟踪状态是否与 `tracked` 匹配。
   - 当前 worktree 是否 clean。
   - 当前内容哈希是否与 `contentHash` 匹配。
   - 当前文件最后提交是否与 `commit` 匹配。
4. 分类统计：
   - ✅ **新鲜 (Fresh)**：指纹匹配。
   - ⚠️ **过期 (Stale)**：commit 或 contentHash 不匹配。
   - 🟠 **脏源 (Dirty Source)**：当前源码 dirty/untracked，正式 KB 不应被视为完全可信。
   - 🧪 **草稿 (Draft)**：文档在 `_draft/` 下或 `notAuthoritative: true`。
   - 🗑️ **孤立 (Orphaned)**：源码文件已被删除。
5. 计算新鲜率：`新鲜数 / 总文件数 × 100%`。

### 第 3 步：链接完整性检查 (Link Integrity Check)
1. 对每个 KB 文件，**仅扫描文件中的 Markdown 链接**（匹配 `[text](path)` 模式），无需理解正文内容。
2. 对于每个相对链接，检查目标文件是否真实存在于文件系统中。
3. 统计：
   - ✅ 有效链接数。
   - 🔗 死链数 (Dead Links) 及其所在文件和行号。

### 第 4 步：词汇表覆盖检查 (Glossary Coverage Check)
1. 读取 `GLOSSARY.md` 的表格。
2. 检查词汇表中每个条目的 `Target KB Document Link` 是否指向一个**实际存在的文件**。
3. 统计：
   - ✅ 有效条目数。
   - 🔗 指向不存在文件的死链条目数。
4. （可选）提取所有 KB 文件 Frontmatter 中的 `tags` 字段，检查是否存在 tag 出现在文件中却未被 `GLOSSARY.md` 索引的"遗漏术语"。

### 第 5 步：验证产物检查 (Validation Artifact Check)
1. 对每个状态为 `built` 的 Manifest 任务，检查是否存在 `.agent/kb/_validation/<task-id>.md`。
2. 仅读取验证文件的标题和摘要字段，统计：
   - ✅ 存在且最新。
   - ⚠️ 缺失。
   - ⚠️ 失败或存在未解决盲区。
   - ⚠️ 验证时间早于 KB 指纹更新时间。
3. draft 文档的验证产物不计入正式覆盖率，但应在报告中单独列出。

### 第 6 步：边界配置检查 (Artifact Boundary Check)
1. 如果存在 `.agent/kb/config.yaml`，检查 KB 文件、GLOSSARY 链接和 Manifest sources 是否落在 include/exclude 边界内。
2. 如果不存在，报告为配置缺失，并建议运行 `kb-plan` 生成 Proposed Artifact Boundary。
3. 对 `releaseExcluded` 中的内容，检查是否被错误描述为发布产物事实来源。

### 第 7 步：生成健康报告 (Generate Health Report)

输出一份结构化的 Markdown 报告：

```markdown
# 📊 知识库健康报告 (KB Health Report)

## 综合评分 (Overall Score)
<根据以下四项的加权平均给出 A/B/C/D/F 评级>

## 📦 Manifest 覆盖率 (Coverage): XX%
- 计划条目总数: N
- Built: M
- Planned/Stale: N
- Merged Into Docs: N
- Deprecated: N
- ⛔ 缺失: [列出缺失的文件]
- ❓ 未索引: [列出未被计划跟踪的文件]

## ⏱️ 新鲜度 (Freshness): XX%
- ✅ 新鲜: N 个文件
- ⚠️ 过期: N 个文件 [列出文件名和过期的源码路径]
- 🟠 脏源: N 个文件 [列出 dirty/untracked source]
- 🧪 草稿/非权威: N 个文件
- 🗑️ 孤立: N 个文件 [列出文件名]

## 🔗 链接完整性 (Link Integrity): XX%
- ✅ 有效链接: N 个
- 🔗 死链: N 个 [列出文件:行号 → 目标路径]

## 📖 词汇表覆盖 (Glossary): XX%
- ✅ 有效条目: N 个
- 🔗 死链条目: N 个

## 🧪 验证产物 (Validation): XX%
- ✅ 有验证产物: N 个
- ⚠️ 缺失验证: N 个
- ⚠️ 失败或有盲区: N 个

## 🧭 边界配置 (Artifact Boundary)
- Config: present/missing
- Boundary violations: N

## 🔧 改进建议 (Recommendations)
<根据以上数据，按优先级推荐以下操作>
- 覆盖率低 → 运行 `kb-plan` 更新 Manifest + `kb-build slice 1` 补充缺失文档
- 新鲜度低 → 运行 `kb-update since <commit>` 或 `kb-update files <path>` 刷新过期文档
- dirty/draft 多 → 先提交源码，再运行 `kb-update` promote/refresh 正式 KB
- 死链 → 运行 `kb-update` 触发级联检查修复链接
- 词汇表覆盖差 → 运行 `kb-update` 的词汇表同步或手动补充 GLOSSARY.md
- 缺失验证 → 运行 `kb-build only <task-id>` 或 `kb-update files <path>` 生成 `_validation`
```

### 评分标准 (Scoring Criteria)

| 评级 | 条件 |
|---|---|
| **A** | 覆盖率、新鲜度、链接、词汇表、验证均 ≥ 90%，且无 dirty authoritative KB |
| **B** | 五项指标均 ≥ 75%，且无 5 个以上 dirty/draft 风险 |
| **C** | 任一指标 < 75% 但 ≥ 50% |
| **D** | 任一指标 < 50% |
| **F** | 任一指标 < 25%、存在 5+ 死链，或正式 KB 大量依赖 dirty/untracked source |
