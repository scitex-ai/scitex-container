#!/usr/bin/env python3
# Timestamp: "2026-03-14"
# File: tests/test_utils.py
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

    def test_returns_string(self):
        utils = _utils()
        try:
            result = utils.detect_container_cmd()
            assert isinstance(result, str)
        except FileNotFoundError:
            pass  # acceptable when neither tool is installed

    def test_returns_apptainer_when_apptainer_available(self):
        """When apptainer is on PATH, it should be preferred."""
        utils = _utils()
        with patch(
            "shutil.which", side_effect=lambda cmd: cmd if cmd == "apptainer" else None
        ):
            result = utils.detect_container_cmd()
        assert result == "apptainer"

    def test_returns_singularity_when_only_singularity_available(self):
        utils = _utils()
        with patch(
            "shutil.which",
            side_effect=lambda cmd: cmd if cmd == "singularity" else None,
        ):
            result = utils.detect_container_cmd()
        assert result == "singularity"

    def test_raises_file_not_found_when_neither_available(self):
        utils = _utils()
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError):
                utils.detect_container_cmd()

    def test_error_message_mentions_apptainer(self):
        utils = _utils()
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError) as exc_info:
                utils.detect_container_cmd()
        assert "apptainer" in str(exc_info.value).lower()

    def test_error_message_mentions_singularity(self):
        utils = _utils()
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError) as exc_info:
                utils.detect_container_cmd()
        assert "singularity" in str(exc_info.value).lower()

    def test_apptainer_preferred_over_singularity(self):
        """When both are present, apptainer should win (checked first)."""
        utils = _utils()
        with patch("shutil.which", return_value="found"):  # both return truthy
            result = utils.detect_container_cmd()
        assert result == "apptainer"

    def test_returned_value_is_apptainer_or_singularity(self):
        utils = _utils()
        with patch(
            "shutil.which",
            side_effect=lambda cmd: cmd
            if cmd in ("apptainer", "singularity")
            else None,
        ):
            result = utils.detect_container_cmd()
        assert result in ("apptainer", "singularity")


# ---------------------------------------------------------------------------
# find_containers_dir
# ---------------------------------------------------------------------------


class TestFindContainersDir:
    """Tests for find_containers_dir."""

    def test_returns_path_when_cwd_containers_has_def(self, tmp_path, monkeypatch):
        """If ./containers/ exists with a .def file, it should be returned."""
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "scitex.def").write_text(
            "Bootstrap: docker\nFrom: ubuntu:22.04\n"
        )

        monkeypatch.chdir(tmp_path)

        utils = _utils()
        result = utils.find_containers_dir()
        assert result == containers

    def test_returned_path_is_path_object(self, tmp_path, monkeypatch):
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "base.def").write_text("Bootstrap: library\n")

        monkeypatch.chdir(tmp_path)

        utils = _utils()
        result = utils.find_containers_dir()
        assert isinstance(result, Path)

    def test_raises_when_no_containers_dir_found(self, tmp_path, monkeypatch):
        """When no candidates exist, FileNotFoundError must be raised."""
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
        monkeypatch.chdir(tmp_path)

        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        utils = _utils()
        with patch("pathlib.Path.home", return_value=fake_home):
            with pytest.raises(FileNotFoundError) as exc_info:
                utils.find_containers_dir()

        msg = str(exc_info.value)
        # Message should hint about at least one searched path
        assert "containers" in msg.lower()

    def test_cwd_containers_dir_without_def_files_is_skipped(
        self, tmp_path, monkeypatch
    ):
        """An empty containers/ dir (no .def) should not be selected."""
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
        fake_home = tmp_path / "fakehome"
        user_containers = fake_home / ".scitex" / "container" / "runtime" / "containers"
        user_containers.mkdir(parents=True)
        (user_containers / "myenv.def").write_text("Bootstrap: docker\n")

        # Make cwd a directory with no containers/ subdir
        cwd = tmp_path / "workdir"
        cwd.mkdir()
        monkeypatch.chdir(cwd)

        utils = _utils()
        with patch("pathlib.Path.home", return_value=fake_home):
            result = utils.find_containers_dir()

        assert result == user_containers

    def test_def_file_required_not_just_any_file(self, tmp_path, monkeypatch):
        """containers/ with only non-.def files should not match."""
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
        containers = tmp_path / "containers"
        containers.mkdir()
        (containers / "scitex-base.def").write_text("Bootstrap: docker\n")
        (containers / "scitex-final.def").write_text("Bootstrap: localimage\n")

        monkeypatch.chdir(tmp_path)

        utils = _utils()
        result = utils.find_containers_dir()
        assert result == containers


