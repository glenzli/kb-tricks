#!/usr/bin/env python3
"""Run a full release rehearsal from source export to installed CLI checks."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import warnings
import zipfile
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIN_SETUPTOOLS = (77,)

SDIST_REQUIRED = [
    "LICENSE",
    "skills/context-build/SKILL.md",
    "tools/context_audit.py",
    "tools/context_build_assist.py",
    "tools/context_migrate_plan.py",
    "tools/release_smoke.py",
    "tools/release_rehearsal.py",
    "spec/CONTEXT_SPEC.md",
    "templates/AGENT_GUIDE.md",
    "templates/context-query-answer.md",
    "dev_cycle/context/audit.py",
    "dev_cycle/context/build_assist.py",
    "dev_cycle/context/migrate_plan.py",
    "dev_cycle/templates/AGENT_GUIDE.md",
    "dev_cycle/templates/config.yaml",
]
WHEEL_REQUIRED = [
    "dev_cycle/context/audit.py",
    "dev_cycle/context/build_assist.py",
    "dev_cycle/context/migrate_plan.py",
    "dev_cycle/context/update_plan.py",
    "dev_cycle/templates/AGENT_GUIDE.md",
    "dev_cycle/templates/config.yaml",
    "dev_cycle/cli.py",
]
WHEEL_FORBIDDEN = [
    "tools/context_audit.py",
    "tools/context_build_assist.py",
    "tools/context_migrate_plan.py",
    "tools/release_smoke.py",
    "tools/release_rehearsal.py",
    "skills/context-build/SKILL.md",
    "spec/CONTEXT_SPEC.md",
    "templates/context-query-answer.md",
]

INSTALLED_PROBE = """
import importlib.util
import json
import dev_cycle.context.audit as audit
print(json.dumps({
    "audit_module": audit.__name__,
    "tools_importable": importlib.util.find_spec("tools") is not None,
}, sort_keys=True))
"""


class RehearsalError(RuntimeError):
    """Release rehearsal failed."""


@dataclass
class ArtifactCheck:
    missing_sdist: list[str]
    missing_wheel: list[str]
    forbidden_wheel: list[str]
    license_entries: list[str]
    metadata_license_lines: list[str]

    @property
    def ok(self) -> bool:
        return (
            not self.missing_sdist
            and not self.missing_wheel
            and not self.forbidden_wheel
            and any(entry.endswith("/LICENSE") for entry in self.license_entries)
            and "License-Expression: MIT" in self.metadata_license_lines
        )


@dataclass
class RehearsalSummary:
    source: str
    tempRoot: str
    sdist: str
    wheel: str
    commands: int
    warnings: int
    artifactCheck: ArtifactCheck


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", value)[:3])


def ensure_build_backend() -> object:
    try:
        setuptools_version = metadata.version("setuptools")
        import setuptools.build_meta as build_meta
    except (metadata.PackageNotFoundError, ModuleNotFoundError) as exc:
        raise RehearsalError(
            "release rehearsal requires setuptools>=77 in the running Python; "
            "create a venv and install build dependencies first"
        ) from exc
    if version_tuple(setuptools_version) < MIN_SETUPTOOLS:
        raise RehearsalError(
            f"release rehearsal requires setuptools>=77; found {setuptools_version}"
        )
    return build_meta


def run_command(
    cmd: list[str],
    cwd: Path,
    *,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(cmd), flush=True)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        check=False,
        capture_output=capture,
    )
    if proc.returncode != 0:
        if capture:
            if proc.stdout:
                print(proc.stdout)
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)
        raise RehearsalError(f"command failed with exit {proc.returncode}: {' '.join(cmd)}")
    return proc


def export_head(repo: Path, target: Path) -> None:
    archive = target.parent / "source.tar"
    run_command(
        ["git", "archive", "--format=tar", "--output", str(archive), "HEAD"],
        repo,
        capture=True,
    )
    with tarfile.open(archive) as tar:
        tar.extractall(target)


def copy_worktree(repo: Path, target: Path) -> None:
    proc = run_command(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        repo,
        capture=True,
    )
    for rel in proc.stdout.splitlines():
        source = repo / rel
        if not source.exists() or source.is_dir():
            continue
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def export_source(repo: Path, target: Path, source: str) -> None:
    target.mkdir(parents=True, exist_ok=True)
    if source == "head":
        export_head(repo, target)
    elif source == "worktree":
        copy_worktree(repo, target)
    else:  # pragma: no cover - argparse constrains this.
        raise ValueError(f"unknown source mode: {source}")


def build_artifacts(source_dir: Path, dist_dir: Path, *, verbose: bool) -> tuple[Path, Path, int]:
    build_meta = ensure_build_backend()
    dist_dir.mkdir(parents=True, exist_ok=True)
    current = Path.cwd()
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        os.chdir(source_dir)
        with warnings.catch_warnings(record=True) as records:
            warnings.simplefilter("always")
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                sdist = dist_dir / build_meta.build_sdist(str(dist_dir))
                wheel = dist_dir / build_meta.build_wheel(str(dist_dir))
    except Exception:
        captured = stdout.getvalue() + stderr.getvalue()
        if captured:
            print(captured)
        raise
    finally:
        os.chdir(current)
    build_text = stdout.getvalue() + stderr.getvalue() + "\n".join(
        str(record.message) for record in records
    )
    if verbose and build_text:
        print(build_text)
    if "project.license" in build_text or "SetuptoolsDeprecationWarning" in build_text:
        raise RehearsalError("build emitted deprecated setuptools license metadata warnings")
    return sdist, wheel, len(records)


def sdist_has(names: set[str], relpath: str) -> bool:
    return any(name == relpath or name.endswith("/" + relpath) for name in names)


def inspect_artifacts(sdist: Path, wheel: Path) -> ArtifactCheck:
    with tarfile.open(sdist) as tar:
        sdist_names = set(tar.getnames())
    with zipfile.ZipFile(wheel) as zip_file:
        wheel_names = set(zip_file.namelist())
        metadata_names = sorted(
            name for name in wheel_names if name.endswith(".dist-info/METADATA")
        )
        metadata_text = zip_file.read(metadata_names[0]).decode("utf-8") if metadata_names else ""

    license_entries = sorted(name for name in wheel_names if ".dist-info/licenses/" in name)
    metadata_license_lines = [
        line for line in metadata_text.splitlines() if line.startswith("License")
    ]
    return ArtifactCheck(
        missing_sdist=[item for item in SDIST_REQUIRED if not sdist_has(sdist_names, item)],
        missing_wheel=[item for item in WHEEL_REQUIRED if item not in wheel_names],
        forbidden_wheel=[item for item in WHEEL_FORBIDDEN if item in wheel_names],
        license_entries=license_entries,
        metadata_license_lines=metadata_license_lines,
    )


def run_installed_checks(repo: Path, source_dir: Path, wheel: Path, root: Path) -> int:
    install_venv = root / "install-venv"
    run_command([sys.executable, "-m", "venv", str(install_venv)], root)
    venv_python = install_venv / "bin" / "python"
    dev_cycle = install_venv / "bin" / "dev-cycle"
    run_command(
        [str(venv_python), "-m", "pip", "install", "--no-index", "--no-cache-dir", str(wheel)],
        root,
    )

    smoke_repo = root / "smoke-repo"
    smoke_repo.mkdir()
    commands = [
        [str(dev_cycle), "self-check", "--json"],
        [str(dev_cycle), "context", "scaffold", "--repo", str(smoke_repo), "--dry-run"],
        [
            str(dev_cycle),
            "context",
            "query-lint",
            "--json",
            str(source_dir / "templates" / "context-query-answer.md"),
        ],
        [str(venv_python), "-c", INSTALLED_PROBE],
        [
            sys.executable,
            str(source_dir / "tools" / "release_smoke.py"),
            "--installed",
            "--dev-cycle",
            str(dev_cycle),
            "--skip-tests",
            "--skip-git-check",
        ],
    ]
    for cmd in commands:
        cwd = repo if cmd[0] == sys.executable else root
        run_command(cmd, cwd)
    return len(commands)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(PROJECT_ROOT), help="Repository to rehearse.")
    parser.add_argument(
        "--source",
        choices=("head", "worktree"),
        default="head",
        help="Source export mode. `head` rehearses committed release state.",
    )
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary rehearsal files.")
    parser.add_argument("--verbose-build", action="store_true", help="Print captured build output.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary.")
    return parser.parse_args(argv)


def run_rehearsal(args: argparse.Namespace) -> RehearsalSummary:
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        raise RehearsalError(f"repo does not exist: {repo}")

    root = Path(tempfile.mkdtemp(prefix="dev-cycle-release-", dir="/private/tmp"))
    source_dir = root / "source"
    dist_dir = root / "dist"
    success = False
    try:
        print(f"REHEARSAL_ROOT {root}", flush=True)
        export_source(repo, source_dir, args.source)
        sdist, wheel, warning_count = build_artifacts(
            source_dir,
            dist_dir,
            verbose=args.verbose_build,
        )
        artifact_check = inspect_artifacts(sdist, wheel)
        print(
            "CONTENT_CHECK "
            + json.dumps(
                {
                    "missing_sdist": artifact_check.missing_sdist,
                    "missing_wheel": artifact_check.missing_wheel,
                    "forbidden_wheel": artifact_check.forbidden_wheel,
                    "license_entries": artifact_check.license_entries,
                    "metadata_license_lines": artifact_check.metadata_license_lines,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        if not artifact_check.ok:
            raise RehearsalError("artifact boundary check failed")
        command_count = run_installed_checks(repo, source_dir, wheel, root)
        summary = RehearsalSummary(
            source=args.source,
            tempRoot=str(root),
            sdist=sdist.name,
            wheel=wheel.name,
            commands=command_count,
            warnings=warning_count,
            artifactCheck=artifact_check,
        )
        success = True
        return summary
    finally:
        if success and not args.keep_temp:
            shutil.rmtree(root)
        elif not success:
            print(f"temporary rehearsal files kept at {root}", file=sys.stderr, flush=True)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        summary = run_rehearsal(args)
    except RehearsalError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    payload = {
        "source": summary.source,
        "tempRoot": summary.tempRoot if args.keep_temp else None,
        "sdist": summary.sdist,
        "wheel": summary.wheel,
        "commands": summary.commands,
        "warnings": summary.warnings,
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True), flush=True)
    else:
        print("REHEARSAL_OK " + json.dumps(payload, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
