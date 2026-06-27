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


def init_repo(repo: Path) -> None:
    run(["git", "init"], repo)
    run(["git", "config", "user.name", "Test User"], repo)
    run(["git", "config", "user.email", "test@example.com"], repo)
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "initial"], repo)


class KbImpactTests(unittest.TestCase):
    def test_since_maps_changed_files_to_tasks_and_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 2\n", encoding="utf-8")
            (repo / "docs" / "release.md").write_text("# Release\n\nUpdated.\n", encoding="utf-8")

            proc, data = impact_json(repo, "--since", "HEAD", "--slice", "1")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["scopeMode"], "since")
            self.assertEqual(data["scope"], {"mode": "since", "since": "HEAD", "files": []})
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
            self.assertEqual(data["scopeMode"], "files")
            self.assertEqual(
                data["scope"],
                {"mode": "files", "files": [".agent/kb/release/packaging.md"]},
            )
            self.assertEqual(data["impactedTasks"][0]["id"], "release-packaging")
            self.assertEqual(
                data["impactedTasks"][0]["matchedFiles"],
                [{"file": ".agent/kb/release/packaging.md", "reason": "kb"}],
            )

    def test_staged_maps_index_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 3\n", encoding="utf-8")
            run(["git", "add", "src/release.py"], repo)

            proc, data = impact_json(repo, "--staged")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["scopeMode"], "staged")
            self.assertEqual(data["changedFiles"], ["src/release.py"])
            self.assertEqual(data["impactedTasks"][0]["id"], "release-packaging")

    def test_worktree_maps_unstaged_and_untracked_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 4\n", encoding="utf-8")
            (repo / "docs" / "draft.md").write_text("# Draft\n", encoding="utf-8")

            proc, data = impact_json(repo, "--worktree")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["scopeMode"], "worktree")
            self.assertEqual(set(data["changedFiles"]), {"src/release.py", "docs/draft.md"})
            self.assertEqual(data["docsChanges"], ["docs/draft.md"])
            self.assertEqual(data["impactedTasks"][0]["id"], "release-packaging")

    def test_docs_changes_respect_exclude_patterns(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            config = repo / ".agent" / "kb" / "config.yaml"
            config.write_text(
                """include:
  - "*.md"
exclude:
  - .agent/**
  - KB_PLAN.md
docs:
  existing:
    - "*.md"
""",
                encoding="utf-8",
            )
            init_repo(repo)
            (repo / "README.md").write_text("# Project\n\nUpdated.\n", encoding="utf-8")
            (repo / "KB_PLAN.md").write_text("# Plan\n\nUpdated.\n", encoding="utf-8")
            (repo / ".agent" / "kb" / "release" / "packaging.md").write_text(
                "# Draft KB\n",
                encoding="utf-8",
            )

            proc, data = impact_json(repo, "--worktree")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["docsChanges"], ["README.md"])

    def test_base_maps_branch_diff_against_base_commitish(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 5\n", encoding="utf-8")
            run(["git", "add", "src/release.py"], repo)
            run(["git", "commit", "-m", "change release"], repo)

            proc, data = impact_json(repo, "--base", "HEAD~1")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["scopeMode"], "base")
            self.assertEqual(data["scope"], {"mode": "base", "base": "HEAD~1", "files": []})
            self.assertEqual(data["changedFiles"], ["src/release.py"])
            self.assertEqual(data["impactedTasks"][0]["id"], "release-packaging")

    def test_scope_options_are_mutually_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)

            proc = run(
                [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--since", "HEAD", "--staged"],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("pass exactly one scope option", proc.stderr)

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
            self.assertIn("pass exactly one scope option", proc.stderr)


if __name__ == "__main__":
    unittest.main()
