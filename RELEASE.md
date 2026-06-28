# Release Notes

## Release Boundary

`kb-tricks` ships deterministic tooling through the `kb` CLI. Skills remain repository-local instructions: a target repository may call an installed `kb`, copy the released `tools/` bundle, or reference this repository through an external mechanism such as `vasmc`.

The target repository owns KB artifacts such as `.agent/kb/config.yaml`, `KB_PLAN.md`, `.agent/kb/**/*.md`, `_validation/`, and `index.json`. The installed package owns only the reusable CLI, deterministic tools, and starter templates.

## Install Smoke

From a clean checkout:

```bash
python3 -m pip install .
kb self-check --json
kb scaffold --repo /tmp/kb-smoke --dry-run
kb query-lint templates/query-answer.md
```

If the environment has `pip` but no importable `setuptools`, use a virtual environment and install build dependencies there. In network-restricted environments, avoid build isolation after the venv has `setuptools`:

```bash
python3 -m venv /tmp/kb-tricks-smoke-venv
/tmp/kb-tricks-smoke-venv/bin/python -m pip install "setuptools>=68"
/tmp/kb-tricks-smoke-venv/bin/python -m pip install --no-build-isolation .
/tmp/kb-tricks-smoke-venv/bin/kb self-check --json
```

When running from a source checkout without installing:

```bash
python3 -B -m kb_tricks.cli self-check --json
python3 tools/kb_scaffold.py --repo /tmp/kb-smoke --dry-run
python3 tools/kb_query_lint.py templates/query-answer.md
```

## Release Verification

Before publishing, run:

```bash
python3 -B tools/release_smoke.py
```

After installing into a virtual environment, run the installed CLI smoke:

```bash
python3 -B tools/release_smoke.py --installed --skip-tests --skip-git-check
# or, when the installed CLI is not on PATH:
python3 -B tools/release_smoke.py --installed --kb .venv/bin/kb --skip-tests --skip-git-check
```

The install smoke should be run in an environment with standard Python packaging support. The repository tests avoid network access and do not require building an isolated wheel.

## Packaging Notes

- `pyproject.toml` exposes `kb = "kb_tricks.cli:main"`.
- `tools` is packaged so installed CLI commands can import deterministic tool modules.
- `kb_tricks/templates/*` is packaged so `kb scaffold` works after installation.
- Root-level `templates/`, `spec/`, and `skills/` directories are included in source distributions for copy/reference workflows.
