"""Smoke: the CLI launches and answers ``--help`` (PS-211).

Subprocess-driven (``sys.executable -m scitex_container``) so this
proves the installed entry point resolves — an in-process parser call
would not. Hermetic: no network, no credentials, no writes outside
tmp dirs (fake ``$SCITEX_DIR`` from the smoke conftest).
"""

from __future__ import annotations

import subprocess
import sys

import pytest

pytestmark = pytest.mark.smoke


def test_top_level_answers_help() -> None:
    # Arrange
    argv = [sys.executable, "-m", "scitex_container", "--help"]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)

    # Assert
    assert completed.returncode == 0


def test_top_level_help_lists_apptainer() -> None:
    # Arrange
    argv = [sys.executable, "-m", "scitex_container", "--help"]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)

    # Assert
    assert "apptainer" in completed.stdout
