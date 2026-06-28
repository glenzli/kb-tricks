from importlib import resources
import sys
import unittest

from test_kb_audit import PROJECT_ROOT

from kb_tricks import __version__
from tools import release_smoke

try:
    import tomllib
except ImportError:  # pragma: no cover - Python < 3.11 compatibility
    tomllib = None


class PackagingTests(unittest.TestCase):
    template_names = [
        "config.yaml",
        "KB_PLAN.md",
        "kb-doc.md",
        "validation.md",
        "query-answer.md",
    ]

    @unittest.skipIf(tomllib is None, "tomllib is unavailable")
    def test_pyproject_declares_released_cli_entrypoint(self):
        data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(data["project"]["name"], "kb-tricks")
        self.assertEqual(data["project"]["version"], __version__)
        self.assertEqual(data["project"]["requires-python"], ">=3.10")
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
