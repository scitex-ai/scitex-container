#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/_cli/test__status.py
"""Tests for scitex_container._cli._status (show-status CLI dashboard)."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_container._cli._status import _collect_status, status


@pytest.fixture()
def runner():
    return CliRunner()


def test_help_exits_zero(runner):
    # Arrange
    # Act
    result = runner.invoke(status, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_default_invocation_result_exit_code_in_n_0_1(runner):
    # Arrange
    # Act
    result = runner.invoke(status, [])
    # Act
    # Assert
    assert result.exit_code in (0, 1)


def test_default_invocation_apptainer_in_out_or_host_packages_in_out_or_docker_in_out(runner):
    # Arrange
    # Act
    result = runner.invoke(status, [])
    # Exit may be 0 or 1 depending on environment; output must not be empty
    # Assert
    # Act
    out = result.output
    # Act
    # Assert
    assert "Apptainer" in out or "Host Packages" in out or "Docker" in out, (
        f"missing dashboard sections in output: {out!r}"
    )




def test_json_flag_emits_valid_json_result_exit_code_in_n_0_1(runner):
    # Arrange
    # Act
    result = runner.invoke(status, ["--json"])
    # Act
    # Assert
    assert result.exit_code in (0, 1)


def test_json_flag_emits_valid_json_parsed_is_dict(runner):
    # Arrange
    # Act
    result = runner.invoke(status, ["--json"])
    # Assert
    # Act
    parsed = json.loads(result.output)
    # Act
    # Assert
    assert isinstance(parsed, dict)




def test_collect_status_returns_dict_payload_is_dict():
    # Arrange
    # Act
    payload = _collect_status()
    # Act
    # Assert
    assert isinstance(payload, dict)


def test_collect_status_returns_dict_apptainer_host_docker_set_payload_keys():
    # Arrange
    # Act
    payload = _collect_status()
    # Act
    # Assert
    assert {"apptainer", "host", "docker"} <= set(payload.keys())




def test_collect_status_apptainer_section_is_dict():
    # Arrange
    # Act
    payload = _collect_status()
    # Assert
    assert isinstance(payload["apptainer"], dict)


def test_collect_status_host_section_is_dict():
    # Arrange
    # Act
    payload = _collect_status()
    # Assert
    assert isinstance(payload["host"], dict)


def test_collect_status_docker_section_is_dict():
    # Arrange
    # Act
    payload = _collect_status()
    # Assert
    assert (isinstance(payload['docker'], dict)) and (all((env in payload['docker'] for env in ('dev', 'prod'))))


# EOF
