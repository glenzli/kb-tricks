#!/usr/bin/env python3
"""Deterministic dev-cycle artifact audit.

This tool validates the structures defined in spec/CONTEXT_SPEC.md. It does not
generate or rewrite Context prose; that remains the job of the skills.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


ALLOWED_STATES = {
    "planned",
    "built",
    "stale",
    "orphaned",
    "merged-into-docs",
    "deprecated",
}

RESERVED_DIRS = {"_draft", "_impact", "_validation"}
AUXILIARY_MD = {"AGENT_GUIDE.md", "GLOSSARY.md", "CHANGELOG.md", "ONBOARDING.md"}
GRADE_ORDER = {"F": 0, "D": 1, "C": 2, "B": 3, "A": 4}


@dataclass
class ManifestTask:
    marker: str
    name: str
    task_id: str
    status: str
    context: str | None = None
    sources: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    fields: dict[str, str] = field(default_factory=dict)
    line: int = 0


@dataclass
class LinkCheck:
    source: str
    target: str
    line: int
    ok: bool


@dataclass
class DocumentAudit:
    path: str
    reserved: bool
    auxiliary: bool
    kind: str
    frontmatter: dict[str, Any] | None
    missing_frontmatter: bool = False
    not_authoritative: bool = False
    draft: bool = False
    stale_reasons: list[str] = field(default_factory=list)
    dirty_reasons: list[str] = field(default_factory=list)
    orphaned_sources: list[str] = field(default_factory=list)
    links: list[LinkCheck] = field(default_factory=list)

    @property
    def stale(self) -> bool:
        return bool(self.stale_reasons)

    @property
    def dirty(self) -> bool:
        return bool(self.dirty_reasons)

    @property
    def orphaned(self) -> bool:
        return bool(self.orphaned_sources)

    @property
    def fresh(self) -> bool:
        return (
            self.frontmatter is not None
            and not self.stale
            and not self.dirty
            and not self.orphaned
            and not self.draft
        )


@dataclass
class AuditResult:
    repo: str
    context_root: str
    manifest_path: str
    config_path: str
    config_present: bool
    manifest_present: bool
    tasks: list[ManifestTask]
    documents: list[DocumentAudit]
    glossary_terms: list[dict[str, Any]]
    glossary_links: list[LinkCheck]
    validation_missing: list[str]
    validation_failed: list[str]
    missing_context: list[str]
    untracked_context: list[str]
    boundary_violations: list[str]
    release_excluded_hits: list[str]
    metrics: dict[str, float]
    grade: str
    failures: list[str]


def run_git(repo: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def strip_value(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    return value.strip()


def parse_scalar(value: str) -> Any:
    value = strip_value(value)
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    if lower in {"null", "none", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [strip_value(part) for part in inner.split(",")]
    return value


def split_csv(value: str) -> list[str]:
    value = value.strip()
    if not value:
        return []
    return [strip_value(part) for part in value.split(",") if strip_value(part)]


def normalize_status(marker: str) -> str:
    marker = marker.strip()
    if marker == "":
        return "planned"
    if marker.lower() == "x":
        return "built"
    return marker


def slugify(value: str) -> str:
    value = strip_value(value)
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return value or "unnamed"


def parse_manifest(path: Path) -> list[ManifestTask]:
    if not path.exists():
        return []
    tasks: list[ManifestTask] = []
    current: ManifestTask | None = None
    task_re = re.compile(r"^- \[(?P<marker>[^\]]*)\]\s+(?P<name>.+?)\s*$")
    field_re = re.compile(r"^\s+- \*\*(?P<key>[^*]+)\*\*:\s*(?P<value>.*)$")
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        task_match = task_re.match(line)
        if task_match:
            marker = task_match.group("marker")
            name = strip_value(task_match.group("name"))
            status = normalize_status(marker)
            current = ManifestTask(
                marker=marker,
                name=name,
                task_id=slugify(name),
                status=status,
                line=line_no,
            )
            tasks.append(current)
            continue
        if current is None:
            continue
        field_match = field_re.match(line)
        if not field_match:
            continue
        key = field_match.group("key").strip()
        value = field_match.group("value").strip()
        normalized_key = key.lower().replace(" ", "")
        clean_value = strip_value(value)
        if normalized_key == "id":
            current.fields[key] = clean_value
            current.task_id = slugify(clean_value)
        elif normalized_key == "context":
            current.fields[key] = clean_value
            current.context = clean_value
        elif normalized_key == "sources":
            current.sources = split_csv(value)
            current.fields[key] = ", ".join(current.sources)
        elif normalized_key == "tags":
            current.tags = split_csv(value)
            current.fields[key] = ", ".join(current.tags)
        elif normalized_key == "status":
            current.fields[key] = clean_value
            current.status = normalize_status(clean_value)
        else:
            current.fields[key] = clean_value
    return tasks


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        return None
    data: dict[str, Any] = {}
    current_list: str | None = None
    current_item: dict[str, Any] | None = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" ") and ":" in raw:
            key, value = raw.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = parse_scalar(value)
                current_list = None
                current_item = None
            else:
                data[key] = []
                current_list = key
                current_item = None
            continue
        if current_list and raw.strip().startswith("- "):
            item_text = raw.strip()[2:].strip()
            current_item = {}
            data.setdefault(current_list, []).append(current_item)
            if ":" in item_text:
                key, value = item_text.split(":", 1)
                current_item[key.strip()] = parse_scalar(value.strip())
            continue
        if current_item is not None and ":" in raw:
            key, value = raw.strip().split(":", 1)
            current_item[key.strip()] = parse_scalar(value.strip())
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def git_tracked(repo: Path, rel: str) -> bool:
    code, _, _ = run_git(repo, ["ls-files", "--error-unmatch", "--", rel])
    return code == 0


def git_dirty(repo: Path, rel: str) -> bool:
    unstaged, _, _ = run_git(repo, ["diff", "--quiet", "--", rel])
    staged, _, _ = run_git(repo, ["diff", "--cached", "--quiet", "--", rel])
    return unstaged != 0 or staged != 0


def git_last_commit(repo: Path, rel: str) -> str | None:
    code, out, _ = run_git(repo, ["log", "-1", "--format=%H", "--", rel])
    if code != 0 or not out:
        return None
    return out.splitlines()[0].strip()


def commits_match(recorded: Any, current: str | None) -> bool:
    if recorded is None or str(recorded).lower() in {"", "null", "none"}:
        return current is None
    if current is None:
        return False
    recorded_s = str(recorded)
    return current.startswith(recorded_s) or recorded_s.startswith(current)


def is_reserved_doc(path: Path, context_root: Path) -> bool:
    rel = path.relative_to(context_root)
    return any(part in RESERVED_DIRS for part in rel.parts)


def is_auxiliary_doc(path: Path) -> bool:
    return path.name in AUXILIARY_MD


def link_targets(text: str) -> list[tuple[int, str]]:
    results: list[tuple[int, str]] = []
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    fence_pattern = re.compile(r"^\s*(```|~~~)")
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), 1):
        if fence_pattern.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in pattern.finditer(line):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            results.append((line_no, target))
    return results


def is_external_link(target: str) -> bool:
    lower = target.lower()
    return (
        not target
        or target.startswith("#")
        or "://" in lower
        or lower.startswith("mailto:")
    )


def resolve_link(source: Path, target: str) -> Path:
    clean = target.split("#", 1)[0].split("?", 1)[0]
    return (source.parent / clean).resolve()


def check_links(path: Path, repo: Path) -> list[LinkCheck]:
    text = path.read_text(encoding="utf-8")
    checks: list[LinkCheck] = []
    for line_no, target in link_targets(text):
        if is_external_link(target):
            continue
        resolved = resolve_link(path, target)
        checks.append(
            LinkCheck(
                source=relpath(path, repo),
                target=target,
                line=line_no,
                ok=resolved.exists(),
            )
        )
    return checks


def parse_config(path: Path) -> dict[str, list[str]]:
    result = {
        "include": [],
        "exclude": [],
        "releaseExcluded": [],
        "docs.existing": [],
    }
    if not path.exists():
        return result
    current: str | None = None
    in_docs = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if not line.startswith(" ") and stripped.endswith(":"):
            key = stripped[:-1]
            in_docs = key == "docs"
            current = key if key in result else None
            continue
        if in_docs and line.startswith("  ") and stripped.endswith(":"):
            key = stripped[:-1]
            current = "docs.existing" if key == "existing" else None
            continue
        if current and stripped.startswith("- "):
            result[current].append(strip_value(stripped[2:]))
    return result


def pattern_matches(path: str, pattern: str) -> bool:
    pattern = pattern.strip()
    if not pattern:
        return False
    if fnmatch(path, pattern):
        return True
    if pattern.endswith("/**"):
        return path == pattern[:-3] or path.startswith(pattern[:-3] + "/")
    return False


def in_patterns(path: str, patterns: list[str]) -> bool:
    return any(pattern_matches(path, pattern) for pattern in patterns)


def audit_document(path: Path, repo: Path, context_root: Path) -> DocumentAudit:
    rel = relpath(path, repo)
    reserved = is_reserved_doc(path, context_root)
    auxiliary = is_auxiliary_doc(path)
    if auxiliary:
        kind = "support"
    elif reserved:
        kind = "reserved"
    else:
        kind = "authoritative"
    frontmatter = parse_frontmatter(path)
    doc = DocumentAudit(
        path=rel,
        reserved=reserved,
        auxiliary=auxiliary,
        kind=kind,
        frontmatter=frontmatter,
        missing_frontmatter=frontmatter is None and not auxiliary and not reserved,
        draft=reserved,
    )
    doc.links = check_links(path, repo)
    if frontmatter is None:
        return doc
    doc.not_authoritative = bool(frontmatter.get("notAuthoritative", False))
    doc.draft = doc.draft or doc.not_authoritative
    fingerprints = frontmatter.get("fingerprint") or []
    if not isinstance(fingerprints, list):
        doc.stale_reasons.append("fingerprint is not a list")
        return doc
    for item in fingerprints:
        if not isinstance(item, dict):
            doc.stale_reasons.append("fingerprint item is not an object")
            continue
        source = item.get("file")
        if not source:
            doc.stale_reasons.append("fingerprint item missing file")
            continue
        source_rel = str(source)
        source_path = repo / source_rel
        if not source_path.exists():
            doc.orphaned_sources.append(source_rel)
            continue
        current_hash = sha256_file(source_path)
        recorded_hash = item.get("contentHash")
        if recorded_hash and str(recorded_hash) != current_hash:
            doc.stale_reasons.append(f"{source_rel}: contentHash mismatch")
        current_commit = git_last_commit(repo, source_rel)
        if not commits_match(item.get("commit"), current_commit):
            doc.stale_reasons.append(f"{source_rel}: commit mismatch")
        current_tracked = git_tracked(repo, source_rel)
        recorded_tracked = item.get("tracked")
        if recorded_tracked is not None and bool(recorded_tracked) != current_tracked:
            doc.stale_reasons.append(f"{source_rel}: tracked mismatch")
        if not current_tracked:
            current_state = "untracked"
        else:
            current_state = "dirty" if git_dirty(repo, source_rel) else "clean"
        recorded_state = str(item.get("worktree", "")).strip().strip('"')
        if recorded_state and recorded_state != current_state:
            doc.dirty_reasons.append(
                f"{source_rel}: worktree is {current_state}, recorded {recorded_state}"
            )
        if current_state != "clean":
            doc.dirty_reasons.append(f"{source_rel}: current worktree is {current_state}")
    return doc


def parse_glossary(glossary: Path, repo: Path) -> tuple[list[dict[str, Any]], list[LinkCheck]]:
    if not glossary.exists():
        return [], []
    terms: list[dict[str, Any]] = []
    links = check_links(glossary, repo)
    for line_no, line in enumerate(glossary.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cols = [col.strip() for col in stripped.strip("|").split("|")]
        if len(cols) < 3:
            continue
        if cols[0].lower() in {"term / keyword", "术语 / 关键字"}:
            continue
        terms.append(
            {
                "term": cols[0],
                "synonyms": cols[1],
                "target": cols[2],
                "line": line_no,
            }
        )
    return terms, links


def collect_boundary_issues(
    tasks: list[ManifestTask],
    documents: list[DocumentAudit],
    config: dict[str, list[str]],
) -> tuple[list[str], list[str]]:
    include = config.get("include", [])
    exclude = config.get("exclude", [])
    release_excluded = config.get("releaseExcluded", [])
    violations: list[str] = []
    release_hits: list[str] = []
    paths: set[str] = set()
    for task in tasks:
        paths.update(task.sources)
    for doc in documents:
        if not doc.frontmatter:
            continue
        for item in doc.frontmatter.get("fingerprint") or []:
            if isinstance(item, dict) and item.get("file"):
                paths.add(str(item["file"]))
    for path in sorted(paths):
        if include and not in_patterns(path, include):
            violations.append(f"{path}: outside include")
        if in_patterns(path, exclude):
            violations.append(f"{path}: inside exclude")
        if in_patterns(path, release_excluded):
            release_hits.append(path)
    return violations, release_hits


def metric_ratio(ok: int, total: int) -> float:
    if total <= 0:
        return 100.0
    return round((ok / total) * 100.0, 2)


def grade_from_metrics(metrics: dict[str, float], dead_links: int, dirty_docs: int) -> str:
    values = list(metrics.values()) or [100.0]
    minimum = min(values)
    if minimum < 25 or dead_links >= 5:
        return "F"
    if minimum < 50:
        return "D"
    if minimum < 75:
        return "C"
    if minimum < 90 or dirty_docs > 0:
        return "B"
    return "A"


def build_index(result: AuditResult) -> dict[str, Any]:
    data = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo": result.repo,
        "contextRoot": result.context_root,
        "manifest": [
            {
                "id": task.task_id,
                "name": task.name,
                "status": task.status,
                "context": task.context,
                "sources": task.sources,
                "tags": task.tags,
            }
            for task in result.tasks
        ],
        "documents": [
            {
                "path": doc.path,
                "id": doc.frontmatter.get("id") if doc.frontmatter else None,
                "title": doc.frontmatter.get("title") if doc.frontmatter else None,
                "status": doc.frontmatter.get("status") if doc.frontmatter else None,
                "tags": doc.frontmatter.get("tags") if doc.frontmatter else [],
                "kind": doc.kind,
                "reserved": doc.reserved,
                "support": doc.auxiliary,
                "notAuthoritative": doc.not_authoritative,
                "draft": doc.draft,
                "fresh": doc.fresh,
                "staleReasons": doc.stale_reasons,
                "dirtyReasons": doc.dirty_reasons,
                "orphanedSources": doc.orphaned_sources,
                "fingerprint": doc.frontmatter.get("fingerprint") if doc.frontmatter else [],
                "links": [
                    {
                        "target": link.target,
                        "line": link.line,
                        "ok": link.ok,
                    }
                    for link in doc.links
                ],
            }
            for doc in result.documents
        ],
        "terms": result.glossary_terms,
        "links": [
            {
                "source": link.source,
                "target": link.target,
                "line": link.line,
                "ok": link.ok,
            }
            for doc in result.documents
            for link in doc.links
        ],
        "summary": {
            "grade": result.grade,
            "metrics": result.metrics,
            "failures": result.failures,
        },
    }
    try:
        from .docs import collect_docs_data

        docs_data = collect_docs_data(
            Path(result.repo),
            Path(result.repo) / result.config_path,
            Path(result.repo) / result.manifest_path,
        )
        data["existingDocs"] = docs_data["existingDocs"]
        data["docsComparison"] = docs_data["docsComparison"]
        data["docsDuplicateHints"] = docs_data["duplicateHints"]
    except Exception as exc:  # pragma: no cover - defensive optional index enrichment
        data["existingDocsError"] = str(exc)
    return data


def audit(repo: Path, context_root: Path, manifest: Path, config_path: Path) -> AuditResult:
    tasks = parse_manifest(manifest)
    context_docs = sorted(context_root.rglob("*.md")) if context_root.exists() else []
    documents = [audit_document(path, repo, context_root) for path in context_docs]
    glossary_terms, glossary_links = parse_glossary(context_root / "GLOSSARY.md", repo)
    task_by_context = {task.context: task for task in tasks if task.context}
    built_tasks = [task for task in tasks if task.status == "built"]

    existing_context_paths = {doc.path for doc in documents}
    missing_context = [
        task.context
        for task in built_tasks
        if task.context and task.context not in existing_context_paths
    ]
    authoritative_docs = [
        doc for doc in documents if not doc.reserved and not doc.auxiliary
    ]
    untracked_context = [
        doc.path
        for doc in authoritative_docs
        if doc.path not in task_by_context
    ]

    validation_missing: list[str] = []
    validation_failed: list[str] = []
    for task in built_tasks:
        validation = context_root / "_validation" / f"{task.task_id}.md"
        if not validation.exists():
            validation_missing.append(task.task_id)
            continue
        text = validation.read_text(encoding="utf-8").lower()
        if re.search(r"\*\*result\*\*:\s*fail|\bresult:\s*fail", text):
            validation_failed.append(task.task_id)

    config = parse_config(config_path)
    boundary_violations, release_excluded_hits = collect_boundary_issues(
        tasks, documents, config
    )

    planned_built_stale = [
        task for task in tasks if task.status in {"planned", "built", "stale"}
    ]
    coverage = metric_ratio(
        len([task for task in built_tasks if task.context and task.context in existing_context_paths]),
        len(planned_built_stale),
    )

    docs_with_fingerprints = [
        doc
        for doc in authoritative_docs
        if doc.frontmatter and doc.frontmatter.get("fingerprint")
    ]
    freshness = metric_ratio(
        len([doc for doc in docs_with_fingerprints if doc.fresh]),
        len(docs_with_fingerprints),
    )

    all_doc_links = [link for doc in documents for link in doc.links]
    all_links = all_doc_links + glossary_links
    dead_links = [link for link in all_links if not link.ok]
    link_integrity = metric_ratio(len(all_links) - len(dead_links), len(all_links))
    glossary_dead = [link for link in glossary_links if not link.ok]
    glossary_metric = metric_ratio(
        len(glossary_links) - len(glossary_dead), len(glossary_links)
    )
    validation_metric = metric_ratio(
        len(built_tasks) - len(validation_missing) - len(validation_failed),
        len(built_tasks),
    )
    metrics = {
        "setup": 100.0 if manifest.exists() and config_path.exists() else 0.0,
        "coverage": coverage,
        "freshness": freshness,
        "links": link_integrity,
        "glossary": glossary_metric,
        "validation": validation_metric,
    }
    dirty_docs = [doc for doc in authoritative_docs if doc.dirty]
    grade = grade_from_metrics(metrics, len(dead_links), len(dirty_docs))
    return AuditResult(
        repo=str(repo),
        context_root=relpath(context_root, repo),
        manifest_path=relpath(manifest, repo),
        config_path=relpath(config_path, repo),
        config_present=config_path.exists(),
        manifest_present=manifest.exists(),
        tasks=tasks,
        documents=documents,
        glossary_terms=glossary_terms,
        glossary_links=glossary_links,
        validation_missing=validation_missing,
        validation_failed=validation_failed,
        missing_context=missing_context,
        untracked_context=untracked_context,
        boundary_violations=boundary_violations,
        release_excluded_hits=release_excluded_hits,
        metrics=metrics,
        grade=grade,
        failures=[],
    )


def failure_reasons(result: AuditResult, fail_on: list[str], min_score: str | None) -> list[str]:
    docs = result.documents
    all_links = [link for doc in docs for link in doc.links] + result.glossary_links
    checks = {
        "missing-manifest": [] if result.manifest_present else [result.manifest_path],
        "missing-config": [] if result.config_present else [result.config_path],
        "stale": [doc.path for doc in docs if doc.stale],
        "dead-links": [
            f"{link.source}:{link.line} -> {link.target}"
            for link in all_links
            if not link.ok
        ],
        "dirty": [doc.path for doc in docs if doc.dirty],
        "draft": [doc.path for doc in docs if doc.draft],
        "missing": result.missing_context,
        "missing-validation": result.validation_missing,
        "failed-validation": result.validation_failed,
        "boundary": result.boundary_violations,
        "orphaned": [doc.path for doc in docs if doc.orphaned],
        "untracked": result.untracked_context,
        "not-authoritative": [doc.path for doc in docs if doc.not_authoritative],
    }
    failures: list[str] = []
    for name in fail_on:
        values = checks.get(name)
        if values:
            failures.append(f"{name}: {len(values)}")
    if min_score:
        wanted = min_score.upper()
        if wanted not in GRADE_ORDER:
            failures.append(f"invalid min-score: {min_score}")
        elif GRADE_ORDER[result.grade] < GRADE_ORDER[wanted]:
            failures.append(f"min-score: grade {result.grade} < {wanted}")
    return failures


def result_to_dict(result: AuditResult) -> dict[str, Any]:
    data = build_index(result)
    data["configPresent"] = result.config_present
    data["manifestPresent"] = result.manifest_present
    data["validationMissing"] = result.validation_missing
    data["validationFailed"] = result.validation_failed
    data["missingContext"] = result.missing_context
    data["untrackedContext"] = result.untracked_context
    data["boundaryViolations"] = result.boundary_violations
    data["releaseExcludedHits"] = result.release_excluded_hits
    data["releaseExcludedUses"] = [
        {
            "path": path,
            "severity": "context",
            "healthConcern": False,
            "reason": "releaseExcluded path is referenced as context; verify prose does not treat it as release authority",
        }
        for path in result.release_excluded_hits
    ]
    return data


def summary_to_dict(result: AuditResult) -> dict[str, Any]:
    docs = result.documents
    all_links = [link for doc in docs for link in doc.links] + result.glossary_links
    dead_links = [
        {
            "source": link.source,
            "target": link.target,
            "line": link.line,
        }
        for link in all_links
        if not link.ok
    ]
    stale = [doc.path for doc in docs if doc.kind == "authoritative" and doc.stale]
    dirty = [doc.path for doc in docs if doc.kind == "authoritative" and doc.dirty]
    orphaned = [doc.path for doc in docs if doc.kind == "authoritative" and doc.orphaned]
    return {
        "schemaVersion": 1,
        "repo": result.repo,
        "contextRoot": result.context_root,
        "manifest": result.manifest_path,
        "config": result.config_path,
        "summary": {
            "grade": result.grade,
            "metrics": result.metrics,
            "failures": result.failures,
        },
        "counts": {
            "tasks": len(result.tasks),
            "documents": len(result.documents),
            "authoritativeDocuments": len([doc for doc in docs if doc.kind == "authoritative"]),
            "supportDocuments": len([doc for doc in docs if doc.kind == "support"]),
            "reservedDocuments": len([doc for doc in docs if doc.kind == "reserved"]),
            "missingContext": len(result.missing_context),
            "untrackedContext": len(result.untracked_context),
            "stale": len(stale),
            "dirty": len(dirty),
            "orphaned": len(orphaned),
            "deadLinks": len(dead_links),
            "missingValidation": len(result.validation_missing),
            "failedValidation": len(result.validation_failed),
            "boundaryViolations": len(result.boundary_violations),
            "releaseExcludedHits": len(result.release_excluded_hits),
        },
        "topIssues": {
            "stale": stale[:10],
            "dirty": dirty[:10],
            "orphaned": orphaned[:10],
            "deadLinks": dead_links[:10],
            "missingContext": result.missing_context[:10],
            "untrackedContext": result.untracked_context[:10],
            "missingValidation": result.validation_missing[:10],
            "failedValidation": result.validation_failed[:10],
            "boundaryViolations": result.boundary_violations[:10],
        },
        "supportDocuments": [
            {
                "path": doc.path,
                "links": [
                    {"target": link.target, "line": link.line, "ok": link.ok}
                    for link in doc.links
                ],
            }
            for doc in docs
            if doc.kind == "support"
        ],
        "releaseExcludedUses": [
            {
                "path": path,
                "severity": "context",
                "healthConcern": False,
            }
            for path in result.release_excluded_hits[:10]
        ],
    }


def print_markdown(result: AuditResult) -> None:
    docs = result.documents
    stale = [doc for doc in docs if doc.stale]
    dirty = [doc for doc in docs if doc.dirty]
    draft = [doc for doc in docs if doc.draft]
    orphaned = [doc for doc in docs if doc.orphaned]
    dead_links = [
        link
        for doc in docs
        for link in doc.links
        if not link.ok
    ] + [link for link in result.glossary_links if not link.ok]
    print("# Context Audit Report")
    print()
    print(f"- Repo: `{result.repo}`")
    print(f"- Context root: `{result.context_root}`")
    print(f"- Manifest: `{result.manifest_path}` ({'present' if result.manifest_present else 'missing'})")
    print(f"- Config: `{result.config_path}` ({'present' if result.config_present else 'missing'})")
    print(f"- Grade: **{result.grade}**")
    print()
    print("## Metrics")
    for key, value in result.metrics.items():
        print(f"- {key}: {value:.2f}%")
    print()
    print("## Findings")
    print(f"- Tasks: {len(result.tasks)}")
    print(f"- Documents: {len(result.documents)}")
    print(f"- Missing Context files: {len(result.missing_context)}")
    print(f"- Untracked Context files: {len(result.untracked_context)}")
    print(f"- Stale documents: {len(stale)}")
    print(f"- Dirty documents: {len(dirty)}")
    print(f"- Draft/not-authoritative documents: {len(draft)}")
    print(f"- Orphaned documents: {len(orphaned)}")
    print(f"- Dead links: {len(dead_links)}")
    print(f"- Missing validation files: {len(result.validation_missing)}")
    print(f"- Failed validation files: {len(result.validation_failed)}")
    print(f"- Boundary violations: {len(result.boundary_violations)}")
    print()
    if result.failures:
        print("## Policy Failures")
        for failure in result.failures:
            print(f"- {failure}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--context-root", default=".dev-cycle/context", help="Context root path.")
    parser.add_argument("--manifest", default="CONTEXT_PLAN.md", help="Manifest path.")
    parser.add_argument("--config", default=".dev-cycle/context/config.yaml", help="Boundary config path.")
    parser.add_argument(
        "--fail-on",
        action="append",
        default=[],
        choices=[
            "stale",
            "dead-links",
            "dirty",
            "draft",
            "missing-manifest",
            "missing-config",
            "missing",
            "missing-validation",
            "failed-validation",
            "boundary",
            "orphaned",
            "untracked",
            "not-authoritative",
        ],
        help="Policy failure condition. May be repeated.",
    )
    parser.add_argument("--min-score", choices=["A", "B", "C", "D", "F"])
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--full-json", action="store_true", help="Print full JSON payload.")
    parser.add_argument("--summary-json", action="store_true", help="Print compact JSON summary.")
    parser.add_argument("--write-index", help="Write generated index JSON to this path.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.summary_json and (args.json or args.full_json):
        print("choose only one JSON mode", file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve()
    context_root = (repo / args.context_root).resolve()
    manifest = (repo / args.manifest).resolve()
    config = (repo / args.config).resolve()
    try:
        result = audit(repo, context_root, manifest, config)
        result.failures = failure_reasons(result, args.fail_on, args.min_score)
        if args.write_index:
            index_path = (repo / args.write_index).resolve()
            index_path.parent.mkdir(parents=True, exist_ok=True)
            index_path.write_text(
                json.dumps(build_index(result), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if args.summary_json:
            print(json.dumps(summary_to_dict(result), indent=2, sort_keys=True))
        elif args.json or args.full_json:
            print(json.dumps(result_to_dict(result), indent=2, sort_keys=True))
        else:
            print_markdown(result)
        return 1 if result.failures else 0
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"context_audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
