---
name: kb-query
description: "一个知识库查询技能，利用语义触发词和知识图谱链路高效检索知识库，并在信息不完整时自动回退到源码验证，杜绝捏造。"
---

# 知识库查询目标 (KB Query Goal)
提供一条高效且抗幻觉的知识库消费路径。Agent 首先从知识库中检索，当 KB 信息不完整或涉及具体 API 细节时，**强制回退到源码或现有 docs 验证**，绝不允许凭记忆或常识捏造答案。

# 核心原则 (Core Principles)
- **KB 是路由与解释层，不是权威事实源**。源码、配置、测试、发布产物和现有维护文档仍然是事实来源。
- **每个事实必须标注来源类型**：KB / 源码回退 / 现有 docs / 推断。
- **推断必须隔离**：任何没有直接 KB、源码或 docs 支撑的内容，只能放在“不确定性与推断”区块，不能混入事实回答。
- **dirty/draft KB 必须降级**：`notAuthoritative: true`、`worktree: dirty` 或 `_draft/` 下的文档只能作为临时上下文，回答必须警告。

# 前置条件 (Prerequisites)
- 项目中存在由 `kb-build` 技能构建的知识库（含 `GLOSSARY.md`）。
- Agent 具有对项目源码的读取权限（用于源码回退）。
- 如果存在 `.agent/kb/config.yaml`，读取其中的 `docs.existing` 以便在 KB 覆盖不足时查询现有文档。

# 操作指令 (Instructions)

### 第 1 步：意图解析与触发词匹配 (Intent Parsing & Glossary Lookup)
1. 解析用户的查询意图，提取核心关键词。
2. 在 `GLOSSARY.md` 中进行**语义触发匹配**——查找关键词及其同义词所映射的目标 KB 文档。
3. 如果匹配命中：进入第 2 步，开始阅读对应的 KB 文档。
4. 如果未匹配：
   - 先尝试在 `KB_PLAN.md` 的施工任务清单中按关键词搜索相关的 `Sources` 和 `Focus` 字段，以此定位可能相关的源码文件路径。如果定位成功，直接跳到第 3 步进行源码回退。
   - 再优先读取 `.agent/kb/index.json` 中的 `existingDocs`；如果 index 缺失或过期且仓库中存在 `tools/kb_docs.py`，运行 `python3 tools/kb_docs.py --repo . --json`。按标题、heading、路径和 duplicate hints 定位现有文档。最后才手动按 `.agent/kb/config.yaml` 的 `docs.existing` 范围搜索。
   - 如果 `KB_PLAN.md` 和现有 docs 中都无法定位，告知用户"当前知识库中没有覆盖该主题"，并建议考虑将其纳入下一次 `kb-plan` 规划。

### 第 2 步：知识图谱遍历与回答 (Graph Walk & Answer)
1. 阅读触发词匹配到的**主文档**。
2. 如果主文档中存在 SSOT 内部链接指向其他相关文档，沿链接进行**图谱遍历 (Graph Walk)**，收集完整的上下文。**不要全量扫描 KB 目录**，仅沿链路按需展开。
3. 基于所收集的 KB 内容，尝试组织回答。
4. **新鲜度与权威性检查**：检查所读取的 KB 文档的 frontmatter：
   - `fingerprint.contentHash` 是否匹配当前源码内容。
   - `fingerprint.commit` 是否匹配当前文件最后提交。
   - `fingerprint.worktree` 是否为 `clean`。
   - `notAuthoritative` 是否为 `true`。
   - 文档是否位于 `.agent/kb/_draft/`。
5. 如果文档过期、dirty、draft 或 notAuthoritative，在回答末尾附加警告：
   ```
   ⚠️ 注意：以下知识库文档不是完全可信的正式 KB，建议先运行 kb-update 或基于 clean commit 重建后再用于决策。
   受影响文档: [列出文件路径和原因]
   ```

### 第 3 步：完整性自检、现有 docs 与源码回退 (Completeness Check, Existing Docs & Source Fallback)
这是本技能的核心防幻觉机制。在输出回答之前，**必须**执行以下自检：

1. **自检清单 (Checklist)**：逐条审视你的回答内容：
   - 是否涉及了**具体的函数签名、参数类型或返回值**？
   - 是否描述了**具体的代码执行路径或条件分支**？
   - 是否存在你"感觉大概率是这样"但 KB 或现有 docs 中**没有明确记载**的信息？
2. **判定规则**：
   - 如果以上任意一条为"是"，则该部分信息**不可信**，必须进入现有 docs 或源码回退。
   - 如果所有信息都有明确的 KB 或现有 docs 出处，则可以直接输出回答，但仍要标注来源类型。

3. **现有 docs 回退流程 (Existing Docs Fallback)**：
   - 从 `.agent/kb/index.json` 的 `existingDocs`、`tools/kb_docs.py --json` 输出、`.agent/kb/config.yaml` 的 `docs.existing` 或 `KB_PLAN.md` 的 Docs Comparison 中定位相关 docs。
   - 精准阅读相关段落，不要全量阅读无关 docs。
   - 若 docs 与 KB 或源码冲突，明确列出冲突，不要自动调和。

4. **源码回退流程 (Source Fallback)**：
   - 从 KB 文档的 `fingerprint` 中获取关联的源码文件路径。
   - **精准阅读**相关的源码文件（仅读取相关函数/类，不要全量扫描）。
   - 用源码中的真实信息**补充或修正**你的回答。
   - 在回答中明确标注哪些信息来自 KB、现有 docs、源码回退或推断：
     ```
     来源: KB (.agent/kb/api/auth.md)
     来源: 现有 docs (docs/auth.md)
     来源: 源码回退 (src/api/auth.ts:42-58)
     来源: 推断 (基于以上来源的非事实性判断)
     ```

### 第 4 步：结构化输出 (Structured Output)
回答必须包含以下结构：

```markdown
## 回答 (Answer)
<对用户问题的直接回答。每个事实句附近必须带来源类型标记，例如 [KB]、[源码回退]、[现有 docs]。>

## 不确定性与推断 (Uncertainty & Inference)
<仅放无法由 KB / 源码 / docs 直接证明的判断。没有推断时写“无”。>

## 引用出处 (Citations)
- 📚 KB: <引用的 KB 文档路径及相关段落>
- 📄 源码: <如有源码回退，列出文件路径和行号>
- 📝 现有 docs: <如有 docs 回退，列出路径和段落>
- ⚠️ 推断: <如有推断，说明推断依据和不确定性>

## 知识库状态 (KB Status)
- ✅ 新鲜 / ⚠️ 部分过期 / ⚠️ dirty 或 draft / ❌ 未覆盖
```

### 第 5 步：盲区上报 (Blindspot Reporting)
如果查询的主题在 KB、现有 docs 和源码中都无法找到充分的信息：
1. **严禁捏造**。明确告知用户这是一个知识盲区。
2. 建议用户考虑将该主题纳入下一次 `kb-plan` 的规划中。
