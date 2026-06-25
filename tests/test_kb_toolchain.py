import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_kb_audit import PROJECT_ROOT, run

AUDIT = PROJECT_ROOT / "tools" / "kb_audit.py"
FINGERPRINT = PROJECT_ROOT / "tools" / "kb_fingerprint.py"
MANIFEST = PROJECT_ROOT / "tools" / "kb_manifest.py"
SCAFFOLD = PROJECT_ROOT / "tools" / "kb_scaffold.py"


def tool(repo: Path, script: Path, *args: str):
    return run(
        [sys.executable, "-B", str(script), "--repo", str(repo), *args],
        PROJECT_ROOT,
        check=False,
    )


def write_plan(repo: Path, status: str) -> None:
    repo.joinpath("KB_PLAN.md").write_text(
        f"""# Knowledge Base Manifest

## Task Manifest

- [{status}] release-packaging
  - **ID**: `release-packaging`
  - **KB**: `.agent/kb/release/packaging.md`
  - **Sources**: `src/release.py`
  - **Focus**: Release package boundary behavior.
  - **Tags**: `release`, `packaging`
  - **Status**: `{status}`
  - **LastValidated**: `2026-06-26`
""",
        encoding="utf-8",
    )


def yaml_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(value)


def write_kb_artifacts(repo: Path, fingerprint: dict) -> None:
    kb = repo / ".agent" / "kb" / "release" / "packaging.md"
    kb.parent.mkdir(parents=True, exist_ok=True)
    kb.write_text(
        f"""---
id: "release-packaging"
title: "Release Packaging"
status: "built"
notAuthoritative: false
fingerprint:
  - file: {yaml_value(fingerprint["file"])}
    commit: {yaml_value(fingerprint["commit"])}
    tracked: {yaml_value(fingerprint["tracked"])}
    worktree: {yaml_value(fingerprint["worktree"])}
    contentHash: {yaml_value(fingerprint["contentHash"])}
tags: ["release", "packaging"]
---

# Release Packaging

## Role

The release module owns package name normalization before artifacts are emitted.

## Contracts

- `package_name(name)` returns a deterministic package identifier.
- Empty names are rejected by the source module before a package identifier is returned.

## Blindspots

- None
""",
        encoding="utf-8",
    )

    glossary = repo / ".agent" / "kb" / "GLOSSARY.md"
    glossary.write_text(
        """| Term / Keyword | Synonyms | Target KB Document Link |
|---|---|---|
| Release packaging | package artifact | [packaging.md](release/packaging.md) |
""",
        encoding="utf-8",
    )

    validation = repo / ".agent" / "kb" / "_validation" / "release-packaging.md"
    validation.write_text(
        """# Validation: release-packaging

- **KB**: `.agent/kb/release/packaging.md`
- **Source Mode**: `clean`
- **Validated At**: `2026-06-26`

## Questions

### Q1 Architecture

- **Question**: Which module owns package name normalization?
- **KB-only Answer**: The release module owns package name normalization.
- **Citations**: `.agent/kb/release/packaging.md`
- **Result**: pass

### Q2 Boundary

- **Question**: What happens for empty names?
- **KB-only Answer**: Empty names are rejected before an identifier is returned.
- **Citations**: `.agent/kb/release/packaging.md`
- **Result**: pass

## Blindspots

- None
""",
        encoding="utf-8",
    )


class KbToolchainTests(unittest.TestCase):
    def test_scaffold_manifest_fingerprint_audit_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            repo.mkdir()
            (repo / "README.md").write_text("# Project\n", encoding="utf-8")
            (repo / "src").mkdir()
            (repo / "src" / "release.py").write_text(
                """def package_name(name):
    if not name:
        raise ValueError("name is required")
    return f"pkg-{name}"
""",
                encoding="utf-8",
            )
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test User"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)
            run(["git", "add", "README.md", "src/release.py"], repo)
            run(["git", "commit", "-m", "initial source"], repo)

            scaffold = tool(repo, SCAFFOLD)
            self.assertEqual(scaffold.returncode, 0, scaffold.stdout + scaffold.stderr)
            self.assertTrue((repo / ".agent" / "kb" / "config.yaml").exists())
            self.assertTrue((repo / ".agent" / "kb" / "_validation").is_dir())

            write_plan(repo, "planned")
            select = tool(
                repo,
                MANIFEST,
                "--only",
                "release-packaging",
                "--slice",
                "1",
                "--json",
            )
            self.assertEqual(select.returncode, 0, select.stdout + select.stderr)
            selection = json.loads(select.stdout)
            self.assertEqual(selection["selectedCount"], 1)
            self.assertEqual(selection["selected"][0]["id"], "release-packaging")
            self.assertEqual(selection["selected"][0]["status"], "planned")

            fingerprint_proc = tool(repo, FINGERPRINT, "--json", "src/release.py")
            self.assertEqual(
                fingerprint_proc.returncode,
                0,
                fingerprint_proc.stdout + fingerprint_proc.stderr,
            )
            fingerprint = json.loads(fingerprint_proc.stdout)["fingerprints"][0]
            self.assertEqual(fingerprint["worktree"], "clean")

            write_plan(repo, "built")
            write_kb_artifacts(repo, fingerprint)

            check = tool(
                repo,
                FINGERPRINT,
                "--json",
                "--check",
                ".agent/kb/release/packaging.md",
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertTrue(json.loads(check.stdout)["checks"][0]["ok"])

            audit = tool(
                repo,
                AUDIT,
                "--json",
                "--write-index",
                ".agent/kb/index.json",
                "--fail-on",
                "stale",
                "--fail-on",
                "dead-links",
                "--fail-on",
                "missing-validation",
                "--fail-on",
                "missing-config",
                "--fail-on",
                "boundary",
                "--min-score",
                "A",
            )
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
            audit_data = json.loads(audit.stdout)
            self.assertEqual(audit_data["summary"]["grade"], "A")
            self.assertEqual(audit_data["summary"]["failures"], [])
            self.assertEqual(audit_data["manifest"][0]["id"], "release-packaging")
            documents = {document["path"]: document for document in audit_data["documents"]}
            self.assertTrue(documents[".agent/kb/release/packaging.md"]["fresh"])

            index = json.loads(
                (repo / ".agent" / "kb" / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(index["summary"]["grade"], "A")
            self.assertEqual(index["terms"][0]["term"], "Release packaging")


if __name__ == "__main__":
    unittest.main()
