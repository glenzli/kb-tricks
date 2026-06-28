import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_kb_audit import PROJECT_ROOT, run
from tools import kb_scaffold

SCAFFOLD = PROJECT_ROOT / "tools" / "kb_scaffold.py"
AUDIT = PROJECT_ROOT / "tools" / "kb_audit.py"


def scaffold(repo, *args):
    return run(
        [sys.executable, "-B", str(SCAFFOLD), "--repo", str(repo), *args],
        PROJECT_ROOT,
        check=False,
    )


class KbScaffoldTests(unittest.TestCase):
    def test_scaffold_creates_expected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / "README.md").write_text("# Project\n", encoding="utf-8")
            (repo / "docs").mkdir()

            proc = scaffold(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((repo / ".agent" / "kb" / "config.yaml").exists())
            self.assertTrue((repo / ".agent" / "kb" / "AGENT_GUIDE.md").exists())
            self.assertTrue((repo / "KB_PLAN.md").exists())
            self.assertTrue((repo / ".agent" / "kb" / "_draft" / ".gitkeep").exists())
            self.assertTrue((repo / ".agent" / "kb" / "_impact" / ".gitkeep").exists())
            self.assertTrue((repo / ".agent" / "kb" / "_validation" / ".gitkeep").exists())
            config = (repo / ".agent" / "kb" / "config.yaml").read_text(encoding="utf-8")
            self.assertIn("README.md", config)
            self.assertIn("docs/**", config)
            guide = (repo / ".agent" / "kb" / "AGENT_GUIDE.md").read_text(encoding="utf-8")
            self.assertIn("This repository uses `kb-tricks`", guide)

    def test_scaffold_can_read_packaged_templates_without_source_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            original_templates = kb_scaffold.TEMPLATES
            try:
                kb_scaffold.TEMPLATES = Path(tmp) / "missing-templates"
                writes = kb_scaffold.plan_writes(repo, force=False)
                for write in writes:
                    kb_scaffold.apply_write(write)
            finally:
                kb_scaffold.TEMPLATES = original_templates

            self.assertTrue((repo / ".agent" / "kb" / "config.yaml").exists())
            self.assertTrue((repo / ".agent" / "kb" / "AGENT_GUIDE.md").exists())
            self.assertIn(
                "Knowledge Base Manifest",
                (repo / "KB_PLAN.md").read_text(encoding="utf-8"),
            )

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            proc = scaffold(repo, "--dry-run")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("WRITE .agent/kb/config.yaml", proc.stdout)
            self.assertIn("WRITE .agent/kb/AGENT_GUIDE.md", proc.stdout)
            self.assertFalse((repo / ".agent").exists())
            self.assertFalse((repo / "KB_PLAN.md").exists())

    def test_existing_files_are_not_overwritten_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / ".agent" / "kb").mkdir(parents=True)
            config = repo / ".agent" / "kb" / "config.yaml"
            manifest = repo / "KB_PLAN.md"
            config.write_text("custom: true\n", encoding="utf-8")
            manifest.write_text("# Custom\n", encoding="utf-8")

            proc = scaffold(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("SKIP .agent/kb/config.yaml", proc.stdout)
            self.assertEqual(config.read_text(encoding="utf-8"), "custom: true\n")
            self.assertEqual(manifest.read_text(encoding="utf-8"), "# Custom\n")

    def test_force_overwrites_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / ".agent" / "kb").mkdir(parents=True)
            config = repo / ".agent" / "kb" / "config.yaml"
            manifest = repo / "KB_PLAN.md"
            config.write_text("custom: true\n", encoding="utf-8")
            manifest.write_text("# Custom\n", encoding="utf-8")

            proc = scaffold(repo, "--force")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertNotEqual(config.read_text(encoding="utf-8"), "custom: true\n")
            self.assertIn("Knowledge Base Manifest", manifest.read_text(encoding="utf-8"))

    def test_scaffold_satisfies_audit_presence_policies(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            run(["git", "init"], repo)
            self.assertEqual(scaffold(repo).returncode, 0)
            proc = run(
                [
                    sys.executable,
                    "-B",
                    str(AUDIT),
                    "--repo",
                    str(repo),
                    "--fail-on",
                    "missing-manifest",
                    "--fail-on",
                    "missing-config",
                    "--fail-on",
                    "untracked",
                ],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_missing_repo_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "missing"
            proc = scaffold(repo)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("repo does not exist", proc.stderr)


if __name__ == "__main__":
    unittest.main()
