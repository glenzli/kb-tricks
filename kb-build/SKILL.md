---
name: kb-build
description: "一个高级执行技能，它按小切片读取并执行 KB_PLAN.md Manifest，利用认知建图流水线构建知识库文档并落盘验证产物。"
---

# 知识库构建目标 (KB Builder Goal)
严格参照前置规划生成的 `KB_PLAN.md` Manifest 执行小步、可控的分块施工。生成高信噪比、带有 dirty-aware 源码指纹、并经过落盘验证的组件认知地图文档。

# 前置条件 (Prerequisites)
- 项目中已经存在由 `kb-plan` 技能生成的 `KB_PLAN.md` 文件。如果不存在，请先中止执行并提示用户运行 `kb-plan`。
- 如果存在 `.agent/kb/config.yaml`，必须遵守其中的 include / exclude / releaseExcluded / docs.existing 边界。

# 调用契约 (Invocation Contract)
由于本项目当前是 skill 套件而非完整 CLI，下列参数以用户自然语言或 Agent 指令形式生效：

| 参数 | 含义 |
|---|---|
| `slice N` | 本轮最多处理 N 个 manifest 任务。默认 `slice 1`。 |
| `only <id|tag|path>` | 只处理匹配的任务 ID、标签、KB 路径或源码路径。 |
| `dry-run` | 只列出将读取的源码、将写入的 KB、将更新的索引和验证产物，不落盘。 |
| `plan-only` | 只检查 Manifest 与边界，不生成 KB 文档。 |
| `draft` | dirty 或 untracked 源码只写入 `.agent/kb/_draft/`，不更新正式 KB。 |
| `allow-dirty` | 用户显式允许基于 dirty/untracked 源码写正式 KB；必须标记 `notAuthoritative: true`。 |
| `until-complete` | 用户显式允许循环处理到无剩余 eligible 任务。未声明时禁止自动全量执行。 |

**默认行为**：`slice 1`，正式 KB 只允许 clean tracked source，dirty/untracked source 进入阻塞或 draft。

# 操作指令 (Instructions)

### 第 1 步：计划载入与小步选择 (Load Plan & Bounded Selection)
1. 读取 `KB_PLAN.md`。
2. 将旧版 `[ ]` 任务视为 `[planned]`，将 `[x]` 任务视为 `[built]`。
3. 选择状态为 `[planned]` 或 `[stale]` 的任务；跳过 `[built]`、`[merged-into-docs]`、`[deprecated]`、`[orphaned]`，除非用户明确指定 `only`。
4. 应用 `only <id|tag|path>` 过滤。
5. 应用 `slice N` 限制。默认只处理 **1 个**任务。禁止默认执行到全部完成。
6. 如果用户指定 `dry-run` 或 `plan-only`，输出本轮将处理的任务、源码、目标 KB、验证文件和词汇表变更后停止，不落盘。
7. 精准地阅读任务中 `Sources` 所列出的源码文件。

### 第 2 步：正式 KB 写入门控 (Authoritative Write Gate)
1. 对每个任务的 `Sources` 检查 Git 状态：
   - clean tracked source：允许写入正式 `.agent/kb/**/*.md`。
   - dirty tracked source：默认阻塞正式写入。
   - untracked source：默认阻塞正式写入。
   - deleted source：不要构建，标记任务为 `orphaned` 候选并建议运行 `kb-update`。
2. 如果存在 dirty/untracked source：
   - 未指定 `draft` 或 `allow-dirty`：停止该任务，报告阻塞原因并建议先提交或改用 `draft`。
   - 指定 `draft`：写入 `.agent/kb/_draft/<task-id>.md`，不更新正式 KB 文档状态为 `built`。
   - 指定 `allow-dirty`：允许写正式 KB，但 frontmatter 必须包含 `notAuthoritative: true` 和 dirty-aware fingerprint；最终报告必须警告该 KB 不应进入发布或 CI 信任链。

### 第 3 步：构建认知地图文档 (Build Cognitive Map Document)
为选定的任务生成知识库 Markdown 文件，并遵从以下规范：

1. **标准元数据 (Frontmatter)**：每个 KB 文件**必须**在头部包含 YAML Frontmatter 区块。
   可参考 `templates/kb-doc.md`；稳定字段定义见 `spec/KB_SPEC.md`。
   ```yaml
   ---
   id: "module-unique-id"
   title: "Module Name or Feature"
   status: "built"
   notAuthoritative: false
   fingerprint:
     - file: "src/path/to/source_file.ext"  # 与任务清单中的 Sources 对应
       commit: "current-git-commit-hash-or-null"
       tracked: true
       worktree: "clean"
       contentHash: "sha256:..."
   tags: ["tag1", "tag2"]
   ---
   ```
   - clean tracked 文件：`tracked: true`, `worktree: clean`, `commit` 为当前文件最后提交，`contentHash` 为当前内容哈希。
   - dirty tracked 文件：`tracked: true`, `worktree: dirty`, `contentHash` 为当前脏内容哈希；正式 KB 默认禁止，除非 `allow-dirty`。
   - untracked 文件：`tracked: false`, `worktree: untracked`, `commit: null`；正式 KB 默认禁止。
   - 如果仓库中存在 `tools/kb_fingerprint.py`，优先使用它生成或检查 fingerprint，避免手工拼写元数据。
