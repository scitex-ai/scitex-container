#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/apptainer/test__utils.py
"""Unit tests for scitex_container.apptainer._utils.

Both detect_container_cmd() and find_containers_dir() are tested.
Tests are written so they pass whether or not apptainer/singularity is
installed on the test host, by patching shutil.which when needed.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def _utils():
    """Import shortcut for the module under test."""
    from scitex_container.apptainer import _utils as u

    return u


# ---------------------------------------------------------------------------
# detect_container_cmd
# ---------------------------------------------------------------------------


class TestDetectContainerCmd:
    """Tests for detect_container_cmd."""

    def test_returns_string_calls_utils(self):
        # Arrange
        # Act
        # Assert
        utils = _utils()
        try:
            result = utils.detect_container_cmd()
            assert isinstance(result, str)
        except FileNotFoundError:
            pass  # acceptable when neither tool is installed

    def test_returns_apptainer_when_apptainer_available(self):
        """When apptainer is on PATH, it should be preferred."""
        # Arrange
        utils = _utils()
        # Act
        with patch(
            "shutil.which", side_effect=lambda cmd: cmd if cmd == "apptainer" else None
        ):
            result = utils.detect_container_cmd()
        # Assert
        assert result == "apptainer"

    def test_returns_singularity_when_only_singularity_available(self):
        # Arrange
        utils = _utils()
        # Act
        with patch(
            "shutil.which",
            side_effect=lambda cmd: cmd if cmd == "singularity" else None,
        ):
            result = utils.detect_container_cmd()
        # Assert
        assert result == "singularity"

    def test_raises_file_not_found_when_neither_available(self):
        # Arrange
        # Act
        # Assert
        utils = _utils()
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError):
                utils.detect_container_cmd()

    def test_error_message_mentions_apptainer(self):
        # Arrange
        utils = _utils()
        with patch("shutil.which", return_value=None):
            try:
                utils.detect_container_cmd()
                msg = ""
            except FileNotFoundError as exc:
                msg = str(exc).lower()
        # Act
        contains_apptainer = "apptainer" in msg
        # Assert
        assert contains_apptainer

    def test_error_message_mentions_singularity(self):
        # Arrange
        utils = _utils()
        with patch("shutil.which", return_value=None):
            try:
                utils.detect_container_cmd()
                msg = ""
            except FileNotFoundError as exc:
                msg = str(exc).lower()
        # Act
        contains_singularity = "singularity" in msg
        # Assert
        assert contains_singularity

    def test_apptainer_preferred_over_singularity(self):
        """When both are present, apptainer should win (checked first)."""
        # Arrange
        utils = _utils()
        # Act
        with patch("shutil.which", return_value="found"):  # both return truthy
            result = utils.detect_container_cmd()
        # Assert
        assert result == "apptainer"

    def test_returned_value_is_apptainer_or_singularity(self):
        # Arrange
        utils = _utils()
        # Act
        with patch(
            "shutil.which",
            side_effect=lambda cmd: cmd
            if cmd in ("apptainer", "singularity")
            else None,
        ):
            result = utils.detect_container_cmd()
        # Assert
        assert result in ("apptainer", "singularity")


# ---------------------------------------------------------------------------
# find_containers_dir
# ---------------------------------------------------------------------------


class TestFindContainersDir:
    """Tests for find_containers_dir."""

    def test_returns_path_when_cwd_containers_has_def(self, tmp_path, monkeypatch):
        """If ./containers/ exists with a .def file, it should be returned."""
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "scitex.def").write_text(
            "Bootstrap: docker\nFrom: ubuntu:22.04\n"
        )

        monkeypatch.chdir(tmp_path)

        utils = _utils()
        # Act
        result = utils.find_containers_dir()
        # Assert
        assert result == containers

    def test_returned_path_is_path_object(self, tmp_path, monkeypatch):
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "base.def").write_text("Bootstrap: library\n")

        monkeypatch.chdir(tmp_path)

        utils = _utils()
        # Act
        result = utils.find_containers_dir()
        # Assert
        assert isinstance(result, Path)

    def test_raises_when_no_containers_dir_found(self, tmp_path, monkeypatch):
        """When no candidates exist, FileNotFoundError must be raised."""
        # Arrange
        # Act
        # Assert
        monkeypatch.chdir(tmp_path)

        # Ensure ~/.scitex/containers does not match by using a fake home
        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        utils = _utils()
        with patch("pathlib.Path.home", return_value=fake_home):
            with pytest.raises(FileNotFoundError):
                utils.find_containers_dir()

    def test_error_message_lists_searched_paths(self, tmp_path, monkeypatch):
        """Error message should describe what was searched."""
        # Arrange
        monkeypatch.chdir(tmp_path)

        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        utils = _utils()
        msg = ""
        with patch("pathlib.Path.home", return_value=fake_home):
            try:
                utils.find_containers_dir()
            except FileNotFoundError as exc:
                msg = str(exc).lower()
        # Act
        contains_containers = "containers" in msg
        # Assert
        assert contains_containers

    def test_cwd_containers_dir_without_def_files_is_skipped(
        self, tmp_path, monkeypatch
    ):
        """An empty containers/ dir (no .def) should not be selected."""
        # Arrange
        # Act
        # Assert
        containers = tmp_path / "containers"
        containers.mkdir()
        # No .def files — only a random file
        (containers / "README.txt").write_text("hello")

        monkeypatch.chdir(tmp_path)

        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        utils = _utils()
        with patch("pathlib.Path.home", return_value=fake_home):
            with pytest.raises(FileNotFoundError):
                utils.find_containers_dir()

    def test_user_home_containers_fallback(self, tmp_path, monkeypatch):
        """~/.scitex/container/runtime/containers/ with .def files is a valid fallback."""
        # Use a temp dir as home to avoid touching the real ~/.scitex
        # Arrange
        fake_home = tmp_path / "fakehome"
        user_containers = fake_home / ".scitex" / "container" / "runtime" / "containers"
        user_containers.mkdir(parents=True)
        (user_containers / "myenv.def").write_text("Bootstrap: docker\n")

        # Make cwd a directory with no containers/ subdir
        cwd = tmp_path / "workdir"
        cwd.mkdir()
        monkeypatch.chdir(cwd)

        utils = _utils()
        # Act
        with patch("pathlib.Path.home", return_value=fake_home):
            result = utils.find_containers_dir()

        # Assert
        assert result == user_containers

    def test_def_file_required_not_just_any_file(self, tmp_path, monkeypatch):
        """containers/ with only non-.def files should not match."""
        # Arrange
        # Act
        # Assert
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "config.yaml").write_text("key: value\n")
        (containers / "notes.txt").write_text("some notes\n")

        monkeypatch.chdir(tmp_path)

        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        utils = _utils()
        with patch("pathlib.Path.home", return_value=fake_home):
            with pytest.raises(FileNotFoundError):
                utils.find_containers_dir()

    def test_multiple_def_files_still_returns_dir(self, tmp_path, monkeypatch):
        """Multiple .def files in containers/ is fine — dir should be returned."""
        # Arrange
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "scitex-base.def").write_text("Bootstrap: docker\n")
        (containers / "scitex-final.def").write_text("Bootstrap: localimage\n")

        monkeypatch.chdir(tmp_path)

        utils = _utils()
        # Act
        result = utils.find_containers_dir()
        # Assert
        assert result == containers


# EOF
