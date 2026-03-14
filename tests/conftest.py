#!/usr/bin/env python3
# Timestamp: "2026-03-14"
# File: tests/conftest.py
"""Pytest configuration and shared fixtures.

Adds the scitex-container src/ and scitex-dev src/ directories to sys.path
so tests can run without a prior ``pip install`` of either package.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure packages are importable from source trees
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCITEX_CONTAINER_SRC = _REPO_ROOT / "src"

# scitex-dev lives as a sibling repo in ~/proj/scitex-dev
_SCITEX_DEV_SRC = _REPO_ROOT.parent / "scitex-dev" / "src"

for _p in (_SCITEX_CONTAINER_SRC, _SCITEX_DEV_SRC):
    _s = str(_p)
    if _p.is_dir() and _s not in sys.path:
        sys.path.insert(0, _s)

# EOF
