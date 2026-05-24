#!/usr/bin/env python3
# Timestamp: "2026-05-24"
# File: tests/scitex_container/apptainer/test__config.py
"""Tests for scitex_container.apptainer._config.

No mocks — config files are written as real YAML into a tmp root and the
user-scope fallback is steered with the SCITEX_DIR environment variable
(honoured by local_state.user_path).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def _config():
    from scitex_container.apptainer import _config as c

    return c


@pytest.fixture
def scitex_dir(tmp_path):
    """Point SCITEX_DIR at a tmp dir so user-scope config is isolated."""
    user_root = tmp_path / "scitex-home"
    user_root.mkdir()
    saved = os.environ.get("SCITEX_DIR")
    os.environ["SCITEX_DIR"] = str(user_root)
    try:
        yield user_root
    finally:
        if saved is None:
            os.environ.pop("SCITEX_DIR", None)
        else:
            os.environ["SCITEX_DIR"] = saved


@pytest.fixture
def no_project_scope(tmp_path):
    """Chdir to an isolated dir with no .scitex/ so project-scope is absent."""
    workdir = tmp_path / "no-scope"
    workdir.mkdir()
    saved = Path.cwd()
    os.chdir(workdir)
    try:
        yield workdir
    finally:
        os.chdir(saved)


class TestDefaults:
    """ImageConfig built-in defaults."""

    def test_default_retain_is_ten(self):
        # Arrange
        c = _config()
        # Act
        cfg = c.ImageConfig()
        # Assert
        assert cfg.retain == 10

    def test_default_require_verified_is_false(self):
        # Arrange
        c = _config()
        # Act
        cfg = c.ImageConfig()
        # Assert
        assert cfg.require_verified is False


class TestDefaultConfigPath:
    """default_config_path resolution."""

    def test_explicit_root_yields_config_yaml_under_it(self, tmp_path):
        # Arrange
        c = _config()
        # Act
        path = c.default_config_path(tmp_path)
        # Assert
        assert path == tmp_path / "config.yaml"

    def test_none_root_resolves_to_user_scope_container(self, scitex_dir):
        # Arrange
        c = _config()
        # Act
        path = c.default_config_path(None)
        # Assert
        assert path == scitex_dir / "container" / "config.yaml"


class TestLoadConfig:
    """load_config cascade and parsing."""

    def test_missing_config_returns_defaults(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        c = _config()
        # Act
        cfg = c.load_config(tmp_path)
        # Assert
        assert cfg == c.ImageConfig()

    def test_reads_retain_from_root_config(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        c = _config()
        (tmp_path / "config.yaml").write_text("images:\n  retain: 3\n")
        # Act
        cfg = c.load_config(tmp_path)
        # Assert
        assert cfg.retain == 3

    def test_reads_require_verified_true_from_root_config(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        c = _config()
        (tmp_path / "config.yaml").write_text("images:\n  require_verified: true\n")
        # Act
        cfg = c.load_config(tmp_path)
        # Assert
        assert cfg.require_verified is True

    def test_invalid_retain_falls_back_to_default(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        c = _config()
        (tmp_path / "config.yaml").write_text("images:\n  retain: not-a-number\n")
        # Act
        cfg = c.load_config(tmp_path)
        # Assert
        assert cfg.retain == c.DEFAULT_RETAIN

    def test_zero_retain_falls_back_to_default(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        c = _config()
        (tmp_path / "config.yaml").write_text("images:\n  retain: 0\n")
        # Act
        cfg = c.load_config(tmp_path)
        # Assert
        assert cfg.retain == c.DEFAULT_RETAIN

    def test_empty_config_file_returns_defaults(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        c = _config()
        (tmp_path / "config.yaml").write_text("")
        # Act
        cfg = c.load_config(tmp_path)
        # Assert
        assert cfg == c.ImageConfig()

    def test_malformed_yaml_falls_back_to_defaults(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        c = _config()
        (tmp_path / "config.yaml").write_text("images: [this is: not valid: mapping\n")
        # Act
        cfg = c.load_config(tmp_path)
        # Assert
        assert cfg == c.ImageConfig()


# EOF
