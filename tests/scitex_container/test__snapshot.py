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

    def test_returns_dict(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert isinstance(result, dict)

    def test_schema_version_present(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert "schema_version" in result

    def test_schema_version_is_string(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert isinstance(result["schema_version"], str)

    def test_schema_version_value(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert result["schema_version"] == "1.0"

    def test_timestamp_present(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert "timestamp" in result

    def test_timestamp_is_iso_format(self):
        from datetime import datetime

        from scitex_container import env_snapshot

        result = env_snapshot()
        ts = result["timestamp"]
        # Should parse without error
        datetime.fromisoformat(ts)

    def test_timestamp_is_utc(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        # UTC timestamps end with +00:00
        assert "+00:00" in result["timestamp"]

    def test_container_key_present(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert "container" in result

    def test_container_value_is_dict(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert isinstance(result["container"], dict)

    def test_host_key_present(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert "host" in result

    def test_host_value_is_dict(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert isinstance(result["host"], dict)

    def test_dev_repos_key_present(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert "dev_repos" in result

    def test_dev_repos_value_is_list(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert isinstance(result["dev_repos"], list)

    def test_dev_repos_defaults_to_empty_list(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert result["dev_repos"] == []

    def test_lock_files_key_present(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert "lock_files" in result

    def test_lock_files_value_is_dict(self):
        from scitex_container import env_snapshot

        result = env_snapshot()
        assert isinstance(result["lock_files"], dict)

    def test_does_not_raise_when_no_containers_dir(self):
        """env_snapshot must not raise even when containers dir does not exist."""
        from scitex_container import env_snapshot

        # Pass a nonexistent path — function must degrade gracefully
        result = env_snapshot(containers_dir="/tmp/__nonexistent_containers__")
        assert isinstance(result, dict)

    def test_does_not_raise_with_empty_dev_repos(self):
        from scitex_container import env_snapshot

        result = env_snapshot(dev_repos=[])
        assert isinstance(result, dict)

    def test_dev_repos_passed_in_are_in_result(self):
        """When dev_repo paths are given, they appear in the result list."""
        from scitex_container import env_snapshot

        with tempfile.TemporaryDirectory() as tmpdir:
            result = env_snapshot(dev_repos=[tmpdir])
        assert len(result["dev_repos"]) == 1

    def test_dev_repo_entry_has_name_and_path_keys(self):
        from scitex_container import env_snapshot

        with tempfile.TemporaryDirectory() as tmpdir:
            result = env_snapshot(dev_repos=[tmpdir])
        entry = result["dev_repos"][0]
        assert "name" in entry
        assert "path" in entry

    def test_nonexistent_dev_repo_has_error_key(self):
        """A non-existent path must produce an entry with an 'error' field."""
        from scitex_container import env_snapshot

        result = env_snapshot(dev_repos=["/tmp/__does_not_exist_repo__"])
        entry = result["dev_repos"][0]
        assert "error" in entry

    def test_result_is_json_serializable(self):
        """Full snapshot must be JSON-serializable (no Path objects, etc.)."""
        import json

        from scitex_container import env_snapshot

        result = env_snapshot()
        serialized = json.dumps(result)
        assert serialized  # not empty


# ---------------------------------------------------------------------------
# _sha256_file
# ---------------------------------------------------------------------------


class TestSha256File:
    """Tests for the internal _sha256_file helper."""

    def test_returns_hex_string(self):
        snap = _snap()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"hello world")
            tmp_path = Path(f.name)
        try:
            result = snap._sha256_file(tmp_path)
            int(result, 16)  # must be valid hex
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_matches_hashlib_sha256(self):
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
        snap = _snap()
        result = snap._sha256_file(Path("/tmp/__no_such_file_sha256__.bin"))
        assert result == ""

    def test_empty_file_has_known_sha256(self):
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
        snap = _snap()
        entry = snap._capture_one_repo(Path("/tmp/__no_such_repo__"))
        assert "error" in entry

    def test_nonexistent_path_preserves_name(self):
        snap = _snap()
        entry = snap._capture_one_repo(Path("/tmp/myrepo"))
        assert entry["name"] == "myrepo"

    def test_nonexistent_path_preserves_path(self):
        snap = _snap()
        target = Path("/tmp/__no_such_repo__")
        entry = snap._capture_one_repo(target)
        assert "path" in entry

    def test_existing_non_git_dir_returns_entry_with_no_commit(self):
        """A plain directory that is not a git repo should not have 'commit' key
        or should have an empty/missing value."""
        snap = _snap()
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = snap._capture_one_repo(Path(tmpdir))
        # Must not crash; commit key should be absent or empty
        assert "error" not in entry or entry.get("commit", "") == ""

    def test_entry_always_has_name_and_path(self):
        snap = _snap()
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = snap._capture_one_repo(Path(tmpdir))
        assert "name" in entry
        assert "path" in entry

    def test_git_repo_has_commit_key(self):
        """When git is available and the directory is a real repo, 'commit'
        should be populated.  This test uses the scitex-container repo itself."""
        import shutil

        if not shutil.which("git"):
            pytest.skip("git not available")

        snap = _snap()
        # The project root is a git repo
        repo_path = Path(__file__).resolve().parents[1]
        entry = snap._capture_one_repo(repo_path)
        assert "commit" in entry
        assert len(entry["commit"]) == 40  # SHA-1 hex

    def test_git_repo_has_dirty_key(self):
        """Entry for a real git repo must contain 'dirty' boolean."""
        import shutil

        if not shutil.which("git"):
            pytest.skip("git not available")

        snap = _snap()
        repo_path = Path(__file__).resolve().parents[1]
        entry = snap._capture_one_repo(repo_path)
        assert "dirty" in entry
        assert isinstance(entry["dirty"], bool)


# ---------------------------------------------------------------------------
# _capture_lock_files
# ---------------------------------------------------------------------------


class TestCaptureLockFiles:
    """Tests for the internal _capture_lock_files helper."""

    def test_no_containers_dir_returns_empty_dict(self):
        snap = _snap()
        result = snap._capture_lock_files("/tmp/__no_containers_here__")
        assert result == {}

    def test_pip_lock_file_detected(self):
        snap = _snap()
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "requirements_lock.txt"
            lock_path.write_text("numpy==1.26.0\n")
            result = snap._capture_lock_files(tmpdir)
        assert "pip" in result
        assert result["pip"] != ""

    def test_dpkg_lock_file_detected(self):
        snap = _snap()
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "dpkg_lock.txt"
            lock_path.write_text("python3 3.10.0\n")
            result = snap._capture_lock_files(tmpdir)
        assert "dpkg" in result
        assert result["dpkg"] != ""

    def test_pip_lock_hash_matches_sha256(self):
        snap = _snap()
        content = b"numpy==1.26.0\n"
        expected = hashlib.sha256(content).hexdigest()

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "requirements_lock.txt"
            lock_path.write_bytes(content)
            result = snap._capture_lock_files(tmpdir)

        assert result.get("pip") == expected

    def test_missing_lock_files_not_in_result(self):
        snap = _snap()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = snap._capture_lock_files(tmpdir)
        assert "pip" not in result
        assert "dpkg" not in result


# ---------------------------------------------------------------------------
# _capture_host
# ---------------------------------------------------------------------------


class TestCaptureHost:
    """Tests for the internal _capture_host helper."""

    def test_returns_dict(self):
        snap = _snap()
        result = snap._capture_host()
        assert isinstance(result, dict)

    def test_texlive_key_present(self):
        snap = _snap()
        result = snap._capture_host()
        assert "texlive" in result

    def test_imagemagick_key_present(self):
        snap = _snap()
        result = snap._capture_host()
        assert "imagemagick" in result

    def test_values_have_installed_key(self):
        snap = _snap()
        result = snap._capture_host()
        for pkg_name, info in result.items():
            assert "installed" in info, f"Missing 'installed' in {pkg_name}"

    def test_installed_values_are_bool(self):
        snap = _snap()
        result = snap._capture_host()
        for pkg_name, info in result.items():
            assert isinstance(info["installed"], bool), (
                f"'installed' is not bool in {pkg_name}"
            )


# EOF
