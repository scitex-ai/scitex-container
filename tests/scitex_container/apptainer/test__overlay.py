#!/usr/bin/env python3
# Timestamp: "2026-07-18"
# File: tests/scitex_container/apptainer/test__overlay.py
"""Tests for scitex_container.apptainer._overlay lifecycle primitives.

No mocks. ``build_overlay_create_command`` is a pure function exercised
directly. ``create_overlay`` is driven against a REAL fake ``apptainer``
executable dropped into a tmp dir and put first on ``PATH`` (a yield-based
fixture that edits ``os.environ`` and restores it on teardown) — so the
real ``subprocess.run`` PATH-resolution + return-code handling is exercised
without a real apptainer backend. ``destroy_overlay`` and ``size_bytes``
are pure filesystem logic exercised against ``tmp_path``.
"""

from __future__ import annotations

import os

import pytest


def _overlay():
    from scitex_container.apptainer import _overlay as o

    return o


@pytest.fixture
def apptainer_on_path(tmp_path):
    """Put a REAL fake ``apptainer`` first on PATH that succeeds + logs argv.

    Yields the argv-log path so a test can assert the exact command executed.
    """
    bindir = tmp_path / "fakebin"
    bindir.mkdir()
    argv_log = bindir / "argv.txt"
    script = bindir / "apptainer"
    script.write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$@" > "' + str(argv_log) + '"\n'
        'touch "${@: -1}"\n'
        "exit 0\n"
    )
    script.chmod(0o755)
    saved = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{bindir}{os.pathsep}{saved}"
    try:
        yield argv_log
    finally:
        os.environ["PATH"] = saved


@pytest.fixture
def failing_apptainer_on_path(tmp_path):
    """Put a REAL fake ``apptainer`` first on PATH that exits nonzero + stderr."""
    bindir = tmp_path / "failbin"
    bindir.mkdir()
    script = bindir / "apptainer"
    script.write_text(
        "#!/usr/bin/env bash\n"
        'echo "no space left on device" >&2\n'
        "exit 1\n"
    )
    script.chmod(0o755)
    saved = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{bindir}{os.pathsep}{saved}"
    try:
        yield bindir
    finally:
        os.environ["PATH"] = saved


class TestBuildOverlayCreateCommand:
    """The pure argv builder: exact shape + headroom math."""

    def test_argv_prefix_shape(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        # Act
        cmd = o.build_overlay_create_command(path, 1000)
        # Assert
        assert cmd[:4] == ["apptainer", "overlay", "create", "--size"]

    def test_overlay_path_is_last_arg(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        # Act
        cmd = o.build_overlay_create_command(path, 1000)
        # Assert
        assert cmd[-1] == str(path)

    def test_headroom_default_6pct(self, tmp_path):
        # Arrange
        o = _overlay()
        # Act — 1000 MB * 1.06 == 1060 exactly
        cmd = o.build_overlay_create_command(tmp_path / "u.img", 1000)
        # Assert
        assert cmd[4] == "1060"

    def test_headroom_rounds_up_on_noninteger(self, tmp_path):
        # Arrange
        o = _overlay()
        # Act — 333 * 1.06 == 352.98 -> ceil -> 353 (proves rounding UP)
        cmd = o.build_overlay_create_command(tmp_path / "u.img", 333)
        # Assert
        assert cmd[4] == "353"

    def test_size_value_is_a_string(self, tmp_path):
        # Arrange
        o = _overlay()
        # Act
        cmd = o.build_overlay_create_command(tmp_path / "u.img", 500)
        # Assert
        assert isinstance(cmd[4], str)

    def test_custom_headroom_frac(self, tmp_path):
        # Arrange
        o = _overlay()
        # Act — 200 * 1.10 == 220 exactly
        cmd = o.build_overlay_create_command(
            tmp_path / "u.img", 200, headroom_frac=0.10
        )
        # Assert
        assert cmd[4] == "220"


class TestCreateOverlaySuccess:
    """create_overlay: success path returns the path + runs the built command."""

    def test_returns_overlay_path(self, tmp_path, apptainer_on_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "nested" / "user.img"
        # Act
        result = o.create_overlay(path, 1000)
        # Assert
        assert result == path

    def test_creates_parent_dir(self, tmp_path, apptainer_on_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "nested" / "user.img"
        # Act
        o.create_overlay(path, 1000)
        # Assert
        assert path.parent.is_dir()

    def test_runs_the_built_command(self, tmp_path, apptainer_on_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        expected = o.build_overlay_create_command(path, 1000)[1:]
        # Act
        o.create_overlay(path, 1000)
        # Assert — the fake apptainer logged the exact argv from the builder
        assert apptainer_on_path.read_text().split() == expected


class TestCreateOverlayFailure:
    """create_overlay: nonzero rc raises loudly with stderr in the message."""

    def test_nonzero_rc_raises_runtimeerror(self, tmp_path, failing_apptainer_on_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        ctx = pytest.raises(RuntimeError)
        # Act
        # Assert
        with ctx:
            o.create_overlay(path, 1000)

    def test_error_message_includes_stderr(self, tmp_path, failing_apptainer_on_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        ctx = pytest.raises(RuntimeError, match="no space left on device")
        # Act
        # Assert
        with ctx:
            o.create_overlay(path, 1000)


class TestDestroyOverlay:
    """destroy_overlay: idempotent removal reporting prior existence."""

    def test_existing_file_returns_true(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        path.write_bytes(b"overlay")
        # Act
        result = o.destroy_overlay(path)
        # Assert
        assert result is True

    def test_existing_file_is_removed(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        path.write_bytes(b"overlay")
        # Act
        o.destroy_overlay(path)
        # Assert
        assert not path.exists()

    def test_absent_file_returns_false(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "missing.img"
        # Act
        result = o.destroy_overlay(path)
        # Assert
        assert result is False

    def test_idempotent_second_call_returns_false(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        path.write_bytes(b"overlay")
        o.destroy_overlay(path)
        # Act
        result = o.destroy_overlay(path)
        # Assert
        assert result is False


class TestSizeBytes:
    """size_bytes: the billing meter — real size, loud on absence."""

    def test_returns_byte_count(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "user.img"
        path.write_bytes(b"x" * 4096)
        # Act
        result = o.size_bytes(path)
        # Assert
        assert result == 4096

    def test_missing_file_raises_filenotfound(self, tmp_path):
        # Arrange
        o = _overlay()
        path = tmp_path / "missing.img"
        ctx = pytest.raises(FileNotFoundError)
        # Act
        # Assert
        with ctx:
            o.size_bytes(path)


# EOF
