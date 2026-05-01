#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_cli/test__mcp.py
"""Tests for scitex_container._cli._mcp (mcp sub-group)."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from scitex_container._cli._mcp import mcp


@pytest.fixture()
def runner():
    return CliRunner()


def test_mcp_group_help(runner):
    result = runner.invoke(mcp, ["--help"])
    assert result.exit_code == 0


def test_mcp_group_lists_subcommands(runner):
    result = runner.invoke(mcp, ["--help"])
    out = result.output
    assert "list-tools" in out
    assert "doctor" in out
    assert "start" in out


def test_mcp_no_subcommand_prints_help(runner):
    """Bare `mcp` (no subcommand) prints the group help."""
    result = runner.invoke(mcp, [])
    assert result.exit_code == 0
    assert "Usage" in result.output or "usage" in result.output.lower()


def test_mcp_help_recursive(runner):
    """--help-recursive should run without crashing."""
    result = runner.invoke(mcp, ["--help-recursive"])
    assert result.exit_code in (0, 2)


def test_mcp_list_tools_help(runner):
    result = runner.invoke(mcp, ["list-tools", "--help"])
    assert result.exit_code == 0


def test_mcp_list_tools_runs(runner):
    """Exit 0 when fastmcp installed; 1 otherwise. Output must always be present."""
    result = runner.invoke(mcp, ["list-tools"])
    assert result.exit_code in (0, 1)
    assert result.output.strip() != ""


def test_mcp_list_tools_json(runner):
    """--json should emit a JSON envelope (or a JSON error)."""
    import json

    result = runner.invoke(mcp, ["list-tools", "--json"])
    assert result.exit_code in (0, 1)
    # Output should be JSON parseable when --json is used
    out = result.output.strip()
    if out:
        parsed = json.loads(out)
        assert isinstance(parsed, dict)


def test_mcp_doctor_help(runner):
    result = runner.invoke(mcp, ["doctor", "--help"])
    assert result.exit_code == 0


def test_mcp_doctor_runs(runner):
    result = runner.invoke(mcp, ["doctor"])
    assert result.exit_code in (0, 1)
    assert "scitex-container MCP Doctor" in result.output


def test_mcp_start_help(runner):
    result = runner.invoke(mcp, ["start", "--help"])
    assert result.exit_code == 0


def test_mcp_start_dry_run(runner):
    result = runner.invoke(mcp, ["start", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower()


# EOF
