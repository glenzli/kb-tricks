import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_kb_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "kb_migrate_plan.py"


def migrate_json(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


class KbMigratePlanTests(unittest.TestCase):
    def test_dry_run_migrates_legacy_path_entries_from_kb_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            kb = repo / ".agent" / "kb" / "core" / "scanner-state.md"
            kb.parent.mkdir(parents=True)
            kb.write_text(
                """---
id: "scanner-state"
title: "Scanner State"
status: "built"
notAuthoritative: false
fingerprint:
  - file: "src/scanner.ts"
    commit: "abc"
    tracked: true
    worktree: "clean"
    contentHash: "sha256:abc"
tags: ["runtime", "scanner"]
---

# Scanner State
""",
                encoding="utf-8",
            )
            (repo / "KB_PLAN.md").write_text(
                """# Knowledge Base Manifest

## Task Manifest

- [x] .agent/kb/core/scanner-state.md
""",
                encoding="utf-8",
            )

            proc, data = migrate_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse(data["written"])
            self.assertEqual(data["legacyCount"], 1)
            entry = data["entries"][0]
            self.assertEqual(entry["id"], "scanner-state")
            self.assertEqual(entry["kb"], ".agent/kb/core/scanner-state.md")
            self.assertEqual(entry["sources"], ["src/scanner.ts"])
            self.assertEqual(entry["tags"], ["runtime", "scanner"])
            self.assertEqual(
                (repo / "KB_PLAN.md").read_text(encoding="utf-8").strip(),
                "# Knowledge Base Manifest\n\n## Task Manifest\n\n- [x] .agent/kb/core/scanner-state.md",
            )

    def test_write_rewrites_legacy_entries_to_explicit_manifest_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / "KB_PLAN.md").write_text(
                """# Knowledge Base Manifest

## Task Manifest

- [ ] .agent/kb/release/release-packaging.md
""",
                encoding="utf-8",
            )

            proc, data = migrate_json(repo, "--write")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(data["written"])
            text = (repo / "KB_PLAN.md").read_text(encoding="utf-8")
            self.assertIn("- [planned] release-packaging", text)
            self.assertIn("- **ID**: `release-packaging`", text)
            self.assertIn("- **KB**: `.agent/kb/release/release-packaging.md`", text)
            self.assertIn("- **Sources**: TBD", text)
            self.assertIn("- **Docs Comparison**: TBD", text)


if __name__ == "__main__":
    unittest.main()
