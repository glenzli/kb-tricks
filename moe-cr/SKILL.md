---
name: moe-cr
description: "一个混合专家 (Mixture-of-Experts) 代码审查技能，将代码差异分发给专用的专家提示词并行处理，与知识库进行交叉验证，并生成带有风险评级的聚合报告。"
---

# MoE-CR 目标 (MoE-CR Goal)
通过将代码变更路由到专用的专家提示词库中来执行严格的多维度代码审查，每个专家被限制在单一审查维度内，最后将他们的发现聚合为一份统一的、带有风险评级的报告。

# 操作指令 (Instructions)

### 第 1 步：路由器 — 上下文分析与专家激活 (Router — Context Analysis & Expert Activation)
1. **收集差异 (Collect the Diff)**：获取待审查的代码变更（如 `git diff`，PR diff）。
2. **检测项目范式 (Detect Project Paradigm)**：检查清单文件（如 `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml` 等）和目录结构，确定项目类型（例如：REST API、CLI 工具、编译器、游戏引擎、数据管道）。
3. **检查 KB 存在性 (Check KB Presence)**：确定是否存在由 `kb-build` 为此项目构建的知识库。
4. **激活专家 (Activate Experts)**：
   - **始终执行**：第 1 层 (所有 6 个基础专家)。
   - **始终执行**：第 2 层 (1 个领域专家，动态生成)。
   - **有条件执行**：第 3 层 (KB 专家) — 仅当 KB 存在时。

---

### 第 2 步：第 1 层 — 基础专家组（并行执行 / Layer 1 — Base Expert Group）

**并行**执行所有 6 个专家。每个专家接收相同的 diff，但被约束为只审查其指定的维度。如果没有发现问题，则返回空。

#### 专家 1：架构 (Architecture)
- **关注点**：分层违规、不当耦合、依赖方向、关注点分离。
- **约束**：不要评论命名、性能或安全性。仅关注结构设计。

#### 专家 2：逻辑边界 (Logic Boundary)
- **关注点**：差一错误 (Off-by-one errors)、空值/未定义路径、未处理的边缘情况、状态机转换、竞态条件。
- **约束**：不要评论代码风格或架构。仅关注逻辑流的正确性。

#### 专家 3：安全 (Security)
- **关注点**：注入媒介、认证/授权绕过、机密信息暴露、不安全的反序列化、SSRF、路径遍历。
- **约束**：不要评论性能或可读性。仅关注攻击面。

#### 专家 4：性能 (Performance)
- **关注点**：N+1 查询、不必要的内存分配、热路径中的阻塞 I/O、错失缓存机会、算法复杂度。
- **约束**：不要评论安全性或命名。仅关注运行时效率。

#### 专家 5：可测试性 (Testability)
- **关注点**：隐藏依赖、全局状态、阻碍 Mock 的紧密耦合、缺少测试钩子、不可测试的私有逻辑。
- **约束**：不要评论性能或架构。仅关注测试的便利性。

#### 专家 6：可维护性 (Maintainability)
- **关注点**：命名清晰度、代码重复、圈复杂度、魔法数字、可读性、文档空白。
- **约束**：不要评论正确性或安全性。仅关注长期可维护性。

#### 统一输出格式（所有专家适用）
每一个发现 (Finding) 必须使用如下格式：
```
[Severity/严重程度: Critical|High|Medium|Low] [File:Line] 
Finding/发现: <简明描述>
Suggestion/建议: <可执行的修复方案>
```

---

### 第 3 步：第 2 层 — 领域专家（动态生成 / Layer 2 — Domain Expert）

1. 基于在第 1 步中检测到的范式，路由器生成**一个单一且聚焦的审查提示词**。不要使用预置的模板，而是动态生成。
2. **各范式的提示词示例**：
   - **REST API**：“作为 REST API 设计专家，请审查路由命名、HTTP 动词语义、状态码使用和资源建模。”
   - **编译器/解释器**：“作为语言实现专家，请审查 AST 遍历正确性、访问者模式的使用和 Pass 排序。”
   - **数据管道**：“作为数据工程专家，请审查幂等性、背压 (backpressure) 处理和 Schema 演进的安全性。”
3. 领域专家使用与第 1 层相同的统一输出格式。

---

### 第 4 步：第 3 层 — KB 专家（按条件执行：需要 `kb-build` KB）

> 如果项目不存在 KB，请完全跳过此步骤。

1. **指纹查找 (Fingerprint Lookup)**：通过 `fingerprint` 元数据识别哪些 KB 文档关联到了被修改的源代码文件。
2. **链路追踪 (Chain Tracing)**：沿着这些 KB 文档的 SSOT 内部链接，发现受此次 diff 影响的完整知识链路。
3. **交叉检查审计 (Cross-Check Audit)**：针对受影响的每条知识链路，分类其影响级别：

   **直接影响 (Direct Impact)** (变更代码自身记录的流程)：
   - 差异是否改变了 KB 中为**该特定文件**记录的流程或契约？
   - 示例：更改了 `auth.ts` 中 `sign()` 的参数，而 KB 记录了 `auth.ts` 的签名流程。
   - → **自动更新**：`KB-Action: UPDATE` — 知识库明确已过期。

   **间接影响 (Indirect Impact)** (虽未直接修改但在相关流程中)：
   - 差异是否**有可能破坏或影响** KB 中为依赖于该代码的**其他模块**所记录的契约/流程？
   - 示例：改变了 `validateToken()` 的返回类型，而另一个 KB 文档记录了下游的 `rbacMiddleware` 会消费该返回值。
   - → **用户决定**：`KB-Action: REVIEW` — 在报告中标记出来供人类判断。

