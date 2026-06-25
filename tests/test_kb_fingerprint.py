import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_kb_audit import PROJECT_ROOT, materialize_fixture, run, sha256

TOOL = PROJECT_ROOT / "tools" / "kb_fingerprint.py"


def fingerprint_json(repo, *args):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 1, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout)


class KbFingerprintTests(unittest.TestCase):
    def test_generates_clean_tracked_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-kb")
            proc, data = fingerprint_json(repo, "src/release.py")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["errors"], [])
            fingerprint = data["fingerprints"][0]
            self.assertEqual(fingerprint["file"], "src/release.py")
            self.assertTrue(fingerprint["tracked"])
            self.assertEqual(fingerprint["worktree"], "clean")
            self.assertEqual(fingerprint["contentHash"], sha256(repo / "src/release.py"))
            self.assertTrue(fingerprint["commit"])

    def test_dirty_tracked_source_requires_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-kb")
            source = repo / "src" / "release.py"
            source.write_text(source.read_text(encoding="utf-8") + "\n# dirty\n", encoding="utf-8")

            proc, data = fingerprint_json(repo, "src/release.py")
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(data["fingerprints"][0]["worktree"], "dirty")
            self.assertTrue(data["errors"])

            allowed, allowed_data = fingerprint_json(repo, "--allow-dirty", "src/release.py")
            self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
            self.assertEqual(allowed_data["errors"], [])
            self.assertEqual(allowed_data["fingerprints"][0]["worktree"], "dirty")

    def test_untracked_source_requires_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-kb")
            untracked = repo / "src" / "new_module.py"
            untracked.write_text("VALUE = 1\n", encoding="utf-8")

            proc, data = fingerprint_json(repo, "src/new_module.py")
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(data["fingerprints"][0]["tracked"])
            self.assertEqual(data["fingerprints"][0]["worktree"], "untracked")

            allowed, allowed_data = fingerprint_json(
                repo, "--allow-untracked", "src/new_module.py"
            )
            self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
            self.assertIsNone(allowed_data["fingerprints"][0]["commit"])

    def test_missing_source_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-kb")
            proc, data = fingerprint_json(repo, "src/missing.py")
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(data["fingerprints"], [])
            self.assertTrue(data["errors"])

    def test_check_valid_kb_doc_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-kb")
            proc, data = fingerprint_json(
                repo, "--check", ".agent/kb/release/packaging.md"
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["errors"], [])
            self.assertTrue(data["checks"][0]["ok"])
            self.assertEqual(data["checks"][0]["file"], "src/release.py")

    def test_check_stale_kb_doc_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-kb")
            source = repo / "src" / "release.py"
            source.write_text(source.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
            run(["git", "add", "src/release.py"], repo)
            run(["git", "commit", "-m", "change source"], repo)

            proc, data = fingerprint_json(
                repo, "--check", ".agent/kb/release/packaging.md"
            )
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(data["checks"][0]["ok"])
            self.assertIn("contentHash mismatch", data["checks"][0]["reasons"])
            self.assertIn("commit mismatch", data["checks"][0]["reasons"])

    def test_check_dirty_kb_doc_fails_without_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-kb")
            source = repo / "src" / "release.py"
            source.write_text(source.read_text(encoding="utf-8") + "\n# dirty\n", encoding="utf-8")

            proc, data = fingerprint_json(
                repo, "--check", ".agent/kb/release/packaging.md"
            )
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(data["checks"][0]["ok"])
            self.assertTrue(
                any("worktree is dirty" in reason for reason in data["checks"][0]["reasons"])
            )


if __name__ == "__main__":
    unittest.main()
