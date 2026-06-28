import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_context_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "context_build_assist.py"


def build_assist(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 1, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


def write_repo(repo: Path) -> None:
    (repo / "src").mkdir()
    (repo / ".dev-cycle" / "context").mkdir(parents=True)
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
""",
        encoding="utf-8",
    )
    (repo / "README.md").write_text("# Project\n", encoding="utf-8")
    (repo / "src" / "release.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "CONTEXT_PLAN.md").write_text(
        """# Context Manifest

## Task Manifest

- [planned] release-packaging
  - **ID**: `release-packaging`
  - **Context**: `.dev-cycle/context/release/packaging.md`
  - **Sources**: `src/release.py`
  - **Focus**: Release package boundaries.
  - **Tags**: `release`, `packaging`
  - **Docs Comparison**: README has no implementation contract.
  - **Status**: `planned`
""",
        encoding="utf-8",
    )


def init_repo(repo: Path) -> None:
    run(["git", "init"], repo)
    run(["git", "config", "user.name", "Test User"], repo)
    run(["git", "config", "user.email", "test@example.com"], repo)
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "initial"], repo)


class ContextBuildAssistTests(unittest.TestCase):
    def test_dry_run_plans_skeleton_writes_without_touching_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_repo(repo)
            init_repo(repo)

            proc, data = build_assist(repo, "--slice", "1")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse((repo / ".dev-cycle" / "context" / "release" / "packaging.md").exists())
            self.assertEqual(data["selectedCount"], 1)
            self.assertFalse(data["write"])
            self.assertEqual(data["plans"][0]["writes"][0]["action"], "write")
            self.assertEqual(data["plans"][0]["fingerprints"][0]["worktree"], "clean")

    def test_write_creates_non_authoritative_context_and_validation_skeletons(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_repo(repo)
            init_repo(repo)

            proc, data = build_assist(repo, "--write", "--slice", "1")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            context = repo / ".dev-cycle" / "context" / "release" / "packaging.md"
            validation = repo / ".dev-cycle" / "context" / "_validation" / "release-packaging.md"
            self.assertTrue(context.exists())
            self.assertTrue(validation.exists())
            context_text = context.read_text(encoding="utf-8")
            validation_text = validation.read_text(encoding="utf-8")
            self.assertIn('id: "release-packaging"', context_text)
            self.assertIn("notAuthoritative: true", context_text)
            self.assertIn('status: "planned"', context_text)
            self.assertIn("contentHash: \"sha256:", context_text)
            self.assertIn("**Result**: pending", validation_text)
            self.assertEqual(data["plans"][0]["writes"][0]["path"], ".dev-cycle/context/release/packaging.md")

    def test_dirty_source_blocks_formal_skeleton(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 2\n", encoding="utf-8")

            proc, data = build_assist(repo, "--write")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("worktree is dirty", data["blocked"][0]["blockedReasons"][0])
            self.assertFalse((repo / ".dev-cycle" / "context" / "release" / "packaging.md").exists())

    def test_draft_allows_dirty_source_under_reserved_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 2\n", encoding="utf-8")

            proc, data = build_assist(repo, "--write", "--draft")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(
                data["plans"][0]["targetContext"],
                ".dev-cycle/context/_draft/release-packaging.md",
            )
            self.assertTrue((repo / ".dev-cycle" / "context" / "_draft" / "release-packaging.md").exists())


if __name__ == "__main__":
    unittest.main()
