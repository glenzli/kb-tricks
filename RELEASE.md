# Release Notes

## Release Boundary

`dev-cycle` ships deterministic context tooling through the `dev-cycle` CLI.
Skills remain repository-local instructions: a target repository may call an
installed `dev-cycle`, run source-checkout wrappers in `tools/`, or reference
this repository through an external mechanism such as `vasmc`.

The target repository owns Context artifacts such as `.dev-cycle/context/config.yaml`, `CONTEXT_PLAN.md`, `.dev-cycle/context/**/*.md`, `_validation/`, and `index.json`. The installed package owns only the reusable CLI, deterministic tools, and starter templates.

## Install Smoke

From a clean checkout:

```bash
python3 -m pip install .
dev-cycle self-check --json
mkdir -p /tmp/dev-cycle-smoke
dev-cycle context scaffold --repo /tmp/dev-cycle-smoke --dry-run
dev-cycle context query-lint templates/context-query-answer.md
```

`dev-cycle context scaffold` expects `--repo` to point at an existing repository directory; the
smoke path is created explicitly so the example matches that contract.

If the environment has `pip` but no importable `setuptools`, use a virtual environment and install build dependencies there. In network-restricted environments, avoid build isolation after the venv has `setuptools`:

```bash
python3 -m venv /tmp/dev-cycle-smoke-venv
/tmp/dev-cycle-smoke-venv/bin/python -m pip install "setuptools>=77"
/tmp/dev-cycle-smoke-venv/bin/python -m pip install --no-build-isolation .
/tmp/dev-cycle-smoke-venv/bin/dev-cycle self-check --json
```

When running from a source checkout without installing:

```bash
python3 -B -m dev_cycle.cli self-check --json
mkdir -p /tmp/dev-cycle-smoke
python3 tools/context_scaffold.py --repo /tmp/dev-cycle-smoke --dry-run
python3 tools/context_query_lint.py templates/context-query-answer.md
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
python3 -B tools/release_smoke.py --installed --dev-cycle .venv/bin/dev-cycle --skip-tests --skip-git-check
```

The install smoke should be run in an environment with standard Python packaging support. The repository tests avoid network access and do not require building an isolated wheel.

## Packaging Notes

- `pyproject.toml` publishes the distribution as `dev-cycle`.
- `pyproject.toml` exposes `dev-cycle = "dev_cycle.cli:main"`.
- `dev_cycle.context` contains the released command implementations used by installed CLI commands.
- `tools/context_*.py` wrappers are included in source distributions for checkout and reference workflows.
- `dev_cycle/templates/*` is packaged so `dev-cycle context scaffold` works after installation.
- Root-level `templates/`, `spec/`, and `skills/` directories are included in source distributions for copy/reference workflows.
