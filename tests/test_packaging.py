from importlib import resources
import sys
import unittest

from test_kb_audit import PROJECT_ROOT

from kb_tricks import __version__

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
        self.assertIn("tools", include)
        self.assertIn("tools.*", include)

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
        self.assertIn("recursive-include kb-* *", manifest)
        self.assertIn("recursive-include moe-* *", manifest)
        self.assertIn("recursive-include kb_tricks/templates *", manifest)

    def test_supported_runtime_is_inside_declared_range(self):
        self.assertGreaterEqual(sys.version_info, (3, 10))


if __name__ == "__main__":
    unittest.main()
