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

# 示例 (Examples)

## 示例：为一个 Express API 项目的鉴权模块构建知识库
1. **计划载入 (Load Plan)**：读取 `KB_PLAN.md`，发现第一个未完成任务：
   ```
   - [ ] `.agent/kb/api/auth-flow.md`
     - **Sources**: `src/api/auth.ts`, `src/middleware/rbac.ts`
     - **Focus**: JWT 令牌的分发、校验机制以及基于角色的访问控制验证链路。
   ```
2. **精准阅读**：仅读取 `src/api/auth.ts` 和 `src/middleware/rbac.ts` 两个文件。
3. **生成文档**：在 `.agent/kb/api/auth-flow.md` 中生成认知地图，包含：
   - Frontmatter（`id: "api-auth-flow"`, `fingerprint` 含两个源码文件的当前 commit hash）。
   - 一个 Mermaid 时序图展示 `Request → rbacMiddleware → JWT Verify → Controller` 流程。
   - SSOT 链接指向 `.agent/kb/core/database.md`（引用用户表结构，不重复定义）。
4. **更新词汇表**：在 `GLOSSARY.md` 中添加 `JWT | Bearer Token, Auth Token | [auth-flow.md](./api/auth-flow.md)`。
5. **自我评估**：
   - *架构问题*："如果要新增一个 'SuperAdmin' 角色，需要修改哪些文件？" — 仅从 KB 回答，成功引用了 `rbac.ts` 的角色枚举。
   - *边界问题*："公钥轮换时尚未过期的 Token 如何处理？" — KB 中未记载，标记为盲区，补充文档后重试通过。
6. **推进计划**：将 `KB_PLAN.md` 中该条目更新为 `[x]`，进入下一个任务。

# 联动触发 (Cross-Skill Triggers)
> 以下建议在对应技能已安装时可选触发。调用时使用技能名称，Agent 会自动查找对应的 SKILL.md。如果技能未安装，在结果中告知用户并建议手动执行对应操作。

| 触发条件 | 建议调用技能 | 目的 |
|---|---|---|
| `KB_PLAN.md` 中所有任务均已完成 | `kb-audit` | 对新构建的知识库进行全面健康体检 |

