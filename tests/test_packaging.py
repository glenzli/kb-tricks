import sys
import unittest

from test_kb_audit import PROJECT_ROOT

from kb_tricks import __version__

try:
    import tomllib
except ImportError:  # pragma: no cover - Python < 3.11 compatibility
    tomllib = None


class PackagingTests(unittest.TestCase):
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

    def test_supported_runtime_is_inside_declared_range(self):
        self.assertGreaterEqual(sys.version_info, (3, 10))


if __name__ == "__main__":
    unittest.main()
