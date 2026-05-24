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
    # Arrange
    # Act
    result = runner.invoke(host, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_host_group_lists_subcommands_install_in_out(runner):
    # Arrange
    result = runner.invoke(host, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "install" in out


def test_host_group_lists_subcommands_check_in_out(runner):
    # Arrange
    result = runner.invoke(host, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "check" in out


def test_host_group_lists_subcommands_show_mounts_in_out(runner):
    # Arrange
    result = runner.invoke(host, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "show-mounts" in out




def test_host_install_help(runner):
    # Arrange
    # Act
    result = runner.invoke(host, ["install", "--help"])
    # Assert
    assert result.exit_code == 0


def test_host_install_dry_run_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(host, ["install", "--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_host_install_dry_run_dry_run_in_result_output_lower(runner):
    # Arrange
    # Act
    result = runner.invoke(host, ["install", "--dry-run"])
    # Act
    # Assert
    assert "dry-run" in result.output.lower()




def test_host_check_runs(runner):
    """check inspects the host; should always return exit 0."""
    # Arrange
    # Act
    result = runner.invoke(host, ["check"])
    # Assert
    assert result.exit_code == 0


def test_host_show_mounts_help(runner):
    # Arrange
    # Act
    result = runner.invoke(host, ["show-mounts", "--help"])
    # Assert
    assert result.exit_code == 0


def test_host_show_mounts_default(runner):
    # Arrange
    # Act
    result = runner.invoke(host, ["show-mounts"])
    # Assert
    assert result.exit_code == 0


def test_host_show_mounts_json_result_exit_code_equals_n_0(runner):
    # Arrange
    import json
    # Act
    result = runner.invoke(host, ["show-mounts", "--json"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_host_show_mounts_json_parsed_is_dict(runner):
    # Arrange
    import json
    # Act
    result = runner.invoke(host, ["show-mounts", "--json"])
    # Assert
    # Act
    parsed = json.loads(result.output)
    # Act
    # Assert
    assert isinstance(parsed, dict)


def test_host_show_mounts_json_mounts_in_parsed(runner):
    # Arrange
    import json
    # Act
    result = runner.invoke(host, ["show-mounts", "--json"])
    # Assert
    # Act
    parsed = json.loads(result.output)
    # Act
    # Assert
    assert "mounts" in parsed




def test_host_mounts_deprecated_redirect_result_exit_code_equals_n_2(runner):
    # Arrange
    # Act
    result = runner.invoke(host, ["mounts"])
    # Act
    # Assert
    assert result.exit_code == 2


def test_host_mounts_deprecated_redirect_show_mounts_in_result_output(runner):
    # Arrange
    # Act
    result = runner.invoke(host, ["mounts"])
    # Act
    # Assert
    assert "show-mounts" in result.output




# EOF
