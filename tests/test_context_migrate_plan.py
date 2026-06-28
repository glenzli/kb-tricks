import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_context_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "context_migrate_plan.py"


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
    def test_dry_run_migrates_legacy_path_entries_from_context_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            context = repo / ".dev-cycle" / "context" / "core" / "scanner-state.md"
            context.parent.mkdir(parents=True)
            context.write_text(
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
            (repo / "CONTEXT_PLAN.md").write_text(
                """# Context Manifest

## Task Manifest

- [x] .dev-cycle/context/core/scanner-state.md
""",
                encoding="utf-8",
            )

            proc, data = migrate_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse(data["written"])
            self.assertEqual(data["legacyCount"], 1)
            entry = data["entries"][0]
            self.assertEqual(entry["id"], "scanner-state")
            self.assertEqual(entry["context"], ".dev-cycle/context/core/scanner-state.md")
            self.assertEqual(entry["sources"], "src/scanner.ts")
            self.assertEqual(entry["tags"], "runtime, scanner")
            self.assertEqual(entry["inferredFields"], ["ID", "Context", "Sources", "Focus", "Tags", "Status"])
            self.assertEqual(entry["missingFields"], ["Docs Comparison"])
            self.assertEqual(
                (repo / "CONTEXT_PLAN.md").read_text(encoding="utf-8").strip(),
                "# Context Manifest\n\n## Task Manifest\n\n- [x] .dev-cycle/context/core/scanner-state.md",
            )

    def test_write_rewrites_legacy_entries_to_explicit_manifest_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / "CONTEXT_PLAN.md").write_text(
                """# Context Manifest

## Task Manifest

- [ ] .dev-cycle/context/release/release-packaging.md
""",
                encoding="utf-8",
            )

            proc, data = migrate_json(repo, "--write")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(data["written"])
            text = (repo / "CONTEXT_PLAN.md").read_text(encoding="utf-8")
            self.assertIn("- [planned] release-packaging", text)
            self.assertIn("- **ID**: `release-packaging`", text)
            self.assertIn("- **Context**: `.dev-cycle/context/release/release-packaging.md`", text)
            self.assertIn("- **Sources**: TBD", text)
            self.assertIn("- **Docs Comparison**: TBD", text)

    def test_existing_legacy_fields_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / "CONTEXT_PLAN.md").write_text(
                """# Context Manifest

## Task Manifest

- [ ] `.dev-cycle/context/release/release-packaging.md`
  - **Sources**: `src/cli/release.ts`, `.vscodeignore`, `package.json`
  - **Focus**: Release packaging behavior.
  - **Tags**: `release`, `packaging`
  - **Docs Comparison**: `docs/release.md` covers user flow.
  - **Status**: `stale`
  - **LastValidated**: `2026-06-28`
""",
                encoding="utf-8",
            )

            proc, data = migrate_json(repo, "--write")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            entry = data["entries"][0]
            self.assertEqual(
                entry["preservedFields"],
                ["Sources", "Focus", "Tags", "Docs Comparison", "Status", "LastValidated"],
            )
            self.assertEqual(entry["missingFields"], [])
            text = (repo / "CONTEXT_PLAN.md").read_text(encoding="utf-8")
            self.assertIn("- [stale] release-packaging", text)
            self.assertIn(
                "- **Sources**: `src/cli/release.ts`, `.vscodeignore`, `package.json`",
                text,
            )
            self.assertIn("- **Focus**: Release packaging behavior.", text)
            self.assertIn("- **Tags**: `release`, `packaging`", text)
            self.assertIn(
                "- **Docs Comparison**: `docs/release.md` covers user flow.",
                text,
            )
            self.assertIn("- **LastValidated**: `2026-06-28`", text)


if __name__ == "__main__":
    unittest.main()
