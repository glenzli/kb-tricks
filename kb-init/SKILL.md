---
name: kb-init
description: "初始化项目的高级编排技能。它会自动驱动 kb-plan 生成 KB_PLAN.md Manifest，并在请求用户确认后启动 kb-build 的小步文档沉淀切片。"
---

# 知识库初始化编排目标 (KB Init Orchestration Goal)
提供可控的知识库初始化体验。通过协调 `kb-plan` 和 `kb-build` 两个子技能，实现“AI 规划 -> 用户审查并确认 -> AI 小步执行”的工作流。默认不全量执行，除非用户明确要求 `until-complete`。

# 工作流指令 (Workflow Instructions)

作为高级编排 Agent，你按照以下流程自主驱动，期间**不要越过用户确认或 bounded execution 约束**。初始化流程必须优先保护仓库可控性，而不是追求一次性全部完成。

### 第 1 阶段：自主规划 (Autonomous Planning)
1. 向用户输出状态提示：“正在进行项目架构的宏观扫描与文档规划，请稍候...”
2. 如果当前环境可访问 `kb-tricks/tools/kb_scaffold.py`，先执行或建议执行 `python3 tools/kb_scaffold.py --repo <target> --dry-run`，展示将创建的 `.agent/kb/config.yaml`、`KB_PLAN.md` 和保留目录。只有在用户确认初始化空白结构时，才执行非 dry-run；不要用 `--force` 覆盖已有文件，除非用户明确要求。
3. **静默调用 `kb-plan` 技能**：遵循 `kb-plan/SKILL.md` 中的指令，先识别 `.agent/kb/config.yaml` 或 Proposed Artifact Boundary，不深入代码细节地分析整个仓库，并生成 `KB_PLAN.md` Manifest。
4. 等待 `KB_PLAN.md` 文件在文件系统中成功生成并落盘。

### 第 2 阶段：交互式确认 (Interactive Confirmation)
1. 规划书生成完毕后，**暂停当前执行流**。
2. 将 `KB_PLAN.md` 的核心内容（或摘要）展示给用户。
3. 也就是向用户索取权限：“我已经生成了初步的知识库 Manifest `KB_PLAN.md`。您可以直接打开该文件查看或修改边界配置、已有文档对比、噪音目录和计划生成的文档焦点。默认我只会执行 `kb-build slice 1`。**您是否确认计划并允许我开始第一个小切片？（回复 'ok' 开始；如需全量请明确回复 'until-complete'）**”
4. 挂起等待用户的输入。

### 第 3 阶段：小步执行 (Bounded Execution)
1. 一旦用户回复确认（如 "ok", "确认", "yes"）或者用户修改完 `KB_PLAN.md` 给出了继续指令。
2. 立即调用 `kb-build` 技能，并传递指令：“请严格遵照 `KB_PLAN.md` 中的状态执行 `slice 1`，除非用户明确给出更大的 slice 或 `until-complete`。”
3. 监控 `kb-build` 的产物：每一次 `kb-build` 将某个条目更新为 `[built]` 并生成完一个文件后，在控制台上向用户输出一行简短的进度日志（例如：“已生成 API 认证模块地图: `.agent/kb/api/auth.md`”）。
4. 如果用户明确回复 `until-complete`，可以重复调用 `kb-build` 的后续 slice，直到没有 eligible 任务。否则，完成第一个 slice 后停止并询问是否继续下一批。
5. 如果遇到 dirty/untracked source 阻塞，尊重 `kb-build` 的 write gate，不要自动使用 `allow-dirty`。提示用户先提交源码或改用 `draft`。

### 第 4 阶段：完工汇报 (Completion Report)
1. 当前 slice 结束后，向用户输出总结：“本轮知识库初始化切片已完成。已生成的认知地图文档、语义词汇表 (`GLOSSARY.md`) 和验证产物已存放在指定的文件夹中。若要继续，请请求下一轮 slice。”
2. 退出工作流。
