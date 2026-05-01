#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/docker/test__mounts.py
"""Tests for scitex_container.docker._mounts.get_dev_mounts."""

from __future__ import annotations

from scitex_container.docker import get_dev_mounts


class TestGetDevMounts:
    def test_empty_list_returns_empty(self):
        assert get_dev_mounts([]) == []

    def test_returns_list_of_strings(self):
        result = get_dev_mounts(
            [{"host": "/a", "container": "/c"}],
        )
        assert isinstance(result, list)
        for s in result:
            assert isinstance(s, str)

    def test_default_mode_is_ro(self):
        result = get_dev_mounts([{"host": "/a", "container": "/c"}])
        assert result == ["/a:/c:ro"]

    def test_explicit_rw_mode(self):
        result = get_dev_mounts([{"host": "/a", "container": "/c", "mode": "rw"}])
        assert result == ["/a:/c:rw"]

    def test_relative_host_preserved(self):
        result = get_dev_mounts(
            [{"host": "../scitex-python", "container": "/scitex-python"}],
        )
        # Relative paths must be preserved so docker-compose can resolve them
        assert result == ["../scitex-python:/scitex-python:ro"]

    def test_missing_host_skipped(self):
        result = get_dev_mounts(
            [{"container": "/c"}, {"host": "/a", "container": "/c"}],
        )
        assert result == ["/a:/c:ro"]

    def test_missing_container_skipped(self):
        result = get_dev_mounts(
            [{"host": "/a"}, {"host": "/a", "container": "/c"}],
        )
        assert result == ["/a:/c:ro"]

    def test_multiple_repos_preserve_order(self):
        result = get_dev_mounts(
            [
                {"host": "/a", "container": "/ca"},
                {"host": "/b", "container": "/cb", "mode": "rw"},
            ],
        )
        assert result == ["/a:/ca:ro", "/b:/cb:rw"]


# EOF
