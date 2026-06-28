---
name: cycle-init
description: "初始化 dev-cycle 上下文的薄编排 recipe：scaffold、kb-plan、用户确认、首个 kb-build 小切片。"
---

# Cycle Init

Use when a repository needs first-time dev-cycle context setup.

## Hard Rules

- Do not overwrite existing scaffold files unless the user explicitly asks for `--force`.
- Do not run a full KB build by default. Default execution is `kb-build slice 1`.
- Stop for user confirmation after `KB_PLAN.md` is created or updated.
- Respect dirty-source gates from `kb-build`; do not auto-use `allow-dirty`.

## Steps

1. Check for `.agent/kb/config.yaml`, `.agent/kb/AGENT_GUIDE.md`, and `KB_PLAN.md`.
2. If scaffold is missing and `tools/kb_scaffold.py` is available, run or propose:
   ```bash
   python3 tools/kb_scaffold.py --repo . --dry-run
   ```
3. Run `kb-plan` or follow `../kb-plan/SKILL.md` to produce or update `KB_PLAN.md`.
4. Show the user the planned boundary, existing-docs comparison, and first few tasks.
5. Ask for confirmation before building.
6. On confirmation, run `kb-build slice 1` unless the user requested a different slice.
7. Stop after the slice and report created KB, validation files, blockers, and next eligible tasks.

## Output

- Scaffold status.
- Manifest summary.
- First build slice result.
- Next recommended command or skill.

