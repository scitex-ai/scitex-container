#!/usr/bin/env python3
# Timestamp: "2026-02-25"
# File: src/scitex_container/__init__.py
"""scitex-container: Unified container management for Apptainer and Docker."""

from __future__ import annotations

from . import apptainer, docker, host
from ._snapshot import env_snapshot

try:
    from importlib.metadata import version as _v, PackageNotFoundError
    try:
        __version__ = _v("scitex-container")
    except PackageNotFoundError:
        __version__ = "0.0.0+local"
    del _v, PackageNotFoundError
except ImportError:  # pragma: no cover — only on ancient Pythons
    __version__ = "0.0.0+local"
__all__ = ["__version__", "apptainer", "docker", "host", "env_snapshot"]
