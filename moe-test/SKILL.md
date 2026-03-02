---
name: moe-test
description: "一个混合专家测试审查技能，对测试代码进行多维度专家级审查，与知识库中记录的契约交叉验证，发现覆盖盲区和质量问题。"
---

# MoE-Test 目标 (MoE-Test Goal)
对测试代码进行多维度专家级审查，找出覆盖盲区、断言质量问题和可维护性隐患。核心价值在于**测试 ↔ KB 的闭环验证**：知识库记录了系统"应该怎么工作"，测试验证它"确实这么工作"——两者交叉比对才能发现真正的盲区。

# 操作指令 (Instructions)

### 第 1 步：路由器 — 收集测试代码与上下文 (Router — Collect Tests & Context)
1. **收集测试文件**：获取待审查的测试文件或测试目录（如 `__tests__/`, `test/`, `*_test.go` 等）。
2. **检测测试框架**：识别使用的测试框架（Jest, Vitest, pytest, Go testing, JUnit 等）和断言库。
3. **检查 KB 存在性**：确定是否存在由 `kb-build` 构建的知识库。
4. **激活专家**：
   - **始终执行**：第 1 层（4 个测试审查专家）。
   - **始终执行**：第 2 层（1 个框架专家，动态生成）。
   - **有条件执行**：第 3 层（KB 契约覆盖专家）— 仅当 KB 存在时。

---

### 第 2 步：第 1 层 — 测试审查专家组（并行执行 / Layer 1 — Test Review Experts）

**并行**执行所有 4 个专家。每个专家接收相同的测试代码，但被约束为只审查其指定的维度。

#### 专家 1：覆盖率缺口 (Coverage Gaps)
- **关注点**：哪些公共函数/方法完全没有被测试、哪些代码分支（if/else/switch）没有对应的测试用例、是否存在"只测试了 happy path 而忽略了 error path"的情况。
- **约束**：不要评论断言质量或代码风格。仅关注"有没有测到"。

#### 专家 2：断言质量 (Assertion Quality)
- **关注点**：断言是否验证了**真正的契约/行为**而非实现细节（如：断言返回值结构 vs 断言内部方法被调用了几次）、是否存在"空断言"（测试运行了但什么也没验证）、断言的粒度是否足够（如只检查了 `status === 200` 但没验证 response body）。
- **约束**：不要评论覆盖率或测试结构。仅关注"断言验证的是不是正确的东西"。

#### 专家 3：测试可维护性 (Test Maintainability)
- **关注点**：过度 Mock（Mock 了太多依赖导致测试与真实行为脱节）、脆弱的 Snapshot 测试（snapshot 太大或太容易被无关改动触发更新）、测试间的隐式依赖（执行顺序依赖、共享可变状态）、魔法数字和硬编码。
- **约束**：不要评论覆盖率或正确性。仅关注"这些测试好不好维护"。

#### 专家 4：边界条件 (Boundary Conditions)
- **关注点**：空值/null/undefined 输入、空集合、极值（MAX_INT, 空字符串）、并发/超时场景、非法输入和错误传播路径。
- **约束**：不要评论代码风格。仅关注"极端情况有没有被测试覆盖"。

#### 统一输出格式（所有专家适用）
```
[Severity/严重程度: Critical|High|Medium|Low] [File:Line/Function]
Finding/发现: <简明描述>
Suggestion/建议: <具体的测试用例建议或修复方案>
```

---

### 第 3 步：第 2 层 — 框架专家（动态生成 / Layer 2 — Framework Expert）

1. 基于检测到的测试框架，路由器动态生成**一个聚焦的审查提示词**。
2. **各框架的提示词示例**：
   - **Jest/Vitest**："作为 Jest 专家，请审查 `describe/it` 组织结构、`beforeEach/afterEach` 清理逻辑、Mock 恢复 (`jest.restoreAllMocks()`) 和异步测试的正确处理。"
   - **pytest**："作为 pytest 专家，请审查 Fixture 的作用域 (scope) 设置、parametrize 的使用合理性、conftest.py 的组织和 monkeypatch 的清理。"
   - **Go testing**："作为 Go 测试专家，请审查 table-driven test 模式的使用、`t.Helper()` 标注、`t.Parallel()` 的安全性和 TestMain 的清理逻辑。"
3. 使用与第 1 层相同的统一输出格式。

---

### 第 4 步：第 3 层 — KB 契约覆盖专家（按条件执行 / Layer 3 — KB Contract Coverage Expert）

> 如果项目不存在 KB，请完全跳过此步骤。

#### 4.0 KB 新鲜度门控 (KB Freshness Gate)
与 `moe-cr` 和 `moe-design` 一致：读取相关 KB 文件的 fingerprint，如果过期则跳过 Layer 3，在最终报告中输出警告。

