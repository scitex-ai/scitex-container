#!/usr/bin/env python3
"""Tests for deterministic container-build storage selection."""

from __future__ import annotations

import os


def _storage():
    from scitex_container.apptainer import _build_storage as storage

    return storage


def test_explicit_apptainer_tmpdir_wins_over_tmpdir(tmp_path):
    # Arrange
    native = tmp_path / "native"
    generic = tmp_path / "generic"

    # Act
    env = _storage().prepare_build_environment(
        runtime="apptainer",
        build_root=tmp_path / "artifacts",
        environ={"APPTAINER_TMPDIR": str(native), "TMPDIR": str(generic)},
    )

    # Assert
    assert env["APPTAINER_TMPDIR"] == str(native)


def test_tmpdir_is_promoted_to_apptainer_tmpdir(tmp_path):
    # Arrange
    scratch = tmp_path / "caller-scratch"

    # Act
    env = _storage().prepare_build_environment(
        runtime="apptainer",
        build_root=tmp_path / "artifacts",
        environ={"TMPDIR": str(scratch)},
    )

    # Assert
    assert env["APPTAINER_TMPDIR"] == str(scratch)


def test_default_storage_uses_physical_artifact_filesystem(tmp_path):
    # Arrange
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()

    expected = (
        artifacts.resolve()
        / ".scitex-container"
        / f"user-{os.getuid()}"
        / "apptainer"
    )

    # Act
    env = _storage().prepare_build_environment(
        runtime="apptainer", build_root=artifacts, environ={}
    )
    observed = (env["APPTAINER_TMPDIR"], env["APPTAINER_CACHEDIR"])

    # Assert
    assert observed == (str(expected / "tmp"), str(expected / "cache"))


def test_explicit_cache_override_is_preserved(tmp_path):
    # Arrange
    cache = tmp_path / "operator-cache"

    # Act
    env = _storage().prepare_build_environment(
        runtime="apptainer",
        build_root=tmp_path / "artifacts",
        environ={"APPTAINER_CACHEDIR": str(cache)},
    )

    # Assert
    assert env["APPTAINER_CACHEDIR"] == str(cache)


def test_singularity_uses_runtime_native_names(tmp_path):
    # Arrange
    scratch = tmp_path / "scratch"

    # Act
    env = _storage().prepare_build_environment(
        runtime="/usr/bin/singularity",
        build_root=tmp_path / "artifacts",
        environ={"TMPDIR": str(scratch)},
    )

    # Assert
    assert (env["SINGULARITY_TMPDIR"], "APPTAINER_TMPDIR" in env) == (
        str(scratch),
        False,
    )


def test_resolution_does_not_mutate_caller_environment(tmp_path):
    # Arrange
    caller = {"TMPDIR": str(tmp_path / "scratch")}

    # Act
    _storage().prepare_build_environment(
        runtime="apptainer", build_root=tmp_path / "artifacts", environ=caller
    )

    # Assert
    assert caller == {"TMPDIR": str(tmp_path / "scratch")}


def test_known_insufficient_capacity_fails_before_runtime(tmp_path):
    # Arrange
    storage = _storage()
    scratch = tmp_path / "small"

    # Act
    try:
        storage.prepare_build_environment(
            runtime="apptainer",
            build_root=tmp_path / "artifacts",
            minimum_tmp_bytes=10**30,
            environ={"APPTAINER_TMPDIR": str(scratch)},
        )
    except storage.BuildStorageError as error:
        observed = (
            "APPTAINER_TMPDIR=" in str(error),
            "known minimum" in str(error),
            "larger local filesystem" in str(error),
        )
    else:
        observed = (False, False, False)

    # Assert
    assert observed == (True, True, True)
