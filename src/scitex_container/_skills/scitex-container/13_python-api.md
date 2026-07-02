---
description: |
  [TOPIC] Python API Reference — apptainer module
  [DETAILS] Python API reference for scitex-container — apptainer module (build/freeze/verify/status, SIF versioning, utilities).
tags: [scitex-container-python-api]
---

# Python API Reference — apptainer module

```python
import scitex_container.apptainer as apptainer
```

See also:
- [14_python-api-sandbox.md](14_python-api-sandbox.md) — sandbox management
- [15_python-api-builders.md](15_python-api-builders.md) — SLURM / exec command builders
- [16_python-api-docker-host.md](16_python-api-docker-host.md) — docker, host, top-level

---

## Build / freeze / verify / status

### build

```python
apptainer.build(
    def_name: str = "scitex-cloud-shared-v0.1.0",
    output_dir: str | Path | None = None,
    force: bool = False,
    sandbox: bool = False,
    *,
    def_path: str | Path | None = None,   # explicit .def path (bypasses lookup)
    image_name: str | None = None,        # image/subdir stem (defaults to def stem)
    use_sudo: bool = False,
    fakeroot: bool | None = None,         # default: True for sandbox, False for SIF
    cwd: str | Path | None = None,        # build context; defaults to output_dir
    retain: int | None = None,            # previous SIFs kept for rollback
) -> Path
```

Build an Apptainer SIF or sandbox directory from a `.def` file. This is
the single safe-build entrypoint — it never overwrites a live image in
place. Auto-detects the containers dir (or use `def_path`), auto-freezes
lock files after SIF builds, and skips the rebuild when the recipe hash
is unchanged (override with `force`). Raises `FileNotFoundError` if the
`.def` is not found; `RuntimeError` on build failure.

**Atomic build (SIF).** The image is built into a fresh timestamped
`<output_dir>/<name>/<name>-<ts>.sif`; on success two stable symlinks are
repointed atomically (temp symlink + `os.replace`):

- `<output_dir>/<name>/<name>.sif` → the inner **boot path** consumers use
- `<output_dir>/<name>.sif` → the top-level path for cross-layer
  `From: ./<name>.sif` (`Bootstrap: localimage`) references

A failed build raises **before** any swap, so the previous symlinks and
their target stay intact (rollback = repoint at a retained older `<ts>`;
see `list_builds`). Returns the resolved real `<name>-<ts>.sif`.

**`cwd`** is the build context apptainer resolves the recipe's relative
`%files` sources and `From: ./<other>.sif` against — settable
independently of where the SIF lands (e.g. stage `%files` in one dir,
publish the SIF in another). Defaults to `output_dir`.

**`retain`** keeps that many *previous* timestamped SIFs (the live build
is always kept, so `retain=N` leaves up to `N + 1` on disk); older ones
are pruned after a successful build. Defaults to the image config's
`retain`. SIF builds only.

Sandbox builds (`sandbox=True`) are built in place (not atomically
swappable) and still honour `cwd`.

### freeze

```python
apptainer.freeze(
    sif_path: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Path]
```

Extract pinned versions from a built SIF.
Returns `{"pip": Path, "dpkg": Path, "node": Path}` for available lock files.

### verify

```python
apptainer.verify(
    sif_path: str | Path,
    def_path: str | Path | None = None,
    lock_dir: str | Path | None = None,
) -> dict
```

Verify SIF integrity: SHA256, `.def` origin hash, pip/dpkg lock consistency.
Returns `{"sif": {...}, "def_origin": {...}, "pip_lock": {...}, "dpkg_lock": {...}, "overall": "pass|fail"}`.

### status

```python
apptainer.status(
    containers_dir: str | Path | None = None,
) -> list[dict]
```

List containers and their status (needs_rebuild flag).
Returns list of dicts with keys: `name`, `def_path`, `sif_path`, `sif_size`, `sif_date`, `hash_current`, `hash_stored`, `needs_rebuild`.

---

## SIF versioning

```python
apptainer.list_versions(containers_dir: Path) -> list[dict]
# Each dict: {"version", "path", "size", "date", "active"}

apptainer.get_active_version(containers_dir: Path) -> str | None
# Returns version string from current.sif symlink, or None

apptainer.switch_version(
    version: str,
    containers_dir: Path,
    use_sudo: bool = False,
) -> None

apptainer.rollback(
    containers_dir: Path,
    use_sudo: bool = False,
) -> str
# Returns the version string that is now active

apptainer.deploy(
    source_dir: Path,
    target_dir: Path = Path("/opt/scitex/singularity"),
) -> None
# Copy active SIF + base SIF to target_dir, recreate current.sif symlink

apptainer.cleanup(
    containers_dir: Path,
    keep: int = 3,
) -> list[Path]
# Remove old scitex-v*.sif files; never removes active version or base images
```

---

## Utilities

```python
apptainer.detect_container_cmd() -> str
# Returns "apptainer" or "singularity"; raises FileNotFoundError if neither found

apptainer.find_containers_dir() -> Path
# Auto-detects containers directory by walking up from cwd
```
