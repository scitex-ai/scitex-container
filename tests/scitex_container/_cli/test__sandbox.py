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
    result = runner.invoke(sandbox, ["--help"])
    assert result.exit_code == 0


def test_sandbox_group_lists_subcommands(runner):
    result = runner.invoke(sandbox, ["--help"])
    out = result.output
    assert "create" in out
    assert "maintain" in out


def test_sandbox_create_help(runner):
    result = runner.invoke(sandbox, ["create", "--help"])
    assert result.exit_code == 0


def test_sandbox_create_dry_run(runner):
    """Dry-run does not require a real source."""
    result = runner.invoke(sandbox, ["create", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower()


def test_sandbox_create_dry_run_with_source(runner):
    result = runner.invoke(
        sandbox,
        ["create", "-s", "/tmp/foo.sif", "--dry-run"],
    )
    assert result.exit_code == 0
    assert "/tmp/foo.sif" in result.output


def test_sandbox_create_without_source_errors(runner):
    """Without --source, real invocation must fail with a clear error."""
    result = runner.invoke(sandbox, ["create"])
    assert result.exit_code != 0
    assert "source" in result.output.lower() or "required" in result.output.lower()


def test_sandbox_maintain_help(runner):
    result = runner.invoke(sandbox, ["maintain", "--help"])
    assert result.exit_code == 0


# EOF
