import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_context_audit import PROJECT_ROOT, run

TOOL = PROJECT_ROOT / "tools" / "context_query_lint.py"
CLI = [sys.executable, "-B", "-m", "dev_cycle.cli"]


GOOD_ANSWER = """## 回答 (Answer)

发布边界由 release packaging Context 说明。[Context]
实际包名生成逻辑以当前源码为准。[源码回退]
用户面发布流程还需要参考维护文档。[现有 docs]

## 不确定性与推断 (Uncertainty & Inference)

无

## 引用出处 (Citations)

- Context: `.dev-cycle/context/release/packaging.md`
- 源码: `src/release.py:1`
- 现有 docs: `docs/release.md`

## 知识库状态 (Context Status)

- ✅ 新鲜
"""


def lint_file(path: Path, *args: str):
    return run(
        [sys.executable, "-B", str(TOOL), "--json", str(path), *args],
        PROJECT_ROOT,
        check=False,
    )


class KbQueryLintTests(unittest.TestCase):
    def test_query_answer_template_passes(self):
        proc = lint_file(PROJECT_ROOT / "templates" / "context-query-answer.md")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_valid_answer_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer = Path(tmp) / "answer.md"
            answer.write_text(GOOD_ANSWER, encoding="utf-8")

            proc = lint_file(answer)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(
                data["results"][0]["usedSources"],
                ["context", "docs", "source"],
            )

    def test_repo_resolves_relative_answer_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "project"
            answers = repo / "answers"
            answers.mkdir(parents=True)
            (answers / "answer.md").write_text(GOOD_ANSWER, encoding="utf-8")

            proc = run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "--repo",
                    str(repo),
                    "--json",
                    "answers/answer.md",
                ],
                PROJECT_ROOT,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["results"][0]["path"], "answers/answer.md")

    def test_answer_line_requires_source_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer = Path(tmp) / "answer.md"
            answer.write_text(
                GOOD_ANSWER.replace("发布边界由 release packaging Context 说明。[Context]", "发布边界由 release packaging Context 说明。"),
                encoding="utf-8",
            )

            proc = lint_file(answer)
            self.assertEqual(proc.returncode, 1)
            data = json.loads(proc.stdout)
            violations = data["results"][0]["violations"]
            self.assertTrue(any(item["code"] == "missing-source" for item in violations))

    def test_inference_is_not_allowed_in_answer_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer = Path(tmp) / "answer.md"
            answer.write_text(
                GOOD_ANSWER.replace("发布边界由 release packaging Context 说明。[Context]", "这可能影响 release 顺序。[推断]"),
                encoding="utf-8",
            )

            proc = lint_file(answer)
            self.assertEqual(proc.returncode, 1)
            data = json.loads(proc.stdout)
            violations = data["results"][0]["violations"]
            self.assertTrue(
                any(item["code"] == "inference-in-answer" for item in violations)
            )

    def test_non_empty_inference_section_must_mark_inference_and_cite_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer = Path(tmp) / "answer.md"
            answer.write_text(
                GOOD_ANSWER.replace(
                    "无\n\n## 引用出处",
                    "- ⚠️ [推断] 这可能影响发版排序。\n\n## 引用出处",
                )
                .replace("- 现有 docs: `docs/release.md`", "- 现有 docs: `docs/release.md`\n- 推断: 基于 Context 和源码关系判断。"),
                encoding="utf-8",
            )

            proc = lint_file(answer)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertIn("inference", data["results"][0]["usedSources"])

    def test_used_source_type_requires_citation(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer = Path(tmp) / "answer.md"
            answer.write_text(
                GOOD_ANSWER.replace("- 源码: `src/release.py:1`\n", ""),
                encoding="utf-8",
            )

            proc = lint_file(answer)
            self.assertEqual(proc.returncode, 1)
            data = json.loads(proc.stdout)
            violations = data["results"][0]["violations"]
            self.assertTrue(any(item["code"] == "missing-citation" for item in violations))

    def test_cli_dispatches_query_lint(self):
        proc = subprocess.run(
            CLI + ["context", "query-lint", "--json", "-"],
            cwd=PROJECT_ROOT,
            input=GOOD_ANSWER,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
