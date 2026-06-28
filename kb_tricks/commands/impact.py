#!/usr/bin/env python3
"""Map changed files to kb-tricks manifest tasks."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .audit import (
    ManifestTask,
    in_patterns,
    parse_config,
    parse_frontmatter,
    parse_manifest,
    relpath,
    run_git,
)
from .manifest import task_to_dict


@dataclass
class Match:
    file: str
    reason: str


@dataclass
class ImpactedTask:
    task: ManifestTask
    matches: list[Match] = field(default_factory=list)


def normalize_path(value: str) -> str:
    value = value.replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value.rstrip("/")


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_path(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def flatten_files(values: list[list[str]]) -> list[str]:
    result: list[str] = []
    for group in values:
        result.extend(group)
    return unique(result)


def changed_files_since(repo: Path, since: str) -> tuple[list[str], str | None]:
    code, stdout, stderr = run_git(repo, ["diff", "--name-only", since, "--"])
    if code != 0:
        return [], stderr or f"git diff failed for {since}"
    return unique(stdout.splitlines()), None


def changed_files_staged(repo: Path) -> tuple[list[str], str | None]:
    code, stdout, stderr = run_git(repo, ["diff", "--name-only", "--cached", "--"])
    if code != 0:
        return [], stderr or "git staged diff failed"
    return unique(stdout.splitlines()), None


def changed_files_worktree(repo: Path) -> tuple[list[str], str | None]:
    code, stdout, stderr = run_git(repo, ["diff", "--name-only", "--"])
    if code != 0:
        return [], stderr or "git worktree diff failed"
    code_untracked, stdout_untracked, stderr_untracked = run_git(
        repo, ["ls-files", "--others", "--exclude-standard"]
    )
    if code_untracked != 0:
        return [], stderr_untracked or "git untracked file scan failed"
    return unique(stdout.splitlines() + stdout_untracked.splitlines()), None


def changed_files_base(repo: Path, base: str) -> tuple[list[str], str | None]:
    code, stdout, stderr = run_git(repo, ["diff", "--name-only", f"{base}...HEAD", "--"])
    if code != 0:
        return [], stderr or f"git base diff failed for {base}"
    return unique(stdout.splitlines()), None


def task_fingerprint_files(repo: Path, task: ManifestTask) -> list[str]:
    if not task.kb:
        return []
    path = repo / task.kb
    if not path.exists() or not path.is_file():
        return []
    frontmatter = parse_frontmatter(path)
    if not frontmatter:
        return []
    files: list[str] = []
    for item in frontmatter.get("fingerprint") or []:
        if isinstance(item, dict) and item.get("file"):
            files.append(str(item["file"]))
    return unique(files)


def path_matches_file(changed: str, candidate: str) -> bool:
    changed = normalize_path(changed)
    candidate = normalize_path(candidate)
    return bool(changed and candidate and changed == candidate)


def task_matches(repo: Path, task: ManifestTask, changed: str) -> list[str]:
    reasons: list[str] = []
    if any(path_matches_file(changed, source) for source in task.sources):
        reasons.append("source")
    if task.kb and path_matches_file(changed, task.kb):
        reasons.append("kb")
    if any(path_matches_file(changed, source) for source in task_fingerprint_files(repo, task)):
        reasons.append("fingerprint")
    return reasons


def collect_impacts(repo: Path, tasks: list[ManifestTask], changed_files: list[str]) -> list[ImpactedTask]:
    by_id: dict[str, ImpactedTask] = {}
    for changed in changed_files:
        for task in tasks:
            reasons = task_matches(repo, task, changed)
            if not reasons:
                continue
            impacted = by_id.setdefault(task.task_id, ImpactedTask(task))
            for reason in reasons:
                match = Match(changed, reason)
                if match not in impacted.matches:
                    impacted.matches.append(match)
    return list(by_id.values())


def collect_docs_changes(config: dict[str, list[str]], changed_files: list[str]) -> list[str]:
    patterns = config.get("docs.existing", [])
    exclude = config.get("exclude", [])
    return [
        path
        for path in changed_files
        if in_patterns(path, patterns) and not in_patterns(path, exclude)
    ]


def collect_special_changes(changed_files: list[str]) -> dict[str, bool]:
    return {
        "configChanged": ".agent/kb/config.yaml" in changed_files,
        "manifestChanged": "KB_PLAN.md" in changed_files,
        "glossaryChanged": ".agent/kb/GLOSSARY.md" in changed_files,
    }


def impact_to_dict(impact: ImpactedTask) -> dict[str, Any]:
    data = task_to_dict(impact.task)
    data["matchedFiles"] = [
        {
            "file": match.file,
            "reason": match.reason,
        }
        for match in impact.matches
    ]
    return data


def build_impact_data(
    repo: Path,
    manifest_path: Path,
    config_path: Path,
    changed_files: list[str],
    scope: dict[str, Any],
    slice_size: int,
    warnings: list[str],
) -> dict[str, Any]:
    tasks = parse_manifest(manifest_path)
    config = parse_config(config_path)
    impacts = collect_impacts(repo, tasks, changed_files)
    docs_changes = collect_docs_changes(config, changed_files)
    impacted_files = {
        match.file
        for impact in impacts
        for match in impact.matches
    }
    special_changes = collect_special_changes(changed_files)
    matched_special = {
        ".agent/kb/config.yaml",
        "KB_PLAN.md",
        ".agent/kb/GLOSSARY.md",
    }
    matched_docs = set(docs_changes)
    unmatched = [
        path
        for path in changed_files
        if path not in impacted_files and path not in matched_docs and path not in matched_special
    ]
    return {
        "schemaVersion": 1,
        "repo": str(repo),
        "manifest": relpath(manifest_path, repo),
        "config": relpath(config_path, repo),
        "scopeMode": scope["mode"],
        "scope": scope,
        "changedFiles": changed_files,
        "impactedTasks": [impact_to_dict(impact) for impact in impacts],
        "selectedTasks": [impact_to_dict(impact) for impact in impacts[:slice_size]],
        "slice": slice_size,
        "docsChanges": docs_changes,
        "specialChanges": special_changes,
        "unmatchedFiles": unmatched,
        "warnings": warnings,
    }


def print_markdown(data: dict[str, Any]) -> None:
    print("# KB Impact Report")
    print()
    print(f"- Scope: {data['scopeMode']}")
    print(f"- Changed files: {len(data['changedFiles'])}")
    print(f"- Impacted tasks: {len(data['impactedTasks'])}")
    print(f"- Selected tasks: {len(data['selectedTasks'])} (slice {data['slice']})")
    if data["docsChanges"]:
        print(f"- Existing docs changes: {len(data['docsChanges'])}")
    if any(data["specialChanges"].values()):
        changed = [key for key, value in data["specialChanges"].items() if value]
        print("- Special changes: " + ", ".join(changed))
    if data["selectedTasks"]:
        print()
        print("## Selected Tasks")
        for task in data["selectedTasks"]:
            matches = ", ".join(
                f"{item['file']} ({item['reason']})" for item in task["matchedFiles"]
            )
            print(f"- {task['id']} [{task['status']}]: {matches}")
    if data["unmatchedFiles"]:
        print()
        print("## Unmatched Files")
        for path in data["unmatchedFiles"]:
            print(f"- {path}")
    if data["warnings"]:
        print()
        print("## Warnings")
        for warning in data["warnings"]:
            print(f"- {warning}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--manifest", default="KB_PLAN.md", help="Manifest path.")
    parser.add_argument("--config", default=".agent/kb/config.yaml", help="Boundary config path.")
    parser.add_argument("--since", help="Git commitish to diff against.")
    parser.add_argument("--staged", action="store_true", help="Map staged changes.")
    parser.add_argument(
        "--worktree",
        action="store_true",
        help="Map unstaged tracked changes plus untracked files.",
    )
    parser.add_argument("--base", help="Git base commitish or branch for base...HEAD diff.")
    parser.add_argument(
        "--files",
        action="append",
        nargs="+",
        default=[],
        help="Changed files to map. May be repeated.",
    )
    parser.add_argument("--slice", type=int, default=1, help="Maximum selected impacted tasks.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def resolve_scope(
    repo: Path, args: argparse.Namespace, explicit_files: list[str]
) -> tuple[list[str], dict[str, Any] | None, str | None]:
    requested = []
    if args.since:
        requested.append("since")
    if explicit_files:
        requested.append("files")
    if args.staged:
        requested.append("staged")
    if args.worktree:
        requested.append("worktree")
    if args.base:
        requested.append("base")

    if len(requested) != 1:
        return [], None, "pass exactly one scope option: --since, --files, --staged, --worktree, or --base"

    mode = requested[0]
    if mode == "files":
        return explicit_files, {"mode": "files", "files": explicit_files}, None
    if mode == "since":
        changed, error = changed_files_since(repo, args.since)
        return changed, {"mode": "since", "since": args.since, "files": []}, error
    if mode == "staged":
        changed, error = changed_files_staged(repo)
        return changed, {"mode": "staged", "staged": True, "files": []}, error
    if mode == "worktree":
        changed, error = changed_files_worktree(repo)
        return changed, {"mode": "worktree", "worktree": True, "files": []}, error

    changed, error = changed_files_base(repo, args.base)
    return changed, {"mode": "base", "base": args.base, "files": []}, error


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo = Path(args.repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"repo does not exist: {repo}", file=sys.stderr)
        return 2
    if args.slice < 1:
        print("--slice must be at least 1", file=sys.stderr)
        return 2
    explicit_files = flatten_files(args.files)
    warnings: list[str] = []
    changed_files, scope, error = resolve_scope(repo, args, explicit_files)
    if error:
        print(error, file=sys.stderr)
        return 2
    manifest = (repo / args.manifest).resolve()
    config = (repo / args.config).resolve()
    if not manifest.exists():
        print(f"manifest does not exist: {manifest}", file=sys.stderr)
        return 2
    if not config.exists():
        warnings.append(f"config missing: {relpath(config, repo)}")
    data = build_impact_data(
        repo,
        manifest,
        config,
        changed_files,
        scope,
        args.slice,
        warnings,
    )
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
