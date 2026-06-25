#!/usr/bin/env python3
"""Select bounded kb-tricks manifest tasks."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kb_audit import ALLOWED_STATES, ManifestTask, parse_manifest, relpath, strip_value


DEFAULT_STATUSES = ("planned", "stale")


@dataclass
class Selection:
    manifest: str
    total: int
    eligible: list[ManifestTask]
    selected: list[ManifestTask]
    statuses: list[str] | None
    only: list[str]
    slice_size: int
    warnings: list[str]


def normalize_text(value: str) -> str:
    return strip_value(value).lower()


def normalize_path(value: str) -> str:
    value = strip_value(value).replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value.rstrip("/").lower()


def path_matches(pattern: str, candidate: str) -> bool:
    pattern = normalize_path(pattern)
    candidate = normalize_path(candidate)
    if not pattern or not candidate:
        return False
    if candidate == pattern:
        return True
    if "/" in pattern:
        return candidate.startswith(pattern + "/")
    return Path(candidate).name.lower() == pattern


def task_matches(task: ManifestTask, pattern: str) -> bool:
    needle = normalize_text(pattern)
    if needle in {
        normalize_text(task.task_id),
        normalize_text(task.name),
        normalize_text(task.status),
    }:
        return True
    if any(needle == normalize_text(tag) for tag in task.tags):
        return True
    if task.kb and path_matches(pattern, task.kb):
        return True
    return any(path_matches(pattern, source) for source in task.sources)


def task_to_dict(task: ManifestTask) -> dict[str, Any]:
    return {
        "id": task.task_id,
        "name": task.name,
        "status": task.status,
        "kb": task.kb,
        "sources": task.sources,
        "tags": task.tags,
        "line": task.line,
        "fields": task.fields,
    }


def parse_statuses(values: list[str]) -> list[str] | None:
    if not values:
        return list(DEFAULT_STATUSES)
    normalized = [normalize_text(value) for value in values]
    if "any" in normalized:
        return None
    invalid = sorted(set(normalized) - ALLOWED_STATES)
    if invalid:
        raise ValueError(f"invalid status: {', '.join(invalid)}")
    return normalized


def select_tasks(
    manifest: Path,
    statuses: list[str] | None,
    only: list[str],
    slice_size: int,
) -> Selection:
    tasks = parse_manifest(manifest)
    warnings: list[str] = []
    invalid_task_statuses = sorted({task.status for task in tasks} - ALLOWED_STATES)
    if invalid_task_statuses:
        warnings.append(f"manifest has unknown status: {', '.join(invalid_task_statuses)}")

    eligible: list[ManifestTask] = []
    for task in tasks:
        if statuses is not None and task.status not in statuses:
            continue
        if only and not any(task_matches(task, pattern) for pattern in only):
            continue
        eligible.append(task)
    selected = eligible[:slice_size]
    return Selection(
        manifest=manifest.as_posix(),
        total=len(tasks),
        eligible=eligible,
        selected=selected,
        statuses=statuses,
        only=only,
        slice_size=slice_size,
        warnings=warnings,
    )


def print_text(selection: Selection) -> None:
    statuses = "any" if selection.statuses is None else ", ".join(selection.statuses)
    print(
        "Selected "
        f"{len(selection.selected)}/{len(selection.eligible)} eligible "
        f"manifest tasks (total {selection.total}, slice {selection.slice_size}, "
        f"status {statuses})"
    )
    for warning in selection.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for task in selection.selected:
        print(f"- {task.task_id} [{task.status}]")
        if task.kb:
            print(f"  KB: {task.kb}")
        if task.sources:
            print(f"  Sources: {', '.join(task.sources)}")
        if task.tags:
            print(f"  Tags: {', '.join(task.tags)}")


def print_json(selection: Selection, repo: Path) -> None:
    data = {
        "manifest": relpath(Path(selection.manifest), repo),
        "total": selection.total,
        "eligibleCount": len(selection.eligible),
        "selectedCount": len(selection.selected),
        "slice": selection.slice_size,
        "statuses": selection.statuses if selection.statuses is not None else "any",
        "only": selection.only,
        "warnings": selection.warnings,
        "eligible": [task_to_dict(task) for task in selection.eligible],
        "selected": [task_to_dict(task) for task in selection.selected],
    }
    print(json.dumps(data, indent=2, sort_keys=True))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument(
        "--manifest",
        default="KB_PLAN.md",
        help="Manifest path relative to repo, or an absolute path.",
    )
    parser.add_argument(
        "--slice",
        type=int,
        default=1,
        help="Maximum tasks to select. Defaults to 1.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Restrict to task id, name, tag, KB path, or source path. May be repeated.",
    )
    parser.add_argument(
        "--status",
        action="append",
        default=[],
        help=(
            "Restrict by manifest status. Defaults to planned and stale. "
            "Use --status any to include every status."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo = Path(args.repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"repo does not exist: {repo}", file=sys.stderr)
        return 2
    if args.slice < 1:
        print("--slice must be at least 1", file=sys.stderr)
        return 2
    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = repo / manifest
    manifest = manifest.resolve()
    if not manifest.exists() or not manifest.is_file():
        print(f"manifest does not exist: {manifest}", file=sys.stderr)
        return 2
    try:
        statuses = parse_statuses(args.status)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    selection = select_tasks(manifest, statuses, args.only, args.slice)
    if args.json:
        print_json(selection, repo)
    else:
        print_text(selection)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