# ---------------------------------------------------------------------------
# host._mounts — get_mount_config (also a utility-style function)
# ---------------------------------------------------------------------------


class TestGetMountConfig:
    """Tests for scitex_container.host.get_mount_config."""

    def _get(self):
        from scitex_container.host import get_mount_config

        return get_mount_config

    def test_returns_dict(self):
        result = self._get()()
        assert isinstance(result, dict)

    def test_result_has_bind_args_key(self):
        result = self._get()()
        assert "bind_args" in result

    def test_result_has_mounts_key(self):
        result = self._get()()
        assert "mounts" in result

    def test_result_has_path_additions_key(self):
        result = self._get()()
        assert "path_additions" in result

    def test_bind_args_is_list(self):
        result = self._get()()
        assert isinstance(result["bind_args"], list)

    def test_mounts_is_list(self):
        result = self._get()()
        assert isinstance(result["mounts"], list)

    def test_raw_mount_spec_parsed_correctly(self):
        """A raw host:container:mode spec should produce one mount entry."""
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/data:/mnt/data:ro")
        raw_mounts = [m for m in result["mounts"] if m.get("host") == "/data"]
        assert raw_mounts, "Expected one mount entry for /data"
        assert raw_mounts[0]["container"] == "/mnt/data"
        assert raw_mounts[0]["mode"] == "ro"

    def test_raw_mount_without_mode_defaults_to_rw(self):
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/src:/dst")
        raw_mounts = [m for m in result["mounts"] if m.get("host") == "/src"]
        assert raw_mounts
        assert raw_mounts[0]["mode"] == "rw"

    def test_multiple_raw_mounts_comma_separated(self):
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/a:/ca:ro,/b:/cb:rw")
        hosts = {m["host"] for m in result["mounts"]}
        assert "/a" in hosts
        assert "/b" in hosts

    def test_bind_args_alternate_bind_and_spec(self):
        """bind_args must be a flat list of alternating '--bind' / spec strings."""
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/x:/y:ro")
        bind_args = result["bind_args"]
        if not bind_args:
            pytest.skip("No bind args produced for this host environment")
        for i in range(0, len(bind_args), 2):
            assert bind_args[i] == "--bind"


# ---------------------------------------------------------------------------
# host._mounts — get_texlive_binds
# ---------------------------------------------------------------------------


class TestGetTexliveBinds:
    """Tests for scitex_container.host.get_texlive_binds."""

    def _get(self):
        from scitex_container.host import get_texlive_binds

        return get_texlive_binds

    def test_returns_list(self):
        result = self._get()()
        assert isinstance(result, list)

    def test_entries_have_host_container_mode_keys(self):
        result = self._get()()
        for entry in result:
            assert "host" in entry
            assert "container" in entry
            assert "mode" in entry

    def test_all_modes_are_readonly(self):
        result = self._get()()
        for entry in result:
            assert entry["mode"] == "ro", (
                f"Expected 'ro' mode for texlive bind, got {entry['mode']!r}"
            )

    def test_custom_prefix_reflected_in_host_paths(self):
        get = self._get()
        result = get(prefix="/opt/texlive")
        for entry in result:
            assert entry["host"].startswith("/opt/texlive"), (
                f"Host path {entry['host']!r} does not start with /opt/texlive"
            )


# ---------------------------------------------------------------------------
# host._packages — check_packages (utility that inspects host environment)
# ---------------------------------------------------------------------------


class TestCheckPackages:
    """Tests for scitex_container.host.check_packages."""

    def test_returns_dict(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result, dict)

    def test_texlive_key_present(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "texlive" in result

    def test_imagemagick_key_present(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "imagemagick" in result

    def test_texlive_entry_has_installed_key(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "installed" in result["texlive"]

    def test_imagemagick_entry_has_installed_key(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "installed" in result["imagemagick"]

    def test_installed_field_is_bool(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result["texlive"]["installed"], bool)
        assert isinstance(result["imagemagick"]["installed"], bool)

    def test_binaries_field_is_list(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result["texlive"]["binaries"], list)
        assert isinstance(result["imagemagick"]["binaries"], list)

    def test_version_field_is_string(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result["texlive"]["version"], str)
        assert isinstance(result["imagemagick"]["version"], str)


# EOF
