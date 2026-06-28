# kb-tricks 技能套件评测方案 (Benchmark Proposal)

为了科学地评测 `kb-build` 及其衍生技能（如 `kb-update`, `kb-audit`, `moe-cr`）的有效性，我们需要结合**静态制品检查**、**动态检索测试**、**可控执行测试**和**维护抗衰退测试**，构建一条完整的评测 Benchmark 链路。

## 1. 测试基准库准备 (Baseline Repositories)

选择 2-3 个复杂度适中、但具有不同架构范式的开源项目作为测试床：
1. **典型后端服务**：如基于 Express / FastAPI / Spring Boot 的项目。用于测试系统对 API 契约、数据流和状态转换的理解。
2. **典型前端/客户端项目**：如小型的 React / Vue / Flutter 项目。用于测试系统对组件树、状态管理和生命周期的理解。
3. **工具/库类项目**：无外部服务依赖的纯逻辑代码库，测试核心算法和边界条件提取。

## 2. 四维评测维度

### 维度一：静态资产与协议检查 (Static Artifact & Spec Assessment)

在目标仓库上先运行 `kb-plan` 生成 `KB_PLAN.md` Manifest，再用 bounded 模式运行 `kb-build slice N`。对生成的知识库目录（如 `.agent/kb/`）进行自动化或人工评估：

*   **信噪比 (Signal-to-Noise Ratio)**：评估是否有效过滤了样板代码（如纯粹的 Get/Set，无逻辑的 DTO），是否提炼出了模块间的核心交互关系（认知地图）。
*   **Manifest 合规率 (Manifest Compliance)**：
    *   检查 `KB_PLAN.md` 是否使用 `planned / built / stale / orphaned / merged-into-docs / deprecated` 状态。
    *   检查每个任务是否有稳定 `ID`、`KB`、`Sources`、`Focus`、`Tags` 和 `Status`。
    *   检查是否记录 artifact boundary 和 existing docs comparison。
*   **合规率 (Compliance Rate)**：
    *   检查是否 100% 的生成文件都在 Frontmatter 头部包含规范的 YAML `fingerprint`（包含关联源码文件路径、commit、tracked、worktree、contentHash）。
    *   检查 dirty/untracked source 是否默认阻塞正式 KB，或只进入 `_draft/` / `_impact/`。
    *   检查是否为每个 built 任务生成 `.agent/kb/_validation/<task-id>.md`。
*   **格式可用性 (Syntax Validity)**：
    *   验证所有 Mermaid 图表语法是否合法且可渲染。
    *   验证 Markdown 相对链接是否连通（无死链），以及是否遵守了单一事实来源（SSOT）原则。
*   **确定性工具检查 (Deterministic Tool Check)**：
    *   运行 `python3 tools/kb_audit.py --repo <target> --fail-on dead-links --fail-on stale --min-score B`。
    *   运行 `python3 tools/kb_audit.py --repo <target> --write-index .agent/kb/index.json` 并检查 index 是否稳定生成。

### 维度二：隔离问答能力审核 (Isolated RAG Audit)

这是测试该技能是否实现了“认知地图”初衷的最核心手段。测试系统生成的知识图谱是否真正有用，且没有幻觉：

*   **评测过程**：
    1. 启动一个**完全没有源码访问权限**的全新 Agent 实例（仅将其上下文挂载于生成的知识库目录）。
    2. 基于项目的业务和技术难点，向 Agent 提出 3 个设计维度的“刁钻”问题（如：如何安全地扩展某个接口而不破坏依赖、某段核心逻辑的异常边界在哪）。
*   **评估指标**：
    *   **准确率 (Accuracy)**：回答的解决思路是否正确。
    *   **溯源率 (Citation Rate)**：回答中是否明确标注来源类型：KB / 源码 fallback / 现有 docs / 推断。
    *   **推断隔离率 (Inference Isolation Rate)**：没有直接来源支撑的内容是否被隔离在“不确定性与推断”区块。
    *   **盲点识别率 (Blindspot Rate)**：面对源码中有但在构建阶段未被知识库记录的细节，Agent 是否能诚实地指出这是“知识库盲区（Blindspot）”而不是捏造幻觉（Hallucination）。

### 维度三：可控执行测试 (Bounded Execution Test)

测试技能是否真的默认小步执行，而不是在大仓库中失控。

*   **评测过程**：
    1. 在包含 10+ 个候选任务的仓库上运行 `kb-build`，不提供任何 slice 参数。
    2. 再分别运行 `kb-build slice 2`、`kb-build only <task-id>`、`kb-build dry-run`。
*   **评估指标**：
    *   **默认 bounded 率**：无参数时是否只处理 1 个任务。
    *   **选择准确率**：`only <task-id>` 是否只读取和写入目标任务。
    *   **dry-run 纯度**：`dry-run` 是否不改动文件，只报告计划。
    *   **dirty gate 命中率**：相关源码 dirty/untracked 时是否阻塞正式 KB，或只写 draft/impact。

### 维度四：抗衰退与可维护性测试 (Resilience & Maintainability Test)

测试构建的知识链路是否具备长期的生命力，此步需要联动 `kb-update` 进行验收：

*   **评测过程**：
    1. 在基准测试仓库中提交一个“破坏性”的改动（如修改核心中间件的方法签名、移除某个组件或重构核心数据表结构）。
    2. 触发 `kb-update since <commit>` 或 `kb-update files <path>` 执行 diff-first 增量维护逻辑。
    3. 再制造一个 dirty worktree 改动，验证正式 KB 是否默认阻塞。
*   **评估指标**：
    *   **精准定位 (Precision Navigation)**：系统能否根据 Manifest、fingerprint 和 diff 范围，直接命中受影响的 1~2 个过时文档，而不是重写或重新通读大量无关文档。
    *   **级联一致性 (Cascade Consistency)**：系统能否沿着已建立的 Markdown 知识图谱链接（如 SSOT 内部引用），顺藤摸瓜更新受影响的下游文档（例如：核心 API 的改动自动反馈到了鉴权文档的补充说明中）。
    *   **指纹刷新准确率 (Fingerprint Refresh Accuracy)**：更新后 `commit`、`tracked`、`worktree` 和 `contentHash` 是否与当前文件一致。
    *   **验证刷新率 (Validation Refresh Rate)**：变更 KB 是否同步更新 `_validation/<task-id>.md`。
