"""Thin command dispatcher for dev-cycle deterministic context tools."""

from __future__ import annotations

import importlib
import json
import sys

from . import __version__


COMMANDS = {
    "audit": "kb_tricks.commands.audit",
    "docs": "kb_tricks.commands.docs",
    "fingerprint": "kb_tricks.commands.fingerprint",
    "impact": "kb_tricks.commands.impact",
    "manifest": "kb_tricks.commands.manifest",
    "migrate-plan": "kb_tricks.commands.migrate_plan",
    "query-lint": "kb_tricks.commands.query_lint",
    "scaffold": "kb_tricks.commands.scaffold",
    "update-plan": "kb_tricks.commands.update_plan",
}


def command_names() -> list[str]:
    return sorted([*COMMANDS, "self-check"])


def print_help() -> None:
    commands = ", ".join(command_names())
    print("usage: kb <command> [args...]")
    print()
    print("Commands:")
    for name in command_names():
        print(f"  {name}")
    print()
    print(f"Run `kb <command> --help` for command-specific help. Available: {commands}")


def run_self_check(argv: list[str]) -> int:
    json_output = False
    if argv:
        if argv == ["--json"]:
            json_output = True
        elif argv[0] in {"-h", "--help"}:
            print("usage: kb self-check [--json]")
            print()
            print("Imports every released CLI tool module and verifies a callable main().")
            return 0
        else:
            print(f"unknown self-check argument: {argv[0]}", file=sys.stderr)
            return 2

    checks = []
    ok = True
    for name, module_name in sorted(COMMANDS.items()):
        check = {"command": name, "module": module_name, "ok": False}
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
        "entryPoint": "kb_tricks.cli:main",
        "commands": checks,
    }
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "ok" if ok else "failed"
        print(f"kb self-check: {status}")
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
    if command not in COMMANDS:
        print(f"unknown command: {command}", file=sys.stderr)
        print_help()
        return 2
    module = importlib.import_module(COMMANDS[command])
    return int(module.main(argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
