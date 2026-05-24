#!/usr/bin/env python3
# Timestamp: "2026-05-24"
# File: tests/scitex_container/apptainer/test__reproducible.py
"""Tests for scitex_container.apptainer._reproducible (use-time gate).

No mocks. The use-time verify gate (check_verified) is exercised against
real marker files in tmp_path. The full round-trip (build_reproducible /
verify_roundtrip) requires apptainer + a real build and lives in the
gated integration test ``test__reproducible_roundtrip.py``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def _repro():
    from scitex_container.apptainer import _reproducible as r

    return r


@pytest.fixture
def scitex_dir(tmp_path):
    """Point SCITEX_DIR at a tmp dir so config resolution is isolated."""
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
    workdir = tmp_path / "no-scope"
    workdir.mkdir()
    saved = Path.cwd()
    os.chdir(workdir)
    try:
        yield workdir
    finally:
        os.chdir(saved)


def _sif_with_marker(tmp_path: Path, marker_ext: str | None, body: str = "") -> Path:
    """Create a fake <name>.sif and an optional sibling marker."""
    sif = tmp_path / "img.sif"
    sif.write_bytes(b"fake")
    if marker_ext is not None:
        (tmp_path / f"img{marker_ext}").write_text(body or "marker\n")
    return sif


class TestCheckVerifiedVerified:
    """A .verified image passes silently."""

    def test_verified_marker_yields_verified_state(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, ".verified")
        # Act
        status = r.check_verified(sif, require_verified=False)
        # Assert
        assert status.state == "verified"

    def test_verified_status_is_verified_true(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, ".verified")
        # Act
        status = r.check_verified(sif, require_verified=False)
        # Assert
        assert status.is_verified is True

    def test_verified_passes_even_under_require_verified(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, ".verified")
        # Act
        status = r.check_verified(sif, require_verified=True)
        # Assert
        assert status.state == "verified"


class TestCheckVerifiedUnverified:
    """An .unverified image warns by default, errors in strict mode."""

    def test_unverified_marker_yields_unverified_state(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, ".unverified", body="numpy drifted\n")
        # Act
        status = r.check_verified(sif, require_verified=False)
        # Assert
        assert status.state == "unverified"

    def test_unverified_detail_carries_drift_reason(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, ".unverified", body="numpy drifted\n")
        # Act
        status = r.check_verified(sif, require_verified=False)
        # Assert
        assert "numpy" in status.detail

    def test_unverified_warns_but_returns_in_default_mode(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, ".unverified", body="drift\n")
        # Act
        status = r.check_verified(sif, require_verified=False)
        # Assert
        assert status.is_verified is False

    def test_unverified_raises_under_require_verified(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, ".unverified", body="drift\n")
        ctx = pytest.raises(r.VerifyError)
        # Act
        # Assert
        with ctx:
            r.check_verified(sif, require_verified=True)


class TestCheckVerifiedUnknown:
    """An image with no marker is treated as unverified."""

    def test_no_marker_yields_unknown_state(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, None)
        # Act
        status = r.check_verified(sif, require_verified=False)
        # Assert
        assert status.state == "unknown"

    def test_no_marker_raises_under_require_verified(self, tmp_path):
        # Arrange
        r = _repro()
        sif = _sif_with_marker(tmp_path, None)
        ctx = pytest.raises(r.VerifyError)
        # Act
        # Assert
        with ctx:
            r.check_verified(sif, require_verified=True)


class TestCheckVerifiedSymlink:
    """A latest-symlink is resolved before the marker lookup."""

    def test_symlink_resolves_to_verified_target(self, tmp_path):
        # Arrange
        r = _repro()
        layer_dir = tmp_path / "base"
        layer_dir.mkdir()
        target = layer_dir / "base-2026-0524-100000.sif"
        target.write_bytes(b"fake")
        (layer_dir / "base-2026-0524-100000.verified").write_text("ok\n")
        link = tmp_path / "base.sif"
        link.symlink_to(Path("base") / "base-2026-0524-100000.sif")
        # Act
        status = r.check_verified(link, require_verified=False)
        # Assert
        assert status.state == "verified"


class TestCheckVerifiedConfigResolution:
    """require_verified is read from config when not passed explicitly."""

    def test_require_verified_from_root_config_raises(
        self, tmp_path, scitex_dir, no_project_scope
    ):
        # Arrange
        r = _repro()
        root = tmp_path / "root"
        root.mkdir()
        (root / "config.yaml").write_text("images:\n  require_verified: true\n")
        sif = _sif_with_marker(tmp_path, ".unverified", body="drift\n")
        ctx = pytest.raises(r.VerifyError)
        # Act
        # Assert
        with ctx:
            r.check_verified(sif, root=root)


class TestPreserveBuildLog:
    """_preserve_build_log relocates _build's scratch log into the canonical slot.

    Pure filesystem logic (no real build): _build writes its log as
    ``<scratch>/<scratch>.build-<inner-ts>.log``; the helper must move it
    to the canonical ``build_log`` path so the rough build's log survives
    the scratch-dir ``rmtree``.
    """

    def _scratch_with_log(self, tmp_path: Path, scratch_name: str, body: str) -> Path:
        scratch_dir = tmp_path / scratch_name
        scratch_dir.mkdir()
        # _build's log name shape: <scratch>.build-<YYYY-MMDD-HHMMSS>.log
        log = scratch_dir / f"{scratch_name}.build-2026-0524-090000.log"
        log.write_text(body)
        return scratch_dir

    def test_relocates_scratch_log_to_canonical_slot(self, tmp_path):
        # Arrange
        r = _repro()
        scratch = self._scratch_with_log(tmp_path, "base-ts", "rough build output\n")
        canonical = tmp_path / "base" / "base-ts.build.log"
        # Act
        r._preserve_build_log(scratch, "base-ts", canonical)
        # Assert
        assert canonical.read_text() == "rough build output\n"

    def test_removes_log_from_scratch_after_move(self, tmp_path):
        # Arrange
        r = _repro()
        scratch = self._scratch_with_log(tmp_path, "base-ts", "x\n")
        canonical = tmp_path / "base" / "base-ts.build.log"
        # Act
        r._preserve_build_log(scratch, "base-ts", canonical)
        # Assert
        assert list(scratch.glob("*.build-*.log")) == []

    def test_picks_newest_log_when_multiple(self, tmp_path):
        # Arrange
        r = _repro()
        scratch = tmp_path / "base-ts"
        scratch.mkdir()
        (scratch / "base-ts.build-2026-0524-080000.log").write_text("old\n")
        (scratch / "base-ts.build-2026-0524-090000.log").write_text("new\n")
        canonical = tmp_path / "base" / "base-ts.build.log"
        # Act
        r._preserve_build_log(scratch, "base-ts", canonical)
        # Assert
        assert canonical.read_text() == "new\n"

    def test_no_log_is_a_silent_noop(self, tmp_path):
        # Arrange
        r = _repro()
        scratch = tmp_path / "base-ts"
        scratch.mkdir()
        canonical = tmp_path / "base" / "base-ts.build.log"
        # Act
        r._preserve_build_log(scratch, "base-ts", canonical)
        # Assert
        assert not canonical.exists()

    def test_missing_scratch_dir_is_a_silent_noop(self, tmp_path):
        # Arrange
        r = _repro()
        canonical = tmp_path / "base" / "base-ts.build.log"
        # Act
        r._preserve_build_log(tmp_path / "absent", "base-ts", canonical)
        # Assert
        assert not canonical.exists()


# EOF
