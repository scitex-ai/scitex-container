#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_cli/test__env_snapshot.py
"""Tests for scitex_container._cli._env_snapshot (save-env-snapshot CLI)."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_container._cli._env_snapshot import env_snapshot_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def test_help_exits_zero(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_dry_run_exits_zero_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, ["--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_dry_run_exits_zero_dry_run_in_result_output_lower(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, ["--dry-run"])
    # Act
    # Assert
    assert "dry-run" in result.output.lower()




def test_default_invocation_succeeds_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, [])
    # Act
    # Assert
    assert result.exit_code == 0


def test_default_invocation_succeeds_result_output_strip(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, [])
    # Act
    # Assert
    assert result.output.strip() != ""




def test_json_flag_emits_valid_json_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, ["--json"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_json_flag_emits_valid_json_parsed_is_dict(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, ["--json"])
    # Assert
    # Act
    parsed = json.loads(result.output)
    # Act
    # Assert
    assert isinstance(parsed, dict)


def test_json_flag_emits_valid_json_schema_version_in_parsed(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, ["--json"])
    # Assert
    # Act
    parsed = json.loads(result.output)
    # Act
    # Assert
    assert "schema_version" in parsed


def test_json_flag_emits_valid_json_timestamp_in_parsed(runner):
    # Arrange
    # Act
    result = runner.invoke(env_snapshot_cmd, ["--json"])
    # Assert
    # Act
    parsed = json.loads(result.output)
    # Act
    # Assert
    assert "timestamp" in parsed




def test_dev_repo_flag_accepts_path_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(
        env_snapshot_cmd,
        ["--dev-repo", "/tmp/__nonexistent__", "--json"],
    )
    # Act
    # Assert
    assert result.exit_code == 0


def test_dev_repo_flag_accepts_path_dev_repos_in_parsed(runner):
    # Arrange
    # Act
    result = runner.invoke(
        env_snapshot_cmd,
        ["--dev-repo", "/tmp/__nonexistent__", "--json"],
    )
    # Assert
    # Act
    parsed = json.loads(result.output)
    # Act
    # Assert
    assert "dev_repos" in parsed




def test_containers_dir_flag_accepted(runner):
    # Arrange
    # Act
    result = runner.invoke(
        env_snapshot_cmd,
        ["--containers-dir", "/tmp/__nonexistent_containers__", "--json"],
    )
    # Assert
    assert result.exit_code == 0


# EOF
