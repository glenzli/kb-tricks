import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_kb_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "kb_manifest.py"


def write_manifest(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "KB_PLAN.md").write_text(
        """# Knowledge Base Manifest

## Task Manifest

- [built] release-packaging
  - **ID**: `release-packaging`
  - **KB**: `.agent/kb/release/packaging.md`
  - **Sources**: `src/release.py`
  - **Focus**: Release package boundaries.
  - **Tags**: `release`, `packaging`
  - **Status**: `built`
- [planned] api-auth-flow
  - **ID**: `api-auth-flow`
  - **KB**: `.agent/kb/api/auth-flow.md`
  - **Sources**: `src/api/auth.py`, `src/api/rbac.py`
  - **Focus**: Authentication and RBAC flow.
  - **Tags**: `api`, `auth`
  - **Status**: `planned`
- [stale] cli-config
  - **ID**: `cli-config`
  - **KB**: `.agent/kb/cli/config.md`
  - **Sources**: `src/cli/config.py`
  - **Focus**: CLI config lifecycle.
  - **Tags**: `cli`, `config`
  - **Status**: `stale`
- [merged-into-docs] onboarding
  - **ID**: `onboarding`
  - **KB**: `.agent/kb/dev/onboarding.md`
  - **Sources**: `docs/onboarding.md`
  - **Focus**: Human-facing onboarding docs.
  - **Tags**: `docs`
  - **Status**: `merged-into-docs`
""",
        encoding="utf-8",
    )


def manifest_json(repo: Path, *args: str):
    proc = run(
        [sys.executable, "-B", str(TOOL), "--repo", str(repo), "--json", *args],
        PROJECT_ROOT,
        check=False,
    )
    if proc.returncode not in {0, 2}:
        raise AssertionError(proc.stderr)
    return proc, json.loads(proc.stdout) if proc.stdout else {}


class KbManifestTests(unittest.TestCase):
    def test_default_selects_one_planned_or_stale_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            write_manifest(repo)

            proc, data = manifest_json(repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(data["statuses"], ["planned", "stale"])
            self.assertEqual(data["eligibleCount"], 2)
            self.assertEqual(data["selectedCount"], 1)
            self.assertEqual(data["selected"][0]["id"], "api-auth-flow")

    def test_slice_selects_multiple_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            write_manifest(repo)

            proc, data = manifest_json(repo, "--slice", "2")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(
                [task["id"] for task in data["selected"]],
                ["api-auth-flow", "cli-config"],
            )

    def test_only_matches_id_tag_kb_and_source_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            write_manifest(repo)

            _, by_id = manifest_json(repo, "--only", "api-auth-flow")
            self.assertEqual([task["id"] for task in by_id["selected"]], ["api-auth-flow"])

            _, by_tag = manifest_json(repo, "--only", "cli")
            self.assertEqual([task["id"] for task in by_tag["selected"]], ["cli-config"])

            _, by_kb = manifest_json(repo, "--only", ".agent/kb/api/auth-flow.md")
            self.assertEqual([task["id"] for task in by_kb["selected"]], ["api-auth-flow"])

            _, by_source = manifest_json(repo, "--only", "src/api/auth.py")
            self.assertEqual([task["id"] for task in by_source["selected"]], ["api-auth-flow"])

    def test_status_filter_can_select_built_or_any(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            write_manifest(repo)

            _, built = manifest_json(repo, "--status", "built")
            self.assertEqual([task["id"] for task in built["selected"]], ["release-packaging"])

            _, any_status = manifest_json(repo, "--status", "any", "--slice", "4")
            self.assertEqual(any_status["selectedCount"], 4)
            self.assertEqual(any_status["statuses"], "any")

    def test_invalid_status_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            write_manifest(repo)

            proc = run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "--repo",
                    str(repo),
                    "--status",
                    "unknown",
                ],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("invalid status", proc.stderr)

    def test_missing_manifest_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            proc = run(
                [sys.executable, "-B", str(TOOL), "--repo", str(repo)],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("manifest does not exist", proc.stderr)


if __name__ == "__main__":
    unittest.main()