2. **高度聚焦 (High Signal)**：重点回答模块间的“交互契约”和“设计权衡”，忽略在阅读代码时可以直接一目了然的琐碎调用栈。
3. **可视化交互 (Visual Interaction)**：如果内容涉及多组件联动或状态流转，必须手写 Mermaid 时序图或状态图。
4. **内部链接 (SSOT)**：使用相对链接指向已有的其他 KB 文档，不抄写重复定义。
5. **权威边界声明**：如果文档来自 draft 或 `allow-dirty`，必须在正文开头声明它不是权威 KB，查询时只能作为临时上下文。

### 第 4 步：更新词汇表 (Update Glossary)
1. 检查或创建全局的 `.agent/kb/GLOSSARY.md`。
2. 提取刚才写好的正式 KB 文档中的核心业务术语，更新至词汇表的 Markdown 表格中。draft 文档中的术语不要写入正式 `GLOSSARY.md`，除非用户显式要求。
   | 术语 / 关键字 | 同义词 | 目标 KB 文档链接 |
   |---|---|---|

### 第 5 步：清空上下文自我评估并落盘 (Context-Cleared Validation Artifact)
为了保证文档并非依赖你大脑内部的临时源码记忆，在生成阶段完成且落地写入完毕后，就当前写入的这篇文档执行一次校验，并把验证产物写入 `.agent/kb/_validation/<task-id>.md`：

可参考 `templates/validation.md`；稳定字段定义见 `spec/KB_SPEC.md`。

1. 设计 1 个架构问题和 1 个边界条件问题（共 2 个刁钻问题）。
2. 在脑内抹除刚刚看过的相关源码的细节记忆。
3. **仅凭借**刚生成的文本内容尝试作答。
4. 如果无法准确作答，说明文档记录不够详实（盲区），立刻补充文档，然后再次测试。
5. 验证文件必须记录：
   ```markdown
   # Validation: <task-id>

   - **KB**: `.agent/kb/...`
   - **Source Mode**: `clean` / `draft` / `allow-dirty`
   - **Validated At**: `YYYY-MM-DD`

   ## Questions
   ### Q1 Architecture
   - **Question**: ...
   - **KB-only Answer**: ...
   - **Citations**: ...
   - **Result**: pass/fail

   ### Q2 Boundary
   - **Question**: ...
   - **KB-only Answer**: ...
   - **Citations**: ...
   - **Result**: pass/fail

   ## Blindspots
   - ...
   ```

### 第 6 步：进度推进 (Advance the Manifest)
1. 回到 `KB_PLAN.md`。
2. 将成功写入正式 KB 且通过验证的任务状态更新为 `[built]`，并更新 `Status: built`、`LastValidated: YYYY-MM-DD`。
3. draft 模式下不要把任务标记为 `built`；可记录 `Draft: .agent/kb/_draft/<task-id>.md`。
4. 如果本轮已达到 `slice N`，停止并汇报剩余任务。只有用户明确指定 `until-complete` 时，才允许返回第 1 步继续处理下一批。

# 示例 (Examples)

## 示例：为一个 Express API 项目的鉴权模块构建知识库
1. **计划载入 (Load Plan)**：读取 `KB_PLAN.md`，发现第一个未完成任务：
   ```
   - [planned] api-auth-flow
     - **ID**: `api-auth-flow`
     - **KB**: `.agent/kb/api/auth-flow.md`
     - **Sources**: `src/api/auth.ts`, `src/middleware/rbac.ts`
     - **Focus**: JWT 令牌的分发、校验机制以及基于角色的访问控制验证链路。
   ```
2. **门控检查**：确认两个源码文件都是 clean tracked source。若 `auth.ts` dirty，则默认阻塞正式 KB，建议提交或使用 `draft`。
3. **精准阅读**：仅读取 `src/api/auth.ts` 和 `src/middleware/rbac.ts` 两个文件。
4. **生成文档**：在 `.agent/kb/api/auth-flow.md` 中生成认知地图，包含：
   - Frontmatter（`id: "api-auth-flow"`, `fingerprint` 含两个源码文件的 commit、worktree 状态和 contentHash）。
   - 一个 Mermaid 时序图展示 `Request → rbacMiddleware → JWT Verify → Controller` 流程。
   - SSOT 链接指向 `.agent/kb/core/database.md`（引用用户表结构，不重复定义）。
5. **更新词汇表**：在 `GLOSSARY.md` 中添加 `JWT | Bearer Token, Auth Token | [auth-flow.md](./api/auth-flow.md)`。
6. **自我评估并落盘**：
   - *架构问题*："如果要新增一个 'SuperAdmin' 角色，需要修改哪些文件？" — 仅从 KB 回答，成功引用了 `rbac.ts` 的角色枚举。
   - *边界问题*："公钥轮换时尚未过期的 Token 如何处理？" — KB 中未记载，标记为盲区，补充文档后重试通过。
   - 写入 `.agent/kb/_validation/api-auth-flow.md`。
7. **推进 Manifest**：将 `KB_PLAN.md` 中该条目更新为 `[built]`，本轮达到默认 `slice 1` 后停止。

# 联动触发 (Cross-Skill Triggers)
> 以下建议在对应技能已安装时可选触发。调用时使用技能名称，Agent 会自动查找对应的 SKILL.md。如果技能未安装，在结果中告知用户并建议手动执行对应操作。

| 触发条件 | 建议调用技能 | 目的 |
|---|---|---|
| 当前 slice 完成 | `kb-audit` | 对本轮新增或修改的 KB 做轻量健康检查 |
| 用户明确要求全量完成且 `KB_PLAN.md` 中所有 eligible 任务均已完成 | `kb-audit` | 对新构建的知识库进行全面健康体检 |
