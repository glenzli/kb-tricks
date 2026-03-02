---
name: kb-audit
description: "一个轻量级、低 Token 消耗的知识库健康体检技能，通过元数据扫描而非内容精读来快速生成健康报告。"
---

# 知识库健康体检目标 (KB Audit Goal)
以最低 Token 成本快速诊断整个知识库的健康状况。通过扫描**元数据 (Frontmatter)、链接结构和词汇表**（而非精读文档正文），输出一份结构化的健康报告和改进建议。

# 前置条件 (Prerequisites)
- 项目中存在由 `kb-build` 技能构建的知识库。
- 项目中存在 `KB_PLAN.md` 蓝图。

# 核心设计原则：省 Token 策略 (Token-Efficient Design)

> **关键约束**：本技能的全部操作都围绕"元数据优先"展开。严禁精读 KB 文档正文或源码文件。所有检查仅依赖以下低成本数据源：
> - YAML Frontmatter（约 5-10 行/文件）
> - `GLOSSARY.md` 表格
> - `KB_PLAN.md` 任务清单
> - 文件系统目录树
> - `git log` 命令输出

# 操作指令 (Instructions)

### 第 1 步：覆盖率检查 (Coverage Check)
1. 读取 `KB_PLAN.md`，统计施工任务清单中的条目总数和已完成 `[x]` 的数量。
2. 扫描知识库目录下实际存在的 `.md` 文件列表。
3. 交叉对比：
   - **计划中有但文件不存在**：→ 标记为 ⛔ 缺失 (Missing)。
   - **文件存在但计划中没有**：→ 标记为 ❓ 未索引 (Untracked)。
4. 计算覆盖率：`已完成数 / 总条目数 × 100%`。

### 第 2 步：新鲜度检查 (Freshness Check)
1. 对每个 KB 文件，**仅读取 YAML Frontmatter 区块**（到第二个 `---` 为止即可停止读取）。
2. 提取 `fingerprint` 中的每个 `file` 和 `commit` 对。
3. 运行 `git log --oneline -1 <file>` 获取当前 commit hash 进行对比。
4. 分类统计：
   - ✅ **新鲜 (Fresh)**：指纹匹配。
   - ⚠️ **过期 (Stale)**：指纹不匹配。
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

### 第 5 步：生成健康报告 (Generate Health Report)

输出一份结构化的 Markdown 报告：

```markdown
# 📊 知识库健康报告 (KB Health Report)

## 综合评分 (Overall Score)
<根据以下四项的加权平均给出 A/B/C/D/F 评级>

## 📦 覆盖率 (Coverage): XX%
- 计划条目总数: N
- 已完成: M
- ⛔ 缺失: [列出缺失的文件]
- ❓ 未索引: [列出未被计划跟踪的文件]

## ⏱️ 新鲜度 (Freshness): XX%
- ✅ 新鲜: N 个文件
- ⚠️ 过期: N 个文件 [列出文件名和过期的源码路径]
- 🗑️ 孤立: N 个文件 [列出文件名]

## 🔗 链接完整性 (Link Integrity): XX%
- ✅ 有效链接: N 个
- 🔗 死链: N 个 [列出文件:行号 → 目标路径]

## 📖 词汇表覆盖 (Glossary): XX%
- ✅ 有效条目: N 个
- 🔗 死链条目: N 个

## 🔧 改进建议 (Recommendations)
<根据以上数据，按优先级推荐以下操作>
- 覆盖率低 → 运行 `kb-plan` 更新蓝图 + `kb-build` 补充缺失文档
- 新鲜度低 → 运行 `kb-update` 刷新过期文档
- 死链 → 运行 `kb-update` 触发级联检查修复链接
- 词汇表覆盖差 → 运行 `kb-update` 的词汇表同步或手动补充 GLOSSARY.md
```

### 评分标准 (Scoring Criteria)

| 评级 | 条件 |
|---|---|
| **A** | 四项指标均 ≥ 90% |
| **B** | 四项指标均 ≥ 75% |
| **C** | 任一指标 < 75% 但 ≥ 50% |
| **D** | 任一指标 < 50% |
| **F** | 任一指标 < 25% 或存在 5+ 死链 |
