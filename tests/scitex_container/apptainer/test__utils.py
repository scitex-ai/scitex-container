#!/usr/bin/env python3
# Timestamp: "2026-05-23"
# File: tests/scitex_container/apptainer/test__utils.py
"""Tests for scitex_container.apptainer._utils.

detect_container_cmd() and find_containers_dir() are exercised against
real collaborators only — no mocks. PATH is steered with real executable
shims in a tmp bin dir; the user-fallback search dir is steered with the
SCITEX_DIR environment variable (honoured by local_state.runtime_path).
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest


def _utils():
    """Import shortcut for the module under test."""
    from scitex_container.apptainer import _utils as u

    return u


def _make_exe(bin_dir: Path, name: str) -> Path:
    """Create a real executable shim named ``name`` in ``bin_dir``."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    exe = bin_dir / name
    exe.write_text("#!/usr/bin/env bash\nexit 0\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return exe


@pytest.fixture
def isolated_path(tmp_path):
    """Yield a tmp bin dir that is the *only* entry on PATH.

    Tests add real executable shims to it so detect_container_cmd()
    resolves them via shutil.which deterministically, regardless of what
    the host actually has installed.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    saved = os.environ.get("PATH", "")
    os.environ["PATH"] = str(bin_dir)
    try:
        yield bin_dir
    finally:
        os.environ["PATH"] = saved


@pytest.fixture
def scitex_dir(tmp_path):
    """Point SCITEX_DIR at a tmp dir so the user-fallback search is isolated."""
    user_root = tmp_path / "scitex-home"
    user_root.mkdir()
    saved = os.environ.get("SCITEX_DIR")
    os.environ["SCITEX_DIR"] = str(user_root)
    try:
        yield user_root
    finally:
        if saved is None:
            os.environ.pop("SCITEX_DIR", None)
        else:
            os.environ["SCITEX_DIR"] = saved


# ---------------------------------------------------------------------------
# detect_container_cmd
# ---------------------------------------------------------------------------


class TestDetectContainerCmd:
    """Tests for detect_container_cmd."""

    def test_returns_apptainer_when_only_apptainer_on_path(self, isolated_path):
        # Arrange
        _make_exe(isolated_path, "apptainer")
        # Act
        result = _utils().detect_container_cmd()
        # Assert
        assert result == "apptainer"

    def test_returns_singularity_when_only_singularity_on_path(self, isolated_path):
        # Arrange
        _make_exe(isolated_path, "singularity")
        # Act
        result = _utils().detect_container_cmd()
        # Assert
        assert result == "singularity"

    def test_prefers_apptainer_when_both_on_path(self, isolated_path):
        # Arrange
        _make_exe(isolated_path, "apptainer")
        _make_exe(isolated_path, "singularity")
        # Act
        result = _utils().detect_container_cmd()
        # Assert
        assert result == "apptainer"

    def test_raises_file_not_found_when_neither_on_path(self, isolated_path):
        # Arrange
        # (isolated_path is empty — no shims created)
        # Act
        ctx = pytest.raises(FileNotFoundError)
        # Assert
        with ctx:
            _utils().detect_container_cmd()

    def test_error_message_mentions_apptainer_when_neither_on_path(self, isolated_path):
        # Arrange
        ctx = pytest.raises(FileNotFoundError, match="apptainer")
        # Act
        # Assert
        with ctx:
            _utils().detect_container_cmd()

    def test_error_message_mentions_singularity_when_neither_on_path(
        self, isolated_path
    ):
        # Arrange
        ctx = pytest.raises(FileNotFoundError, match="singularity")
        # Act
        # Assert
        with ctx:
            _utils().detect_container_cmd()


# ---------------------------------------------------------------------------
# find_containers_dir
# ---------------------------------------------------------------------------


class TestFindContainersDir:
    """Tests for find_containers_dir."""

    def test_returns_cwd_containers_when_it_has_def_file(self, tmp_path, scitex_dir):
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "scitex.def").write_text(
            "Bootstrap: docker\nFrom: ubuntu:22.04\n"
        )
        os.chdir(tmp_path)
        # Act
        result = _utils().find_containers_dir()
        # Assert
        assert result == containers

    def test_returned_value_is_path_instance(self, tmp_path, scitex_dir):
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "base.def").write_text("Bootstrap: library\n")
        os.chdir(tmp_path)
        # Act
        result = _utils().find_containers_dir()
        # Assert
        assert isinstance(result, Path)

    def test_raises_when_no_containers_dir_found(self, tmp_path, scitex_dir):
        # Arrange
        os.chdir(tmp_path)
        ctx = pytest.raises(FileNotFoundError, match="containers")
        # Act
        # Assert
        with ctx:
            _utils().find_containers_dir()

    def test_cwd_containers_without_def_file_is_skipped(self, tmp_path, scitex_dir):
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "README.txt").write_text("hello")
        os.chdir(tmp_path)
        ctx = pytest.raises(FileNotFoundError)
        # Act
        # Assert
        with ctx:
            _utils().find_containers_dir()

    def test_user_fallback_dir_with_def_file_is_returned(self, tmp_path, scitex_dir):
        # Arrange
        from scitex_config._ecosystem import local_state

        user_containers = local_state.runtime_path("container", "containers")
        user_containers.mkdir(parents=True)
        (user_containers / "myenv.def").write_text("Bootstrap: docker\n")
        workdir = tmp_path / "workdir"
        workdir.mkdir()
        os.chdir(workdir)
        # Act
        result = _utils().find_containers_dir()
        # Assert
        assert result == user_containers

    def test_containers_dir_with_only_non_def_files_is_skipped(
        self, tmp_path, scitex_dir
    ):
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "config.yaml").write_text("key: value\n")
        os.chdir(tmp_path)
        ctx = pytest.raises(FileNotFoundError)
        # Act
        # Assert
        with ctx:
            _utils().find_containers_dir()

    def test_multiple_def_files_still_returns_cwd_containers(
        self, tmp_path, scitex_dir
    ):
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "scitex-base.def").write_text("Bootstrap: docker\n")
        (containers / "scitex-final.def").write_text("Bootstrap: localimage\n")
        os.chdir(tmp_path)
        # Act
        result = _utils().find_containers_dir()
        # Assert
        assert result == containers


# EOF
