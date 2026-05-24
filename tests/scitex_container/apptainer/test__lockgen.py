#!/usr/bin/env python3
# Timestamp: "2026-05-24"
# File: tests/scitex_container/apptainer/test__lockgen.py
"""Tests for scitex_container.apptainer._lockgen.

No mocks. The lock-parse / write / round-trip / def-gen / compare logic
is exercised against real Lock objects and real files in tmp_path. The
SIF-introspection path (capture_lock) requires apptainer + a built image
and is covered by the round-trip integration test (gated on apptainer).
"""

from __future__ import annotations

import pytest


def _lockgen():
    from scitex_container.apptainer import _lockgen as lg

    return lg


def _make_lock(pip=None, dpkg=None, node=""):
    lg = _lockgen()
    return lg.Lock(pip=pip or {}, dpkg=dpkg or {}, node=node)


class TestVersionSet:
    """Lock.version_set flattening."""

    def test_pip_packages_are_prefixed_pip(self):
        # Arrange
        lock = _make_lock(pip={"numpy": "2.1.0"})
        # Act
        vs = lock.version_set()
        # Assert
        assert vs["pip:numpy"] == "2.1.0"

    def test_dpkg_packages_are_prefixed_dpkg(self):
        # Arrange
        lock = _make_lock(dpkg={"libc6": "2.39-0ubuntu8"})
        # Act
        vs = lock.version_set()
        # Assert
        assert vs["dpkg:libc6"] == "2.39-0ubuntu8"

    def test_node_globals_are_flattened_and_prefixed_node(self):
        # Arrange
        node_json = '{"dependencies": {"npm": {"version": "10.8.2"}}}'
        lock = _make_lock(node=node_json)
        # Act
        vs = lock.version_set()
        # Assert
        assert vs["node:npm"] == "10.8.2"

    def test_empty_node_json_contributes_no_entries(self):
        # Arrange
        lock = _make_lock(pip={"a": "1.0"}, node="")
        # Act
        vs = lock.version_set()
        # Assert
        assert all(not k.startswith("node:") for k in vs)


class TestWriteReadRoundTrip:
    """write_lock then read_lock preserves the version sets."""

    def test_pip_versions_survive_round_trip(self, tmp_path):
        # Arrange
        lg = _lockgen()
        lock = _make_lock(pip={"numpy": "2.1.0", "scipy": "1.14.0"})
        path = tmp_path / "x.lock"
        lg.write_lock(lock, path)
        # Act
        reloaded = lg.read_lock(path)
        # Assert
        assert reloaded.pip == {"numpy": "2.1.0", "scipy": "1.14.0"}

    def test_dpkg_versions_survive_round_trip(self, tmp_path):
        # Arrange
        lg = _lockgen()
        lock = _make_lock(dpkg={"libc6": "2.39-0ubuntu8.3"})
        path = tmp_path / "x.lock"
        lg.write_lock(lock, path)
        # Act
        reloaded = lg.read_lock(path)
        # Assert
        assert reloaded.dpkg == {"libc6": "2.39-0ubuntu8.3"}

    def test_node_block_survives_round_trip(self, tmp_path):
        # Arrange
        lg = _lockgen()
        node_json = '{"dependencies": {"npm": {"version": "10.8.2"}}}'
        lock = _make_lock(node=node_json)
        path = tmp_path / "x.lock"
        lg.write_lock(lock, path)
        # Act
        reloaded = lg.read_lock(path)
        # Assert
        assert reloaded.version_set()["node:npm"] == "10.8.2"

    def test_written_lock_has_section_headers(self, tmp_path):
        # Arrange
        lg = _lockgen()
        lock = _make_lock(pip={"a": "1.0"})
        path = tmp_path / "x.lock"
        # Act
        lg.write_lock(lock, path)
        # Assert
        assert "[pip]" in path.read_text()


