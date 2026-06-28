#!/usr/bin/env python3
"""Migrate legacy dev-cycle manifest entries to explicit task fields."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audit import (
    ManifestTask,
    normalize_status,
    parse_frontmatter,
    relpath,
    slugify,
    strip_value,
)


TASK_RE = re.compile(r"^- \[(?P<marker>[^\]]*)\]\s+(?P<name>.+?)\s*$")
FIELD_RE = re.compile(r"^\s+- \*\*(?P<key>[^*]+)\*\*:\s*(?P<value>.*)$")


@dataclass
class MigratedEntry:
    line: int
    legacy_name: str
    task_id: str
    status: str
    context: str
    sources: str
    focus: str
    tags: str
    docs_comparison: str
    last_validated: str | None
    title: str
    preserved_fields: list[str]
    missing_fields: list[str]
    inferred_fields: list[str]


def legacy_context_path(value: str) -> str | None:
    clean = strip_value(value)
    if " " in clean or not clean.endswith(".md"):
        return None
    if clean.startswith(".dev-cycle/context/"):
        return clean
    if clean.startswith("./.dev-cycle/context/"):
        return clean[2:]
    return None


def legacy_task(task: ManifestTask) -> bool:
    return task.context is None and legacy_context_path(task.name) is not None


def title_from_path(context: str) -> str:
    stem = Path(context).stem.replace("-", " ").replace("_", " ").strip()
    return " ".join(part.capitalize() for part in stem.split()) or "Untitled"


def id_from_path(context: str) -> str:
    clean = context
    if clean.startswith("./"):
        clean = clean[2:]
    if clean.startswith(".dev-cycle/context/"):
        clean = clean[len(".dev-cycle/context/") :]
    if clean.endswith(".md"):
        clean = clean[:-3]
    parts = [part for part in clean.split("/") if part]
    if len(parts) >= 2 and parts[-1].startswith(parts[-2] + "-"):
        return slugify(parts[-1]).lower()
    return slugify("-".join(parts)).lower()


def tags_from_path(context: str) -> list[str]:
    clean = context
    if clean.startswith("./"):
        clean = clean[2:]
    if clean.startswith(".dev-cycle/context/"):
        clean = clean[len(".dev-cycle/context/") :]
    if clean.endswith(".md"):
        clean = clean[:-3]
    tags: list[str] = []
    for part in re.split(r"[/._-]+", clean):
        tag = slugify(part).lower()
        if tag and tag not in tags:
            tags.append(tag)
    return tags[:6]


def frontmatter_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            result.append(item)
    return result


def fingerprint_sources(frontmatter: dict[str, Any] | None) -> list[str]:
    if not frontmatter:
        return []
    result: list[str] = []
    fingerprints = frontmatter.get("fingerprint")
    if not isinstance(fingerprints, list):
        return result
    for item in fingerprints:
        if isinstance(item, dict) and item.get("file"):
            source = str(item["file"])
            if source not in result:
                result.append(source)
    return result


def normalize_field_key(value: str) -> str:
    return value.strip().lower().replace(" ", "")


def block_field_values(block: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block:
        match = FIELD_RE.match(line)
        if not match:
            continue
        fields[normalize_field_key(match.group("key"))] = match.group("value").strip()
    return fields


def field_present(fields: dict[str, str], key: str) -> bool:
    return normalize_field_key(key) in fields and bool(fields[normalize_field_key(key)].strip())


def field_value(fields: dict[str, str], key: str) -> str:
    return fields.get(normalize_field_key(key), "").strip()


def infer_status(marker: str, frontmatter: dict[str, Any] | None) -> str:
    if frontmatter and frontmatter.get("status"):
        return normalize_status(str(frontmatter["status"]))
    return normalize_status(marker)


def entry_from_legacy(
    repo: Path,
    line: int,
    marker: str,
    legacy_name: str,
    fields: dict[str, str],
) -> MigratedEntry:
    context = legacy_context_path(legacy_name)
    if context is None:  # pragma: no cover - guarded by caller
        raise ValueError(f"not a legacy Context path: {legacy_name}")
    frontmatter = parse_frontmatter(repo / context) if (repo / context).exists() else None
    preserved: list[str] = []
    missing: list[str] = []
    inferred: list[str] = ["Context"]

    if field_present(fields, "ID"):
        task_id = slugify(strip_value(field_value(fields, "ID")))
        preserved.append("ID")
    elif frontmatter and frontmatter.get("id"):
        task_id = slugify(str(frontmatter["id"]))
        inferred.append("ID")
    else:
        task_id = id_from_path(context)
        inferred.append("ID")

    if field_present(fields, "Status"):
        status = normalize_status(strip_value(field_value(fields, "Status")))
        preserved.append("Status")
    else:
        status = infer_status(marker, frontmatter)
        inferred.append("Status")

    if field_present(fields, "Sources"):
        sources = field_value(fields, "Sources")
        preserved.append("Sources")
    else:
        frontmatter_sources = fingerprint_sources(frontmatter)
        sources = format_csv(frontmatter_sources, "TBD")
        if frontmatter_sources:
            inferred.append("Sources")
        else:
            missing.append("Sources")

    if field_present(fields, "Focus"):
        focus = field_value(fields, "Focus")
        preserved.append("Focus")
    else:
        focus = f"Migrated legacy Context entry for {title_from_path(context)}."
        inferred.append("Focus")

    if field_present(fields, "Tags"):
        tags = field_value(fields, "Tags")
        preserved.append("Tags")
    else:
        frontmatter_tags = frontmatter_list(frontmatter.get("tags")) if frontmatter else []
        tags = format_csv(frontmatter_tags or tags_from_path(context), "TBD")
        if tags == "TBD":
            missing.append("Tags")
        else:
            inferred.append("Tags")

    if field_present(fields, "Docs Comparison"):
        docs_comparison = field_value(fields, "Docs Comparison")
        preserved.append("Docs Comparison")
    else:
        docs_comparison = "TBD"
        missing.append("Docs Comparison")

    last_validated = None
    if field_present(fields, "LastValidated"):
        last_validated = field_value(fields, "LastValidated")
        preserved.append("LastValidated")

    field_order = [
        "ID",
        "Context",
        "Sources",
        "Focus",
        "Tags",
        "Docs Comparison",
        "Status",
        "LastValidated",
    ]
    preserved = [field for field in field_order if field in preserved]
    missing = [field for field in field_order if field in missing]
    inferred = [field for field in field_order if field in inferred]

    title = str(frontmatter.get("title")) if frontmatter and frontmatter.get("title") else title_from_path(context)
    return MigratedEntry(
        line=line,
        legacy_name=strip_value(legacy_name),
        task_id=task_id,
        status=status,
        context=context,
        sources=sources,
        focus=focus,
        tags=tags,
        docs_comparison=docs_comparison,
        last_validated=last_validated,
        title=title,
        preserved_fields=preserved,
        missing_fields=missing,
        inferred_fields=inferred,
    )


def format_csv(values: list[str], fallback: str) -> str:
    return ", ".join(values) if values else fallback


def format_entry(entry: MigratedEntry) -> list[str]:
    lines = [
        f"- [{entry.status}] {entry.task_id}",
        f"  - **ID**: `{entry.task_id}`",
        f"  - **Context**: `{entry.context}`",
        f"  - **Sources**: {entry.sources}",
        f"  - **Focus**: {entry.focus}",
        f"  - **Tags**: {entry.tags}",
        f"  - **Docs Comparison**: {entry.docs_comparison}",
        f"  - **Status**: `{entry.status}`",
    ]
    if entry.last_validated is not None:
        lines.append(f"  - **LastValidated**: {entry.last_validated}")
    return lines


def block_fields(block: list[str]) -> set[str]:
    fields: set[str] = set()
    for line in block:
        match = FIELD_RE.match(line)
        if match:
            fields.add(match.group("key").strip().lower().replace(" ", ""))
    return fields


def migrate_manifest(repo: Path, manifest: Path) -> tuple[str, list[MigratedEntry]]:
    lines = manifest.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    entries: list[MigratedEntry] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        task_match = TASK_RE.match(line)
        if not task_match:
            output.append(line)
            index += 1
            continue

        end = index + 1
        while end < len(lines) and not TASK_RE.match(lines[end]):
            end += 1
        block = lines[index:end]
        fields = block_fields(block)
        field_values = block_field_values(block)
        legacy_name = task_match.group("name")
        context = legacy_context_path(legacy_name)
        if context and "context" not in fields and "id" not in fields:
            entry = entry_from_legacy(
                repo,
                index + 1,
                task_match.group("marker"),
                legacy_name,
                field_values,
            )
            entries.append(entry)
            output.extend(format_entry(entry))
        else:
            output.extend(block)
        index = end
    return "\n".join(output) + "\n", entries


def entry_to_dict(entry: MigratedEntry) -> dict[str, Any]:
    return {
        "line": entry.line,
        "legacyName": entry.legacy_name,
        "id": entry.task_id,
        "status": entry.status,
        "context": entry.context,
        "sources": entry.sources,
        "focus": entry.focus,
        "tags": entry.tags,
        "docsComparison": entry.docs_comparison,
        "lastValidated": entry.last_validated,
        "title": entry.title,
        "preservedFields": entry.preserved_fields,
        "missingFields": entry.missing_fields,
        "inferredFields": entry.inferred_fields,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--manifest", default="CONTEXT_PLAN.md", help="Manifest path.")
    parser.add_argument("--write", action="store_true", help="Rewrite the manifest in place.")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without writing.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.write and args.dry_run:
        print("choose only one of --write or --dry-run", file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"repo does not exist: {repo}", file=sys.stderr)
        return 2
    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = repo / manifest
    manifest = manifest.resolve()
    if not manifest.exists() or not manifest.is_file():
        print(f"manifest does not exist: {manifest}", file=sys.stderr)
        return 2

    migrated_text, entries = migrate_manifest(repo, manifest)
    changed = bool(entries) and migrated_text != manifest.read_text(encoding="utf-8")
    if args.write and changed:
        manifest.write_text(migrated_text, encoding="utf-8")

    data = {
        "schemaVersion": 1,
        "repo": str(repo),
        "manifest": relpath(manifest, repo),
        "legacyCount": len(entries),
        "changed": changed,
        "written": bool(args.write and changed),
        "entries": [entry_to_dict(entry) for entry in entries],
    }
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        action = "wrote" if data["written"] else "preview"
        print(f"dev-cycle context migrate-plan: {action} {len(entries)} legacy entr{'y' if len(entries) == 1 else 'ies'}")
        for entry in entries:
            print(f"- line {entry.line}: {entry.legacy_name} -> {entry.task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
