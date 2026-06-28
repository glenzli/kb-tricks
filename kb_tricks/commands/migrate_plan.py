#!/usr/bin/env python3
"""Migrate legacy kb-tricks manifest entries to explicit task fields."""

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
    kb: str
    sources: list[str]
    tags: list[str]
    title: str


def legacy_kb_path(value: str) -> str | None:
    clean = strip_value(value)
    if " " in clean or not clean.endswith(".md"):
        return None
    if clean.startswith(".agent/kb/") or clean.startswith("agent/kb/"):
        return clean
    if clean.startswith("./.agent/kb/"):
        return clean[2:]
    return None


def legacy_task(task: ManifestTask) -> bool:
    return task.kb is None and legacy_kb_path(task.name) is not None


def title_from_path(kb: str) -> str:
    stem = Path(kb).stem.replace("-", " ").replace("_", " ").strip()
    return " ".join(part.capitalize() for part in stem.split()) or "Untitled"


def id_from_path(kb: str) -> str:
    clean = kb
    if clean.startswith("./"):
        clean = clean[2:]
    if clean.startswith(".agent/kb/"):
        clean = clean[len(".agent/kb/") :]
    if clean.endswith(".md"):
        clean = clean[:-3]
    parts = [part for part in clean.split("/") if part]
    if len(parts) >= 2 and parts[-1].startswith(parts[-2] + "-"):
        return slugify(parts[-1]).lower()
    return slugify("-".join(parts)).lower()


def tags_from_path(kb: str) -> list[str]:
    clean = kb
    if clean.startswith("./"):
        clean = clean[2:]
    if clean.startswith(".agent/kb/"):
        clean = clean[len(".agent/kb/") :]
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


def entry_from_legacy(repo: Path, line: int, marker: str, legacy_name: str) -> MigratedEntry:
    kb = legacy_kb_path(legacy_name)
    if kb is None:  # pragma: no cover - guarded by caller
        raise ValueError(f"not a legacy KB path: {legacy_name}")
    frontmatter = parse_frontmatter(repo / kb) if (repo / kb).exists() else None
    task_id = slugify(str(frontmatter.get("id"))) if frontmatter and frontmatter.get("id") else id_from_path(kb)
    status = (
        normalize_status(str(frontmatter.get("status")))
        if frontmatter and frontmatter.get("status")
        else normalize_status(marker)
    )
    tags = frontmatter_list(frontmatter.get("tags")) if frontmatter else []
    if not tags:
        tags = tags_from_path(kb)
    title = str(frontmatter.get("title")) if frontmatter and frontmatter.get("title") else title_from_path(kb)
    return MigratedEntry(
        line=line,
        legacy_name=strip_value(legacy_name),
        task_id=task_id,
        status=status,
        kb=kb,
        sources=fingerprint_sources(frontmatter),
        tags=tags,
        title=title,
    )


def format_csv(values: list[str], fallback: str) -> str:
    return ", ".join(values) if values else fallback


def format_entry(entry: MigratedEntry) -> list[str]:
    focus = f"Migrated legacy KB entry for {entry.title}."
    return [
        f"- [{entry.status}] {entry.task_id}",
        f"  - **ID**: `{entry.task_id}`",
        f"  - **KB**: `{entry.kb}`",
        f"  - **Sources**: {format_csv(entry.sources, 'TBD')}",
        f"  - **Focus**: {focus}",
        f"  - **Tags**: {format_csv(entry.tags, 'TBD')}",
        "  - **Docs Comparison**: TBD",
        f"  - **Status**: `{entry.status}`",
    ]


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
        legacy_name = task_match.group("name")
        kb = legacy_kb_path(legacy_name)
        if kb and "kb" not in fields and "id" not in fields:
            entry = entry_from_legacy(
                repo,
                index + 1,
                task_match.group("marker"),
                legacy_name,
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
        "kb": entry.kb,
        "sources": entry.sources,
        "tags": entry.tags,
        "title": entry.title,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--manifest", default="KB_PLAN.md", help="Manifest path.")
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
        print(f"kb migrate-plan: {action} {len(entries)} legacy entr{'y' if len(entries) == 1 else 'ies'}")
        for entry in entries:
            print(f"- line {entry.line}: {entry.legacy_name} -> {entry.task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
