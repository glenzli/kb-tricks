import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_kb_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "kb_docs.py"


def docs_json(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 1, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


def write_docs_repo(repo: Path, include_all_comparisons: bool = False) -> None:
    (repo / ".agent" / "kb").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".agent" / "kb" / "config.yaml").write_text(
        """include:
  - src/**
exclude:
  - dist/**
releaseExcluded:
  - .agent/**
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
    (repo / "KB_PLAN.md").write_text(
        f"""# Knowledge Base Manifest

## Task Manifest

- [planned] release-packaging
  - **ID**: `release-packaging`
  - **KB**: `.agent/kb/release/packaging.md`
  - **Sources**: `src/release.py`
  - **Focus**: Release package boundaries.
  - **Tags**: `release`, `packaging`
  - **Docs Comparison**: `docs/release.md` covers overview only.
  - **Status**: `planned`
- [planned] api-auth-flow
  - **ID**: `api-auth-flow`
  - **KB**: `.agent/kb/api/auth-flow.md`
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
            hints = data["duplicateHints"]
            self.assertTrue(
                any(
                    hint["taskId"] == "release-packaging"
                    and hint["doc"] == "docs/release.md"
                    and any("source-mentioned" in reason for reason in hint["reasons"])
                    for hint in hints
                ),
                hints,
            )

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
