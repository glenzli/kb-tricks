#!/usr/bin/env python3
"""Plan bounded dev-cycle updates from deterministic impact data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .audit import (
    ManifestTask,
    commits_match,
    git_dirty,
    git_last_commit,
    git_tracked,
    in_patterns,
    parse_config,
    parse_frontmatter,
    parse_manifest,
    relpath,
    sha256_file,
)
from .impact import (
    build_impact_data,
    flatten_files,
    normalize_path,
    resolve_scope,
)


SPECIAL_FILES = {
    "configChanged": ".agent/kb/config.yaml",
    "manifestChanged": "KB_PLAN.md",
    "glossaryChanged": ".agent/kb/GLOSSARY.md",
}


def source_state(repo: Path, source: str) -> dict[str, Any]:
    rel = normalize_path(source)
    path = (repo / rel).resolve()
    state: dict[str, Any] = {
        "file": rel,
        "exists": path.exists() and path.is_file(),
        "tracked": False,
        "worktree": "missing",
        "commit": None,
        "contentHash": None,
    }
    if not state["exists"]:
        state["tracked"] = git_tracked(repo, rel)
        return state

    tracked = git_tracked(repo, rel)
    state["tracked"] = tracked
    state["contentHash"] = sha256_file(path)
    if not tracked:
        state["worktree"] = "untracked"
        return state

    state["commit"] = git_last_commit(repo, rel)
    state["worktree"] = "dirty" if git_dirty(repo, rel) else "clean"
    return state


def gate_reasons(
    states: list[dict[str, Any]],
    allow_dirty: bool,
    allow_untracked: bool,
    draft: bool,
) -> list[str]:
    if draft:
        return []
    reasons: list[str] = []
    for state in states:
        source = state["file"]
        if not state["exists"]:
            reasons.append(f"{source}: source missing")
        elif state["worktree"] == "dirty" and not allow_dirty:
            reasons.append(f"{source}: worktree dirty")
        elif state["worktree"] == "untracked" and not (allow_dirty or allow_untracked):
            reasons.append(f"{source}: source untracked")
    return reasons


def source_is_non_authoritative(
    states: list[dict[str, Any]],
    allow_dirty: bool,
    allow_untracked: bool,
    draft: bool,
) -> bool:
    if draft:
        return any(state["worktree"] in {"dirty", "untracked"} for state in states)
    if allow_dirty:
        return any(state["worktree"] in {"dirty", "untracked"} for state in states)
    if allow_untracked:
        return any(state["worktree"] == "untracked" for state in states)
    return False


def fingerprint_reasons(repo: Path, task: ManifestTask) -> list[str]:
    if not task.kb:
        return []
    path = repo / task.kb
    if not path.exists() or not path.is_file():
        return ["kb missing"]
    frontmatter = parse_frontmatter(path)
    if not frontmatter:
        return ["kb missing frontmatter"]
    fingerprints = frontmatter.get("fingerprint")
    if not isinstance(fingerprints, list) or not fingerprints:
        return ["kb missing fingerprint"]

    reasons: list[str] = []
    for item in fingerprints:
        if not isinstance(item, dict):
            reasons.append("invalid fingerprint item")
            continue
        source = item.get("file")
        if not source:
            reasons.append("fingerprint item missing file")
            continue
        current = source_state(repo, str(source))
        if not current["exists"]:
            reasons.append(f"{source}: source missing")
            continue
        if item.get("contentHash") and item.get("contentHash") != current.get("contentHash"):
            reasons.append(f"{source}: contentHash mismatch")
        if not commits_match(item.get("commit"), current.get("commit")):
            reasons.append(f"{source}: commit mismatch")
        if "tracked" in item and bool(item.get("tracked")) != bool(current.get("tracked")):
            reasons.append(f"{source}: tracked mismatch")
        if item.get("worktree") and item.get("worktree") != current.get("worktree"):
            reasons.append(
                f"{source}: worktree mismatch recorded={item.get('worktree')} current={current.get('worktree')}"
            )
    return reasons


def task_action(task: dict[str, Any], repo: Path, draft: bool) -> str:
    kb = task.get("kb")
    status = task.get("status")
    if kb and not (repo / kb).exists():
        base = "create"
    elif status == "planned":
        base = "create"
    elif status == "orphaned":
        base = "review-orphaned"
    elif status in {"deprecated", "merged-into-docs"}:
        base = "review-deprecated"
    else:
        base = "update"
    if draft and base in {"create", "update"}:
        return f"draft-{base}"
    return base


def draft_target(task_id: str) -> str:
    return f".agent/kb/_draft/{task_id}.md"


def task_by_id(tasks: list[ManifestTask]) -> dict[str, ManifestTask]:
    return {task.task_id: task for task in tasks}


def plan_task_action(
    repo: Path,
    manifest_task: ManifestTask,
    task: dict[str, Any],
    allow_dirty: bool,
    allow_untracked: bool,
    draft: bool,
) -> dict[str, Any]:
    states = [source_state(repo, source) for source in manifest_task.sources]
    blocked_reasons = gate_reasons(states, allow_dirty, allow_untracked, draft)
    match_reasons = sorted({match["reason"] for match in task.get("matchedFiles", [])})
    stale_reasons = fingerprint_reasons(repo, manifest_task)
    action = task_action(task, repo, draft)
    not_authoritative = source_is_non_authoritative(
        states, allow_dirty, allow_untracked, draft
    )
    if action in {"review-orphaned", "review-deprecated"}:
        allowed = True
    else:
        allowed = not blocked_reasons
    reasons = match_reasons + stale_reasons
    if not reasons:
        reasons = ["selected"]
    result = {
        "task": manifest_task.task_id,
        "kb": manifest_task.kb,
        "targetKb": manifest_task.kb,
        "status": manifest_task.status,
        "action": action,
        "allowed": allowed,
        "notAuthoritative": not_authoritative,
        "reasons": reasons,
        "blockedReasons": blocked_reasons,
        "matchedFiles": task.get("matchedFiles", []),
        "sourceStates": states,
    }
    if action.startswith("draft-"):
        result["draftTarget"] = draft_target(manifest_task.task_id)
    return result


def boundary_classification(config: dict[str, list[str]], path: str) -> dict[str, bool]:
    include = config.get("include", [])
    exclude = config.get("exclude", [])
    release_excluded = config.get("releaseExcluded", [])
    return {
        "included": not include or in_patterns(path, include),
        "excluded": in_patterns(path, exclude),
        "releaseExcluded": in_patterns(path, release_excluded),
    }


def plan_new_candidate(
    repo: Path,
    path: str,
    config: dict[str, list[str]],
    allow_dirty: bool,
    allow_untracked: bool,
    draft: bool,
) -> dict[str, Any] | None:
    boundary = boundary_classification(config, path)
    if not boundary["included"] or boundary["excluded"] or boundary["releaseExcluded"]:
        return None
    state = source_state(repo, path)
    if not state["exists"]:
        return None
    blocked_reasons = gate_reasons([state], allow_dirty, allow_untracked, draft)
    action = "draft-create" if draft else "create"
    result = {
        "file": normalize_path(path),
        "action": action,
        "allowed": not blocked_reasons,
        "notAuthoritative": source_is_non_authoritative(
            [state], allow_dirty, allow_untracked, draft
        ),
        "reasons": ["unmatched included source"],
        "blockedReasons": blocked_reasons,
        "sourceState": state,
        "boundary": boundary,
    }
    if action.startswith("draft-"):
        result["draftTarget"] = draft_target(Path(path).stem)
    return result


def docs_actions(docs_changes: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "file": path,
            "action": "review-existing-docs",
            "allowed": True,
            "reasons": ["docs.existing"],
        }
        for path in docs_changes
    ]


def special_actions(special_changes: dict[str, bool]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for key, changed in special_changes.items():
        if changed:
            result.append(
                {
                    "file": SPECIAL_FILES[key],
                    "action": f"review-{key.removesuffix('Changed')}",
                    "allowed": True,
                    "reasons": ["special artifact changed"],
                }
            )
    return result


def build_update_plan(
    repo: Path,
    manifest_path: Path,
    config_path: Path,
    impact: dict[str, Any],
    allow_dirty: bool,
    allow_untracked: bool,
    draft: bool,
    warnings: list[str],
) -> dict[str, Any]:
    manifest_tasks = task_by_id(parse_manifest(manifest_path))
    config = parse_config(config_path)
    config_present = config_path.exists()
    setup_warnings: list[dict[str, Any]] = list(impact.get("setupWarnings", []))
    setup_candidate_files: set[str] = set()
    if not config_present:
        setup_candidate_files = {
            path
            for path in impact["unmatchedFiles"]
            if path.startswith(".agent/kb/")
        }
        if setup_candidate_files:
            setup_warnings.append(
                {
                    "code": "missing-config-kb-support-files",
                    "message": "config missing; KB support files may be treated as source candidates",
                    "files": sorted(setup_candidate_files),
                }
            )
    actions = [
        plan_task_action(
            repo,
            manifest_tasks[task["id"]],
            task,
            allow_dirty,
            allow_untracked,
            draft,
        )
        for task in impact["selectedTasks"]
        if task["id"] in manifest_tasks
    ]
    release_excluded_changes = [
        path
        for path in impact["changedFiles"]
        if boundary_classification(config, path)["releaseExcluded"]
    ]
    candidates = [
        candidate
        for path in impact["unmatchedFiles"]
        if path not in setup_candidate_files
        for candidate in [
            plan_new_candidate(
                repo, path, config, allow_dirty, allow_untracked, draft
            )
        ]
        if candidate is not None
    ]
    blocked = [
        item
        for item in [*actions, *candidates]
        if not item["allowed"]
    ]
    return {
        "schemaVersion": 1,
        "repo": str(repo),
        "manifest": relpath(manifest_path, repo),
        "config": relpath(config_path, repo),
        "scopeMode": impact["scopeMode"],
        "scope": impact["scope"],
        "slice": impact["slice"],
        "changedFiles": impact["changedFiles"],
        "impactedTasks": impact["impactedTasks"],
        "selectedTasks": impact["selectedTasks"],
        "actions": actions,
        "blocked": blocked,
        "docsChanges": impact["docsChanges"],
        "docsActions": docs_actions(impact["docsChanges"]),
        "possibleContextDocs": impact.get("possibleContextDocs", []),
        "newKbCandidates": candidates,
        "specialChanges": impact["specialChanges"],
        "specialActions": special_actions(impact["specialChanges"]),
        "releaseExcludedChanges": release_excluded_changes,
        "setupWarnings": setup_warnings,
        "unmatchedFiles": impact["unmatchedFiles"],
        "policy": {
            "draft": draft,
            "allowDirty": allow_dirty,
            "allowUntracked": allow_untracked,
        },
        "warnings": [*impact.get("warnings", []), *warnings],
    }


def print_markdown(data: dict[str, Any]) -> None:
    print("# KB Update Plan")
    print()
    print(f"- Scope: {data['scopeMode']}")
    print(f"- Changed files: {len(data['changedFiles'])}")
    print(f"- Actions: {len(data['actions'])}")
    print(f"- Blocked: {len(data['blocked'])}")
    print(f"- New KB candidates: {len(data['newKbCandidates'])}")
    if data.get("possibleContextDocs"):
        print(f"- Possible context docs: {len(data['possibleContextDocs'])}")
    if data["actions"]:
        print()
        print("## Actions")
        for action in data["actions"]:
            label = "allowed" if action["allowed"] else "blocked"
            print(f"- {action['task']}: {action['action']} ({label})")
            for reason in action["blockedReasons"]:
                print(f"  - {reason}")
    if data["newKbCandidates"]:
        print()
        print("## New KB Candidates")
        for candidate in data["newKbCandidates"]:
            label = "allowed" if candidate["allowed"] else "blocked"
            print(f"- {candidate['file']}: {candidate['action']} ({label})")
            for reason in candidate["blockedReasons"]:
                print(f"  - {reason}")
    if data.get("possibleContextDocs"):
        print()
        print("## Possible Context Docs")
        for item in data["possibleContextDocs"]:
            print(f"- {item['file']}: {item['recommendation']}")
    if data["setupWarnings"]:
        print()
        print("## Setup Warnings")
        for warning in data["setupWarnings"]:
            print(f"- {warning['message']}")
            for path in warning["files"]:
                print(f"  - {path}")
    if data["docsActions"]:
        print()
        print("## Existing Docs")
        for action in data["docsActions"]:
            print(f"- {action['file']}: {action['action']}")
    if data["specialActions"]:
        print()
        print("## Special Artifacts")
        for action in data["specialActions"]:
            print(f"- {action['file']}: {action['action']}")
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
    parser.add_argument("--staged", action="store_true", help="Plan staged changes.")
    parser.add_argument(
        "--worktree",
        action="store_true",
        help="Plan unstaged tracked changes plus untracked files.",
    )
    parser.add_argument("--base", help="Git base commitish or branch for base...HEAD diff.")
    parser.add_argument(
        "--files",
        action="append",
        nargs="+",
        default=[],
        help="Changed files to plan. May be repeated.",
    )
    parser.add_argument("--slice", type=int, default=1, help="Maximum selected task actions.")
    parser.add_argument("--draft", action="store_true", help="Plan dirty work as draft actions.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow dirty tracked and untracked sources in the plan.",
    )
    parser.add_argument(
        "--allow-untracked",
        action="store_true",
        help="Allow untracked sources without allowing dirty tracked sources.",
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

    explicit_files = flatten_files(args.files)
    changed_files, scope, error = resolve_scope(repo, args, explicit_files)
    if error:
        print(error, file=sys.stderr)
        return 2

    manifest = (repo / args.manifest).resolve()
    config = (repo / args.config).resolve()
    if not manifest.exists():
        print(f"manifest does not exist: {manifest}", file=sys.stderr)
        return 2

    warnings: list[str] = []
    if not config.exists():
        warnings.append(f"config missing: {relpath(config, repo)}")

    impact = build_impact_data(
        repo,
        manifest,
        config,
        changed_files,
        scope,
        args.slice,
        warnings,
    )
    data = build_update_plan(
        repo,
        manifest,
        config,
        impact,
        args.allow_dirty,
        args.allow_untracked,
        args.draft,
        [],
    )
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
