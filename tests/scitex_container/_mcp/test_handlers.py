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
def test_handler_exists_hasattr_handlers_name(name):
    # Arrange
    # Act
    # Assert
    assert hasattr(handlers, name), f"handlers module missing {name!r}"


@pytest.mark.parametrize("name", _HANDLER_NAMES)
def test_handler_is_coroutine_function(name):
    # Arrange
    # Act
    fn = getattr(handlers, name)
    # Assert
    assert inspect.iscoroutinefunction(fn), (
        f"{name} must be `async def` (MCP requires coroutine handlers)"
    )


# ---------------------------------------------------------------------------
# Envelope shape — call each handler with safe args and assert dict-with-success
# ---------------------------------------------------------------------------


def _run(coro):
    """Helper: run a coroutine to completion."""
    return asyncio.run(coro)


def test_list_handler_returns_envelope_result_is_dict():
    # Arrange
    # Act
    result = _run(handlers.list_handler())
    # Act
    # Assert
    assert isinstance(result, dict)


def test_list_handler_returns_envelope_success_in_result():
    # Arrange
    # Act
    result = _run(handlers.list_handler())
    # Act
    # Assert
    assert "success" in result




def test_list_handler_handles_missing_dir_result_is_dict():
    # Arrange
    # Act
    result = _run(handlers.list_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert isinstance(result, dict)


def test_list_handler_handles_missing_dir_result_get_success_is_true():
    # Arrange
    # Act
    result = _run(handlers.list_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert result.get("success") is True


def test_list_handler_handles_missing_dir_result_get_versions():
    # Arrange
    # Act
    result = _run(handlers.list_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert result.get("versions") == []




def test_status_handler_returns_envelope_result_is_dict():
    # Arrange
    # Act
    result = _run(handlers.status_handler())
    # Act
    # Assert
    assert isinstance(result, dict)


def test_status_handler_returns_envelope_result():
    # Arrange
    # Act
    result = _run(handlers.status_handler())
    # Act
    # Assert
    assert result  # non-empty




def test_host_check_handler_returns_envelope():
    # Arrange
    # Act
    result = _run(handlers.host_check_handler())
    # Assert
    assert isinstance(result, dict)


def test_env_snapshot_handler_returns_envelope():
    """env_snapshot is designed never to raise."""
    # Arrange
    # Act
    result = _run(handlers.env_snapshot_handler())
    # Assert
    assert isinstance(result, dict)


def test_rollback_handler_handles_missing_dir_result_is_dict():
    # Arrange
    # Act
    result = _run(handlers.rollback_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert isinstance(result, dict)


def test_rollback_handler_handles_missing_dir_result_get_success_is_false():
    # Arrange
    # Act
    result = _run(handlers.rollback_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert result.get("success") is False




def test_switch_handler_handles_missing_dir_result_is_dict():
    # Arrange
    # Act
    result = _run(
        handlers.switch_handler(
            version="9.9.9", containers_dir="/__nonexistent__/__here__"
        )
    )
    # Act
    # Assert
    assert isinstance(result, dict)


def test_switch_handler_handles_missing_dir_result_get_success_is_false():
    # Arrange
    # Act
    result = _run(
        handlers.switch_handler(
            version="9.9.9", containers_dir="/__nonexistent__/__here__"
        )
    )
    # Act
    # Assert
    assert result.get("success") is False




def test_cleanup_handler_handles_missing_dir_result_is_dict():
    # Arrange
    # Act
    result = _run(handlers.cleanup_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert isinstance(result, dict)


def test_cleanup_handler_handles_missing_dir_result_get_success_is_true():
    # Arrange
    # Act
    result = _run(handlers.cleanup_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert result.get("success") is True


def test_cleanup_handler_handles_missing_dir_result_get_removed():
    # Arrange
    # Act
    result = _run(handlers.cleanup_handler(containers_dir="/__nonexistent__/__here__"))
    # Act
    # Assert
    assert result.get("removed") == []




def test_build_handler_handles_missing_def_result_is_dict():
    # Arrange
    # Act
    result = _run(handlers.build_handler(name="__nonexistent_def_name__"))
    # Act
    # Assert
    assert isinstance(result, dict)


def test_build_handler_handles_missing_def_result_get_success_is_false():
    # Arrange
    # Act
    result = _run(handlers.build_handler(name="__nonexistent_def_name__"))
    # Act
    # Assert
    assert result.get("success") is False




def test_sandbox_create_handler_handles_missing_sif_result_is_dict():
    # Arrange
    # Act
    result = _run(handlers.sandbox_create_handler(source_sif="/__nonexistent__.sif"))
    # Act
    # Assert
    assert isinstance(result, dict)


def test_sandbox_create_handler_handles_missing_sif_success_in_result_or_error_in_result():
    # Arrange
    # Act
    result = _run(handlers.sandbox_create_handler(source_sif="/__nonexistent__.sif"))
    # Act
    # Assert
    assert "success" in result or "error" in result




# EOF
