import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_context_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "context_docs.py"


def docs_json(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 1, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


def docs_summary_json(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--summary-json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 1, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


def write_docs_repo(repo: Path, include_all_comparisons: bool = False) -> None:
    (repo / ".dev-cycle" / "context").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".dev-cycle" / "context" / "config.yaml").write_text(
        """include:
  - src/**
exclude:
  - dist/**
releaseExcluded:
  - .dev-cycle/**
docs:
  existing:
    - README.md
    - docs/**
    - missing/**
""",
        encoding="utf-8",
    )
    (repo / "README.md").write_text(
        """# Project

See [release docs](docs/release.md).
""",
        encoding="utf-8",
    )
    (repo / "docs" / "release.md").write_text(
        """# Release Packaging

This doc covers `src/release.py` and the release package artifact flow.

## Boundary

Release packaging normalizes package names.
""",
        encoding="utf-8",
    )
    api_comparison = (
        "  - **Docs Comparison**: Existing docs mention API auth.\n"
        if include_all_comparisons
        else ""
    )
    (repo / "CONTEXT_PLAN.md").write_text(
        f"""# Knowledge Base Manifest

## Task Manifest

- [planned] release-packaging
  - **ID**: `release-packaging`
  - **Context**: `.dev-cycle/context/release/packaging.md`
  - **Sources**: `src/release.py`
  - **Focus**: Release package boundaries.
  - **Tags**: `release`, `packaging`
  - **Docs Comparison**: `docs/release.md` covers overview only.
  - **Status**: `planned`
- [planned] api-auth-flow
  - **ID**: `api-auth-flow`
  - **Context**: `.dev-cycle/context/api/auth-flow.md`
  - **Sources**: `src/api/auth.py`
  - **Focus**: API auth flow.
  - **Tags**: `api`, `auth`
{api_comparison}  - **Status**: `planned`
""",
        encoding="utf-8",
    )


class KbDocsTests(unittest.TestCase):
    def test_inventories_existing_docs_and_manifest_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_docs_repo(repo)

            proc, data = docs_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(
                [doc["path"] for doc in data["existingDocs"]],
                ["README.md", "docs/release.md"],
            )
            self.assertEqual(data["existingDocs"][1]["title"], "Release Packaging")
            self.assertEqual(data["unmatchedPatterns"], ["missing/**"])
            self.assertEqual(data["docsComparison"]["coverage"], 50.0)
            self.assertEqual(data["docsComparison"]["missing"], ["api-auth-flow"])
            self.assertEqual(data["deadLinks"], [])
            hints = data["duplicateHints"]
            self.assertEqual(data["duplicateHintCount"], len(hints))
            self.assertEqual(data["duplicateHintSeverityCounts"]["high"], len(hints))
            self.assertTrue(
                any(
                    hint["taskId"] == "release-packaging"
                    and hint["doc"] == "docs/release.md"
                    and hint["severity"] == "high"
                    and any("source-mentioned" in reason for reason in hint["reasons"])
                    for hint in hints
                ),
                hints,
            )

    def test_summary_json_omits_full_heading_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_docs_repo(repo)

            proc, data = docs_summary_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["existingDocsCount"], 2)
            self.assertEqual(data["docsComparison"]["missing"], ["api-auth-flow"])
            self.assertIn("topDuplicateHints", data)
            self.assertIn("release-packaging", data["topDuplicateHintsByTask"])
            self.assertNotIn("existingDocs", data)

    def test_generic_tag_only_matches_do_not_create_duplicate_hints(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / ".dev-cycle" / "context").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / ".dev-cycle" / "context" / "config.yaml").write_text(
                """docs:
  existing:
    - docs/**
""",
                encoding="utf-8",
            )
            (repo / "docs" / "brief.md").write_text(
                "# Development Brief\n\nPreview cache verification notes.\n",
                encoding="utf-8",
            )
            (repo / "CONTEXT_PLAN.md").write_text(
                """# Knowledge Base Manifest

## Task Manifest

- [planned] unrelated-runtime
  - **ID**: `unrelated-runtime`
  - **Context**: `.dev-cycle/context/runtime/unrelated.md`
  - **Sources**: `src/runtime.ts`
  - **Focus**: Runtime behavior.
  - **Tags**: `preview`, `cache`, `verification`
  - **Docs Comparison**: No existing docs.
  - **Status**: `planned`
""",
                encoding="utf-8",
            )

            proc, data = docs_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["duplicateHints"], [])
            self.assertEqual(data["duplicateHintSeverityCounts"], {"high": 0, "medium": 0, "low": 0})

    def test_general_doc_source_mentions_are_medium_severity(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / ".dev-cycle" / "context").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / ".dev-cycle" / "context" / "config.yaml").write_text(
                """docs:
  existing:
    - docs/**
""",
                encoding="utf-8",
            )
            (repo / "docs" / "brief.md").write_text(
                "# Brief\n\nSee README.md for the overview.\n",
                encoding="utf-8",
            )
            (repo / "CONTEXT_PLAN.md").write_text(
                """# Knowledge Base Manifest

## Task Manifest

- [planned] overview-routing
  - **ID**: `overview-routing`
  - **Context**: `.dev-cycle/context/overview/routing.md`
  - **Sources**: `README.md`
  - **Focus**: Overview routing.
  - **Tags**: `docs`
  - **Docs Comparison**: No existing docs.
  - **Status**: `planned`
""",
                encoding="utf-8",
            )

            proc, data = docs_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["duplicateHintSeverityCounts"], {"high": 0, "medium": 1, "low": 0})
            self.assertEqual(data["duplicateHints"][0]["severity"], "medium")
            self.assertEqual(data["duplicateHints"][0]["sourceMentionKind"], "docs")

    def test_check_manifest_fails_when_comparison_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_docs_repo(repo)

            proc, data = docs_json(repo, "--check-manifest")
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(data["docsComparison"]["missing"], ["api-auth-flow"])

    def test_check_manifest_passes_when_comparison_is_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_docs_repo(repo, include_all_comparisons=True)

            proc, data = docs_json(repo, "--check-manifest")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["docsComparison"]["missing"], [])

    def test_dead_links_are_reported_and_checkable(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_docs_repo(repo, include_all_comparisons=True)
            release_doc = repo / "docs" / "release.md"
            release_doc.write_text(
                release_doc.read_text(encoding="utf-8")
                + "\nSee [missing](missing.md).\n"
                + "\n```markdown\n[example only](ignored.md)\n```\n",
                encoding="utf-8",
            )

            proc, data = docs_json(repo, "--check-links")
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(
                data["deadLinks"],
                [{"line": 9, "source": "docs/release.md", "target": "missing.md"}],
            )

            text_proc = run(
                [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--duplicate-limit", "0"],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(text_proc.returncode, 0, text_proc.stdout + text_proc.stderr)
            self.assertIn("## Dead Links", text_proc.stdout)
            self.assertIn("docs/release.md:9 -> missing.md", text_proc.stdout)
            self.assertIn("## Duplicate Hints (0/", text_proc.stdout)
            self.assertIn("more omitted", text_proc.stdout)

    def test_existing_docs_respect_exclude_patterns(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / ".dev-cycle" / "context").mkdir(parents=True)
            (repo / ".dev-cycle" / "context" / "config.yaml").write_text(
                """include:
  - "*.md"
exclude:
  - .dev-cycle/**
  - CONTEXT_PLAN.md
docs:
  existing:
    - "*.md"
""",
                encoding="utf-8",
            )
            (repo / "README.md").write_text("# Project\n", encoding="utf-8")
            (repo / "CONTEXT_PLAN.md").write_text("# Plan\n", encoding="utf-8")
            (repo / ".dev-cycle" / "context" / "draft.md").write_text("# Draft\n", encoding="utf-8")

            proc, data = docs_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual([doc["path"] for doc in data["existingDocs"]], ["README.md"])

    def test_missing_repo_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "missing"
            proc = run(
                [sys.executable, "-B", str(TOOL), "--repo", str(repo)],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("repo does not exist", proc.stderr)


if __name__ == "__main__":
    unittest.main()
