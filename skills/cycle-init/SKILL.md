---
name: cycle-init
description: "初始化 dev-cycle 上下文的薄编排 recipe：scaffold、context-plan、用户确认、首个 context-build 小切片。"
---

# Cycle Init

Use when a repository needs first-time dev-cycle context setup.

## Hard Rules

- Do not overwrite existing scaffold files unless the user explicitly asks for `--force`.
- Do not run a full Context build by default. Default execution is `context-build slice 1`.
- Stop for user confirmation after `CONTEXT_PLAN.md` is created or updated.
- Respect dirty-source gates from `context-build`; do not auto-use `allow-dirty`.

## Steps

1. Check for `.dev-cycle/context/config.yaml`, `.dev-cycle/context/AGENT_GUIDE.md`, and `CONTEXT_PLAN.md`.
2. If scaffold is missing and `tools/context_scaffold.py` is available, run or propose:
   ```bash
   python3 tools/context_scaffold.py --repo . --dry-run
   ```
3. Run `context-plan` or follow `../context-plan/SKILL.md` to produce or update `CONTEXT_PLAN.md`.
4. Show the user the planned boundary, existing-docs comparison, and first few tasks.
5. Ask for confirmation before building.
6. On confirmation, run `context-build slice 1` unless the user requested a different slice.
7. Stop after the slice and report created Context, validation files, blockers, and next eligible tasks.

## Output

- Scaffold status.
- Manifest summary.
- First build slice result.
- Next recommended command or skill.

