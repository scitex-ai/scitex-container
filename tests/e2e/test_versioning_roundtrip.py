"""E2E: versioned-SIF switch/rollback against real filesystem state (PS-212).

The full story — two fake ``scitex-v*.sif`` files in a tmp containers
dir, ``switch_version`` flips the real ``current.sif`` symlink via
``ln``/``mv``, ``rollback`` walks back by modification time, and
``list_versions`` reports the active marker. No Apptainer binary, no
network beyond loopback (none at all), no credentials beyond tmp files.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e


def _seed_two_versions(containers_dir: Path) -> tuple[str, str]:
    """Write two fake versioned SIFs with distinct mtimes (older, newer)."""
    older, newer = "1.0", "2.0"
    first = containers_dir / f"scitex-v{older}.sif"
    second = containers_dir / f"scitex-v{newer}.sif"
    first.write_bytes(b"fake-sif-older")
    second.write_bytes(b"fake-sif-newer")
    old_mtime = time.time() - 100
    os.utime(first, (old_mtime, old_mtime))
    return older, newer


def test_switch_points_active_symlink_at_target(tmp_path: Path) -> None:
    # Arrange
    from scitex_container.apptainer import _versioning as ver

    _older, newer = _seed_two_versions(tmp_path)

    # Act
    ver.switch_version(newer, tmp_path)

    # Assert
    assert ver.get_active_version(tmp_path) == newer


def test_rollback_returns_to_previous_version(tmp_path: Path) -> None:
    # Arrange
    from scitex_container.apptainer import _versioning as ver

    older, newer = _seed_two_versions(tmp_path)
    ver.switch_version(newer, tmp_path)

    # Act
    previous = ver.rollback(tmp_path)

    # Assert
    assert (previous, ver.get_active_version(tmp_path)) == (older, older)


def test_list_versions_marks_active(tmp_path: Path) -> None:
    # Arrange
    from scitex_container.apptainer import _versioning as ver

    _older, newer = _seed_two_versions(tmp_path)
    ver.switch_version(newer, tmp_path)

    # Act
    rows = ver.list_versions(tmp_path)

    # Assert
    assert [r["version"] for r in rows if r["active"]] == [newer]
