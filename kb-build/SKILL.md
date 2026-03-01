---
name: kb-build
description: "一个高级执行技能，它读取并执行 KB_PLAN.md 计划书，利用认知建图流水线来构建出实际的知识库文档并执行 3D 验证。"
---

# 知识库构建目标 (KB Builder Goal)
严格参照前置规划生成的 `KB_PLAN.md` 执行分块施工。生成高信噪比、带有源码指纹、并经过 3D 对抗性审计验证的组件认知地图文档。

# 前置条件 (Prerequisites)
- 项目中已经存在由 `kb-plan` 技能生成的 `KB_PLAN.md` 文件。如果不存在，请先中止执行并提示用户运行 `kb-plan`。

# 操作指令 (Instructions)

### 第 1 步：计划载入与分块选择 (Load Plan & Chunking)
1. 读取 `KB_PLAN.md`。
2. 找到第一个未处于选中状态 `[ ]` 的任务条目。
3. **每次仅选取 1 到 2 个任务**作为本次迭代的工作上下文。千万不要一次性尝试完成所有的文档生成。
4. 精准地阅读任务中 `Sources` 所列出的源码文件。

### 第 2 步：构建认知地图文档 (Build Cognitive Map Document)
为选定的任务生成知识库 Markdown 文件，并遵从以下规范：

1. **标准元数据 (Frontmatter)**：每个 KB 文件**必须**在头部包含 YAML Frontmatter 区块。
   ```yaml
   ---
   id: "module-unique-id"
   title: "Module Name or Feature"
   fingerprint:
     - file: "src/path/to/source_file.ext"  # 与任务清单中的 Sources 对应
       commit: "current-git-commit-hash"
   tags: ["tag1", "tag2"]
   ---
   ```
2. **高度聚焦 (High Signal)**：重点回答模块间的“交互契约”和“设计权衡”，忽略在阅读代码时可以直接一目了然的琐碎调用栈。
3. **可视化交互 (Visual Interaction)**：如果内容涉及多组件联动或状态流转，必须手写 Mermaid 时序图或状态图。
4. **内部链接 (SSOT)**：使用相对链接指向已有的其他 KB 文档，不抄写重复定义。

### 第 3 步：更新词汇表 (Update Glossary)
1. 检查或创建全局的 `.agent/kb/GLOSSARY.md`。
2. 提取刚才写好的文档中的核心业务术语，更新至词汇表的 Markdown 表格中。
   | 术语 / 关键字 | 同义词 | 目标 KB 文档链接 |
   |---|---|---|

### 第 4 步：清空上下文自我评估 (Context-Cleared Self-Evaluation)
为了保证文档并非依赖你大脑内部的临时源码记忆，在生成阶段完成且落地写入完毕后，就当前写入的这篇文档执行一次校验：

1. 设计 1 个架构问题和 1 个边界条件问题（共 2 个刁钻问题）。
2. 在脑内抹除刚刚看过的相关源码的细节记忆。
3. **仅凭借**刚生成的文本内容尝试作答。
4. 如果无法准确作答，说明文档记录不够详实（盲区），立刻补充文档，然后再次测试。

### 第 5 步：进度推进 (Advance the Plan)
1. 回到 `KB_PLAN.md`。
2. 将刚刚完美执行完毕的任务的复选框从 `[ ]` 更新为 `[x]`。
3. **重复循环**返回【第 1 步】，继续认领下一个未完成的任务，直到 `KB_PLAN.md` 中的所有复选框均被打勾完毕。
