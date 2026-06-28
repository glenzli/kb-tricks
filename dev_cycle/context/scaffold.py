#!/usr/bin/env python3
"""Scaffold dev-cycle artifacts into a target repository."""

from __future__ import annotations

import argparse
from importlib import resources
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = PROJECT_ROOT / "templates"
PACKAGE_TEMPLATES = "dev_cycle"


@dataclass
class PlannedWrite:
    source: Path | None
    target: Path
    action: str
    content: str | None = None


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def existing_docs_entries(repo: Path) -> list[str]:
    entries: list[str] = []
    if (repo / "README.md").exists():
        entries.append("README.md")
    if (repo / "docs").is_dir():
        entries.append("docs/**")
    return entries


def template_text(name: str) -> str:
    source = TEMPLATES / name
    if source.exists():
        return source.read_text(encoding="utf-8")
    try:
        return (
            resources.files(PACKAGE_TEMPLATES)
            .joinpath("templates")
            .joinpath(name)
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise FileNotFoundError(f"template not found: {name}") from exc


def render_config(repo: Path) -> str:
    template = template_text("config.yaml")
    entries = existing_docs_entries(repo)
    if not entries:
        return template
    lines = template.splitlines()
    rendered: list[str] = []
    in_existing = False
    replaced = False
    for line in lines:
        stripped = line.strip()
        if stripped == "existing:" and line.startswith("  "):
            rendered.append(line)
            for entry in entries:
                rendered.append(f"    - {entry}")
            in_existing = True
            replaced = True
            continue
        if in_existing:
            if line.startswith("    - "):
                continue
            in_existing = False
        rendered.append(line)
    if not replaced:
        rendered.extend(["docs:", "  existing:"])
        rendered.extend(f"    - {entry}" for entry in entries)
    return "\n".join(rendered).rstrip() + "\n"


def plan_writes(repo: Path, force: bool) -> list[PlannedWrite]:
    writes = [
        PlannedWrite(None, repo / ".dev-cycle" / "context" / "config.yaml", "write", render_config(repo)),
        PlannedWrite(
            None,
            repo / ".dev-cycle" / "context" / "AGENT_GUIDE.md",
            "write",
            template_text("AGENT_GUIDE.md"),
        ),
        PlannedWrite(None, repo / "CONTEXT_PLAN.md", "write", template_text("CONTEXT_PLAN.md")),
        PlannedWrite(None, repo / ".dev-cycle" / "context" / "_draft" / ".gitkeep", "touch", ""),
        PlannedWrite(None, repo / ".dev-cycle" / "context" / "_impact" / ".gitkeep", "touch", ""),
        PlannedWrite(None, repo / ".dev-cycle" / "context" / "_validation" / ".gitkeep", "touch", ""),
    ]
    if force:
        return writes
    filtered: list[PlannedWrite] = []
    for write in writes:
        if write.target.exists():
            filtered.append(PlannedWrite(write.source, write.target, "skip", write.content))
        else:
            filtered.append(write)
    return filtered


def apply_write(write: PlannedWrite) -> None:
    if write.action == "skip":
        return
    write.target.parent.mkdir(parents=True, exist_ok=True)
    if write.action == "copy":
        if write.source is None:
            raise ValueError(f"{write.target}: copy action missing source")
        shutil.copyfile(write.source, write.target)
    elif write.action in {"write", "touch"}:
        write.target.write_text(write.content or "", encoding="utf-8")
    else:
        raise ValueError(f"unknown action: {write.action}")


def print_plan(repo: Path, writes: list[PlannedWrite]) -> None:
    for write in writes:
        print(f"{write.action.upper()} {relpath(write.target, repo)}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo = Path(args.repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"repo does not exist: {repo}", file=sys.stderr)
        return 2
    try:
        writes = plan_writes(repo, args.force)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print_plan(repo, writes)
    if args.dry_run:
        return 0
    for write in writes:
        apply_write(write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
