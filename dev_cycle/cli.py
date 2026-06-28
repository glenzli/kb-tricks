"""Thin command dispatcher for dev-cycle deterministic context tools."""

from __future__ import annotations

import importlib
import json
import sys

from . import __version__


CONTEXT_COMMANDS = {
    "audit": "dev_cycle.context.audit",
    "docs": "dev_cycle.context.docs",
    "fingerprint": "dev_cycle.context.fingerprint",
    "impact": "dev_cycle.context.impact",
    "manifest": "dev_cycle.context.manifest",
    "migrate-plan": "dev_cycle.context.migrate_plan",
    "query-lint": "dev_cycle.context.query_lint",
    "scaffold": "dev_cycle.context.scaffold",
    "update-plan": "dev_cycle.context.update_plan",
}


def command_names() -> list[str]:
    return ["self-check", *[f"context {name}" for name in sorted(CONTEXT_COMMANDS)]]


def print_help() -> None:
    commands = ", ".join(command_names())
    print("usage: dev-cycle <command> [args...]")
    print()
    print("Commands:")
    for name in command_names():
        print(f"  {name}")
    print()
    print(
        "Run `dev-cycle context <command> --help` for context command help. "
        f"Available: {commands}"
    )


def run_self_check(argv: list[str]) -> int:
    json_output = False
    if argv:
        if argv == ["--json"]:
            json_output = True
        elif argv[0] in {"-h", "--help"}:
            print("usage: dev-cycle self-check [--json]")
            print()
            print("Imports every released CLI tool module and verifies a callable main().")
            return 0
        else:
            print(f"unknown self-check argument: {argv[0]}", file=sys.stderr)
            return 2

    checks = []
    ok = True
    for name, module_name in sorted(CONTEXT_COMMANDS.items()):
        check = {"command": f"context {name}", "module": module_name, "ok": False}
        try:
            module = importlib.import_module(module_name)
            if callable(getattr(module, "main", None)):
                check["ok"] = True
            else:
                check["error"] = "missing callable main()"
        except Exception as exc:  # pragma: no cover - defensive release boundary
            check["error"] = f"{type(exc).__name__}: {exc}"
        ok = ok and check["ok"]
        checks.append(check)

    result = {
        "ok": ok,
        "version": __version__,
        "entryPoint": "dev_cycle.cli:main",
        "commands": checks,
    }
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "ok" if ok else "failed"
        print(f"dev-cycle self-check: {status}")
        for check in checks:
            suffix = "" if check["ok"] else f" ({check.get('error', 'unknown error')})"
            print(f"- {check['command']}: {check['module']}{suffix}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        print_help()
        return 0
    command = argv[0]
    if command == "self-check":
        return run_self_check(argv[1:])
    if command != "context":
        print(f"unknown command group: {command}", file=sys.stderr)
        print_help()
        return 2
    if len(argv) < 2:
        print("missing context command", file=sys.stderr)
        print_help()
        return 2
    context_command = argv[1]
    if context_command not in CONTEXT_COMMANDS:
        print(f"unknown context command: {context_command}", file=sys.stderr)
        print_help()
        return 2
    module = importlib.import_module(CONTEXT_COMMANDS[context_command])
    return int(module.main(argv[2:]))


if __name__ == "__main__":
    raise SystemExit(main())
