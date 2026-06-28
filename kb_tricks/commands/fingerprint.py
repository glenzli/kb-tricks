#!/usr/bin/env python3
"""Generate and check dirty-aware kb-tricks source fingerprints."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .audit import (
    commits_match,
    git_dirty,
    git_last_commit,
    git_tracked,
    parse_frontmatter,
    relpath,
    run_git,
    sha256_file,
)


@dataclass
class FingerprintResult:
    fingerprint: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    exit_code: int = 0


@dataclass
class CheckResult:
    document: str
    file: str | None = None
    ok: bool = False
    reasons: list[str] = field(default_factory=list)
    recorded: dict[str, Any] | None = None
    current: dict[str, Any] | None = None


def normalize_source(repo: Path, source: str) -> tuple[Path, str]:
    path = Path(source)
    if path.is_absolute():
        resolved = path.resolve()
    else:
        resolved = (repo / path).resolve()
    try:
        rel = resolved.relative_to(repo.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"{source}: source is outside repo") from exc
    return resolved, rel


def source_fingerprint(repo: Path, source: str) -> FingerprintResult:
    try:
        path, rel = normalize_source(repo, source)
    except ValueError as exc:
        return FingerprintResult(errors=[str(exc)], exit_code=2)
    if not path.exists() or not path.is_file():
        return FingerprintResult(errors=[f"{rel}: file does not exist"], exit_code=2)

    tracked = git_tracked(repo, rel)
    if not tracked:
        worktree = "untracked"
        commit = None
    else:
        worktree = "dirty" if git_dirty(repo, rel) else "clean"
        commit = git_last_commit(repo, rel)

    return FingerprintResult(
        fingerprint={
            "file": rel,
            "commit": commit,
            "tracked": tracked,
            "worktree": worktree,
            "contentHash": sha256_file(path),
        }
    )


def policy_errors(
    fingerprint: dict[str, Any],
    allow_dirty: bool,
    allow_untracked: bool,
) -> list[str]:
    worktree = fingerprint.get("worktree")
    source = fingerprint.get("file")
    if worktree == "dirty" and not allow_dirty:
        return [f"{source}: worktree is dirty; commit first or pass --allow-dirty"]
    if worktree == "untracked" and not (allow_dirty or allow_untracked):
        return [
            f"{source}: file is untracked; commit first or pass --allow-untracked"
        ]
    return []


def generate_fingerprints(
    repo: Path,
    sources: list[str],
    allow_dirty: bool,
    allow_untracked: bool,
) -> tuple[list[dict[str, Any]], list[str], int]:
    fingerprints: list[dict[str, Any]] = []
    errors: list[str] = []
    exit_code = 0
    for source in sources:
        result = source_fingerprint(repo, source)
        if result.fingerprint:
            fingerprints.append(result.fingerprint)
            errors.extend(policy_errors(result.fingerprint, allow_dirty, allow_untracked))
        errors.extend(result.errors)
        exit_code = max(exit_code, result.exit_code)
    if exit_code == 0 and errors:
        exit_code = 1
    return fingerprints, errors, exit_code


def compare_fingerprint(
    repo: Path,
    document: Path,
    recorded: dict[str, Any],
    allow_dirty: bool,
    allow_untracked: bool,
) -> CheckResult:
    source = recorded.get("file")
    result = CheckResult(
        document=relpath(document, repo),
        file=str(source) if source else None,
        recorded=recorded,
    )
    if not source:
        result.reasons.append("fingerprint item missing file")
        return result

    current_result = source_fingerprint(repo, str(source))
    result.current = current_result.fingerprint
    if current_result.errors:
        result.reasons.extend(current_result.errors)
        return result
    if not current_result.fingerprint:
        result.reasons.append("could not compute current fingerprint")
        return result

    current = current_result.fingerprint
    recorded_hash = recorded.get("contentHash")
    if recorded_hash and recorded_hash != current.get("contentHash"):
        result.reasons.append("contentHash mismatch")
    if not commits_match(recorded.get("commit"), current.get("commit")):
        result.reasons.append("commit mismatch")
    if "tracked" in recorded and bool(recorded.get("tracked")) != bool(current.get("tracked")):
        result.reasons.append("tracked mismatch")
    if recorded.get("worktree") and recorded.get("worktree") != current.get("worktree"):
        result.reasons.append(
            f"worktree mismatch: recorded {recorded.get('worktree')}, current {current.get('worktree')}"
        )
    result.reasons.extend(policy_errors(current, allow_dirty, allow_untracked))
    result.ok = not result.reasons
    return result


def check_document(
    repo: Path,
    document: str,
    allow_dirty: bool,
    allow_untracked: bool,
) -> tuple[list[CheckResult], list[str], int]:
    path, rel = normalize_source(repo, document)
    if not path.exists() or not path.is_file():
        return [], [f"{rel}: document does not exist"], 2
    frontmatter = parse_frontmatter(path)
    if frontmatter is None:
        return [CheckResult(document=rel, reasons=["missing frontmatter"])], [], 1
    fingerprints = frontmatter.get("fingerprint")
    if not isinstance(fingerprints, list) or not fingerprints:
        return [CheckResult(document=rel, reasons=["missing fingerprint list"])], [], 1
    checks = [
        compare_fingerprint(repo, path, item, allow_dirty, allow_untracked)
        for item in fingerprints
        if isinstance(item, dict)
    ]
    if len(checks) != len(fingerprints):
        checks.append(CheckResult(document=rel, reasons=["invalid fingerprint item"]))
    return checks, [], 1 if any(not check.ok for check in checks) else 0


def yaml_quote(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(str(value))


def print_yaml_fingerprints(fingerprints: list[dict[str, Any]]) -> None:
    for item in fingerprints:
        print(f"- file: {yaml_quote(item.get('file'))}")
        print(f"  commit: {yaml_quote(item.get('commit'))}")
        print(f"  tracked: {yaml_quote(item.get('tracked'))}")
        print(f"  worktree: {yaml_quote(item.get('worktree'))}")
        print(f"  contentHash: {yaml_quote(item.get('contentHash'))}")


def print_check_results(checks: list[CheckResult]) -> None:
    for check in checks:
        label = "OK" if check.ok else "FAIL"
        target = check.file or check.document
        print(f"{label} {check.document}: {target}")
        for reason in check.reasons:
            print(f"  - {reason}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", help="Source files to fingerprint.")
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow dirty tracked and untracked sources.",
    )
    parser.add_argument(
        "--allow-untracked",
        action="store_true",
        help="Allow untracked sources without also allowing dirty tracked sources.",
    )
    parser.add_argument(
        "--check",
        action="append",
        default=[],
        help="Check fingerprint entries in a KB document. May be repeated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo = Path(args.repo).resolve()
    code, _, stderr = run_git(repo, ["rev-parse", "--show-toplevel"])
    if code != 0:
        print(f"not a git repository: {repo}: {stderr}", file=sys.stderr)
        return 2

    fingerprints, errors, generate_exit = generate_fingerprints(
        repo, args.sources, args.allow_dirty, args.allow_untracked
    )
    all_checks: list[CheckResult] = []
    check_errors: list[str] = []
    check_exit = 0
    for document in args.check:
        checks, doc_errors, exit_code = check_document(
            repo, document, args.allow_dirty, args.allow_untracked
        )
        all_checks.extend(checks)
        check_errors.extend(doc_errors)
        check_exit = max(check_exit, exit_code)

    exit_code = max(generate_exit, check_exit)
    if check_errors:
        exit_code = max(exit_code, 2)
    if args.json:
        print(
            json.dumps(
                {
                    "fingerprints": fingerprints,
                    "checks": [
                        {
                            "document": check.document,
                            "file": check.file,
                            "ok": check.ok,
                            "reasons": check.reasons,
                            "recorded": check.recorded,
                            "current": check.current,
                        }
                        for check in all_checks
                    ],
                    "errors": errors + check_errors,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        if fingerprints:
            print_yaml_fingerprints(fingerprints)
        if all_checks:
            print_check_results(all_checks)
        for error in errors + check_errors:
            print(f"error: {error}", file=sys.stderr)
    if exit_code == 0 and (errors or check_errors):
        return 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
