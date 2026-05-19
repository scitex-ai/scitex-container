#!/usr/bin/env python3
# Timestamp: "2026-03-14"
# File: tests/test_snapshot.py
"""Unit tests for scitex_container._snapshot.

env_snapshot() is designed to degrade gracefully — it never raises and always
returns a dict with a fixed schema.  These tests verify the shape and content
of the returned snapshot without requiring actual containers or container
runtimes.

Private helpers (_sha256_file, _capture_one_repo, etc.) are also tested
directly since they contain non-trivial logic that benefits from isolation.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def _snap():
    """Import shortcut for the module under test."""
    from scitex_container import _snapshot as snap

    return snap


# ---------------------------------------------------------------------------
# env_snapshot — top-level contract
# ---------------------------------------------------------------------------


class TestEnvSnapshot:
    """Tests for env_snapshot public function."""

    def test_returns_dict_result_is_dict_2(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert isinstance(result, dict)

    def test_schema_version_present(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert "schema_version" in result

    def test_schema_version_is_string(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert isinstance(result["schema_version"], str)

    def test_schema_version_value(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert result["schema_version"] == "1.0"

    def test_timestamp_present_timestamp_in_result(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert "timestamp" in result

    def test_timestamp_is_iso_format(self):
        # Arrange
        from datetime import datetime

        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        ts = result["timestamp"]
        parsed = datetime.fromisoformat(ts)
        # Assert
        assert parsed is not None

    def test_timestamp_is_utc(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # UTC timestamps end with +00:00
        # Assert
        assert "+00:00" in result["timestamp"]

    def test_container_key_present(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert "container" in result

    def test_container_value_is_dict(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert isinstance(result["container"], dict)

    def test_host_key_present(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert "host" in result

    def test_host_value_is_dict(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert isinstance(result["host"], dict)

    def test_dev_repos_key_present(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert "dev_repos" in result

    def test_dev_repos_value_is_list(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert isinstance(result["dev_repos"], list)

    def test_dev_repos_defaults_to_empty_list(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert result["dev_repos"] == []

    def test_lock_files_key_present(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert "lock_files" in result

    def test_lock_files_value_is_dict(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot()
        # Assert
        assert isinstance(result["lock_files"], dict)

    def test_does_not_raise_when_no_containers_dir(self):
        """env_snapshot must not raise even when containers dir does not exist."""
        # Arrange
        from scitex_container import env_snapshot

        # Pass a nonexistent path — function must degrade gracefully
        # Act
        result = env_snapshot(containers_dir="/tmp/__nonexistent_containers__")
        # Assert
        assert isinstance(result, dict)

    def test_does_not_raise_with_empty_dev_repos(self):
        # Arrange
        from scitex_container import env_snapshot

        # Act
        result = env_snapshot(dev_repos=[])
        # Assert
        assert isinstance(result, dict)

    def test_dev_repos_passed_in_are_in_result(self):
        """When dev_repo paths are given, they appear in the result list."""
        # Arrange
        from scitex_container import env_snapshot

        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            result = env_snapshot(dev_repos=[tmpdir])
        # Assert
        assert len(result["dev_repos"]) == 1

    def test_dev_repo_entry_has_name_and_path_keys_name_in_entry(self):
        # Arrange
        from scitex_container import env_snapshot

        with tempfile.TemporaryDirectory() as tmpdir:
            result = env_snapshot(dev_repos=[tmpdir])
        # Act
        entry = result["dev_repos"][0]
        # Act
        # Assert
        assert "name" in entry

    def test_dev_repo_entry_has_name_and_path_keys_path_in_entry(self):
        # Arrange
        from scitex_container import env_snapshot

        with tempfile.TemporaryDirectory() as tmpdir:
            result = env_snapshot(dev_repos=[tmpdir])
        # Act
        entry = result["dev_repos"][0]
        # Act
        # Assert
        assert "path" in entry

    def test_nonexistent_dev_repo_has_error_key(self):
        """A non-existent path must produce an entry with an 'error' field."""
        # Arrange
        from scitex_container import env_snapshot

        result = env_snapshot(dev_repos=["/tmp/__does_not_exist_repo__"])
        # Act
        entry = result["dev_repos"][0]
        # Assert
        assert "error" in entry

    def test_result_is_json_serializable(self):
        """Full snapshot must be JSON-serializable (no Path objects, etc.)."""
        # Arrange
        import json

        from scitex_container import env_snapshot

        result = env_snapshot()
        # Act
        serialized = json.dumps(result)
        # Assert
        assert serialized  # not empty


# ---------------------------------------------------------------------------
# _sha256_file
# ---------------------------------------------------------------------------


class TestSha256File:
    """Tests for the internal _sha256_file helper."""

    def test_returns_hex_string(self):
        # Arrange
        snap = _snap()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"hello world")
            tmp_path = Path(f.name)
        try:
            # Act
            result = snap._sha256_file(tmp_path)
            parsed_int = int(result, 16)  # must be valid hex
            # Assert
            assert parsed_int >= 0
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_matches_hashlib_sha256(self):
        # Arrange
        # Act
        # Assert
        snap = _snap()
        content = b"scitex-container test content"
        expected = hashlib.sha256(content).hexdigest()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(content)
            tmp_path = Path(f.name)
        try:
            result = snap._sha256_file(tmp_path)
            assert result == expected
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_returns_empty_string_for_nonexistent_file(self):
        # Arrange
        snap = _snap()
        # Act
        result = snap._sha256_file(Path("/tmp/__no_such_file_sha256__.bin"))
        # Assert
        assert result == ""

    def test_empty_file_has_known_sha256(self):
        # Arrange
        # Act
        # Assert
        snap = _snap()
        expected = hashlib.sha256(b"").hexdigest()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            tmp_path = Path(f.name)
        try:
            result = snap._sha256_file(tmp_path)
            assert result == expected
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_different_contents_different_hashes(self):
        # Arrange
        # Act
        # Assert
        snap = _snap()
        with (
            tempfile.NamedTemporaryFile(delete=False) as f1,
            tempfile.NamedTemporaryFile(delete=False) as f2,
        ):
            f1.write(b"content A")
            f2.write(b"content B")
            p1, p2 = Path(f1.name), Path(f2.name)
        try:
            assert snap._sha256_file(p1) != snap._sha256_file(p2)
        finally:
            p1.unlink(missing_ok=True)
            p2.unlink(missing_ok=True)

    def test_large_file_chunked_correctly(self):
        """Files larger than chunk_size must hash correctly."""
        # Arrange
        # Act
        # Assert
        snap = _snap()
        content = b"x" * (3 * 1024 * 1024)  # 3 MB, larger than default 1 MB chunk
        expected = hashlib.sha256(content).hexdigest()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(content)
            tmp_path = Path(f.name)
        try:
            result = snap._sha256_file(tmp_path)
            assert result == expected
        finally:
            tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# _capture_one_repo
# ---------------------------------------------------------------------------


class TestCaptureOneRepo:
    """Tests for the internal _capture_one_repo helper."""

    def test_nonexistent_path_returns_error_key(self):
        # Arrange
        snap = _snap()
        # Act
        entry = snap._capture_one_repo(Path("/tmp/__no_such_repo__"))
        # Assert
        assert "error" in entry

    def test_nonexistent_path_preserves_name(self):
        # Arrange
        snap = _snap()
        # Act
        entry = snap._capture_one_repo(Path("/tmp/myrepo"))
        # Assert
        assert entry["name"] == "myrepo"

    def test_nonexistent_path_preserves_path(self):
        # Arrange
        snap = _snap()
        target = Path("/tmp/__no_such_repo__")
        # Act
        entry = snap._capture_one_repo(target)
        # Assert
        assert "path" in entry

    def test_existing_non_git_dir_returns_entry_with_no_commit(self):
        """A plain directory that is not a git repo should not have 'commit' key
        or should have an empty/missing value."""
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = snap._capture_one_repo(Path(tmpdir))
        # Must not crash; commit key should be absent or empty
        # Assert
        assert "error" not in entry or entry.get("commit", "") == ""

    def test_entry_always_has_name_and_path_name_in_entry(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = snap._capture_one_repo(Path(tmpdir))
        # Act
        # Assert
        assert "name" in entry

    def test_entry_always_has_name_and_path_path_in_entry(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = snap._capture_one_repo(Path(tmpdir))
        # Act
        # Assert
        assert "path" in entry

    @pytest.mark.skipif(
        not __import__("shutil").which("git"), reason="git not available"
    )
    def test_git_repo_has_commit_key_commit_in_entry(self):
        # Arrange
        snap = _snap()
        repo_path = Path(__file__).resolve().parents[1]
        # Act
        entry = snap._capture_one_repo(repo_path)
        # Assert
        assert "commit" in entry

    @pytest.mark.skipif(
        not __import__("shutil").which("git"), reason="git not available"
    )
    def test_git_repo_has_commit_key_len_entry_commit_is_40(self):
        # Arrange
        snap = _snap()
        repo_path = Path(__file__).resolve().parents[1]
        # Act
        entry = snap._capture_one_repo(repo_path)
        # Assert
        assert len(entry["commit"]) == 40  # SHA-1 hex

    @pytest.mark.skipif(
        not __import__("shutil").which("git"), reason="git not available"
    )
    def test_git_repo_has_dirty_key_dirty_in_entry(self):
        # Arrange
        snap = _snap()
        repo_path = Path(__file__).resolve().parents[1]
        # Act
        entry = snap._capture_one_repo(repo_path)
        # Assert
        assert "dirty" in entry

    @pytest.mark.skipif(
        not __import__("shutil").which("git"), reason="git not available"
    )
    def test_git_repo_has_dirty_key_isinstance_entry_dirty_bool(self):
        # Arrange
        snap = _snap()
        repo_path = Path(__file__).resolve().parents[1]
        # Act
        entry = snap._capture_one_repo(repo_path)
        # Assert
        assert isinstance(entry["dirty"], bool)


# ---------------------------------------------------------------------------
# _capture_lock_files
# ---------------------------------------------------------------------------


class TestCaptureLockFiles:
    """Tests for the internal _capture_lock_files helper."""

    def test_no_containers_dir_returns_empty_dict(self):
        # Arrange
        snap = _snap()
        # Act
        result = snap._capture_lock_files("/tmp/__no_containers_here__")
        # Assert
        assert result == {}

    def test_pip_lock_file_detected_pip_in_result(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "requirements_lock.txt"
            lock_path.write_text("numpy==1.26.0\n")
            result = snap._capture_lock_files(tmpdir)
        # Act
        # Assert
        assert "pip" in result

    def test_pip_lock_file_detected_result_pip(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "requirements_lock.txt"
            lock_path.write_text("numpy==1.26.0\n")
            result = snap._capture_lock_files(tmpdir)
        # Act
        # Assert
        assert result["pip"] != ""

    def test_dpkg_lock_file_detected_dpkg_in_result(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "dpkg_lock.txt"
            lock_path.write_text("python3 3.10.0\n")
            result = snap._capture_lock_files(tmpdir)
        # Act
        # Assert
        assert "dpkg" in result

    def test_dpkg_lock_file_detected_result_dpkg(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "dpkg_lock.txt"
            lock_path.write_text("python3 3.10.0\n")
            result = snap._capture_lock_files(tmpdir)
        # Act
        # Assert
        assert result["dpkg"] != ""

    def test_pip_lock_hash_matches_sha256(self):
        # Arrange
        snap = _snap()
        content = b"numpy==1.26.0\n"
        expected = hashlib.sha256(content).hexdigest()

        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "requirements_lock.txt"
            lock_path.write_bytes(content)
            result = snap._capture_lock_files(tmpdir)

        # Assert
        assert result.get("pip") == expected

    def test_missing_lock_files_not_in_result_pip_not_in_result(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            result = snap._capture_lock_files(tmpdir)
        # Act
        # Assert
        assert "pip" not in result

    def test_missing_lock_files_not_in_result_dpkg_not_in_result(self):
        # Arrange
        snap = _snap()
        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            result = snap._capture_lock_files(tmpdir)
        # Act
        # Assert
        assert "dpkg" not in result


# ---------------------------------------------------------------------------
# _capture_host
# ---------------------------------------------------------------------------


class TestCaptureHost:
    """Tests for the internal _capture_host helper."""

    def test_returns_dict_result_is_dict_2(self):
        # Arrange
        snap = _snap()
        # Act
        result = snap._capture_host()
        # Assert
        assert isinstance(result, dict)

    def test_texlive_key_present(self):
        # Arrange
        snap = _snap()
        # Act
        result = snap._capture_host()
        # Assert
        assert "texlive" in result

    def test_imagemagick_key_present(self):
        # Arrange
        snap = _snap()
        # Act
        result = snap._capture_host()
        # Assert
        assert "imagemagick" in result

    def test_values_have_installed_key(self):
        # Arrange
        # Act
        # Assert
        snap = _snap()
        # Act
        result = snap._capture_host()
        # Assert
        assert all("installed" in info for (pkg_name, info) in result.items()), (
            f"Missing 'installed' in {pkg_name}"
        )

    def test_installed_values_are_bool(self):
        # Arrange
        # Act
        # Assert
        snap = _snap()
        # Act
        result = snap._capture_host()
        # Assert
        assert all(
            isinstance(info["installed"], bool) for (pkg_name, info) in result.items()
        ), f"'installed' is not bool in {pkg_name}"


# EOF
