#!/usr/bin/env python3
"""Lint dev-cycle query answers for provenance and inference isolation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SECTION_ALIASES = {
    "answer": {
        "回答",
        "answer",
        "回答 answer",
        "回答 (answer)",
    },
    "inference": {
        "不确定性与推断",
        "uncertainty & inference",
        "uncertainty and inference",
        "不确定性与推断 uncertainty & inference",
        "不确定性与推断 (uncertainty & inference)",
    },
    "citations": {
        "引用出处",
        "citations",
        "引用出处 citations",
        "引用出处 (citations)",
    },
    "status": {
        "知识库状态",
        "kb status",
        "知识库状态 kb status",
        "知识库状态 (kb status)",
    },
}

SOURCE_PATTERNS = {
    "kb": [
        r"\[KB\]",
        r"来源:\s*KB",
        r"Source:\s*KB",
    ],
    "source": [
        r"\[源码回退\]",
        r"\[Source Fallback\]",
        r"来源:\s*源码回退",
        r"Source:\s*Source Fallback",
    ],
    "docs": [
        r"\[现有 docs\]",
        r"\[Existing Docs\]",
        r"来源:\s*现有 docs",
        r"Source:\s*Existing Docs",
    ],
    "inference": [
        r"\[推断\]",
        r"\[Inference\]",
        r"来源:\s*推断",
        r"Source:\s*Inference",
    ],
}

CITATION_PATTERNS = {
    "kb": [r"\bKB\b", r"知识库"],
    "source": [r"源码", r"Source"],
    "docs": [r"现有 docs", r"Existing Docs", r"docs"],
    "inference": [r"推断", r"Inference"],
}


@dataclass
class LintViolation:
    code: str
    message: str
    section: str | None = None
    line: int | None = None


@dataclass
class LintResult:
    path: str
    ok: bool = True
    used_sources: list[str] = field(default_factory=list)
    violations: list[LintViolation] = field(default_factory=list)


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_heading(value: str) -> str:
    value = value.strip().strip("#").strip()
    value = re.sub(r"\s+", " ", value)
    return value.lower()


def section_key(heading: str) -> str | None:
    normalized = normalize_heading(heading)
    for key, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return key
    return None


def parse_sections(text: str) -> dict[str, list[tuple[int, str]]]:
    sections: dict[str, list[tuple[int, str]]] = {}
    current: str | None = None
    in_comment = False
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            continue
        if line.startswith("## "):
            current = section_key(line[3:])
            if current:
                sections.setdefault(current, [])
            continue
        if current:
            sections[current].append((line_no, line))
    return sections


def line_sources(line: str) -> set[str]:
    sources: set[str] = set()
    for source, patterns in SOURCE_PATTERNS.items():
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns):
            sources.add(source)
    return sources


def has_citation_for(section: list[tuple[int, str]], source: str) -> bool:
    text = "\n".join(line for _, line in section)
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in CITATION_PATTERNS[source]
    )


def is_content_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("<!--", "|---", "```")):
        return False
    if set(stripped) <= {"-", "*", "_"}:
        return False
    return True


def is_empty_inference(section: list[tuple[int, str]]) -> bool:
    content = [line.strip() for _, line in section if is_content_line(line)]
    if not content:
        return True
    joined = " ".join(content).strip().lower()
    return joined in {"无", "none", "- 无", "- none", "n/a"}


def add_violation(
    result: LintResult,
    code: str,
    message: str,
    section: str | None = None,
    line: int | None = None,
) -> None:
    result.ok = False
    result.violations.append(LintViolation(code, message, section, line))


def lint_text(path: str, text: str) -> LintResult:
    result = LintResult(path=path)
    sections = parse_sections(text)
    for required in ["answer", "inference", "citations", "status"]:
        if required not in sections:
            add_violation(
                result,
                "missing-section",
                f"missing required section: {required}",
                required,
            )

    answer = sections.get("answer", [])
    used_sources: set[str] = set()
    for line_no, line in answer:
        if not is_content_line(line):
            continue
        sources = line_sources(line)
        if "inference" in sources:
            add_violation(
                result,
                "inference-in-answer",
                "inference must be isolated in the inference section",
                "answer",
                line_no,
            )
        fact_sources = sources - {"inference"}
        if not fact_sources:
            add_violation(
                result,
                "missing-source",
                "answer content line is missing a source type marker",
                "answer",
                line_no,
            )
        used_sources.update(fact_sources)

    inference = sections.get("inference", [])
    if inference and not is_empty_inference(inference):
        inference_has_marker = any(
            "inference" in line_sources(line)
            for _, line in inference
            if is_content_line(line)
        )
        if not inference_has_marker:
            add_violation(
                result,
                "unmarked-inference",
                "non-empty inference section must mark inference explicitly",
                "inference",
            )
        else:
            used_sources.add("inference")

    citations = sections.get("citations", [])
    for source in sorted(used_sources):
        if not has_citation_for(citations, source):
            add_violation(
                result,
                "missing-citation",
                f"citations do not include source type: {source}",
                "citations",
            )

    result.used_sources = sorted(used_sources)
    return result


def result_to_dict(result: LintResult) -> dict[str, Any]:
    return {
        "path": result.path,
        "ok": result.ok,
        "usedSources": result.used_sources,
        "violations": [
            {
                "code": violation.code,
                "message": violation.message,
                "section": violation.section,
                "line": violation.line,
            }
            for violation in result.violations
        ],
    }


def print_text(results: list[LintResult]) -> None:
    for result in results:
        label = "OK" if result.ok else "FAIL"
        print(f"{label} {result.path}")
        for violation in result.violations:
            location = ""
            if violation.line:
                location = f":{violation.line}"
            elif violation.section:
                location = f":{violation.section}"
            print(f"  - {violation.code}{location}: {violation.message}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Resolve answer paths relative to this repository.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "answers",
        nargs="*",
        help="Markdown answer drafts to lint. Use '-' or no files to read stdin.",
    )
    return parser.parse_args(argv)


def read_inputs(paths: list[str], repo: Path) -> tuple[list[tuple[str, str]], list[str]]:
    if not paths:
        return [("<stdin>", sys.stdin.read())], []
    inputs: list[tuple[str, str]] = []
    errors: list[str] = []
    for value in paths:
        if value == "-":
            inputs.append(("<stdin>", sys.stdin.read()))
            continue
        path = Path(value)
        if not path.is_absolute():
            path = repo / path
        if not path.exists() or not path.is_file():
            errors.append(f"{value}: file does not exist")
            continue
        inputs.append((relpath(path, repo), path.read_text(encoding="utf-8")))
    return inputs, errors


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo = Path(args.repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"repo does not exist: {repo}", file=sys.stderr)
        return 2
    inputs, errors = read_inputs(args.answers, repo)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    results = [lint_text(path, text) for path, text in inputs]
    if args.json:
        print(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "ok": all(result.ok for result in results),
                    "results": [result_to_dict(result) for result in results],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_text(results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
