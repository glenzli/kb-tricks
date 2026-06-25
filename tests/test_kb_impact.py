import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_kb_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "kb_impact.py"


def impact_json(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


def write_impact_repo(repo: Path) -> None:
    (repo / ".agent" / "kb" / "release").mkdir(parents=True)
    (repo / "src").mkdir()
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
    - docs/**
""",
        encoding="utf-8",
    )
    (repo / "KB_PLAN.md").write_text(
        """# Knowledge Base Manifest

## Task Manifest

- [built] release-packaging
  - **ID**: `release-packaging`
  - **KB**: `.agent/kb/release/packaging.md`
  - **Sources**: `src/release.py`
  - **Focus**: Release package boundaries.
  - **Tags**: `release`, `packaging`
  - **Docs Comparison**: `docs/release.md` has overview only.
  - **Status**: `built`
- [built] api-auth-flow
  - **ID**: `api-auth-flow`
  - **KB**: `.agent/kb/api/auth-flow.md`
  - **Sources**: `src/api/auth.py`
  - **Focus**: API auth flow.
  - **Tags**: `api`, `auth`
  - **Docs Comparison**: No existing docs.
  - **Status**: `built`
""",
        encoding="utf-8",
    )
    (repo / "src" / "release.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "docs" / "release.md").write_text("# Release\n", encoding="utf-8")
    (repo / ".agent" / "kb" / "release" / "packaging.md").write_text(
        """---
id: "release-packaging"
title: "Release Packaging"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "src/release.py"
    commit: null
    tracked: true
    worktree: "clean"
    contentHash: "sha256:placeholder"
tags: ["release", "packaging"]
---

# Release Packaging
""",
        encoding="utf-8",
    )


class KbImpactTests(unittest.TestCase):
    def test_since_maps_changed_files_to_tasks_and_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test User"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "initial"], repo)
            (repo / "src" / "release.py").write_text("VALUE = 2\n", encoding="utf-8")
            (repo / "docs" / "release.md").write_text("# Release\n\nUpdated.\n", encoding="utf-8")

            proc, data = impact_json(repo, "--since", "HEAD", "--slice", "1")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(set(data["changedFiles"]), {"src/release.py", "docs/release.md"})
            self.assertEqual(data["impactedTasks"][0]["id"], "release-packaging")
            self.assertEqual(data["selectedTasks"][0]["id"], "release-packaging")
            self.assertEqual(data["docsChanges"], ["docs/release.md"])
            self.assertEqual(data["unmatchedFiles"], [])

    def test_files_maps_kb_path_to_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)

            proc, data = impact_json(repo, "--files", ".agent/kb/release/packaging.md")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["impactedTasks"][0]["id"], "release-packaging")
            self.assertEqual(
                data["impactedTasks"][0]["matchedFiles"],
                [{"file": ".agent/kb/release/packaging.md", "reason": "kb"}],
            )

    def test_requires_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)

            proc = run(
                [sys.executable, "-B", str(TOOL), "--repo", str(repo)],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("pass --since or --files", proc.stderr)


if __name__ == "__main__":
    unittest.main()
