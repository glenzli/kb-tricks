#!/usr/bin/env python3
"""Run the dev-cycle release smoke checks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_command(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd))
    try:
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, text=True, check=False)
    except FileNotFoundError as exc:
        print(f"missing executable: {exc.filename}", file=sys.stderr)
        return 127
    return proc.returncode


def resolve_kb(value: str | None) -> str:
    if value:
        return value
    kb = shutil.which("kb")
    if kb is not None:
        return kb
    local = PROJECT_ROOT / ".venv" / "bin" / "kb"
    if local.exists():
        return str(local)
    return "kb"


def cli_command(installed: bool, kb: str | None, *args: str) -> list[str]:
    if installed:
        return [resolve_kb(kb), *args]
    return [sys.executable, "-B", "-m", "kb_tricks.cli", *args]


def smoke_commands(
    installed: bool,
    include_tests: bool,
    include_git_check: bool,
    kb: str | None = None,
) -> list[list[str]]:
    commands: list[list[str]] = []
    if include_tests:
        commands.append([sys.executable, "-B", "-m", "unittest", "discover", "tests"])
    commands.extend(
        [
            cli_command(installed, kb, "self-check", "--json"),
            cli_command(installed, kb, "query-lint", "--json", "templates/query-answer.md"),
        ]
    )
    if include_git_check:
        commands.append(["git", "diff", "--check"])
    return commands


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--installed",
        action="store_true",
        help="Run CLI checks through an installed `kb` executable.",
    )
    parser.add_argument("--kb", help="Path to an installed kb executable.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unittest discovery.")
    parser.add_argument("--skip-git-check", action="store_true", help="Skip git diff --check.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    include_tests = not args.skip_tests
    include_git_check = not args.skip_git_check
    commands = smoke_commands(args.installed, include_tests, include_git_check, args.kb)
    with tempfile.TemporaryDirectory(prefix="dev-cycle-smoke-") as tmp:
        repo = Path(tmp) / "project"
        repo.mkdir()
        commands.insert(
            3 if include_tests else 2,
            cli_command(args.installed, args.kb, "scaffold", "--repo", str(repo), "--dry-run"),
        )
        for cmd in commands:
            code = run_command(cmd)
            if code != 0:
                return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
