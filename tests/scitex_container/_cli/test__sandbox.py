#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_cli/test__sandbox.py
"""Tests for scitex_container._cli._sandbox (sandbox sub-group)."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from scitex_container._cli._sandbox import sandbox


@pytest.fixture()
def runner():
    return CliRunner()


def test_sandbox_group_help(runner):
    # Arrange
    # Act
    result = runner.invoke(sandbox, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_sandbox_group_lists_subcommands_create_in_out(runner):
    # Arrange
    result = runner.invoke(sandbox, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "create" in out


def test_sandbox_group_lists_subcommands_maintain_in_out(runner):
    # Arrange
    result = runner.invoke(sandbox, ["--help"])
    # Act
    out = result.output
    # Act
    # Assert
    assert "maintain" in out




def test_sandbox_create_help(runner):
    # Arrange
    # Act
    result = runner.invoke(sandbox, ["create", "--help"])
    # Assert
    assert result.exit_code == 0


def test_sandbox_create_dry_run_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(sandbox, ["create", "--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_sandbox_create_dry_run_dry_run_in_result_output_lower(runner):
    # Arrange
    # Act
    result = runner.invoke(sandbox, ["create", "--dry-run"])
    # Act
    # Assert
    assert "dry-run" in result.output.lower()




def test_sandbox_create_dry_run_with_source_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(
        sandbox,
        ["create", "-s", "/tmp/foo.sif", "--dry-run"],
    )
    # Act
    # Assert
    assert result.exit_code == 0


def test_sandbox_create_dry_run_with_source_tmp_foo_sif_in_result_output(runner):
    # Arrange
    # Act
    result = runner.invoke(
        sandbox,
        ["create", "-s", "/tmp/foo.sif", "--dry-run"],
    )
    # Act
    # Assert
    assert "/tmp/foo.sif" in result.output




def test_sandbox_create_without_source_errors_result_exit_code_0(runner):
    # Arrange
    # Act
    result = runner.invoke(sandbox, ["create"])
    # Act
    # Assert
    assert result.exit_code != 0


def test_sandbox_create_without_source_errors_source_in_result_output_lower_or_required_in_result_output_l(runner):
    # Arrange
    # Act
    result = runner.invoke(sandbox, ["create"])
    # Act
    # Assert
    assert "source" in result.output.lower() or "required" in result.output.lower()




def test_sandbox_maintain_help(runner):
    # Arrange
    # Act
    result = runner.invoke(sandbox, ["maintain", "--help"])
    # Assert
    assert result.exit_code == 0


# EOF
