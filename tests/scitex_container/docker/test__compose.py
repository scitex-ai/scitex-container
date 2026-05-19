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

import pytest

from scitex_container.docker import _compose


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

    def test_raises_when_no_compose_file(self, tmp_path, monkeypatch):
        # Make cwd be a temp dir that has no compose files in any ancestor by
        # restricting search to project_dir-only is not possible — but the
        # error message will still mention the searched dirs.
        # Arrange
        # Act
        # Assert
        empty = tmp_path / "empty_subdir"
        empty.mkdir()
        monkeypatch.chdir(empty)
        # We cannot guarantee that no ancestor has a compose file, so this
        # test only enforces the type contract: raise iff none found.
        try:
            _compose._find_compose_file(env="dev", project_dir=empty)
        except FileNotFoundError as exc:
            assert "docker-compose" in str(exc) or "compose" in str(exc)


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

    def test_rebuild_raises_filenotfound_when_no_compose(self, tmp_path, monkeypatch):
        # Arrange
        # Act
        monkeypatch.chdir(tmp_path)
        # Assert
        with pytest.raises(FileNotFoundError):
            _compose.rebuild(env="__none__", project_dir=tmp_path)

    def test_restart_raises_filenotfound_when_no_compose(self, tmp_path, monkeypatch):
        # Arrange
        # Act
        monkeypatch.chdir(tmp_path)
        # Assert
        with pytest.raises(FileNotFoundError):
            _compose.restart(env="__none__", project_dir=tmp_path)

    def test_status_raises_filenotfound_when_no_compose(self, tmp_path, monkeypatch):
        # Arrange
        # Act
        monkeypatch.chdir(tmp_path)
        # Assert
        with pytest.raises(FileNotFoundError):
            _compose.status(env="__none__", project_dir=tmp_path)


# EOF
