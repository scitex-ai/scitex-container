#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_mcp/test_handlers.py
"""Tests for scitex_container._mcp.handlers (async MCP wrappers).

Each handler is exercised with asyncio.run().  Handlers are designed to
degrade gracefully — they catch FileNotFoundError / RuntimeError and return
a {"success": bool, ...} envelope without ever raising — so these tests
work without Apptainer, Docker, or SLURM installed on the test host.
"""

from __future__ import annotations

import asyncio
import inspect

import pytest

from scitex_container._mcp import handlers


# ---------------------------------------------------------------------------
# Smoke / API surface
# ---------------------------------------------------------------------------


_HANDLER_NAMES = [
    "build_handler",
    "list_handler",
    "switch_handler",
    "rollback_handler",
    "deploy_handler",
    "cleanup_handler",
    "sandbox_create_handler",
    "status_handler",
    "docker_rebuild_handler",
    "docker_restart_handler",
    "host_install_handler",
    "host_check_handler",
    "env_snapshot_handler",
]


@pytest.mark.parametrize("name", _HANDLER_NAMES)
def test_handler_exists(name):
    assert hasattr(handlers, name), f"handlers module missing {name!r}"


@pytest.mark.parametrize("name", _HANDLER_NAMES)
def test_handler_is_coroutine_function(name):
    fn = getattr(handlers, name)
    assert inspect.iscoroutinefunction(fn), (
        f"{name} must be `async def` (MCP requires coroutine handlers)"
    )


# ---------------------------------------------------------------------------
# Envelope shape — call each handler with safe args and assert dict-with-success
# ---------------------------------------------------------------------------


def _run(coro):
    """Helper: run a coroutine to completion."""
    return asyncio.run(coro)


def test_list_handler_returns_envelope():
    """list_handler with no args; should return {"success": bool, ...}."""
    result = _run(handlers.list_handler())
    assert isinstance(result, dict)
    assert "success" in result


def test_list_handler_handles_missing_dir():
    """Bogus containers_dir → returns envelope with success=True and empty
    versions list (graceful degrade — no SIFs to list is not an error)."""
    result = _run(handlers.list_handler(containers_dir="/__nonexistent__/__here__"))
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert result.get("versions") == []


def test_status_handler_returns_envelope():
    result = _run(handlers.status_handler())
    assert isinstance(result, dict)
    # status_handler aggregates many subsystems — at minimum return a dict
    assert result  # non-empty


def test_host_check_handler_returns_envelope():
    result = _run(handlers.host_check_handler())
    assert isinstance(result, dict)


def test_env_snapshot_handler_returns_envelope():
    """env_snapshot is designed never to raise."""
    result = _run(handlers.env_snapshot_handler())
    assert isinstance(result, dict)


def test_rollback_handler_handles_missing_dir():
    result = _run(handlers.rollback_handler(containers_dir="/__nonexistent__/__here__"))
    assert isinstance(result, dict)
    assert result.get("success") is False


def test_switch_handler_handles_missing_dir():
    result = _run(
        handlers.switch_handler(
            version="9.9.9", containers_dir="/__nonexistent__/__here__"
        )
    )
    assert isinstance(result, dict)
    assert result.get("success") is False


def test_cleanup_handler_handles_missing_dir():
    """Empty/missing dir → success=True with removed=[]; nothing to clean is
    not an error condition."""
    result = _run(handlers.cleanup_handler(containers_dir="/__nonexistent__/__here__"))
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert result.get("removed") == []


def test_build_handler_handles_missing_def():
    """No .def files → success=False with error key, never raises."""
    result = _run(handlers.build_handler(name="__nonexistent_def_name__"))
    assert isinstance(result, dict)
    assert result.get("success") is False


def test_sandbox_create_handler_handles_missing_sif():
    result = _run(handlers.sandbox_create_handler(source_sif="/__nonexistent__.sif"))
    assert isinstance(result, dict)
    # sandbox_create may degrade with success=False or raise — accept dict envelope
    assert "success" in result or "error" in result


# EOF
