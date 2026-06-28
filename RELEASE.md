# Release Notes

## Release Boundary

`dev-cycle` ships deterministic context tooling through the `kb` CLI. Skills remain repository-local instructions: a target repository may call an installed `kb`, run source-checkout wrappers in `tools/`, or reference this repository through an external mechanism such as `vasmc`.

The target repository owns KB artifacts such as `.agent/kb/config.yaml`, `KB_PLAN.md`, `.agent/kb/**/*.md`, `_validation/`, and `index.json`. The installed package owns only the reusable CLI, deterministic tools, and starter templates.

## Install Smoke

From a clean checkout:

```bash
python3 -m pip install .
kb self-check --json
mkdir -p /tmp/kb-smoke
kb scaffold --repo /tmp/kb-smoke --dry-run
kb query-lint templates/query-answer.md
```

`kb scaffold` expects `--repo` to point at an existing repository directory; the
smoke path is created explicitly so the example matches that contract.

If the environment has `pip` but no importable `setuptools`, use a virtual environment and install build dependencies there. In network-restricted environments, avoid build isolation after the venv has `setuptools`:

```bash
python3 -m venv /tmp/dev-cycle-smoke-venv
/tmp/dev-cycle-smoke-venv/bin/python -m pip install "setuptools>=77"
/tmp/dev-cycle-smoke-venv/bin/python -m pip install --no-build-isolation .
/tmp/dev-cycle-smoke-venv/bin/kb self-check --json
```

When running from a source checkout without installing:

```bash
python3 -B -m kb_tricks.cli self-check --json
mkdir -p /tmp/kb-smoke
python3 tools/kb_scaffold.py --repo /tmp/kb-smoke --dry-run
python3 tools/kb_query_lint.py templates/query-answer.md
```

## Release Verification

Before publishing, run:

```bash
python3 -B tools/release_smoke.py
python3 -B tools/release_rehearsal.py
```

`release_smoke.py` is the fast source/installed CLI check. `release_rehearsal.py`
exports committed `HEAD` to a temporary source tree, builds sdist and wheel,
checks the release artifact boundary, installs the wheel into a temporary
virtual environment, and then runs installed CLI smoke checks. Use
`--source worktree` only when validating uncommitted release-script changes.

After installing into a virtual environment, run the installed CLI smoke:

```bash
python3 -B tools/release_smoke.py --installed --skip-tests --skip-git-check
# or, when the installed CLI is not on PATH:
python3 -B tools/release_smoke.py --installed --kb .venv/bin/kb --skip-tests --skip-git-check
```

The install smoke should be run in an environment with standard Python packaging support. The repository tests avoid network access and do not require building an isolated wheel.

## Packaging Notes

- `pyproject.toml` publishes the distribution as `dev-cycle`.
- `pyproject.toml` exposes `kb = "kb_tricks.cli:main"`.
- `kb_tricks.commands` contains the released command implementations used by installed CLI commands; the import package name is retained for compatibility during the rename.
- `tools/kb_*.py` wrappers are included in source distributions for checkout and reference workflows.
- `kb_tricks/templates/*` is packaged so `kb scaffold` works after installation.
- Root-level `templates/`, `spec/`, and `skills/` directories are included in source distributions for copy/reference workflows.
