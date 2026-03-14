#!/usr/bin/env python3
# Timestamp: "2026-03-14"
# File: examples/05_env_snapshot.py
# Author: ywatanabe
"""Demonstrate scitex_container.env_snapshot().

env_snapshot() captures a lightweight, JSON-serializable snapshot of the
current environment — container version, SIF hash, host package status,
dev-repo git commits, and lock-file hashes.  It degrades gracefully when
container tools or git are absent.

Output artifacts are written to examples/05_env_snapshot_out/.
"""

import json
from pathlib import Path

import scitex_container

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

OUT_DIR = Path(__file__).parent / "05_env_snapshot_out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Basic snapshot (no arguments — auto-detects containers dir)
# ---------------------------------------------------------------------------

print("=" * 60)
print("env_snapshot() — basic (auto-detect containers dir)")
print("=" * 60)
print()

snap = scitex_container.env_snapshot()
print(json.dumps(snap, indent=2))
print()

# ---------------------------------------------------------------------------
# Snapshot with explicit dev-repo paths
# ---------------------------------------------------------------------------

print("=" * 60)
print("env_snapshot() — with dev_repos argument")
print("=" * 60)
print()

# Use the package's own git repo as an example dev repo.
package_dir = Path(scitex_container.__file__).parent.parent.parent

try:
    snap_with_repos = scitex_container.env_snapshot(
        dev_repos=[package_dir],
    )
    print(json.dumps(snap_with_repos, indent=2))
    print()
except Exception as exc:
    # env_snapshot is designed never to raise, but guard just in case.
    print(f"env_snapshot raised unexpectedly: {exc}")
    snap_with_repos = snap

# ---------------------------------------------------------------------------
# Inspect snapshot structure
# ---------------------------------------------------------------------------

print("=" * 60)
print("Snapshot structure summary")
print("=" * 60)
print()

print(f"  schema_version : {snap.get('schema_version', 'N/A')}")
print(f"  timestamp      : {snap.get('timestamp', 'N/A')}")

container = snap.get("container", {})
if container:
    print(f"  container      :")
    for k, v in container.items():
        print(f"    {k}: {v}")
else:
    print("  container      : (not detected — Apptainer containers dir absent)")

host = snap.get("host", {})
if host:
    print(f"  host packages  :")
    for pkg, info in host.items():
        installed = info.get("installed", False)
        version = info.get("version", "")
        status = "installed" if installed else "missing"
        print(f"    {pkg}: {status}" + (f" ({version})" if version else ""))
else:
    print("  host packages  : (none detected)")

dev_repos = snap_with_repos.get("dev_repos", [])
if dev_repos:
    print("  dev_repos      :")
    for repo in dev_repos:
        name = repo.get("name", "?")
        commit = repo.get("commit", "unknown")[:12] if repo.get("commit") else "unknown"
        branch = repo.get("branch", "unknown")
        dirty = repo.get("dirty", False)
        dirty_flag = " [dirty]" if dirty else ""
        print(f"    {name}: {branch}@{commit}{dirty_flag}")
else:
    print("  dev_repos      : (none provided)")

lock_files = snap.get("lock_files", {})
if lock_files:
    print("  lock_files     :")
    for lock_type, sha in lock_files.items():
        print(f"    {lock_type}: {sha[:16]}...")
else:
    print("  lock_files     : (none found)")

print()

# ---------------------------------------------------------------------------
# Save snapshots as JSON artifacts
# ---------------------------------------------------------------------------

basic_path = OUT_DIR / "snapshot_basic.json"
basic_path.write_text(json.dumps(snap, indent=2))
print(f"Basic snapshot written to   : {basic_path}")

repos_path = OUT_DIR / "snapshot_with_repos.json"
repos_path.write_text(json.dumps(snap_with_repos, indent=2))
print(f"Dev-repos snapshot written to: {repos_path}")

# EOF
