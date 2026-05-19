#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_cli/test__docker.py
"""Tests for scitex_container._cli._docker (docker compose CLI sub-group)."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from scitex_container._cli._docker import docker


@pytest.fixture()
def runner():
    return CliRunner()


def test_docker_group_help(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_docker_group_lists_subcommands_rebuild_in_result_output(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["--help"])
    # Act
    # Assert
    assert "rebuild" in result.output


def test_docker_group_lists_subcommands_restart_in_result_output(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["--help"])
    # Act
    # Assert
    assert "restart" in result.output




def test_docker_rebuild_help(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["rebuild", "--help"])
    # Assert
    assert result.exit_code == 0


def test_docker_restart_help(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["restart", "--help"])
    # Assert
    assert result.exit_code == 0


def test_docker_rebuild_dry_run_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["rebuild", "--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_docker_rebuild_dry_run_dry_run_in_result_output_lower(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["rebuild", "--dry-run"])
    # Act
    # Assert
    assert "dry-run" in result.output.lower()




def test_docker_restart_dry_run_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["restart", "--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_docker_restart_dry_run_dry_run_in_result_output_lower(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["restart", "--dry-run"])
    # Act
    # Assert
    assert "dry-run" in result.output.lower()




def test_docker_rebuild_env_flag_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["rebuild", "--env", "prod", "--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_docker_rebuild_env_flag_prod_in_result_output(runner):
    # Arrange
    # Act
    result = runner.invoke(docker, ["rebuild", "--env", "prod", "--dry-run"])
    # Act
    # Assert
    assert "prod" in result.output




# EOF
