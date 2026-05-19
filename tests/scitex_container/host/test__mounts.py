#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/host/test__mounts.py
"""Unit tests for scitex_container.host._mounts.

Covers get_mount_config (parses raw mount specs and assembles bind args)
and get_texlive_binds (returns the canonical TeX Live bind list).
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# get_mount_config
# ---------------------------------------------------------------------------


class TestGetMountConfig:
    """Tests for scitex_container.host.get_mount_config."""

    def _get(self):
        from scitex_container.host import get_mount_config

        return get_mount_config

    def test_returns_dict_result_is_dict(self):
        # Arrange
        # Act
        result = self._get()()
        # Assert
        assert isinstance(result, dict)

    def test_result_has_bind_args_key(self):
        # Arrange
        # Act
        result = self._get()()
        # Assert
        assert "bind_args" in result

    def test_result_has_mounts_key(self):
        # Arrange
        # Act
        result = self._get()()
        # Assert
        assert "mounts" in result

    def test_result_has_path_additions_key(self):
        # Arrange
        # Act
        result = self._get()()
        # Assert
        assert "path_additions" in result

    def test_bind_args_is_list(self):
        # Arrange
        # Act
        result = self._get()()
        # Assert
        assert isinstance(result["bind_args"], list)

    def test_mounts_is_list(self):
        # Arrange
        # Act
        result = self._get()()
        # Assert
        assert isinstance(result["mounts"], list)

    def test_raw_mount_spec_parsed_correctly_raw_mounts(self):
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/data:/mnt/data:ro")
        # Act
        raw_mounts = [m for m in result["mounts"] if m.get("host") == "/data"]
        # Act
        # Assert
        assert raw_mounts, "Expected one mount entry for /data"

    def test_raw_mount_spec_parsed_correctly_raw_mounts_0_container_mnt_data(self):
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/data:/mnt/data:ro")
        # Act
        raw_mounts = [m for m in result["mounts"] if m.get("host") == "/data"]
        # Act
        # Assert
        assert raw_mounts[0]["container"] == "/mnt/data"

    def test_raw_mount_spec_parsed_correctly_raw_mounts_0_mode_ro(self):
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/data:/mnt/data:ro")
        # Act
        raw_mounts = [m for m in result["mounts"] if m.get("host") == "/data"]
        # Act
        # Assert
        assert raw_mounts[0]["mode"] == "ro"

    def test_raw_mount_without_mode_defaults_to_rw_raw_mounts(self):
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/src:/dst")
        # Act
        raw_mounts = [m for m in result["mounts"] if m.get("host") == "/src"]
        # Act
        # Assert
        assert raw_mounts

    def test_raw_mount_without_mode_defaults_to_rw_raw_mounts_0_mode_rw(self):
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/src:/dst")
        # Act
        raw_mounts = [m for m in result["mounts"] if m.get("host") == "/src"]
        # Act
        # Assert
        assert raw_mounts[0]["mode"] == "rw"

    def test_multiple_raw_mounts_comma_separated_a_in_hosts(self):
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/a:/ca:ro,/b:/cb:rw")
        # Act
        hosts = {m["host"] for m in result["mounts"]}
        # Act
        # Assert
        assert "/a" in hosts

    def test_multiple_raw_mounts_comma_separated_b_in_hosts(self):
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/a:/ca:ro,/b:/cb:rw")
        # Act
        hosts = {m["host"] for m in result["mounts"]}
        # Act
        # Assert
        assert "/b" in hosts

    def test_bind_args_alternate_bind_and_spec(self):
        """bind_args must be a flat list of alternating '--bind' / spec strings."""
        # Arrange
        get = self._get()
        result = get(texlive_prefix="", host_mounts_raw="/x:/y:ro")
        bind_args = result["bind_args"]
        if not bind_args:
            return
        # Act
        all_bind_tokens = all(
            bind_args[i] == "--bind" for i in range(0, len(bind_args), 2)
        )
        # Assert
        assert all_bind_tokens


# ---------------------------------------------------------------------------
# get_texlive_binds
# ---------------------------------------------------------------------------


class TestGetTexliveBinds:
    """Tests for scitex_container.host.get_texlive_binds."""

    def _get(self):
        from scitex_container.host import get_texlive_binds

        return get_texlive_binds

    def test_returns_list_result_is_list(self):
        # Arrange
        # Act
        result = self._get()()
        # Assert
        assert isinstance(result, list)

    def test_entries_have_host_container_mode_keys(self):
        # Arrange
        # Act
        # Assert
        result = self._get()()
        for entry in result:
            assert ("host" in entry) and ("container" in entry) and ("mode" in entry)

    def test_all_modes_are_readonly(self):
        # Arrange
        # Act
        # Assert
        result = self._get()()
        # Assert
        assert all(entry["mode"] == "ro" for entry in result), (
            f"Expected 'ro' mode for texlive bind, got {entry['mode']!r}"
        )

    def test_custom_prefix_reflected_in_host_paths(self):
        # Arrange
        # Act
        # Assert
        get = self._get()
        # Act
        result = get(prefix="/opt/texlive")
        # Assert
        assert all(entry["host"].startswith("/opt/texlive") for entry in result), (
            f"Host path {entry['host']!r} does not start with /opt/texlive"
        )


# EOF
