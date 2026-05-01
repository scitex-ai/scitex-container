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
    result = runner.invoke(env_snapshot_cmd, ["--help"])
    assert result.exit_code == 0


def test_dry_run_exits_zero(runner):
    result = runner.invoke(env_snapshot_cmd, ["--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower()


def test_default_invocation_succeeds(runner):
    """env_snapshot is designed to never fail."""
    result = runner.invoke(env_snapshot_cmd, [])
    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_json_flag_emits_valid_json(runner):
    result = runner.invoke(env_snapshot_cmd, ["--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert isinstance(parsed, dict)
    assert "schema_version" in parsed
    assert "timestamp" in parsed


def test_dev_repo_flag_accepts_path(runner):
    """--dev-repo PATH (repeatable) must be accepted; non-existent path is OK."""
    result = runner.invoke(
        env_snapshot_cmd,
        ["--dev-repo", "/tmp/__nonexistent__", "--json"],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert "dev_repos" in parsed


def test_containers_dir_flag_accepted(runner):
    result = runner.invoke(
        env_snapshot_cmd,
        ["--containers-dir", "/tmp/__nonexistent_containers__", "--json"],
    )
    assert result.exit_code == 0


# EOF