class TestGenerateLockedDef:
    """generate_locked_def emits a pinned %post stanza."""

    @pytest.fixture
    def rough_def(self, tmp_path):
        p = tmp_path / "rough.def"
        p.write_text(
            "Bootstrap: docker\nFrom: ubuntu:24.04\n\n%post\n    apt-get update\n"
        )
        return p

    def test_locked_def_pins_each_pip_version(self, tmp_path, rough_def):
        # Arrange
        lg = _lockgen()
        lock = _make_lock(pip={"numpy": "2.1.0"})
        out = tmp_path / "locked.def"
        # Act
        lg.generate_locked_def(rough_def, lock, out)
        # Assert
        assert "numpy==2.1.0" in out.read_text()

    def test_locked_def_preserves_rough_body(self, tmp_path, rough_def):
        # Arrange
        lg = _lockgen()
        lock = _make_lock(pip={"numpy": "2.1.0"})
        out = tmp_path / "locked.def"
        # Act
        lg.generate_locked_def(rough_def, lock, out)
        # Assert
        assert "From: ubuntu:24.04" in out.read_text()

    def test_locked_def_handles_empty_pip_set(self, tmp_path, rough_def):
        # Arrange
        lg = _lockgen()
        lock = _make_lock(pip={})
        out = tmp_path / "locked.def"
        # Act
        lg.generate_locked_def(rough_def, lock, out)
        # Assert
        assert "no pip packages captured" in out.read_text()

    def test_locked_def_marks_its_generated_stanza(self, tmp_path, rough_def):
        # Arrange
        lg = _lockgen()
        lock = _make_lock(pip={"a": "1.0"})
        out = tmp_path / "locked.def"
        # Act
        lg.generate_locked_def(rough_def, lock, out)
        # Assert
        assert "scitex-container: pinned pip versions" in out.read_text()


class TestCompareLocks:
    """compare_locks — the round-trip gate."""

    def test_identical_locks_compare_equal(self):
        # Arrange
        lg = _lockgen()
        a = _make_lock(pip={"numpy": "2.1.0"}, dpkg={"libc6": "2.39"})
        b = _make_lock(pip={"numpy": "2.1.0"}, dpkg={"libc6": "2.39"})
        # Act
        diff = lg.compare_locks(a, b)
        # Assert
        assert diff.identical is True

    def test_changed_version_is_not_identical(self):
        # Arrange
        lg = _lockgen()
        a = _make_lock(pip={"numpy": "2.1.0"})
        b = _make_lock(pip={"numpy": "2.2.0"})
        # Act
        diff = lg.compare_locks(a, b)
        # Assert
        assert diff.identical is False

    def test_changed_version_recorded_with_both_values(self):
        # Arrange
        lg = _lockgen()
        a = _make_lock(pip={"numpy": "2.1.0"})
        b = _make_lock(pip={"numpy": "2.2.0"})
        # Act
        diff = lg.compare_locks(a, b)
        # Assert
        assert diff.changed["pip:numpy"] == ("2.1.0", "2.2.0")

    def test_package_only_in_rough_is_flagged(self):
        # Arrange
        lg = _lockgen()
        a = _make_lock(pip={"numpy": "2.1.0", "extra": "1.0"})
        b = _make_lock(pip={"numpy": "2.1.0"})
        # Act
        diff = lg.compare_locks(a, b)
        # Assert
        assert "pip:extra" in diff.only_in_a

    def test_package_only_in_rebuild_is_flagged(self):
        # Arrange
        lg = _lockgen()
        a = _make_lock(pip={"numpy": "2.1.0"})
        b = _make_lock(pip={"numpy": "2.1.0", "added": "9.9"})
        # Act
        diff = lg.compare_locks(a, b)
        # Assert
        assert "pip:added" in diff.only_in_b

    def test_identical_summary_says_identical(self):
        # Arrange
        lg = _lockgen()
        a = _make_lock(pip={"numpy": "2.1.0"})
        b = _make_lock(pip={"numpy": "2.1.0"})
        # Act
        diff = lg.compare_locks(a, b)
        # Assert
        assert "identical" in diff.summary()

    def test_drift_summary_names_changed_package(self):
        # Arrange
        lg = _lockgen()
        a = _make_lock(pip={"numpy": "2.1.0"})
        b = _make_lock(pip={"numpy": "2.2.0"})
        # Act
        diff = lg.compare_locks(a, b)
        # Assert
        assert "numpy" in diff.summary()


# EOF
