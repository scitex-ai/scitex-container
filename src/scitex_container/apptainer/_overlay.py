#!/usr/bin/env python3
# Timestamp: "2026-07-18"
# File: src/scitex_container/apptainer/_overlay.py
"""Overlay-lifecycle primitives for the SIF+overlay migration.

This is the UNWIRED overlay-lifecycle module: a standalone create /
destroy / measure surface for per-user apptainer overlay images. It is
deliberately not imported by ``_command_builder`` or any Django code yet —
Increment 1 taught ``build_exec_args`` to accept an ``overlay_path``; this
increment provides the primitives that manage that image's whole life.

Overlay model (operator-designed SIF+overlay architecture):

- A single read-only base SIF is shared by every session.
- Each user gets their own writable ``--overlay <image>`` layer.
- A VISITOR overlay is ephemeral (created on arrival, destroyed on
  teardown); signing in PROMOTES it to a persistent USER overlay.
- Billing meters the persistent overlay by its on-disk size
  (``size_bytes``), so the meter must be loud about a missing image
  rather than silently reporting 0.

All configuration is passed as explicit function parameters so this
module has no dependency on Django settings or any project-specific
config files, matching the pure-builder + thin-action convention in
``_command_builder``.
"""

from __future__ import annotations

import logging
import math
import subprocess
from pathlib import Path

from scitex_container._compat import supports_return_as

logger = logging.getLogger(__name__)


@supports_return_as
def build_overlay_create_command(
    overlay_path: str | Path,
    size_mb: int,
    headroom_frac: float = 0.06,
) -> list[str]:
    """Build the ``apptainer overlay create`` argument list (pure, no subprocess).

    The requested ``size_mb`` is the user's intended USABLE quota. fuse-overlayfs
    imposes a few percent of filesystem overhead, so the image is created
    slightly larger — ``size_mb`` inflated by ``headroom_frac`` and rounded UP —
    so that after the overhead the usable space is approximately ``size_mb``.

    Parameters
    ----------
    overlay_path : str or Path
        Destination path for the overlay image file.
    size_mb : int
        Intended usable quota in megabytes (before headroom inflation).
    headroom_frac : float
        Fractional headroom added on top of ``size_mb`` to absorb
        fuse-overlayfs overhead. Defaults to ``0.06`` (~6%).

    Returns
    -------
    list[str]
        ``["apptainer", "overlay", "create", "--size", <effective_mb>,
        <overlay_path>]``, where ``<effective_mb>`` is the inflated,
        rounded-up size as a string.
    """
    # round() before ceil() neutralises IEEE-754 noise so an exact percentage
    # does not jitter the quota by 1 MB (e.g. 200 * 1.10 == 220.00000000000003,
    # whose bare ceil would wrongly be 221). Six decimals preserve any genuine
    # sub-MB fraction, which still ceils up as intended.
    effective_mb = math.ceil(round(size_mb * (1.0 + headroom_frac), 6))
    return [
        "apptainer",
        "overlay",
        "create",
        "--size",
        str(effective_mb),
        str(overlay_path),
    ]


def create_overlay(
    overlay_path: str | Path,
    size_mb: int,
    headroom_frac: float = 0.06,
) -> Path:
    """Create a per-user overlay image (thin action over the pure builder).

    Ensures the parent directory exists, builds the command via
    :func:`build_overlay_create_command`, and runs it. No silent fallback:
    a nonzero return code raises with the captured stderr in the message.

    Parameters
    ----------
    overlay_path : str or Path
        Destination path for the overlay image file.
    size_mb : int
        Intended usable quota in megabytes (before headroom inflation).
    headroom_frac : float
        Fractional headroom passed through to the builder. Defaults to ``0.06``.

    Returns
    -------
    Path
        The overlay image path, on success.

    Raises
    ------
    RuntimeError
        If ``apptainer overlay create`` exits nonzero. The message includes
        the captured stderr.
    """
    overlay_path = Path(overlay_path)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_overlay_create_command(
        overlay_path,
        size_mb,
        headroom_frac=headroom_frac,
    )
    logger.info("Creating overlay: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"apptainer overlay create failed (rc={result.returncode}) "
            f"for {overlay_path}: {result.stderr.strip()}"
        )
    return overlay_path


def destroy_overlay(overlay_path: str | Path) -> bool:
    """Remove an overlay image file. Idempotent.

    Parameters
    ----------
    overlay_path : str or Path
        Path to the overlay image file.

    Returns
    -------
    bool
        ``True`` if the image existed and was removed, ``False`` if it was
        already absent.
    """
    overlay_path = Path(overlay_path)
    existed = overlay_path.exists()
    overlay_path.unlink(missing_ok=True)
    if existed:
        logger.info("Destroyed overlay: %s", overlay_path)
    return existed


def size_bytes(overlay_path: str | Path) -> int:
    """Return the on-disk size of an overlay image in bytes (the billing meter).

    Parameters
    ----------
    overlay_path : str or Path
        Path to the overlay image file.

    Returns
    -------
    int
        Size of the overlay image in bytes.

    Raises
    ------
    FileNotFoundError
        If the overlay image does not exist. Deliberately loud — the billing
        meter must never silently report 0 for a missing image.
    """
    overlay_path = Path(overlay_path)
    if not overlay_path.exists():
        raise FileNotFoundError(
            f"Overlay image not found (cannot meter size): {overlay_path}"
        )
    return overlay_path.stat().st_size


# EOF
