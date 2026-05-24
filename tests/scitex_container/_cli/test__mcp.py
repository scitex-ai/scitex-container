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
    # Arrange
    # Act
    result = runner.invoke(mcp, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_mcp_group_lists_subcommands_list_tools_in_out(runner):
    # Arrange
    result = runner.invoke(mcp, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "list-tools" in out


def test_mcp_group_lists_subcommands_doctor_in_out(runner):
    # Arrange
    result = runner.invoke(mcp, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "doctor" in out


def test_mcp_group_lists_subcommands_start_in_out(runner):
    # Arrange
    result = runner.invoke(mcp, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "start" in out


def test_mcp_no_subcommand_prints_help_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, [])
    # Act
    # Assert
    assert result.exit_code == 0


def test_mcp_no_subcommand_prints_help_usage_in_result_output_or_usage_in_result_output_lower(
    runner,
):
    # Arrange
    # Act
    result = runner.invoke(mcp, [])
    # Act
    # Assert
    assert "Usage" in result.output or "usage" in result.output.lower()


def test_mcp_help_recursive(runner):
    """--help-recursive should run without crashing."""
    # Arrange
    # Act
    result = runner.invoke(mcp, ["--help-recursive"])
    # Assert
    assert result.exit_code in (0, 2)


def test_mcp_list_tools_help(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["list-tools", "--help"])
    # Assert
    assert result.exit_code == 0


def test_mcp_list_tools_runs_result_exit_code_in_n_0_1(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["list-tools"])
    # Act
    # Assert
    assert result.exit_code in (0, 1)


def test_mcp_list_tools_runs_result_output_strip(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["list-tools"])
    # Act
    # Assert
    assert result.output.strip() != ""


def test_mcp_list_tools_json_exit_code(runner):
    """--json should exit cleanly (0 or 1 envelope error)."""
    # Arrange
    # Act
    result = runner.invoke(mcp, ["list-tools", "--json"])
    # Assert
    assert result.exit_code in (0, 1)


def test_mcp_list_tools_json_payload_is_dict(runner):
    """When --json emits output, it must be a JSON object."""
    # Arrange
    import json

    # Act
    result = runner.invoke(mcp, ["list-tools", "--json"])
    out = result.output.strip()
    parsed = json.loads(out) if out else {}
    # Assert
    assert isinstance(parsed, dict)


def test_mcp_doctor_help(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["doctor", "--help"])
    # Assert
    assert result.exit_code == 0


def test_mcp_doctor_runs_result_exit_code_in_n_0_1(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["doctor"])
    # Act
    # Assert
    assert result.exit_code in (0, 1)


def test_mcp_doctor_runs_scitex_container_mcp_doctor_in_result_output(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["doctor"])
    # Act
    # Assert
    assert "scitex-container MCP Doctor" in result.output


def test_mcp_start_help(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["start", "--help"])
    # Assert
    assert result.exit_code == 0


def test_mcp_start_dry_run_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["start", "--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_mcp_start_dry_run_dry_run_in_result_output_lower(runner):
    # Arrange
    # Act
    result = runner.invoke(mcp, ["start", "--dry-run"])
    # Act
    # Assert
    assert "dry-run" in result.output.lower()


# EOF
