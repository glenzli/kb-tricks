import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_context_audit import PROJECT_ROOT, run
from test_context_manifest import write_manifest


CLI = [sys.executable, "-B", "-m", "dev_cycle.cli"]
PACKAGE_CLI = [sys.executable, "-B", "-m", "dev_cycle"]


class DevCycleCliTests(unittest.TestCase):
    def test_help_lists_commands(self):
        proc = run(CLI + ["--help"], PROJECT_ROOT, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("audit", proc.stdout)
        self.assertIn("impact", proc.stdout)
        self.assertIn("migrate-plan", proc.stdout)
        self.assertIn("query-lint", proc.stdout)
        self.assertIn("self-check", proc.stdout)
        self.assertIn("update-plan", proc.stdout)

    def test_package_module_entrypoint_lists_commands(self):
        proc = run(PACKAGE_CLI + ["--help"], PROJECT_ROOT, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("usage: dev-cycle <command>", proc.stdout)
        self.assertIn("self-check", proc.stdout)

    def test_manifest_command_delegates_to_tool(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            write_manifest(repo)

            proc = run(
                CLI
                + [
                    "context",
                    "manifest",
                    "--repo",
                    str(repo),
                    "--only",
                    "api-auth-flow",
                    "--json",
                ],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["selected"][0]["id"], "api-auth-flow")

    def test_unknown_command_exits_two(self):
        proc = run(CLI + ["missing"], PROJECT_ROOT, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown command group", proc.stderr)

    def test_self_check_imports_all_released_commands(self):
        proc = run(CLI + ["self-check", "--json"], PROJECT_ROOT, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["entryPoint"], "dev_cycle.cli:main")
        commands = {item["command"]: item for item in data["commands"]}
        self.assertIn("context audit", commands)
        self.assertIn("context impact", commands)
        self.assertIn("context migrate-plan", commands)
        self.assertIn("context query-lint", commands)
        self.assertIn("context update-plan", commands)
        self.assertTrue(all(item["ok"] for item in commands.values()))


if __name__ == "__main__":
    unittest.main()
