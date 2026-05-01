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
    result = runner.invoke(status, ["--help"])
    assert result.exit_code == 0


def test_default_invocation(runner):
    """show-status must run cleanly even without containers/docker installed."""
    result = runner.invoke(status, [])
    # Exit may be 0 or 1 depending on environment; output must not be empty
    assert result.exit_code in (0, 1)
    out = result.output
    assert "Apptainer" in out or "Host Packages" in out or "Docker" in out, (
        f"missing dashboard sections in output: {out!r}"
    )


def test_json_flag_emits_valid_json(runner):
    result = runner.invoke(status, ["--json"])
    assert result.exit_code in (0, 1)
    parsed = json.loads(result.output)
    assert isinstance(parsed, dict)
    for section in ("apptainer", "host", "docker"):
        assert section in parsed, f"missing section: {section}"


def test_collect_status_returns_dict():
    """Internal aggregator should always return a populated dict."""
    payload = _collect_status()
    assert isinstance(payload, dict)
    assert {"apptainer", "host", "docker"} <= set(payload.keys())


def test_collect_status_apptainer_section_is_dict():
    payload = _collect_status()
    assert isinstance(payload["apptainer"], dict)


def test_collect_status_host_section_is_dict():
    payload = _collect_status()
    assert isinstance(payload["host"], dict)


def test_collect_status_docker_section_is_dict():
    payload = _collect_status()
    assert isinstance(payload["docker"], dict)
    # Each env should appear (dev/prod) — even if values report errors
    for env in ("dev", "prod"):
        assert env in payload["docker"]


# EOF
