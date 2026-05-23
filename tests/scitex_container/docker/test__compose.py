#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/docker/test__compose.py
"""Tests for scitex_container.docker._compose (rebuild / restart / status).

The internal helper `_find_compose_file` is exercised in isolation since it
is pure-Python (no docker required).  The public rebuild/restart/status
entry points only need a smoke test (they shell out to `docker compose`,
which may not be installed).
"""

from __future__ import annotations

import os

import pytest

from scitex_container.docker import _compose


@pytest.fixture
def chdir_isolated(tmp_path):
    """chdir into an isolated tmp dir whose ancestors hold no compose file.

    Real cwd manipulation (not a mock): restores the original cwd on
    teardown. Used by the "raise when not found" contract tests so the
    upward cwd-walk in _find_compose_file can't accidentally pick up a
    compose file from a real ancestor of the test runner's cwd.
    """
    workdir = tmp_path / "isolated"
    workdir.mkdir()
    saved = os.getcwd()
    os.chdir(workdir)
    try:
        yield workdir
    finally:
        os.chdir(saved)


# ---------------------------------------------------------------------------
# _find_compose_file
# ---------------------------------------------------------------------------


class TestFindComposeFile:
    """Tests for the private compose-file locator."""

    def test_finds_env_specific_compose(self, tmp_path):
        # Arrange
        target = tmp_path / "docker-compose.dev.yml"
        target.write_text("services: {}\n")
        # Act
        result = _compose._find_compose_file(env="dev", project_dir=tmp_path)
        # Assert
        assert result == target.resolve()

    def test_finds_generic_compose_when_no_env_specific(self, tmp_path):
        # Arrange
        target = tmp_path / "docker-compose.yml"
        target.write_text("services: {}\n")
        # Act
        result = _compose._find_compose_file(env="dev", project_dir=tmp_path)
        # Assert
        assert result == target.resolve()

    def test_finds_compose_yml_fallback(self, tmp_path):
        # Arrange
        target = tmp_path / "compose.yml"
        target.write_text("services: {}\n")
        # Act
        result = _compose._find_compose_file(env="dev", project_dir=tmp_path)
        # Assert
        assert result == target.resolve()

    def test_env_specific_preferred_over_generic(self, tmp_path):
        # Arrange
        env_file = tmp_path / "docker-compose.prod.yml"
        env_file.write_text("services: {}\n")
        generic = tmp_path / "docker-compose.yml"
        generic.write_text("services: {}\n")
        # Act
        result = _compose._find_compose_file(env="prod", project_dir=tmp_path)
        # Assert
        assert result == env_file.resolve()

    def test_raises_filenotfound_when_no_compose_file(self, chdir_isolated):
        # Arrange
        ctx = pytest.raises(FileNotFoundError, match="compose")
        # Act
        # Assert
        with ctx:
            _compose._find_compose_file(env="__none__", project_dir=chdir_isolated)


# ---------------------------------------------------------------------------
# Public API smoke
# ---------------------------------------------------------------------------


class TestPublicApiSmoke:
    """Public API exists and is callable.  Real exec is integration-only."""

    def test_rebuild_callable_callable_compose_rebuild(self):
        # Arrange
        # Act
        # Assert
        assert callable(_compose.rebuild)

    def test_restart_callable_callable_compose_restart(self):
        # Arrange
        # Act
        # Assert
        assert callable(_compose.restart)

    def test_status_callable_callable_compose_status(self):
        # Arrange
        # Act
        # Assert
        assert callable(_compose.status)

    def test_rebuild_raises_filenotfound_when_no_compose(self, chdir_isolated):
        # Arrange
        ctx = pytest.raises(FileNotFoundError)
        # Act
        # Assert
        with ctx:
            _compose.rebuild(env="__none__", project_dir=chdir_isolated)

    def test_restart_raises_filenotfound_when_no_compose(self, chdir_isolated):
        # Arrange
        ctx = pytest.raises(FileNotFoundError)
        # Act
        # Assert
        with ctx:
            _compose.restart(env="__none__", project_dir=chdir_isolated)

    def test_status_raises_filenotfound_when_no_compose(self, chdir_isolated):
        # Arrange
        ctx = pytest.raises(FileNotFoundError)
        # Act
        # Assert
        with ctx:
            _compose.status(env="__none__", project_dir=chdir_isolated)


# EOF
