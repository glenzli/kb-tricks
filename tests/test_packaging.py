from importlib import resources
import sys
import unittest

from test_kb_audit import PROJECT_ROOT

from kb_tricks import __version__
from tools import release_rehearsal, release_smoke

try:
    import tomllib
except ImportError:  # pragma: no cover - Python < 3.11 compatibility
    tomllib = None


class PackagingTests(unittest.TestCase):
    template_names = [
        "config.yaml",
        "AGENT_GUIDE.md",
        "KB_PLAN.md",
        "kb-doc.md",
        "validation.md",
        "query-answer.md",
    ]

    @unittest.skipIf(tomllib is None, "tomllib is unavailable")
    def test_pyproject_declares_released_cli_entrypoint(self):
        data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertIn("setuptools>=77", data["build-system"]["requires"])
        self.assertEqual(data["project"]["name"], "kb-tricks")
        self.assertEqual(data["project"]["version"], __version__)
        self.assertEqual(data["project"]["requires-python"], ">=3.10")
        self.assertEqual(data["project"]["license"], "MIT")
        self.assertEqual(data["project"]["license-files"], ["LICENSE"])
        self.assertEqual(data["project"]["scripts"]["kb"], "kb_tricks.cli:main")

        include = set(data["tool"]["setuptools"]["packages"]["find"]["include"])
        self.assertIn("kb_tricks", include)
        self.assertIn("kb_tricks.*", include)
        self.assertNotIn("tools", include)
        self.assertNotIn("tools.*", include)

        package_data = data["tool"]["setuptools"]["package-data"]["kb_tricks"]
        self.assertIn("templates/*", package_data)

    def test_package_templates_match_source_templates(self):
        package_root = resources.files("kb_tricks").joinpath("templates")
        for name in self.template_names:
            source = PROJECT_ROOT / "templates" / name
            packaged = package_root.joinpath(name)
            self.assertEqual(
                packaged.read_text(encoding="utf-8"),
                source.read_text(encoding="utf-8"),
                name,
            )

    def test_sdist_manifest_includes_release_artifacts(self):
        manifest = (PROJECT_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        self.assertIn("include RELEASE.md", manifest)
        self.assertIn("recursive-include templates *", manifest)
        self.assertIn("recursive-include spec *.md", manifest)
        self.assertIn("recursive-include skills *", manifest)
        self.assertIn("recursive-include tools *.py", manifest)
        self.assertIn("recursive-include kb_tricks/templates *", manifest)

    def test_release_rehearsal_defaults_to_committed_source(self):
        args = release_rehearsal.parse_args([])

        self.assertEqual(args.source, "head")

    def test_release_rehearsal_checks_artifact_boundaries(self):
        self.assertIn("tools/release_rehearsal.py", release_rehearsal.SDIST_REQUIRED)
        self.assertIn("tools/release_rehearsal.py", release_rehearsal.WHEEL_FORBIDDEN)
        self.assertIn("skills/kb-build/SKILL.md", release_rehearsal.SDIST_REQUIRED)
        self.assertIn("skills/kb-build/SKILL.md", release_rehearsal.WHEEL_FORBIDDEN)
        self.assertIn("kb_tricks/commands/audit.py", release_rehearsal.WHEEL_REQUIRED)
        self.assertIn("kb_tricks/templates/AGENT_GUIDE.md", release_rehearsal.WHEEL_REQUIRED)
        self.assertIn("kb_tricks/templates/config.yaml", release_rehearsal.WHEEL_REQUIRED)

    def test_release_smoke_commands_cover_source_checks(self):
        commands = release_smoke.smoke_commands(
            installed=False,
            include_tests=True,
            include_git_check=True,
        )
        rendered = [" ".join(command) for command in commands]
        self.assertTrue(any("unittest discover tests" in item for item in rendered))
        self.assertTrue(any("kb_tricks.cli self-check --json" in item for item in rendered))
        self.assertTrue(any("query-lint --json templates/query-answer.md" in item for item in rendered))
        self.assertIn("git diff --check", rendered)

    def test_release_docs_create_scaffold_target_before_smoke(self):
        release_notes = (PROJECT_ROOT / "RELEASE.md").read_text(encoding="utf-8")

        self.assertIn("mkdir -p /tmp/kb-smoke", release_notes)
        self.assertIn("kb scaffold --repo /tmp/kb-smoke --dry-run", release_notes)
        self.assertIn(
            "python3 tools/kb_scaffold.py --repo /tmp/kb-smoke --dry-run",
            release_notes,
        )

    def test_release_docs_reference_full_rehearsal(self):
        release_notes = (PROJECT_ROOT / "RELEASE.md").read_text(encoding="utf-8")

        self.assertIn("python3 -B tools/release_rehearsal.py", release_notes)

    def test_ci_workflow_uses_release_smoke(self):
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python -B tools/release_smoke.py", workflow)
        self.assertIn("python -m pip install .", workflow)
        self.assertIn(
            "python -B tools/release_smoke.py --installed --skip-tests --skip-git-check",
            workflow,
        )

    def test_supported_runtime_is_inside_declared_range(self):
        self.assertGreaterEqual(sys.version_info, (3, 10))


if __name__ == "__main__":
    unittest.main()
