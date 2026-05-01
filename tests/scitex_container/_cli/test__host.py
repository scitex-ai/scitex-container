#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_cli/test__host.py
"""Tests for scitex_container._cli._host (host sub-group)."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from scitex_container._cli._host import host


@pytest.fixture()
def runner():
    return CliRunner()


def test_host_group_help(runner):
    result = runner.invoke(host, ["--help"])
    assert result.exit_code == 0


def test_host_group_lists_subcommands(runner):
    result = runner.invoke(host, ["--help"])
    out = result.output
    assert "install" in out
    assert "check" in out
    assert "show-mounts" in out


def test_host_install_help(runner):
    result = runner.invoke(host, ["install", "--help"])
    assert result.exit_code == 0


def test_host_install_dry_run(runner):
    result = runner.invoke(host, ["install", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower()


def test_host_check_runs(runner):
    """check inspects the host; should always return exit 0."""
    result = runner.invoke(host, ["check"])
    assert result.exit_code == 0


def test_host_show_mounts_help(runner):
    result = runner.invoke(host, ["show-mounts", "--help"])
    assert result.exit_code == 0


def test_host_show_mounts_default(runner):
    result = runner.invoke(host, ["show-mounts"])
    assert result.exit_code == 0


def test_host_show_mounts_json(runner):
    import json

    result = runner.invoke(host, ["show-mounts", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert isinstance(parsed, dict)
    assert "mounts" in parsed


def test_host_mounts_deprecated_redirect(runner):
    """Legacy `host mounts` exits 2 with a rename hint."""
    result = runner.invoke(host, ["mounts"])
    assert result.exit_code == 2
    assert "show-mounts" in result.output


# EOF
