#!/usr/bin/env python3
"""Compatibility wrapper for :mod:`kb_tricks.commands.migrate_plan`."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from kb_tricks.commands.migrate_plan import *  # noqa: F401,F403,E402
from kb_tricks.commands.migrate_plan import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
