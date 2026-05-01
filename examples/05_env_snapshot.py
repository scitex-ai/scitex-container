#!/usr/bin/env python3
"""Demonstrate scitex_container.env_snapshot().

``env_snapshot()`` captures a lightweight, JSON-serializable snapshot of the
current environment - container version, SIF hash, host package status,
dev-repo git commits, and lock-file hashes. It degrades gracefully when
container tools or git are absent.

Output artifacts are written to ``examples/05_env_snapshot_out/``.

Usage:
    python 05_env_snapshot.py
"""

import json
import logging
from pathlib import Path

import scitex_container

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    out_dir = Path(__file__).parent / "05_env_snapshot_out"
    out_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Basic snapshot (no arguments - auto-detects containers dir)
    # -----------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("env_snapshot() - basic (auto-detect containers dir)")
    logger.info("=" * 60)
    logger.info("")

    snap = scitex_container.env_snapshot()
    logger.info("%s", json.dumps(snap, indent=2))
    logger.info("")

    # -----------------------------------------------------------------------
    # Snapshot with explicit dev-repo paths
    # -----------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("env_snapshot() - with dev_repos argument")
    logger.info("=" * 60)
    logger.info("")

    # Use the package's own git repo as an example dev repo.
    package_dir = Path(scitex_container.__file__).parent.parent.parent

    try:
        snap_with_repos = scitex_container.env_snapshot(
            dev_repos=[package_dir],
        )
        logger.info("%s", json.dumps(snap_with_repos, indent=2))
        logger.info("")
    except Exception as exc:
        # env_snapshot is designed never to raise, but guard just in case.
        logger.info("env_snapshot raised unexpectedly: %s", exc)
        snap_with_repos = snap

    # -----------------------------------------------------------------------
    # Inspect snapshot structure
    # -----------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("Snapshot structure summary")
    logger.info("=" * 60)
    logger.info("")

    logger.info("  schema_version : %s", snap.get("schema_version", "N/A"))
    logger.info("  timestamp      : %s", snap.get("timestamp", "N/A"))

    container = snap.get("container", {})
    if container:
        logger.info("  container      :")
        for k, v in container.items():
            logger.info("    %s: %s", k, v)
    else:
        logger.info(
            "  container      : (not detected - Apptainer containers dir absent)"
        )

    host = snap.get("host", {})
    if host:
        logger.info("  host packages  :")
        for pkg, info in host.items():
            installed = info.get("installed", False)
            version = info.get("version", "")
            status = "installed" if installed else "missing"
            suffix = f" ({version})" if version else ""
            logger.info("    %s: %s%s", pkg, status, suffix)
    else:
        logger.info("  host packages  : (none detected)")

    dev_repos = snap_with_repos.get("dev_repos", [])
    if dev_repos:
        logger.info("  dev_repos      :")
        for repo in dev_repos:
            name = repo.get("name", "?")
            commit_raw = repo.get("commit")
            commit = commit_raw[:12] if commit_raw else "unknown"
            branch = repo.get("branch", "unknown")
            dirty_flag = " [dirty]" if repo.get("dirty", False) else ""
            logger.info("    %s: %s@%s%s", name, branch, commit, dirty_flag)
    else:
        logger.info("  dev_repos      : (none provided)")

    lock_files = snap.get("lock_files", {})
    if lock_files:
        logger.info("  lock_files     :")
        for lock_type, sha in lock_files.items():
            logger.info("    %s: %s...", lock_type, sha[:16])
    else:
        logger.info("  lock_files     : (none found)")

    logger.info("")

    # -----------------------------------------------------------------------
    # Save snapshots as JSON artifacts
    # -----------------------------------------------------------------------
    basic_path = out_dir / "snapshot_basic.json"
    basic_path.write_text(json.dumps(snap, indent=2))
    logger.info("Basic snapshot written to   : %s", basic_path)

    repos_path = out_dir / "snapshot_with_repos.json"
    repos_path.write_text(json.dumps(snap_with_repos, indent=2))
    logger.info("Dev-repos snapshot written to: %s", repos_path)

    return 0


if __name__ == "__main__":
    main()
