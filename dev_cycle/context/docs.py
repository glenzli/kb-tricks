#!/usr/bin/env python3
"""Inventory existing docs for dev-cycle planning and querying."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audit import (
    LinkCheck,
    ManifestTask,
    check_links,
    parse_config,
    parse_manifest,
    pattern_matches,
    relpath,
    sha256_file,
    slugify,
    strip_value,
)


COMPARISON_STATES = {"planned", "built", "stale", "merged-into-docs"}
GENERIC_TAGS = {
    "api",
    "audit",
    "cache",
    "ci",
    "cli",
    "config",
    "docs",
    "documentation",
    "preview",
    "release",
    "source",
    "test",
    "testing",
    "verification",
}
SEVERITY_SCORE = {"high": 3, "medium": 2, "low": 1}
GENERAL_DOC_NAMES = {"README.md", "RELEASE.md", "ROADMAP.md", "CHANGELOG.md"}
GENERAL_DOC_PREFIXES = ("docs/", "spec/")


@dataclass
class ExistingDoc:
    path: str
    title: str | None
    headings: list[dict[str, Any]]
    content_hash: str
    matched_patterns: list[str]
    links: list[LinkCheck]


def heading_slug(value: str) -> str:
    return slugify(value).lower()


def clean_heading(value: str) -> str:
    value = value.strip().strip("#").strip()
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    return value.strip()


def extract_headings(path: Path) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = pattern.match(line)
        if not match:
            continue
        title = clean_heading(match.group(2))
        if not title:
            continue
        headings.append(
            {
                "level": len(match.group(1)),
                "title": title,
                "slug": heading_slug(title),
                "line": line_no,
            }
        )
    return headings


def markdown_candidates(repo: Path) -> list[Path]:
    return sorted(
        path
        for path in repo.rglob("*.md")
        if path.is_file() and ".git" not in path.parts
    )


def collect_existing_docs(
    repo: Path,
    patterns: list[str],
    exclude: list[str] | None = None,
) -> tuple[list[ExistingDoc], list[str]]:
    docs: list[ExistingDoc] = []
    matched_patterns: set[str] = set()
    exclude_patterns = exclude or []
    for path in markdown_candidates(repo):
        rel = relpath(path, repo)
        if any(pattern_matches(rel, pattern) for pattern in exclude_patterns):
            continue
        matches = [pattern for pattern in patterns if pattern_matches(rel, pattern)]
        if not matches:
            continue
        matched_patterns.update(matches)
        headings = extract_headings(path)
        docs.append(
            ExistingDoc(
                path=rel,
                title=headings[0]["title"] if headings else None,
                headings=headings,
                content_hash=sha256_file(path),
                matched_patterns=matches,
                links=check_links(path, repo),
            )
        )
    unmatched = [pattern for pattern in patterns if pattern not in matched_patterns]
    return docs, unmatched


def field_value(task: ManifestTask, field: str) -> str:
    wanted = field.lower().replace(" ", "")
    for key, value in task.fields.items():
        if key.lower().replace(" ", "") == wanted:
            return strip_value(value)
    return ""


def docs_comparison_summary(tasks: list[ManifestTask]) -> dict[str, Any]:
    required = [task for task in tasks if task.status in COMPARISON_STATES]
    covered = [
        task.task_id
        for task in required
        if field_value(task, "Docs Comparison")
    ]
    missing = [task.task_id for task in required if task.task_id not in covered]
    coverage = 100.0 if not required else round((len(covered) / len(required)) * 100.0, 2)
    return {
        "requiredCount": len(required),
        "coveredCount": len(covered),
        "coverage": coverage,
        "covered": covered,
        "missing": missing,
    }


def text_for_doc(repo: Path, doc: ExistingDoc) -> str:
    return (repo / doc.path).read_text(encoding="utf-8").lower()


def doc_slugs(doc: ExistingDoc) -> set[str]:
    values = {Path(doc.path).stem}
    if doc.title:
        values.add(doc.title)
    values.update(str(heading["title"]) for heading in doc.headings)
    return {heading_slug(value) for value in values if heading_slug(value)}


def task_slugs(task: ManifestTask) -> set[str]:
    values = {task.task_id, task.name}
    if task.context:
        values.add(Path(task.context).stem)
    return {heading_slug(value) for value in values if heading_slug(value)}


def strong_source_mentions(sources: list[str]) -> bool:
    for source in sources:
        normalized = source.replace("\\", "/")
        if normalized in GENERAL_DOC_NAMES:
            continue
        if normalized.startswith(GENERAL_DOC_PREFIXES):
            continue
        if normalized.endswith(".md"):
            continue
        return True
    return False


def duplicate_severity(reasons: list[str], source_mentions: list[str]) -> str:
    if source_mentions and strong_source_mentions(source_mentions):
        return "high"
    if source_mentions:
        return "medium"
    if any(reason.startswith("shared-title-or-slug:") for reason in reasons):
        return "medium"
    return "low"


def duplicate_hints(repo: Path, docs: list[ExistingDoc], tasks: list[ManifestTask]) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    doc_texts = {doc.path: text_for_doc(repo, doc) for doc in docs}
    for task in tasks:
        if task.status == "deprecated":
            continue
        task_slug_set = task_slugs(task)
        for doc in docs:
            reasons: list[str] = []
            shared_slugs = sorted(task_slug_set & doc_slugs(doc))
            if shared_slugs:
                reasons.append("shared-title-or-slug: " + ", ".join(shared_slugs))
            lower_text = doc_texts[doc.path]
            source_mentions = [source for source in task.sources if source.lower() in lower_text]
            if source_mentions:
                reasons.append("source-mentioned: " + ", ".join(source_mentions))
            specific_tag_mentions = [
                tag
                for tag in task.tags
                if tag.lower() in lower_text and heading_slug(tag) not in GENERIC_TAGS
            ]
            generic_tag_mentions = [
                tag
                for tag in task.tags
                if tag.lower() in lower_text and heading_slug(tag) in GENERIC_TAGS
            ]
            if specific_tag_mentions:
                reasons.append("tag-mentioned: " + ", ".join(specific_tag_mentions))
            if generic_tag_mentions and reasons:
                reasons.append("generic-tag-mentioned: " + ", ".join(generic_tag_mentions))
            if not reasons:
                continue
            severity = duplicate_severity(reasons, source_mentions)
            hints.append(
                {
                    "taskId": task.task_id,
                    "taskStatus": task.status,
                    "doc": doc.path,
                    "severity": severity,
                    "score": SEVERITY_SCORE[severity],
                    "sourceMentionKind": (
                        "source"
                        if strong_source_mentions(source_mentions)
                        else "docs"
                        if source_mentions
                        else None
                    ),
                    "reasons": reasons,
                }
            )
    return sorted(
        hints,
        key=lambda item: (-item["score"], item["taskId"], item["doc"]),
    )


def dead_links(docs: list[ExistingDoc]) -> list[dict[str, Any]]:
    return [
        {
            "source": doc.path,
            "target": link.target,
            "line": link.line,
        }
        for doc in docs
        for link in doc.links
        if not link.ok
    ]


def doc_to_dict(doc: ExistingDoc) -> dict[str, Any]:
    return {
        "path": doc.path,
        "title": doc.title,
        "headings": doc.headings,
        "contentHash": doc.content_hash,
        "matchedPatterns": doc.matched_patterns,
        "links": [
            {
                "target": link.target,
                "line": link.line,
                "ok": link.ok,
            }
            for link in doc.links
        ],
    }


def collect_docs_data(repo: Path, config_path: Path, manifest_path: Path) -> dict[str, Any]:
    config = parse_config(config_path)
    patterns = config.get("docs.existing", [])
    docs, unmatched = collect_existing_docs(repo, patterns, config.get("exclude", []))
    tasks = parse_manifest(manifest_path)
    hints = duplicate_hints(repo, docs, tasks)
    return {
        "schemaVersion": 1,
        "repo": str(repo),
        "config": relpath(config_path, repo),
        "manifest": relpath(manifest_path, repo),
        "patterns": patterns,
        "unmatchedPatterns": unmatched,
        "existingDocs": [doc_to_dict(doc) for doc in docs],
        "docsComparison": docs_comparison_summary(tasks),
        "duplicateHints": hints,
        "duplicateHintCount": len(hints),
        "duplicateHintSeverityCounts": {
            severity: len([hint for hint in hints if hint["severity"] == severity])
            for severity in ["high", "medium", "low"]
        },
        "deadLinks": dead_links(docs),
        "warnings": warnings(config_path, manifest_path, patterns),
    }


def warnings(config_path: Path, manifest_path: Path, patterns: list[str]) -> list[str]:
    result: list[str] = []
    if not config_path.exists():
        result.append(f"config missing: {config_path}")
    if not manifest_path.exists():
        result.append(f"manifest missing: {manifest_path}")
    if config_path.exists() and not patterns:
        result.append("docs.existing is empty")
    return result


def print_markdown(data: dict[str, Any], duplicate_limit: int) -> None:
    print("# Context Existing Docs Report")
    print()
    print(f"- Config: `{data['config']}`")
    print(f"- Manifest: `{data['manifest']}`")
    print(f"- Existing docs: {len(data['existingDocs'])}")
    comparison = data["docsComparison"]
    print(
        "- Docs Comparison coverage: "
        f"{comparison['coveredCount']}/{comparison['requiredCount']} "
        f"({comparison['coverage']:.2f}%)"
    )
    if data["unmatchedPatterns"]:
        print("- Unmatched patterns: " + ", ".join(data["unmatchedPatterns"]))
    if comparison["missing"]:
        print()
        print("## Missing Docs Comparison")
        for task_id in comparison["missing"]:
            print(f"- {task_id}")
    if data["deadLinks"]:
        print()
        print("## Dead Links")
        for link in data["deadLinks"]:
            print(f"- {link['source']}:{link['line']} -> {link['target']}")
    if data["duplicateHints"]:
        print()
        total = len(data["duplicateHints"])
        visible = data["duplicateHints"] if duplicate_limit < 0 else data["duplicateHints"][:duplicate_limit]
        print(f"## Duplicate Hints ({len(visible)}/{total})")
        for hint in visible:
            print(
                f"- [{hint['severity']}] {hint['taskId']} <-> {hint['doc']}: "
                f"{'; '.join(hint['reasons'])}"
            )
        omitted = total - len(visible)
        if omitted > 0:
            print(f"- ... {omitted} more omitted; use --summary-json, --json, or --duplicate-limit -1 for more.")
    if data["warnings"]:
        print()
        print("## Warnings")
        for warning in data["warnings"]:
            print(f"- {warning}")


def summary_data(data: dict[str, Any], duplicate_limit: int = 5) -> dict[str, Any]:
    visible_hints = data["duplicateHints"] if duplicate_limit < 0 else data["duplicateHints"][:duplicate_limit]
    grouped_hints: dict[str, list[dict[str, Any]]] = {}
    for hint in data["duplicateHints"]:
        grouped_hints.setdefault(hint["taskId"], []).append(hint)
    if duplicate_limit >= 0:
        grouped_hints = {
            task_id: hints[:duplicate_limit]
            for task_id, hints in grouped_hints.items()
        }
    return {
        "schemaVersion": data["schemaVersion"],
        "repo": data["repo"],
        "config": data["config"],
        "manifest": data["manifest"],
        "warnings": data["warnings"],
        "patterns": data["patterns"],
        "unmatchedPatterns": data["unmatchedPatterns"],
        "existingDocsCount": len(data["existingDocs"]),
        "docsComparison": data["docsComparison"],
        "deadLinks": data["deadLinks"][:10],
        "deadLinkCount": len(data["deadLinks"]),
        "duplicateHintCount": data["duplicateHintCount"],
        "duplicateHintSeverityCounts": data["duplicateHintSeverityCounts"],
        "topDuplicateHints": visible_hints,
        "topDuplicateHintsByTask": grouped_hints,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--config", default=".dev-cycle/context/config.yaml", help="Boundary config path.")
    parser.add_argument("--manifest", default="CONTEXT_PLAN.md", help="Manifest path.")
    parser.add_argument("--json", action="store_true", help="Print full machine-readable JSON.")
    parser.add_argument("--full-json", action="store_true", help="Print full machine-readable JSON.")
    parser.add_argument("--summary-json", action="store_true", help="Print compact machine-readable JSON.")
    parser.add_argument(
        "--duplicate-limit",
        type=int,
        default=5,
        help="Maximum duplicate hints to print in text output. Use -1 for all.",
    )
    parser.add_argument(
        "--check-manifest",
        action="store_true",
        help="Exit 1 when active manifest tasks lack Docs Comparison.",
    )
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="Exit 1 when existing docs contain dead local links.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.summary_json and (args.json or args.full_json):
        print("choose only one JSON mode", file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"repo does not exist: {repo}", file=sys.stderr)
        return 2
    if args.duplicate_limit < -1:
        print("--duplicate-limit must be -1 or greater", file=sys.stderr)
        return 2
    config = (repo / args.config).resolve()
    manifest = (repo / args.manifest).resolve()
    data = collect_docs_data(repo, config, manifest)
    if args.summary_json:
        print(json.dumps(summary_data(data), indent=2, sort_keys=True))
    elif args.json or args.full_json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data, args.duplicate_limit)
    if args.check_manifest and not manifest.exists():
        return 2
    if args.check_manifest and data["docsComparison"]["missing"]:
        return 1
    if args.check_links and data["deadLinks"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
