"""Thin command dispatcher for kb-tricks deterministic tools."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import tools


COMMANDS = {
    "audit": "tools.kb_audit",
    "docs": "tools.kb_docs",
    "fingerprint": "tools.kb_fingerprint",
    "impact": "tools.kb_impact",
    "manifest": "tools.kb_manifest",
    "scaffold": "tools.kb_scaffold",
}


def ensure_legacy_tool_imports() -> None:
    tools_dir = Path(tools.__file__).resolve().parent
    tools_path = str(tools_dir)
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)


def print_help() -> None:
    commands = ", ".join(sorted(COMMANDS))
    print("usage: kb <command> [args...]")
    print()
    print("Commands:")
    for name in sorted(COMMANDS):
        print(f"  {name}")
    print()
    print(f"Run `kb <command> --help` for command-specific help. Available: {commands}")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        print_help()
        return 0
    command = argv[0]
    if command not in COMMANDS:
        print(f"unknown command: {command}", file=sys.stderr)
        print_help()
        return 2
    ensure_legacy_tool_imports()
    module = importlib.import_module(COMMANDS[command])
    return int(module.main(argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