4. **KB 新鲜度警告 (KB Freshness Warning)**：如果指纹 Commit ID 已经过期（在本次审查前就已不匹配），请作为一个注意事项提出来——交叉检查可能是基于过时的知识进行的。
5. **输出结果**：
   - 使用与第 1 层相同的统一格式。
   - 追加一个 `KB-Action` 字段说明相应的处理级别：
   ```
   # 直接影响 — 自动更新
   [Severity: High] [src/auth.ts:42]
   Finding: sign() 签名已更改；KB 记录的还是旧签名。
   Suggestion: 更新 KB 以反映新的 RS256 以及 privateKey 参数。
   KB-Action: UPDATE api/authentication.md

   # 间接影响 — 人工审查
   [Severity: Medium] [src/auth.ts:42]
   Finding: validateToken() 返回类型发生变化；KB 中记录的下游 rbacMiddleware 可能会受到影响。
   Suggestion: 验证 rbacMiddleware 是否仍然可以处理新的返回数据结构。
   KB-Action: REVIEW api/auth-flow.md (间接影响: rbac 依赖链)
   ```

---

### 第 5 步：聚合器 — 合并、去重与评级 (Aggregator — Merge, Deduplicate & Rate)

1. **收集 (Collect)** 所有专家的输出（第 1 层 + 第 2 层 + 激活时的第 3 层）。
2. **去重 (Deduplicate)**：如果多个专家标记了同一个 `[File:Line]`，将其合并为一个发现 (finding)。保留最高的严重级别并汇总建议。
3. **冲突解决 (Conflict Resolution)**：当专家的意见相互矛盾时，按以下优先级解决：
   ```
   安全性 (Security) > 正确性 (Logic Boundary) > 性能 (Performance) > 可维护性 (Maintainability)
   ```
   在报告中记录冲突以及解决的理由。
4. **风险评级 (Risk Rating)**：根据尚未解决的、严重级别最高的发现给出总体风险等级：

   | 最高级发现 | 总体风险 | 合并建议 |
   |----------------|-------------|---------------------|
   | Critical / 致命 | 🔴 Critical | **禁止合并 (Block merge)** |
   | High / 高危 | 🟠 High | 禁止合并，需要修复 |
   | Medium / 中危 | 🟡 Medium | 可以合并，但需要后续跟进 |
   | Low / 低危 | 🟢 Low | 可以正常合并 |
   | None / 无 | ✅ Clean | 可以正常合并 |

5. **最终报告结构 (Final Report Structure)**：
   ```markdown
   # 代码审查报告 (Code Review Report)
   ## 风险等级 (Risk): [🔴|🟠|🟡|🟢|✅] [级别]
   ## 概要 (Summary)
   <1-2 句的概述>
   ## 致远与高危发现 (Critical & High Findings)
   <分组列出发现>
   ## 中危与低危发现 (Medium & Low Findings)
   <分组列出发现>
   ## 知识库影响 (KB Impact) (如果适用)
   <供给 kb-update 使用的 KB-Action 项>
   ## 已解决冲突 (Conflicts Resolved)
   <专家分歧及解决方案>
   ```

# 示例 (Examples)

## 示例：审查一个向 Auth API 添加限流功能的 PR
1. **路由器 (Router)**：检测到 Node.js REST API 项目 (`package.json`)，并确认存在 KB。
2. **第 1 层 (Layer 1)** (并行执行)：
   - *Architecture (架构)*：“限流器被实现在了控制器内部，而不是作为中间件。” `[Medium]`
   - *Security (安全)*：没有发现（限流提高了安全性）。
   - *Performance (性能)*：“每个请求都要查询 Redis，但没有使用连接池。” `[High]`
   - *Logic Boundary (逻辑边界)*：“服务器重启时限流计数器会重置（使用了内存回退）。” `[High]`
   - *Testability (可测试性)*：没有发现。
   - *Maintainability (可维护性)*：没有发现。
3. **第 2 层 (Layer 2)** (领域专家 — REST API)：“响应中未设置限流相关 Header (`X-RateLimit-Remaining`)。” `[Medium]`
4. **第 3 层 (Layer 3)** (KB 专家)：KB 记录了 `请求 → AuthMiddleware → Controller` 流程。新加入的限流器被插入代码，但**并未反映在 KB 知识链中**。 `[KB-Action: UPDATE api/auth-flow.md]`。交叉检查没有发现契约破坏。
5. **聚合器 (Aggregator)**：总体风险 = 🟠 High。2 个高危发现（Redis 连接池 + 内存回退计数器），2 个中危发现。知识库需要更新。
