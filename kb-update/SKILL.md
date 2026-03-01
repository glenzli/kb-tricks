---
name: kb-update
description: "一个增量知识库维护技能，通过指纹检测文档腐化并执行范围性更新，涉及创建任务时引用 kb-build。"
---

# 知识库更新目标 (KB Update Goal)
通过比对源码指纹 (Fingerprint) 检测变更，执行限定范围的重写，并运行针对性的验证，从而保持现有知识库的新鲜度和准确性——无需全量重建。

# 前置条件 (Prerequisites)
- 一个之前由 `kb-build` 技能构建的知识库，且每个 KB 文件中都包含指纹 (Fingerprint) 元数据。
- 必须能够访问 `kb-build/SKILL.md` 以便引用其中的步骤。

# 操作指令 (Instructions)

### 第 1 步：指纹差异对比 (Fingerprint Diff)
1. 扫描所有 KB 文件中的 `fingerprint` YAML 区块。
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

### 第 3 步：范围性重写 / 创建 (Scoped Rewrite / Creation)
1. **对于补丁级变更**：更新现有 KB 文件中受影响的段落。保持文档的整体结构不变。
2. **对于破坏性变更**：重写受影响的章节。更新所有指向已变更定义的 SSOT 交叉引用。
3. **对于新模块**：→ **参考 `kb-build/SKILL.md` 第 1 步（认知建图）**来决定新模块是否为“高信噪比”。如果是，→ **参考 `kb-build/SKILL.md` 第 2 步（标准元数据与结构设计）**来创建包含正确层级结构及 Mermaid 图表（若适用）的新 KB 文件。

### 第 4 步：词汇表同步 (GLOSSARY Sync)
1. → **参考 `kb-build/SKILL.md` 第 4 步（语义触发词汇表）**。
2. 扫描所有更新或新创建的 KB 文件以寻找术语变更：
   - **新术语**：附带同义词和对应的 KB 章节映射添加到 `GLOSSARY.md` 中。
   - **重命名术语**：更新现有条目，将旧名称保留为同义词。
   - **移除术语**：标记为已废弃 (deprecated) 而不是直接删除（防止破坏检索路径）。

### 第 5 步：针对性验证 (Targeted Validation)
1. → **参考 `kb-build/SKILL.md` 第 5 步（3D 对抗性验证）**获取格式和评分规则。
2. **缩小范围**：**为每个变更的 KB 文件**设计 1-2 个问题（而不是全量构建时的 3-5 个）。
3. 至少要有一个问题覆盖到**具体的变更内容**（例如：“`authenticate()` 现在返回什么类型？”）。
4. 如果创建了**新模块**，则将针对该文件的问题增加到 2-3 个以确保足够的覆盖率。
5. **迭代**：规则与 `kb-build` 第 5 步相同——如果得分 < 95%，则更新并重试（最多 2 次迭代）。

### 第 6 步：刷新指纹 (Fingerprint Refresh)
1. 用当前的 Git Commit ID 更新**每一个**被修改或新创建的 KB 文件的 `fingerprint` 区块。
2. 将 `maintenance.status` 设为 `"linked"`（或其他相应的状态）。
3. 对于被移除的**孤立 (Orphaned)** KB 文件，确保其他 KB 文件中没有残留的死链 (dangling SSOT links)。

# 示例 (Examples)

## 示例：JWT 签名算法从 HS256 改为了 RS256
1. **对比 (Diff)**：检测到 `auth.ts` 指纹不匹配。`git diff` 显示 `sign()` 现在使用 `RS256` 并且接收一个 `privateKey` 参数。
2. **影响 (Impact)**：**破坏性 (Breaking)** — 公共 API 签名改变。级联检查发现 `GLOSSARY.md` 中引用了 "HS256"。
3. **重写 (Rewrite)**：更新 `api/authentication.md` 以反映新的签名方法和参数。更新 Mermaid 时序图。
4. **词汇表 (Glossary)**：添加 "RS256", "非对称签名 (Asymmetric Signing)"。保留 "HS256" 作为废弃的同义词。
5. **验证 (Validate)**：提问：“`sign()` 现在需要哪种类型的密钥？” — Agent 必须仅从 KB 中作答。
6. **指纹 (Fingerprint)**：刷新 `auth.ts` 的 commit ID。
