---
name: kb-update
description: "一个增量知识库维护技能，通过指纹检测文档腐化并执行范围性更新，与 KB_PLAN.md 蓝图保持同步。"
---

# 知识库更新目标 (KB Update Goal)
通过比对源码指纹 (Fingerprint) 检测变更，执行限定范围的分块重写，并运行针对性的清空上下文自我评估，从而保持现有知识库的新鲜度和准确性——无需全量重建。

# 前置条件 (Prerequisites)
- 一个之前由 `kb-build` 技能构建的知识库，且每个 KB 文件都包含符合标准 Frontmatter 模板的指纹 (Fingerprint) 元数据。
- 项目中存在由 `kb-plan` 技能生成的 `KB_PLAN.md` 蓝图文件。
- 必须能够访问 `kb-build/SKILL.md` 以便引用其中的规范。

# 操作指令 (Instructions)

### 第 1 步：指纹差异对比 (Fingerprint Diff)
1. 扫描所有 KB 文件中 YAML Frontmatter 头部的 `fingerprint` 区块。
2. 对于每个记录的源码文件，将其 `commit` ID 与当前的 Git 提交记录 (`git log --oneline -1 <file>`) 进行对比。
3. 对每个 KB 文件进行分类：
   - **新鲜 (Fresh)**：所有指纹均匹配 → 跳过。
   - **过期 (Stale)**：一个或多个指纹不匹配 → 标记为待更新。
   - **孤立 (Orphaned)**：记录的源码文件已不存在 → 标记为待审查/清理。

### 第 2 步：影响面分析 (Impact Analysis)
1. 对于每个**过期 (Stale)**的 KB 文件，运行 `git diff <old_commit>..<current_commit> -- <source_file>` 来理解变更的性质。
2. 对变更范围进行分类：
   - **补丁级 (Patch)**：签名/外部行为未变，仅内部实现修改 → 只需要微调 KB 文本。
   - **破坏性 (Breaking)**：公共 API 签名、返回类型或契约发生改变 → 重写相关受影响的 KB 章节。
   - **新模块 (New Module)**：检测到完全未被任何 KB 文件覆盖的全新源码文件 → 需要创建新的 KB 文件。
3. **级联检查 (Cascade Check)**：沿着过期 KB 文件中的 SSOT (单一事实来源) 内部链接，找出引用了该文件的其他 KB 文件，并将它们也标记为待审查。

### 第 3 步：分块认领与范围性重写 (Chunked Scoped Rewrite)
**每次仅认领 1 到 2 个过期文档**进行处理。不要尝试一次性修复所有过期文件，以防上下文窗口溢出。

1. **对于补丁级变更**：更新现有 KB 文件中受影响的段落。保持文档的整体结构不变。
2. **对于破坏性变更**：重写受影响的章节。更新所有指向已变更定义的 SSOT 交叉引用。更新或重绘相关的 Mermaid 图表。
3. **对于新模块**：
   - 参考 **`kb-build/SKILL.md` 第 2 步（构建认知地图文档）**中的标准 Frontmatter 模板和文档规范来创建新的 KB 文件。
   - 新文件必须包含完整的 YAML Frontmatter（`id`, `title`, `fingerprint`, `tags`）。
   - 如涉及多组件联动，必须包含 Mermaid 图表。

### 第 4 步：`KB_PLAN.md` 蓝图同步 (Blueprint Sync)
维护时必须保证 `KB_PLAN.md` 作为知识库全局索引的完整性：

1. **新增文件**：当在第 3 步中为"新模块"创建了新的 KB 文件时，必须将新条目追加到 `KB_PLAN.md` 的施工任务清单中，状态标记为 `[x]`（已完成），并附带 `Sources` 和 `Focus` 信息。
2. **删除文件**：当某个"孤立 (Orphaned)"的 KB 文件被移除时，必须在 `KB_PLAN.md` 中同步删除或标注对应的条目（如添加 `[已废弃]` 标注）。
3. 确保没有残留的死链 (dangling SSOT links) 指向已删除的文件。

### 第 5 步：词汇表同步 (GLOSSARY Sync)
1. 参考 **`kb-build/SKILL.md` 第 3 步（更新词汇表）**的 Markdown 表格 Schema。
2. 扫描所有更新或新创建的 KB 文件以寻找术语变更：
   - **新术语**：附带同义词和对应的 KB 文档链接添加到 `GLOSSARY.md` 表格中。
   - **重命名术语**：更新现有条目，将旧名称保留为同义词。
   - **移除术语**：标记为已废弃 (deprecated) 而不是直接删除（防止破坏检索路径）。

### 第 6 步：清空上下文自我评估 (Context-Cleared Self-Evaluation)
与 **`kb-build/SKILL.md` 第 4 步**保持一致的验证方式，但范围缩小：

1. **为每个变更的 KB 文件**设计 1-2 个刁钻问题（而不是全量构建时的 2 个）。
2. 至少要有一个问题覆盖到**具体的变更内容**（例如："`authenticate()` 现在返回什么类型？"）。
3. 如果创建了**新模块**，则增加到 2 个问题以确保覆盖率。
4. 在脑内抹除刚刚看过的相关源码记忆，**仅凭借** KB 文本作答。如果无法准确作答，说明文档记录不够详实（盲区），立刻补充文档后重试。

### 第 7 步：刷新指纹 (Fingerprint Refresh)
1. 用当前的 Git Commit ID 更新**每一个**被修改或新创建的 KB 文件 Frontmatter 中的 `fingerprint` 区块。
2. 确认所有 Frontmatter 字段（`id`, `title`, `fingerprint`, `tags`）符合标准模板规范。

### 第 8 步：进度推进与循环 (Advance & Loop)
1. 当本次认领的 1~2 个过期文档处理完毕后，回到**第 1 步**检查是否还有剩余的过期/孤立文件。
2. 如果有，继续认领下一批，**重复循环**直到所有过期文件均处理完毕。
3. 全部完成后，向用户输出更新摘要（包括：多少文件被更新、多少被新建、多少被标记为废弃）。

# 示例 (Examples)

## 示例：JWT 签名算法从 HS256 改为了 RS256
1. **对比 (Diff)**：检测到 `auth.ts` 指纹不匹配。`git diff` 显示 `sign()` 现在使用 `RS256` 并且接收一个 `privateKey` 参数。
2. **影响 (Impact)**：**破坏性 (Breaking)** — 公共 API 签名改变。级联检查发现 `GLOSSARY.md` 中引用了 "HS256"。
3. **重写 (Rewrite)**：更新 `api/authentication.md` 以反映新的签名方法和参数。更新 Mermaid 时序图。
4. **蓝图同步 (Blueprint Sync)**：此例无新增/删除文件，`KB_PLAN.md` 无需更改。
5. **词汇表 (Glossary)**：添加 "RS256", "非对称签名 (Asymmetric Signing)"。保留 "HS256" 作为废弃的同义词。
6. **验证 (Validate)**：提问："`sign()` 现在需要哪种类型的密钥？" — 清空源码记忆后仅从 KB 中作答。
7. **指纹 (Fingerprint)**：刷新 `auth.ts` 的 commit ID，确认 Frontmatter 完整。

# 联动触发 (Cross-Skill Triggers)
> 以下建议在对应技能已安装时可选触发。调用时使用技能名称，Agent 会自动查找对应的 SKILL.md。如果技能未安装，在结果中告知用户并建议手动执行对应操作。

| 触发条件 | 建议调用技能 | 目的 |
|---|---|---|
| 所有过期文档处理完毕 | `kb-changelog` | 自动生成本次更新的人类可读变更日志 |

