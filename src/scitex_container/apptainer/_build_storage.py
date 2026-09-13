#!/usr/bin/env python3
"""Resolve and validate host storage used by Apptainer builds."""

from __future__ import annotations

import os
import shutil
from collections.abc import Mapping
from pathlib import Path


class BuildStorageError(RuntimeError):
    """The selected container-build storage cannot safely hold the build."""


def prepare_build_environment(
    *,
    runtime: str,
    build_root: str | Path,
    minimum_tmp_bytes: int = 0,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return a validated subprocess environment for a container build.

    Explicit runtime-native overrides always win. Otherwise an explicit
    ``TMPDIR`` becomes the runtime temp root. With no override, both temp and
    cache storage live on the physical artifact filesystem, avoiding a small
    host ``/tmp`` or home filesystem by construction.

    ``minimum_tmp_bytes`` is a known lower bound, not an estimate. The
    reproducible replay supplies the size of its already-built SIF; Apptainer
    may require more because it constructs the image uncompressed.
    """
    env = dict(os.environ if environ is None else environ)
    prefix = (
        "SINGULARITY" if Path(runtime).name.startswith("singularity") else "APPTAINER"
    )
    tmp_key = f"{prefix}_TMPDIR"
    cache_key = f"{prefix}_CACHEDIR"

    artifact_root = Path(build_root).expanduser().resolve()
    private_root = (
        artifact_root
        / ".scitex-container"
        / f"user-{os.getuid()}"
        / "apptainer"
    )
    explicit_tmp = env.get(tmp_key) or env.get("TMPDIR")
    tmp_root = (
        Path(explicit_tmp).expanduser().resolve()
        if explicit_tmp
        else private_root / "tmp"
    )
    tmp_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    env[tmp_key] = str(tmp_root)

    explicit_cache = env.get(cache_key)
    cache_root = (
        Path(explicit_cache).expanduser().resolve()
        if explicit_cache
        else (
            tmp_root / f"scitex-container-user-{os.getuid()}-cache"
            if explicit_tmp
            else private_root / "cache"
        )
    )
    cache_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    env[cache_key] = str(cache_root)

    _validate_directory(tmp_key, tmp_root, minimum_tmp_bytes)
    _validate_directory(cache_key, cache_root, 0)
    return env


def _validate_directory(name: str, path: Path, minimum_free: int) -> None:
    if not path.is_dir() or not os.access(path, os.W_OK | os.X_OK):
        raise BuildStorageError(
            f"{name}={path} is not a writable directory; choose writable local "
            "storage with enough capacity for the uncompressed image"
        )
    free = shutil.disk_usage(path).free
    if free < minimum_free:
        raise BuildStorageError(
            f"{name}={path} has {_human_bytes(free)} free, below the known "
            f"minimum {_human_bytes(minimum_free)} for this build. Apptainer "
            "needs additional room for the uncompressed image and temporary "
            f"files; set {name} (or TMPDIR when no runtime override is set) "
            "to a larger local filesystem."
        )


def _human_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if amount < 1024 or unit == "PiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    raise AssertionError("unreachable")
