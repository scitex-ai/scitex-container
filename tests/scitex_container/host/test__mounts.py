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
# get_texlive_binds
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


# EOF
