# dev-skeleton

<p align="center">
  <img src="assets/dev-skeleton-banner.webp" width="100%" alt="dev-skeleton banner: a central code workspace held within a sparse, open structural framework">
</p>

[中文](#中文) · [English](#english)

---

<a id="中文"></a>

## 中文

`dev-skeleton` 是一组面向 LLM 辅助开发的仓库定向文件、skill 和模板。它帮助 agent 先找到项目的目的、边界和事实来源，再按任务阅读实际源码。

它不维护第二份实现说明，也不提供 CLI、代码索引、知识库构建或项目管理流程。

### 包含内容

- `SKELETON.md`：项目目的、稳定边界、事实来源和有限的导航。
- `REVIEW_SKELETON.md`：审查重点与明确的阻止项。
- `AGENTS.md`：面向 agent 的仓库约束。
- `skills/`：初始化、刷新、审计、结构维护和审查 skill。
- `templates/`：上述三个定向文件的可复制模板。

Skeleton 记录稳定的判断依据和导航，不复述模块、API 或当前行为。代码、配置、测试、发布产物和维护中的文档仍是实现事实的来源。

### 在 Codex 中安装

```bash
codex plugin marketplace add glenzli/marketplace --ref main
codex plugin add dev-skeleton@glenzli-marketplace
```

Marketplace 提供经过验证的发布快照；本仓库用于开发。安装或更新时始终从已注册的 marketplace 显式选择 `dev-skeleton`。

### 使用

将 `templates/` 中需要的文件复制到目标仓库，并保留所选 skill 的完整目录及其调用元数据和条件 reference。

- `skeleton-init`：为尚未采用这套文件的仓库建立初始定向。
- `skeleton-refresh`：只在长期意图、边界或事实来源改变时更新定向文件。
- `skeleton-audit`：检查冗余实现说明、陈旧声明和 source-first 违规。
- `maintain-source-cohesion`：在职责增加、移动或拆分时判断合适的语义所有权。
- `review-skeleton`：根据项目的审查偏好评估源码和变更。

`skeleton-init` 依赖 bundle 顶层的 `templates/`，因此应随完整仓库或 plugin bundle 分发，不能作为孤立目录使用。

### 项目导航

- [插件清单](.codex-plugin/plugin.json)
- [Skill 说明](skills/README.md)
- [模板](templates/)
- [本仓库的 Skeleton](SKELETON.md)
- [本仓库的审查约束](REVIEW_SKELETON.md)

## English

`dev-skeleton` is a set of repository-orientation files, skills, and templates for LLM-assisted development. It helps an agent find a project's purpose, boundaries, and sources of fact before reading the source required by a task.

It does not maintain a second implementation manual, or provide a CLI, code indexer, knowledge-base builder, or project-management workflow.

### Contents

- `SKELETON.md`: project purpose, durable boundaries, sources of fact, and bounded navigation.
- `REVIEW_SKELETON.md`: review priorities and explicit blocking conditions.
- `AGENTS.md`: repository constraints for agents.
- `skills/`: initialization, refresh, audit, structural-maintenance, and review skills.
- `templates/`: copyable templates for the three orientation files.

Skeletons record durable judgment and navigation; they do not repeat modules, APIs, or current behavior. Code, configuration, tests, release artifacts, and maintained documentation remain the sources for implementation facts.

### Install with Codex

```bash
codex plugin marketplace add glenzli/marketplace --ref main
codex plugin add dev-skeleton@glenzli-marketplace
```

The marketplace provides validated release snapshots; this repository is for development. Install or update `dev-skeleton` explicitly from the registered marketplace.

### Use

Copy the files you need from `templates/` into a target repository. Keep each selected skill directory intact, including its invocation metadata and conditional references.

- `skeleton-init`: establish initial orientation for a repository that does not yet use these files.
- `skeleton-refresh`: update orientation only when durable intent, boundaries, or sources of fact change.
- `skeleton-audit`: find redundant implementation descriptions, stale claims, and source-first violations.
- `maintain-source-cohesion`: judge semantic ownership when responsibilities grow, move, or split.
- `review-skeleton`: assess source and changes against the project's review preferences.

`skeleton-init` depends on the bundle-level `templates/` directory. Distribute it with the complete repository or plugin bundle, not as an isolated directory.

### Project navigation

- [Plugin manifest](.codex-plugin/plugin.json)
- [Skill notes](skills/README.md)
- [Templates](templates/)
- [This repository's Skeleton](SKELETON.md)
- [This repository's review constraints](REVIEW_SKELETON.md)

## License

MIT. See [LICENSE](LICENSE).
