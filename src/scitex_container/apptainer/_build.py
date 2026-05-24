#!/usr/bin/env python3
# Timestamp: "2026-05-12"
# File: src/scitex_container/apptainer/_build.py
"""Build Apptainer/Singularity SIF or sandbox from .def file.

Dir-per-image layout — every artifact for one ``<name>.def`` lives in
its own ``<out_dir>/<name>/`` subdir alongside a top-level symlink:

    containers/
    ├── <name>.def                      (the recipe — caller-managed input)
    ├── <name>.sif -> <name>/<name>.sif (convenience symlink)
    └── <name>/
        ├── <name>.sif                  (the built image)
        ├── <name>.def                  (snapshot of the recipe at build time)
        ├── <name>.build-YYYY-MMDD-HHMMSS.log  (full build log)
        └── .def-hash                   (sha256 of the recipe, for skip-rebuild)

The symlink lets recipes that say ``From: ./<base-name>.sif`` work
when the next layer builds from the containers dir as cwd, without
the recipe needing to know about the dir-per-image layout.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import logging
import shutil
import subprocess
from pathlib import Path

from scitex_container._compat import supports_return_as

from ._utils import detect_container_cmd, find_containers_dir

logger = logging.getLogger(__name__)


@supports_return_as
def build(
    def_name: str = "scitex-cloud-shared-v0.1.0",
    output_dir: str | Path | None = None,
    force: bool = False,
    sandbox: bool = False,
    *,
    def_path: str | Path | None = None,
    image_name: str | None = None,
    use_sudo: bool = False,
    fakeroot: bool | None = None,
) -> Path:
    """Build Apptainer/Singularity SIF or sandbox from .def file.

    Parameters
    ----------
    def_name : str
        Name of the .def file (without extension) when looking it up in
        the discovered containers dir. Ignored if ``def_path`` is given.
    output_dir : str or Path, optional
        Directory under which the per-image subdir is created (i.e.
        the artifact lands at ``<output_dir>/<image_name>/<image_name>.sif``).
        Defaults to the directory containing the resolved ``.def`` file.
    force : bool
        Force rebuild even if .def is unchanged.
    sandbox : bool
        If True, build a sandbox directory instead of a SIF image.
        Uses: apptainer build --sandbox --fakeroot output-sandbox/ input.def
    def_path : str or Path, optional
        Explicit path to the ``.def`` file. Lets out-of-tree callers
        (e.g. scitex-agent-container, whose recipes ship inside its
        own wheel) bypass ``find_containers_dir``. When given,
        ``def_name`` is ignored for lookup and ``image_name`` defaults
        to the .def's stem.
    image_name : str, optional
        Name of the per-image subdir + artifact stem (i.e. the artifact
        lands at ``<output_dir>/<image_name>/<image_name>.sif``).
        Defaults to ``def_name`` (or the .def stem when ``def_path``
        is given). Use this when the on-disk recipe is named
        differently from the image you want to produce — e.g. sac's
        ``apptainer-base.def`` → ``sac-base/sac-base.sif``.

    Returns
    -------
    Path
        Path to the built .sif file or sandbox directory.

    Raises
    ------
    FileNotFoundError
        If .def file or container command not found.
    RuntimeError
        If build fails.
    """
    cmd = detect_container_cmd()
    if def_path is not None:
        resolved_def = Path(def_path)
        if not resolved_def.is_absolute():
            resolved_def = Path.cwd() / resolved_def
    else:
        containers_dir = find_containers_dir()
        resolved_def = containers_dir / f"{def_name}.def"

    if not resolved_def.exists():
        raise FileNotFoundError(f"Definition file not found: {resolved_def}")

    name = image_name or (def_name if def_path is None else resolved_def.stem)
    out_dir = Path(output_dir) if output_dir else resolved_def.parent
    image_dir = out_dir / name
    image_dir.mkdir(parents=True, exist_ok=True)

    if sandbox:
        output_path = image_dir / f"{name}.sandbox"
        hash_file = image_dir / ".sandbox-hash"
    else:
        output_path = image_dir / f"{name}.sif"
        hash_file = image_dir / ".def-hash"

    current_hash = _hash_file(resolved_def)

    if not force and output_path.exists() and hash_file.exists():
        stored_hash = hash_file.read_text().strip()
        if current_hash == stored_hash:
            logger.info("Output is up-to-date (hash: %s...)", current_hash[:12])
            return output_path

    # Snapshot the recipe alongside the artifact so the build is
    # self-describing even if the source .def is later edited.
    shutil.copy2(resolved_def, image_dir / f"{name}.def")

    ts = _dt.datetime.now().strftime("%Y-%m%d-%H%M%S")
    log_path = image_dir / f"{name}.build-{ts}.log"

    # Default fakeroot policy: ON for sandbox builds (the original
    # behaviour; needed to chown files inside the sandbox tree as the
    # build user), OFF for SIF builds (apptainer's SIF format is
    # already rootless when the host has setuid-installed apptainer
    # OR the user passes ``--fakeroot`` explicitly). Caller can override.
    if fakeroot is None:
        fakeroot = sandbox

    privilege_args: list[str] = []
    if use_sudo:
        privilege_args.append("sudo")

    flag_args: list[str] = []
    if sandbox:
        flag_args += ["--sandbox"]
    if fakeroot:
        flag_args += ["--fakeroot"]
    flag_args += ["--force"]

    kind = "sandbox" if sandbox else "image"
    logger.info("Building %s %s from %s", kind, output_path.name, resolved_def.name)
    build_args = [
        *privilege_args,
        cmd,
        "build",
        *flag_args,
        str(output_path),
        str(resolved_def),
    ]

    logger.info("Build log → %s", log_path)
    # Recipes commonly reference ``./<other>.sif`` (resolved against
    # cwd) when layering on top of a prior build — running with the
    # containers dir as cwd keeps that working.
    with open(log_path, "wb") as log_fh:
        result = subprocess.run(
            build_args,
            cwd=str(out_dir),
            stdout=log_fh,
            stderr=subprocess.STDOUT,
        )
    if result.returncode != 0:
        raise RuntimeError(
            f"Build failed with exit code {result.returncode}; see {log_path}"
        )

    hash_file.write_text(current_hash + "\n")

    # Top-level symlink for cross-layer ``From: ./<name>.sif`` lookups
    # (and so existing tooling that points at <containers>/<name>.sif
    # keeps working through the layout change).
    if not sandbox:
        link = out_dir / f"{name}.sif"
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(Path(name) / f"{name}.sif")

    logger.info("Build complete: %s", output_path)

    # Auto-freeze lock files after a successful non-sandbox build
    if not sandbox:
        try:
            from ._freeze import freeze

            freeze(output_path, output_dir=out_dir)
            logger.info("Auto-freeze: lock files saved alongside SIF")
        except Exception as exc:
            logger.warning("Auto-freeze failed (non-fatal): %s", exc)

    return output_path


def _hash_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# EOF
