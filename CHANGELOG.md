# Changelog

All notable changes to `scitex-container` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.0]

### Added

- `apptainer.build()` is now the SSOT for **safe SIF builds**: it builds
  into a fresh timestamped `<name>/<name>-<ts>.sif` and, on success,
  atomically repoints two stable symlinks (temp symlink + `os.replace`,
  via the new `_store.atomic_symlink` primitive) — the inner
  `<name>/<name>.sif` (the path consumers boot from) and the top-level
  `<name>.sif` (for cross-layer `From: ./<name>.sif`). A live image is
  never overwritten in place; a failed build leaves the prior symlinks
  and their targets intact.
- `build(..., cwd=...)`: explicit build context — the directory apptainer
  resolves the recipe's relative `%files` and `From: ./<other>.sif`
  against — settable independently of `output_dir` (defaults to
  `output_dir`, fully back-compatible).
- `build(..., retain=N)`: keep the last N *previous* timestamped SIFs for
  rollback (the live build is always kept). Defaults to the image
  config's `retain`; reuses `_store.prune`.
- `_store.atomic_symlink(link, rel_target)`: reusable atomic symlink-swap
  primitive; `point_latest` now builds on it.

### Changed

- A successful SIF `build()` returns the resolved real timestamped SIF
  (`<name>-<ts>.sif`); `<name>/<name>.sif` and `<name>.sif` are stable
  symlinks pointing at it. Consumers booting from the inner
  `<name>/<name>.sif` path are unaffected.

## [0.1.10]

- Initial CHANGELOG entry — see git log for prior history.
