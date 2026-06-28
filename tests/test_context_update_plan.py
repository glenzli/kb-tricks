import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_context_audit import PROJECT_ROOT, run
from test_context_impact import init_repo, write_impact_repo

TOOL = PROJECT_ROOT / "tools" / "context_update_plan.py"


def plan_json(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


class KbUpdatePlanTests(unittest.TestCase):
    def test_since_clean_commit_plans_allowed_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 2\n", encoding="utf-8")
            run(["git", "add", "src/release.py"], repo)
            run(["git", "commit", "-m", "change release"], repo)

            proc, data = plan_json(repo, "--since", "HEAD~1")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["scopeMode"], "since")
            self.assertEqual(data["blocked"], [])
            self.assertEqual(data["actions"][0]["task"], "release-packaging")
            self.assertEqual(data["actions"][0]["action"], "update")
            self.assertTrue(data["actions"][0]["allowed"])
            self.assertFalse(data["actions"][0]["notAuthoritative"])
            self.assertEqual(data["actions"][0]["sourceStates"][0]["worktree"], "clean")

    def test_worktree_dirty_source_blocks_authoritative_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 3\n", encoding="utf-8")

            proc, data = plan_json(repo, "--worktree")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            action = data["actions"][0]
            self.assertEqual(action["task"], "release-packaging")
            self.assertFalse(action["allowed"])
            self.assertEqual(action["blockedReasons"], ["src/release.py: worktree dirty"])
            self.assertEqual(data["blocked"][0]["task"], "release-packaging")

    def test_draft_mode_allows_dirty_update_as_non_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "release.py").write_text("VALUE = 4\n", encoding="utf-8")

            proc, data = plan_json(repo, "--worktree", "--draft")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            action = data["actions"][0]
            self.assertTrue(action["allowed"])
            self.assertEqual(action["action"], "draft-update")
            self.assertEqual(action["targetContext"], ".dev-cycle/context/release/packaging.md")
            self.assertEqual(action["draftTarget"], ".dev-cycle/context/_draft/release-packaging.md")
            self.assertTrue(action["notAuthoritative"])
            self.assertEqual(data["blocked"], [])

    def test_missing_config_groups_context_support_files_as_setup_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            (repo / ".dev-cycle" / "context" / "config.yaml").unlink()
            init_repo(repo)
            (repo / ".dev-cycle" / "context" / "AGENT_GUIDE.md").write_text(
                "# Agent Guide\n",
                encoding="utf-8",
            )

            proc, data = plan_json(repo, "--worktree", "--draft")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["newContextCandidates"], [])
            self.assertEqual(
                data["setupWarnings"],
                [
                    {
                        "code": "missing-config-context-support-files",
                        "files": [".dev-cycle/context/AGENT_GUIDE.md"],
                        "message": (
                            "config missing; Context support files may be treated as source candidates"
                        ),
                    }
                ],
            )

    def test_missing_config_keeps_dev_docs_out_of_new_context_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            (repo / ".dev-cycle" / "context" / "config.yaml").unlink()
            init_repo(repo)
            (repo / "docs" / "dev").mkdir()
            (repo / "docs" / "dev" / "context.md").write_text(
                "# Development Context\n",
                encoding="utf-8",
            )

            proc, data = plan_json(repo, "--worktree", "--draft")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["newContextCandidates"], [])
            self.assertEqual(data["possibleContextDocs"][0]["file"], "docs/dev/context.md")

    def test_unmatched_included_source_becomes_blocked_new_context_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "src" / "new_module.py").write_text("VALUE = 1\n", encoding="utf-8")

            proc, data = plan_json(repo, "--worktree")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["actions"], [])
            self.assertEqual(data["newContextCandidates"][0]["file"], "src/new_module.py")
            self.assertEqual(data["newContextCandidates"][0]["action"], "create")
            self.assertFalse(data["newContextCandidates"][0]["allowed"])
            self.assertEqual(
                data["newContextCandidates"][0]["blockedReasons"],
                ["src/new_module.py: source untracked"],
            )

    def test_docs_and_special_changes_are_review_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)
            (repo / "docs" / "release.md").write_text("# Release\n\nUpdated.\n", encoding="utf-8")
            (repo / "CONTEXT_PLAN.md").write_text(
                (repo / "CONTEXT_PLAN.md").read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )

            proc, data = plan_json(repo, "--worktree")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(
                data["docsActions"],
                [
                    {
                        "file": "docs/release.md",
                        "action": "review-existing-docs",
                        "allowed": True,
                        "reasons": ["docs.existing"],
                    }
                ],
            )
            self.assertEqual(data["specialActions"][0]["file"], "CONTEXT_PLAN.md")
            self.assertEqual(data["specialActions"][0]["action"], "review-manifest")

    def test_requires_exactly_one_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            write_impact_repo(repo)
            init_repo(repo)

            proc = run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "--repo",
                    str(repo),
                    "--since",
                    "HEAD",
                    "--staged",
                ],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("pass exactly one scope option", proc.stderr)


if __name__ == "__main__":
    unittest.main()
