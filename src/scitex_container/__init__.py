#!/usr/bin/env python3
# Timestamp: "2026-07-02"
# File: src/scitex_container/__init__.py
"""scitex-container: Unified container management for Apptainer and Docker.

The top-level namespace is lazy (PEP 562 ``__getattr__``): importing
``scitex_container`` costs only ``importlib.metadata.version`` — the heavy
submodules (``apptainer`` pulls ``scitex_config`` et al.) load on first
attribute access, not at import time. This keeps ``scitex-container``
CLI startup and shell tab-completion fast (see the python-api skill leaf
``04_lazy-imports-and-optional-deps.md`` §"PEP 562 module __getattr__").
"""

from __future__ import annotations

# NOTHING heavy at import time — not even `importlib.metadata` (its first
# use cold-imports email/zipfile/inspect and dominated startup). `__version__`
# is computed lazily on first access via __getattr__, same as every submodule.


def _compute_version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            return version("scitex-container")
        except PackageNotFoundError:
            return "0.0.0+local"
    except ImportError:  # pragma: no cover — only on ancient Pythons
        return "0.0.0+local"


# Submodules exposed as `scitex_container.<name>`, imported on first access.
_LAZY_SUBMODULES = ("apptainer", "docker", "host")

# Public callable → (submodule, attribute-in-submodule). These mirror the
# MCP tool surface so each `container_*` / `sandbox_*` / `docker_*` /
# `host_*` tool maps to a top-level Python callable. One row per symbol
# that would previously have been `from .X import Y`.
# See _cli/audit/_summary/_mcp_audit.py §6.
_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "env_snapshot": ("_snapshot", "env_snapshot"),
    # apptainer
    "build": ("apptainer", "build"),
    "build_reproducible": ("apptainer", "build_reproducible"),
    "check_verified": ("apptainer", "check_verified"),
    "cleanup": ("apptainer", "cleanup"),
    "deploy": ("apptainer", "deploy"),
    "list_builds": ("apptainer", "list_builds"),
    "list_versions": ("apptainer", "list_versions"),
    "rollback": ("apptainer", "rollback"),
    "sandbox_create": ("apptainer", "sandbox_create"),
    "status": ("apptainer", "status"),
    "switch": ("apptainer", "switch_version"),
    "verify": ("apptainer", "verify"),
    "verify_roundtrip": ("apptainer", "verify_roundtrip"),
    # docker
    "docker_rebuild": ("docker", "rebuild"),
    "docker_restart": ("docker", "restart"),
    # host
    "host_check": ("host", "check_packages"),
    "host_install": ("host", "install_packages"),
}


def __getattr__(name: str):
    """PEP 562 lazy-loader: import the backing submodule on first access."""
    if name == "__version__":
        version = _compute_version()
        globals()["__version__"] = version  # cache
        return version

    from importlib import import_module

    if name in _LAZY_SUBMODULES:
        mod = import_module(f".{name}", __name__)
        globals()[name] = mod  # cache; subsequent access skips this hook
        return mod

    entry = _LAZY_ATTRS.get(name)
    if entry is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    submodule, attr = entry
    value = getattr(import_module(f".{submodule}", __name__), attr)
    globals()[name] = value  # cache
    return value


def __dir__() -> list[str]:
    return sorted(set(_LAZY_SUBMODULES) | set(_LAZY_ATTRS) | set(globals()))


__all__ = [
    "__version__",
    "apptainer",
    "docker",
    "host",
    "env_snapshot",
    # MCP-parity re-exports
    "build",
    "cleanup",
    "deploy",
    "list_versions",
    "rollback",
    "sandbox_create",
    "status",
    "switch",
    "verify",
    "docker_rebuild",
    "docker_restart",
    "host_check",
    "host_install",
    # reproducible round-trip
    "build_reproducible",
    "verify_roundtrip",
    "check_verified",
    "list_builds",
]
