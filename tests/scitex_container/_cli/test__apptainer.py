#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_cli/test__apptainer.py
"""Tests for scitex_container._cli._apptainer.

Exercises every Apptainer-group leaf command via Click's CliRunner.
--help and --dry-run paths must succeed without an Apptainer install.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from scitex_container._cli import _apptainer as mod


@pytest.fixture()
def runner():
    return CliRunner()


_LEAF_COMMANDS = [
    "build",
    "freeze",
    "list_containers",
    "switch",
    "rollback",
    "deploy",
    "cleanup",
    "verify",
]


@pytest.mark.parametrize("name", _LEAF_COMMANDS)
def test_leaf_command_exposed(name):
    # Arrange
    # Act
    # Assert
    assert hasattr(mod, name), f"_cli._apptainer missing {name!r}"


@pytest.mark.parametrize("name", _LEAF_COMMANDS)
def test_leaf_command_is_click(name):
    # Arrange
    import click

    # Act
    cmd = getattr(mod, name)
    # Assert
    assert isinstance(cmd, click.BaseCommand), f"{name} must be a Click command/group"


@pytest.mark.parametrize("name", _LEAF_COMMANDS)
def test_leaf_help_exits_zero(name, runner):
    # Arrange
    cmd = getattr(mod, name)
    # Act
    result = runner.invoke(cmd, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_register_attaches_all_leaves():
    """register(main) should add every leaf to the parent group."""
    # Arrange
    import click

    parent = click.Group()
    mod.register(parent)
    registered = set(parent.commands.keys())
    # Click sub-command names use hyphens or the function name; spot-check core
    # Note: actual Click command names (with hyphens / aliases): cleanup → "clean",
    # list_containers → "list".
    # Act
    expected = {
        "build",
        "freeze",
        "list",
        "switch",
        "rollback",
        "deploy",
        "clean",
        "verify",
    }
    # Assert
    assert expected.issubset(registered), (
        f"register() missing some commands; got {registered}"
    )


def test_build_dry_run_succeeds_result_exit_code_equals_n_0(runner):
    # Arrange
    # Act
    result = runner.invoke(mod.build, ["--dry-run"])
    # Act
    # Assert
    assert result.exit_code == 0


def test_build_dry_run_succeeds_dry_run_in_result_output_lower(runner):
    # Arrange
    # Act
    result = runner.invoke(mod.build, ["--dry-run"])
    # Act
    # Assert
    assert "dry-run" in result.output.lower()




# EOF
