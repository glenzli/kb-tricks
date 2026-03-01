---
name: kb-build
description: "一个高级技能，使用认知建图 (cognitive-mapping) 流水线来构建高效的、面向 Agent 消费的、并经过验证的知识库。"
---

# 知识库构建目标 (KB Builder Goal)
创建一个高信噪比、低维护成本的知识库。该知识库作为代码库的**认知地图 (Cognitive Map)**，专注于稳定的接口，并通过严格的 3D 对抗性审计进行验证。

# 操作指令 (Instructions)

### 第 1 步：渐进式扫描与认知建图 (Progressive Scanning & Cognitive Mapping)
1. **不要尝试一次性读取整个仓库。** 首先读取 `README.md`、配置文件（如 `package.json`）和根目录结构，以获得宏观视图。
2. 逐模块渐进式分析仓库，以区分“高信噪比 (High Signal)”与“高噪音 (High Noise)”逻辑。
   - **应当包含 (High Signal)**：跨模块契约、隐式状态转换、设计权衡（即“为什么这么做”）以及稳定的公共 API。
   - **应当排除 (High Noise)**：自解释的代码逻辑、样板代码 (boilerplate) 以及瞬时的内部实现细节。
3. 起草一份基于**认知地图**优先级的提纲——强调组件之间如何交互，而不仅仅是它们是什么。在一个指定的目录（例如项目根目录下的 `.agent/kb/`）中生成知识库，以保持源码库的整洁。

### 第 2 步：标准元数据与结构设计 (Standardized Metadata & Structural Design)
1. **格式规则**：每个生成的 KB Markdown 文件**必须**在最开始（文件头部）包含一个 YAML Frontmatter 区块，以标准化其元数据并追踪其足迹。
2. **Frontmatter 模板**：
   ```yaml
   ---
   id: "module-unique-id"
   title: "Module Name or Feature"
   fingerprint:
     - file: "src/path/to/source_file.ext"
       commit: "current-git-commit-hash"
   tags: ["tag1", "tag2"]
   ---
   ```
3. **可视化交互 (Visual Interaction)**：对于复杂的公共 API 调用链或交互逻辑，**必须**包含 Mermaid 图表来可视化数据流向和依赖关系。
4. 保持粒度平衡：目标是每 1 个 KB 文件对应 1-3 个相关的核心源码文件，以此来最小化后期维护时的“爆炸半径 (blast radius)”。

### 第 3 步：无冗余索引 / 单一事实来源 (SSOT)
1. 维护一个“单一事实来源 (Single Source of Truth, SSOT)”。使用相对的内部 Markdown 链接来引用稳定的定义，而不是复制粘贴这些定义。这有助于后续的 Agent 进行知识图谱的遍历。

### 第 4 步：语义触发词汇表 (Semantic Trigger Glossary)
1. 生成 `GLOSSARY.md` 作为给用于检索的 Agent 获取知识的**语义触发列表 (Semantic Trigger List)**。使用结构化的 Markdown 表格格式以便机器读取。
2. **Schema 定义**：
   | 术语 / 关键字 (Term / Keyword) | 同义词 (Synonyms) | 目标 KB 文档链接 (Target KB Document Link) |
   |---|---|---|
   | ExampleTerm | Alias1, Alias2 | `[feature-x.md](./feature-x.md)` |
3. 将每个专业技术词汇、项目特有关键字及其同义词映射到 KB 中相应的章节。

### 第 5 步：3D 对抗性验证 / 清空上下文自我评估 (3-Dimensional Adversarial Validation / Context-Cleared Self-Evaluation)
1. **问题设计**：跨越三个维度设计 3-5 个问题：
   - **架构 (Architectural)**：“如何在不破坏 Y 的情况下扩展 X？”
   - **设计意图 (Design Intent)**：“为什么这个模块选择了 Z 模式？”
   - **边界/边缘情况 (Boundary/Edge)**：“当输入 A 违反了契约 B 时会发生什么？”
2. **执行验证**：在脑海中清空你当前对源码记忆的上下文。**仅**使用你生成的 KB 文本作为事实来源，尝试回答这些问题。
3. **强制标明出处 (Mandatory Citations)**：你必须严格提供全部来自 KB 内容的引用出处（文件路径和行号）。
4. **反幻觉评分 (Anti-Hallucination Scoring)**：
   - **需要 95%+ 的得分**：如果你的回答依赖了常识、不在 KB 中的源码记忆，或者你捏造了细节，则扣分。如果 KB 中没有答案，需如实声明这是一个“盲区 (Blindspot)”。
5. **迭代 (Iteration)**：如果验证失败或暴露了盲区，请更新 KB 以填补信息空白，并重复该评估。

# 示例 (Examples)

## 示例：文档化一个“认证和授权系统”
1. **建图 (Mapping)**：将 `login()`, `validateToken()` 和 `rbacMiddleware` 识别为高信噪比。忽略内部的盐值生成辅助函数。
2. **图表 (Diagram)**：包含一个 Mermaid 时序图，展示 `请求 -> Middleware -> JWT 验证 -> Controller` 的流程。
3. **词汇表 (Glossary)**：在 `GLOSSARY.md` 的 Markdown 表格中填入 "JWT"（同义词："Bearer Token"），并链接到 auth 相关的文档。
4. **审计 (Audit)**：
   - *架构 (Arch)*：“我要如何添加一个新的 'SuperAdmin' 角色？”
   - *设计 (Design)*：“为什么我们使用非对称加密 (RS256) 而不是对称加密 (HS256) 来签名？”
   - *边界 (Boundary)*：“如果公钥在 token 仍然有效时被轮换了会发生什么？”