#### 4.1 契约提取 (Contract Extraction)
*(仅在通过新鲜度门控后执行)*
1. 从 KB 中读取与被测源码相关的知识文档。
2. 提取 KB 中明确记录的**关键契约**：
   - 公共 API 签名和返回值约定。
   - 跨模块交互流程（如 Mermaid 图中的步骤）。
   - 设计决策中提到的约束条件（如"超时必须不超过 5 秒"）。
   - 边界行为（如"输入为空时返回 404"）。

#### 4.2 契约 ↔ 测试交叉比对 (Contract-Test Cross-Check)
将提取的契约逐条与现有测试进行比对：

| KB 契约状态 | 判定 | 行动 |
|---|---|---|
| 契约有对应测试覆盖 | ✅ 已覆盖 | 无需操作 |
| 契约无对应测试 | ⛔ 盲区 | 输出为 Critical/High 级发现 |
| 测试存在但断言不匹配 KB 描述 | ⚠️ 偏移 | 输出为 Medium 级发现，可能是 KB 过期或测试过期 |

#### 4.3 输出格式
```
[Severity: High] [Contract: auth.sign() 必须使用 RS256]
Finding: KB (.agent/kb/api/auth.md) 记录了 sign() 使用 RS256 签名，但测试中未验证签名算法类型。
Suggestion: 添加测试用例验证 sign() 输出的 JWT header 中 alg === 'RS256'。
KB-Ref: .agent/kb/api/auth.md#签名流程
```

---

### 第 5 步：聚合器 — 合并与评级 (Aggregator — Merge & Rate)

1. **收集**所有专家的输出。
2. **去重**：合并指向同一函数/文件的发现。
3. **冲突解决**：优先级排序：
   ```
   KB 契约盲区 > 覆盖率缺口 > 断言质量 > 边界条件 > 可维护性
   ```
4. **测试健康评级 (Test Health Rating)**：

   | 最高级发现 | 评级 | 建议 |
   |---|---|---|
   | Critical / 致命 | 🔴 **Unsafe** | 核心契约缺乏测试保护，存在回归风险 |
   | High / 高危 | 🟠 **Weak** | 存在显著覆盖盲区 |
   | Medium / 中危 | 🟡 **Adequate** | 基本覆盖，但有改进空间 |
   | Low / 低危 | 🟢 **Good** | 测试质量良好 |
   | None / 无 | ✅ **Excellent** | 测试全面且高质量 |

5. **最终报告结构**：
   ```markdown
   # 测试审查报告 (Test Review Report)
   ## 测试健康度 (Health): [🔴|🟠|🟡|🟢|✅] [级别]
   ## 概要 (Summary)
   <1-2 句的概述>
   ## KB 契约覆盖分析 (Contract Coverage) (如果适用)
   <契约 ↔ 测试比对结果表格>
   ## 致命与高危发现 (Critical & High Findings)
   <分组列出发现>
   ## 中危与低危发现 (Medium & Low Findings)
   <分组列出发现>
   ```

# 示例 (Examples)

## 示例：审查一个鉴权模块的测试文件
1. **路由器 (Router)**：检测到 Jest 框架，确认存在 KB。
2. **第 1 层 (Layer 1)** (并行执行)：
   - *Coverage Gaps (覆盖率)*："`refreshToken()` 函数完全没有测试。" `[High]`
   - *Assertion Quality (断言质量)*："`login()` 测试只检查了 `status === 200`，未验证返回的 token 结构和过期时间。" `[Medium]`
   - *Maintainability (可维护性)*："`authService` 被 Mock 了 12 个方法，测试与真实行为严重脱节。" `[Medium]`
   - *Boundary Conditions (边界)*：没有测试过期 Token 刷新和并发登录冲突。`[High]`
3. **第 2 层 (Layer 2)** (框架专家 — Jest)："`afterEach` 中缺少 `jest.restoreAllMocks()`，Mock 可能泄漏到其他测试。" `[Medium]`
4. **第 3 层 (Layer 3)** (KB 契约覆盖)：KB 记录了 3 个关键契约。`sign()` 使用 RS256 — ✅ 已覆盖。`rbacMiddleware` 角色优先级链 — ⛔ 无测试。`Token 过期后返回 401` — ⛔ 无测试。
5. **聚合器 (Aggregator)**：测试健康度 = 🔴 Unsafe。2 个 KB 契约盲区，2 个高危覆盖缺口。

# 联动触发 (Cross-Skill Triggers)
> 以下建议在对应技能已安装时可选触发。调用时使用技能名称，Agent 会自动查找对应的 SKILL.md。如果技能未安装，在结果中告知用户并建议手动执行对应操作。

| 触发条件 | 建议调用技能 | 目的 |
|---|---|---|
| 发现 ⚠️ 契约偏移（测试与 KB 描述不匹配） | `kb-update` | KB 可能已过期，刷新后重新验证 |

