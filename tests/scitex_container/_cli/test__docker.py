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
    result = runner.invoke(docker, ["--help"])
    assert result.exit_code == 0


def test_docker_group_lists_subcommands(runner):
    result = runner.invoke(docker, ["--help"])
    assert "rebuild" in result.output
    assert "restart" in result.output


def test_docker_rebuild_help(runner):
    result = runner.invoke(docker, ["rebuild", "--help"])
    assert result.exit_code == 0


def test_docker_restart_help(runner):
    result = runner.invoke(docker, ["restart", "--help"])
    assert result.exit_code == 0


def test_docker_rebuild_dry_run(runner):
    result = runner.invoke(docker, ["rebuild", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower()


def test_docker_restart_dry_run(runner):
    result = runner.invoke(docker, ["restart", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower()


def test_docker_rebuild_env_flag(runner):
    """--env / -e accepts a custom value."""
    result = runner.invoke(docker, ["rebuild", "--env", "prod", "--dry-run"])
    assert result.exit_code == 0
    assert "prod" in result.output


# EOF
