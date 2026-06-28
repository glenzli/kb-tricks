import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"
TOOL = PROJECT_ROOT / "tools" / "context_audit.py"


def run(cmd, cwd, check=True):
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test User",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test User",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
    )
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise AssertionError(
            f"command failed: {cmd}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def sha256(path):
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def materialize_fixture(tmpdir, name):
    source = FIXTURES / name
    repo = Path(tmpdir) / name
    shutil.copytree(source, repo)
    run(["git", "init"], repo)
    run(["git", "config", "user.name", "Test User"], repo)
    run(["git", "config", "user.email", "test@example.com"], repo)
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "fixture source"], repo)

    commit = run(
        ["git", "log", "-1", "--format=%H", "--", "src/release.py"], repo
    ).stdout.strip()
    content_hash = sha256(repo / "src" / "release.py")
    for path in repo.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text.replace("__COMMIT__", commit).replace("__HASH__", content_hash)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "materialize fingerprints"], repo)
    return repo


def audit_json(repo, *args):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 1}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout)


def audit_summary_json(repo, *args):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--summary-json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 1}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout)


class KbAuditTests(unittest.TestCase):
    def test_valid_fixture_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-context")
            proc, data = audit_json(
                repo,
                "--fail-on",
                "stale",
                "--fail-on",
                "dead-links",
                "--fail-on",
                "missing-validation",
                "--min-score",
                "A",
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["summary"]["grade"], "A")
            self.assertEqual(data["summary"]["failures"], [])
            self.assertEqual(data["validationMissing"], [])
            self.assertEqual(data["missingContext"], [])
            documents = {document["path"]: document for document in data["documents"]}
            self.assertIn(".dev-cycle/context/release/packaging.md", documents)
            self.assertIn(".dev-cycle/context/GLOSSARY.md", documents)
            self.assertIn(".dev-cycle/context/_validation/release-packaging.md", documents)
            self.assertFalse(documents[".dev-cycle/context/release/packaging.md"]["draft"])
            self.assertEqual(
                documents[".dev-cycle/context/release/packaging.md"]["kind"], "authoritative"
            )
            self.assertEqual(documents[".dev-cycle/context/GLOSSARY.md"]["kind"], "support")
            self.assertEqual(
                documents[".dev-cycle/context/_validation/release-packaging.md"]["kind"],
                "reserved",
            )

    def test_summary_json_is_compact_and_classifies_support_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-context")
            proc, data = audit_summary_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["summary"]["grade"], "A")
            self.assertEqual(data["summary"]["healthGrade"], "A")
            self.assertEqual(data["summary"]["completenessGrade"], "A")
            self.assertEqual(data["summary"]["completeness"]["status"], "complete")
            self.assertEqual(data["counts"]["authoritativeDocuments"], 1)
            self.assertEqual(data["counts"]["supportDocuments"], 1)
            self.assertEqual(data["counts"]["reservedDocuments"], 1)
            self.assertEqual(data["supportDocuments"][0]["path"], ".dev-cycle/context/GLOSSARY.md")
            self.assertEqual(
                data["supportDocuments"][0]["links"][0]["target"],
                "./release/packaging.md",
            )
            self.assertNotIn("documents", data)

    def test_summary_reports_context_artifact_git_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-context")
            glossary = repo / ".dev-cycle" / "context" / "GLOSSARY.md"
            glossary.write_text(
                glossary.read_text(encoding="utf-8") + "| New term | synonym | [packaging.md](./release/packaging.md) |\n",
                encoding="utf-8",
            )

            proc, data = audit_summary_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["counts"]["artifactGitState"], 1)
            self.assertEqual(
                data["artifactGitState"],
                [
                    {
                        "path": ".dev-cycle/context/GLOSSARY.md",
                        "state": "modified",
                        "xy": " M",
                    }
                ],
            )

    def test_partial_bounded_context_keeps_health_separate_from_completeness(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-context")
            manifest = repo / "CONTEXT_PLAN.md"
            manifest.write_text(
                manifest.read_text(encoding="utf-8")
                + """
- [planned] second-task
  - **ID**: `second-task`
  - **Context**: `.dev-cycle/context/second.md`
  - **Sources**: `src/release.py`
  - **Focus**: Second bounded task.
  - **Tags**: `test`
  - **Docs Comparison**: No existing docs.
  - **Status**: `planned`
""",
                encoding="utf-8",
            )

            proc, data = audit_summary_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["summary"]["healthGrade"], "A")
            self.assertEqual(data["summary"]["completenessGrade"], "C")
            self.assertEqual(data["summary"]["completeness"]["coverage"], 50.0)
            self.assertEqual(data["summary"]["completeness"]["status"], "incomplete")

    def test_broken_fixture_reports_policy_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "broken-context")
            proc, data = audit_json(
                repo,
                "--fail-on",
                "stale",
                "--fail-on",
                "dead-links",
                "--fail-on",
                "missing",
                "--fail-on",
                "missing-validation",
                "--fail-on",
                "draft",
                "--fail-on",
                "orphaned",
            )
            self.assertEqual(proc.returncode, 1)
            failures = data["summary"]["failures"]
            self.assertTrue(any(item.startswith("stale:") for item in failures), failures)
            self.assertTrue(
                any(item.startswith("dead-links:") for item in failures), failures
            )
            self.assertTrue(any(item.startswith("missing:") for item in failures), failures)
            self.assertTrue(
                any(item.startswith("missing-validation:") for item in failures),
                failures,
            )
            self.assertTrue(any(item.startswith("draft:") for item in failures), failures)
            self.assertTrue(any(item.startswith("orphaned:") for item in failures), failures)
            self.assertEqual(data["missingContext"], [".dev-cycle/context/missing.md"])
            self.assertEqual(set(data["validationMissing"]), {"release-packaging", "missing-doc"})

    def test_dirty_source_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-context")
            source = repo / "src" / "release.py"
            source.write_text(source.read_text(encoding="utf-8") + "\n# dirty\n", encoding="utf-8")
            proc, data = audit_json(repo, "--fail-on", "dirty")
            self.assertEqual(proc.returncode, 1)
            failures = data["summary"]["failures"]
            self.assertTrue(any(item.startswith("dirty:") for item in failures), failures)
            documents = {
                document["path"]: document for document in data["documents"]
            }
            self.assertTrue(documents[".dev-cycle/context/release/packaging.md"]["dirtyReasons"])

    def test_write_index_outputs_expected_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = materialize_fixture(tmp, "valid-context")
            index_path = repo / ".dev-cycle" / "context" / "index.json"
            proc = run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "--repo",
                    str(repo),
                    "--write-index",
                    ".dev-cycle/context/index.json",
                ],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(data["schemaVersion"], 1)
            self.assertEqual(data["summary"]["grade"], "A")
            self.assertEqual(data["manifest"][0]["id"], "release-packaging")
            self.assertEqual(data["documents"][0]["path"], ".dev-cycle/context/GLOSSARY.md")
            self.assertEqual(data["existingDocs"][0]["path"], "README.md")
            self.assertEqual(data["docsComparison"]["missing"], ["release-packaging"])

    def test_missing_manifest_policy_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "empty"
            repo.mkdir()
            run(["git", "init"], repo)
            default_proc, default_data = audit_json(repo)
            self.assertEqual(default_proc.returncode, 0, default_proc.stdout + default_proc.stderr)
            self.assertEqual(default_data["summary"]["grade"], "F")
            self.assertEqual(default_data["summary"]["metrics"]["setup"], 0.0)

            proc = run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "--repo",
                    str(repo),
                    "--fail-on",
                    "missing-manifest",
                ],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("missing-manifest: 1", proc.stdout)


if __name__ == "__main__":
    unittest.main()
