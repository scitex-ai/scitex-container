#!/usr/bin/env python3
# Timestamp: "2026-07-02"
# File: tests/scitex_container/apptainer/test__build.py
"""Tests for scitex_container.apptainer._build atomic-publish logic.

No mocks. The safety-critical part of the atomic build strategy — the
dual stable-symlink publish and its interaction with retention — is pure
filesystem logic, so it is exercised directly against tmp_path with
fake-byte ``.sif`` files (the store never execs them), exactly like the
_store tests. The subprocess-invoking ``build()`` end-to-end path needs a
real apptainer image and is covered by the gated round-trip integration
test (``test__reproducible_roundtrip.py``, which drives ``build()`` via
the rough build).
"""

from __future__ import annotations

from pathlib import Path


def _build():
    from scitex_container.apptainer import _build as b

    return b


def _mk_ts_sif(image_dir: Path, name: str, ts: str) -> Path:
    """Materialize a fake timestamped artifact <image_dir>/<name>-<ts>.sif."""
    image_dir.mkdir(parents=True, exist_ok=True)
    sif = image_dir / f"{name}-{ts}.sif"
    sif.write_bytes(b"fake-sif-" + ts.encode())
    return sif


class TestPublishAtomicInner:
    """The inner <name>/<name>.sif symlink — the path consumers boot from."""

    def test_creates_inner_symlink(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert (image_dir / "sac-base.sif").is_symlink()

    def test_inner_resolves_to_timestamped_sif(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        sif = _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert (image_dir / "sac-base.sif").resolve() == sif.resolve()

    def test_inner_target_is_relative(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert not (image_dir / "sac-base.sif").readlink().is_absolute()


class TestPublishAtomicTopLevel:
    """The top-level <name>.sif symlink — cross-layer From: ./<name>.sif."""

    def test_creates_top_level_symlink(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert (tmp_path / "sac-base.sif").is_symlink()

    def test_top_resolves_to_timestamped_sif(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        sif = _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert (tmp_path / "sac-base.sif").resolve() == sif.resolve()

    def test_top_target_is_relative(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert not (tmp_path / "sac-base.sif").readlink().is_absolute()


class TestPublishAtomicReturn:
    """_publish_atomic returns the resolved real timestamped SIF."""

    def test_returns_real_timestamped_sif(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        sif = _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        result = b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert result == sif

    def test_returned_path_is_not_a_symlink(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        # Act
        result = b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Assert
        assert not result.is_symlink()


class TestRepublishSwap:
    """A rebuild atomically repoints both symlinks; prior build retained."""

    def test_inner_repoints_to_new_build(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-110000")
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-110000")
        # Assert
        assert (image_dir / "sac-base.sif").resolve().name == "sac-base-2026-0702-110000.sif"

    def test_top_repoints_to_new_build(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-110000")
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-110000")
        # Assert
        assert (tmp_path / "sac-base.sif").resolve().name == "sac-base-2026-0702-110000.sif"

    def test_prior_build_retained_on_disk(self, tmp_path):
        # Arrange
        b = _build()
        image_dir = tmp_path / "sac-base"
        prior = _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-110000")
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-100000")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-110000")
        # Assert — the prior SIF stays available for rollback
        assert prior.exists()


class TestPublishThenRetain:
    """publish + _store.prune — build()'s retention behaviour, no apptainer."""

    def _store(self):
        from scitex_container.apptainer import _store as s

        return s

    def test_prune_keeps_live_plus_retain(self, tmp_path):
        # Arrange
        b = _build()
        s = self._store()
        image_dir = tmp_path / "sac-base"
        for ts in ("2026-0702-100000", "2026-0702-110000", "2026-0702-120000"):
            _mk_ts_sif(image_dir, "sac-base", ts)
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-120000")
        # Act
        s.prune(tmp_path, "sac-base", retain=1)
        # Assert — live build + 1 previous kept (store semantic: N+1 total)
        assert len(list(image_dir.glob("sac-base-*.sif"))) == 2

    def test_prune_removes_oldest(self, tmp_path):
        # Arrange
        b = _build()
        s = self._store()
        image_dir = tmp_path / "sac-base"
        oldest = _mk_ts_sif(image_dir, "sac-base", "2026-0702-100000")
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-110000")
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-120000")
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-120000")
        # Act
        s.prune(tmp_path, "sac-base", retain=1)
        # Assert
        assert not oldest.exists()

    def test_live_symlink_valid_after_prune(self, tmp_path):
        # Arrange
        b = _build()
        s = self._store()
        image_dir = tmp_path / "sac-base"
        for ts in ("2026-0702-100000", "2026-0702-110000", "2026-0702-120000"):
            _mk_ts_sif(image_dir, "sac-base", ts)
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-120000")
        # Act
        s.prune(tmp_path, "sac-base", retain=1)
        # Assert — the boot symlink still resolves to an existing file
        assert (image_dir / "sac-base.sif").resolve().exists()

    def test_active_build_never_pruned(self, tmp_path):
        # Arrange
        b = _build()
        s = self._store()
        image_dir = tmp_path / "sac-base"
        for ts in ("2026-0702-100000", "2026-0702-110000", "2026-0702-120000"):
            _mk_ts_sif(image_dir, "sac-base", ts)
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-120000")
        # Act
        pruned = s.prune(tmp_path, "sac-base", retain=1)
        # Assert
        assert "2026-0702-120000" not in pruned


class TestMigratesPreAtomicRealFile:
    """A pre-atomic-layout real file at the inner path is replaced by a symlink."""

    def test_real_inner_file_replaced_by_symlink(self, tmp_path):
        # Arrange — legacy layout: <name>/<name>.sif is a real file
        b = _build()
        image_dir = tmp_path / "sac-base"
        _mk_ts_sif(image_dir, "sac-base", "2026-0702-120000")
        (image_dir / "sac-base.sif").write_bytes(b"legacy-real-file")
        # Act
        b._publish_atomic(tmp_path, image_dir, "sac-base", "2026-0702-120000")
        # Assert
        assert (image_dir / "sac-base.sif").is_symlink()


# EOF
