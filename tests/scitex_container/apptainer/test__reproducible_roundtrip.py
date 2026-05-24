#!/usr/bin/env python3
# Timestamp: "2026-05-24"
# File: tests/scitex_container/apptainer/test__reproducible_roundtrip.py
"""Gated integration test: full reproducible round-trip with a real build.

No mocks. This exercises ``build_reproducible`` end-to-end against a real
``apptainer`` build of a tiny alpine+python recipe:

    rough build -> freeze lock -> generate locked def
                -> rebuild from locked def -> compare version sets -> mark.

It is **skip-gated on apptainer presence** (the package's pytest CI runner
has no apptainer install). It runs locally / on any host that has apptainer.

What it asserts (the bits the fast unit tests cannot reach because they
need a real SIF on disk):

- the artifact tree: ``<layer>.sif`` symlink -> ``<layer>/<layer>-<ts>.sif``,
  paired ``.lock`` + ``.def``, ``.verified`` (or ``.unverified``) marker,
  and the ``.rough.def`` snapshot;
- **cleanup #2** — the rough build log lands in the canonical
  ``<layer>-<ts>.build.log`` slot (not lost to the scratch ``rmtree``);
- **cleanup #1** — no stray ``<layer>-<ts>.verify.lock`` remains after the
  round-trip compare;
- the throwaway verify SIF + its scratch dir are auto-deleted;
- ``check_verified`` on the ``latest`` symlink returns ``verified``;
- no stray root-level lock files (``requirements-lock.txt`` etc.).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

_HAS_APPTAINER = (
    shutil.which("apptainer") is not None or shutil.which("singularity") is not None
)

pytestmark = pytest.mark.skipif(
    not _HAS_APPTAINER,
    reason="apptainer/singularity not installed; round-trip integration test skipped",
)

# A genuinely tiny, network-light recipe: alpine + python3/pip. The rough
# build installs pip's own deps (packaging, pyparsing, ...) so the lock
# captures a real, non-empty pip version set to pin and reproduce.
_ROUGH_DEF = """Bootstrap: docker
From: alpine:3.19

%post
    apk add --no-cache python3 py3-pip
"""


def _repro():
    from scitex_container.apptainer import _reproducible as r

    return r


def _store():
    from scitex_container.apptainer import _store as s

    return s


@pytest.fixture
def containers_root(tmp_path):
    """An isolated containers/ output root with the rough .def written in."""
    root = tmp_path / "containers"
    root.mkdir()
    (root / "repro-smoke.def").write_text(_ROUGH_DEF)
    return root


class TestRoundTripRealBuild:
    """One real round-trip; assertions split one-per-test against the result."""

    @pytest.fixture(scope="class")
    def result(self, tmp_path_factory):
        """Run the full round-trip ONCE for the whole class (a real build)."""
        r = _repro()
        root = tmp_path_factory.mktemp("containers")
        def_path = root / "repro-smoke.def"
        def_path.write_text(_ROUGH_DEF)
        res = r.build_reproducible(
            layer="repro-smoke",
            root=root,
            def_path=def_path,
            verify=True,
        )
        return res, root

    def test_roundtrip_is_verified(self, result):
        # Arrange
        res, _root = result
        # Act
        verified = res.verified
        # Assert
        assert verified is True

    def test_canonical_sif_exists(self, result):
        # Arrange
        res, _root = result
        # Act
        exists = res.sif.exists()
        # Assert
        assert exists is True

    def test_latest_symlink_points_at_timestamped_sif(self, result):
        # Arrange
        res, root = result
        link = root / "repro-smoke.sif"
        # Act
        resolved_name = link.resolve().name
        # Assert
        assert resolved_name == f"repro-smoke-{res.ts}.sif"

    def test_paired_lock_exists(self, result):
        # Arrange
        res, _root = result
        # Act
        exists = res.lock.exists()
        # Assert
        assert exists is True

    def test_locked_def_exists(self, result):
        # Arrange
        res, _root = result
        # Act
        exists = res.locked_def.exists()
        # Assert
        assert exists is True

    def test_rough_def_snapshot_exists(self, result):
        # Arrange
        res, root = result
        snapshot = root / "repro-smoke" / f"repro-smoke-{res.ts}.rough.def"
        # Act
        exists = snapshot.exists()
        # Assert
        assert exists is True

    def test_verified_marker_present(self, result):
        # Arrange
        res, root = result
        marker = root / "repro-smoke" / f"repro-smoke-{res.ts}.verified"
        # Act
        exists = marker.exists()
        # Assert
        assert exists is True

    def test_rough_build_log_preserved_in_canonical_slot(self, result):
        # Cleanup #2: the rough build log must survive the scratch rmtree.
        # Arrange
        res, root = result
        build_log = root / "repro-smoke" / f"repro-smoke-{res.ts}.build.log"
        # Act
        exists = build_log.exists()
        # Assert
        assert exists is True

    def test_no_stray_verify_lock_remains(self, result):
        # Cleanup #1: the throwaway .verify.lock must be deleted post-compare.
        # Arrange
        res, root = result
        verify_lock = root / "repro-smoke" / f"repro-smoke-{res.ts}.verify.lock"
        # Act
        exists = verify_lock.exists()
        # Assert
        assert exists is False

    def test_verify_sif_auto_deleted(self, result):
        # Arrange
        res, root = result
        verify_scratch = root / f"repro-smoke-{res.ts}-verify"
        # Act
        exists = verify_scratch.exists()
        # Assert
        assert exists is False

    def test_check_verified_on_symlink_returns_verified(self, result):
        # Arrange
        r = _repro()
        _res, root = result
        link = root / "repro-smoke.sif"
        # Act
        status = r.check_verified(link, require_verified=False)
        # Assert
        assert status.state == "verified"

    def test_no_stray_root_lock_files(self, result):
        # Arrange
        _res, root = result
        # Act
        strays = [
            (root / name).exists()
            for name in ("requirements-lock.txt", "dpkg-lock.txt", "node-lock.txt")
        ]
        # Assert
        assert not any(strays)


# EOF
