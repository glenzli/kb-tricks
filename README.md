# dev-skeleton

<p align="center">
  <img src="assets/dev-skeleton-banner.webp" width="100%" alt="dev-skeleton banner: a central code workspace held within a sparse, open structural framework">
</p>

[English](#english) | [中文](#中文)

## English

Source-first project skeletons for LLM-assisted development.

`dev-skeleton` ships concise, LLM-readable core skills, conditional references, and copyable templates. It is not tied to any specific agent runtime, and it does not ship a CLI, code indexer, KB builder, or project-management workflow.

The repository is also an installable Codex plugin. Its manifest packages the complete `skills/`
and bundle-level `templates/` from this same source tree; local marketplaces may point at the
repository without copying individual skills into a global skill directory.

`SKELETON.md` orients the model before source reading. The development skill supplies boundary
principles while source remains authoritative; neither replaces implementation inspection or the
model's judgment.

### Rules

- Source is authority: code, config, tests, release artifacts, and maintained docs.
- Skeleton is orientation: purpose, boundaries, truth sources, architectural priors, stable owners,
  and a bounded semantic map.
- Do not mirror modules, classes, functions, call graphs, APIs, or current behavior.
- Let the model inspect source for the task at hand.
- Update skeletons only when durable intent, constraints, truth sources, or review preferences change.
- Routine implementation changes should not update skeletons.

### Source As Index

Source-first is economical only when the code tree preserves clear semantic ownership. Code that shares one intent, lifecycle, invariant, or failure policy should stay together; responsibilities that change independently should separate. Large cohesive modules are acceptable. Mixed-responsibility hubs are not.

Root `SKELETON.md` should route readers to subsystems, while source entries and optional subsystem
skeletons route them to semantic owners. README remains free to serve product, installation, public
documentation, or package-specific needs. Implementation facts still belong in source; the skeleton
records stable ownership and navigation, not a second inventory of the codebase.

The `maintain-source-cohesion` skill supplies reusable architectural judgment for changes that put
those boundaries under pressure. It is guidance, not a mandatory growth-review procedure.

### Layout

```text
.codex-plugin/
  plugin.json
skills/
  skeleton-init/
  skeleton-refresh/
  skeleton-audit/
  maintain-source-cohesion/
    references/
  review-skeleton/
templates/
  SKELETON.md
  REVIEW_SKELETON.md
  AGENTS.md
```

Root `SKELETON.md`, `REVIEW_SKELETON.md`, and `AGENTS.md` describe this repo itself.

### Use

Copy the templates into a target repo. Keep each selected skill directory intact so its conditional
references and invocation metadata remain available. `skeleton-init` also consumes the maintained
bundle-level `templates/`; distribute it with the dev-skeleton repository or plugin bundle rather
than as an isolated directory:

- `skeleton-init`: create initial skeleton files, including a bounded semantic map.
- `skeleton-refresh`: update skeletons after durable direction changes.
- `skeleton-audit`: find over-detail, stale claims, and source-first violations.
- `maintain-source-cohesion`: keep the code tree navigable while adding, moving, or splitting responsibilities.
- `review-skeleton`: review source and diffs using project review preferences.

Conditional references for `maintain-source-cohesion`, loaded only when the task touches their boundary:

- `async-ui.md`: asynchronous lifecycles, state projection, declarative UI, and runtime interaction.
- `native-cross-language.md`: native module ownership, ABI/FFI contracts, bridges, and build graphs.
- `large-payload-and-acceleration.md`: large buffers, caching, zero-copy ownership, tiling, and acceleration.
- `test-topology-and-migration.md`: test ownership, reachability, legacy topology, and suite migration.

The plugin is the preferred Codex distribution unit. Individual skill directories remain portable
when they declare no bundle-level asset, but `skeleton-init` and its templates must travel as the
complete repository/plugin bundle.

### Boundaries

- No persistent implementation KB.
- No generated or exhaustive source index.
- No CLI.
- No standalone test, onboarding, release, or multi-agent workflow.

### Maintenance

When a skeleton starts explaining how the code works today, delete that detail and point back to source.
Keep broadly triggered skills short. Move stack-specific guidance into references that are loaded only when the task touches that boundary.

## 中文

面向 LLM 辅助开发的 source-first 项目骨架。

`dev-skeleton` 提供精简、可被 LLM 直接阅读的核心 skill、条件 reference 和可复制模板。它不绑定任何特定 agent runtime，也不提供 CLI、代码索引、KB 构建器或项目管理流程。

本仓库同时也是可安装的 Codex plugin。Plugin manifest 从同一源码树打包完整的 `skills/` 和
bundle 顶层 `templates/`；本地 marketplace 可以直接指向本仓库，不再把单个 skill 复制或链接
到全局 skill 目录。

`SKELETON.md` 在模型阅读源码前提供方向；开发期 skill 在源码仍然权威的前提下补充边界判断，两者都不代替对实现的阅读，也不替代模型自身决策。

### 规则

- 源码优先：代码、配置、测试、release 产物和维护中的文档才是权威。
- 骨架只做定向：记录目的、边界、事实来源、架构先验、稳定 owner 和有界语义地图。
- 不镜像模块、类、函数、调用图、API 或当前行为。
- 让模型根据当前任务动态阅读源码。
- 只有长期意图、约束、事实来源或 review 偏好变化时，才更新 skeleton。
- 日常实现改动不应该触发 skeleton 更新。

### 源码作为索引

只有当代码树保持清晰的语义所有权时，source-first 才是经济的。共享同一意图、生命周期、不变量或失败策略的代码应当聚合；因不同原因独立变化的责任应当分离。大而内聚的模块可以保留，混合责任的中心文件不应继续增长。

根 `SKELETON.md` 负责指向子系统，源码入口和必要时的子系统 skeleton 负责指向语义 owner。
README 可以继续承担产品介绍、安装、公共文档或包说明，不必兼任内部导航。实现事实仍以源码为准；
Skeleton 只记录稳定所有权和导航，不维护第二份代码清单。

`maintain-source-cohesion` skill 在边界受到压力时提供可复用的架构判断，但不规定一套强制增长审查流程。

### 结构

```text
.codex-plugin/
  plugin.json
skills/
  skeleton-init/
  skeleton-refresh/
  skeleton-audit/
  maintain-source-cohesion/
    references/
  review-skeleton/
templates/
  SKELETON.md
  REVIEW_SKELETON.md
  AGENTS.md
```

根目录的 `SKELETON.md`、`REVIEW_SKELETON.md` 和 `AGENTS.md` 描述的是本仓库自身。

### 使用

把模板复制到目标仓库。分发 skill 时必须保留完整目录，确保 agent 可以读取其中的 reference
和调用元数据。`skeleton-init` 还会读取 bundle 顶层维护的 `templates/`，因此不能把它作为孤立
目录分发；应随 dev-skeleton 仓库或插件 bundle 一起提供：

- `skeleton-init`：创建包含有界语义地图的初始 skeleton 文件。
- `skeleton-refresh`：在长期方向变化后更新 skeleton。
- `skeleton-audit`：检查过度细节、陈旧声明和 source-first 违规。
- `maintain-source-cohesion`：在增加、移动或拆分责任时保持代码树可导航。
- `review-skeleton`：基于项目 review 偏好审查源码和 diff。

`maintain-source-cohesion` 的条件 reference 只在任务触及相应边界时加载：

- `async-ui.md`：异步生命周期、状态投影、声明式 UI 和运行时交互。
- `native-cross-language.md`：原生模块所有权、ABI/FFI 契约、bridge 和构建图。
- `large-payload-and-acceleration.md`：大型缓冲区、缓存、零拷贝所有权、分块和加速。
- `test-topology-and-migration.md`：测试归属、可达性、遗留拓扑和 suite 迁移。

Codex 中优先以 plugin 作为完整分发单元。没有声明 bundle 级资源的 skill 仍可按完整目录移植；
但 `skeleton-init` 与其模板必须随完整仓库/plugin bundle 一起分发。

### 边界

- 不做持久化实现 KB。
- 不做生成式或穷举式源码索引。
- 不做 CLI。
- 不做独立的测试、新人引导、release 或多 agent 工作流。

### 维护

当 skeleton 开始解释“当前代码如何工作”时，删掉这部分细节，让模型回到源码。
高频触发的 skill 必须保持精简；技术栈相关指导应放入仅在任务触及相应边界时才读取的 reference。
