# SciTeX Container

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Unified container management for Apptainer/Singularity and Docker — versioned SIFs, atomic switch/rollback, and reproducible env snapshots.</b></p>

<p align="center">
  <a href="https://scitex-container.readthedocs.io/">Full Documentation</a> · <code>uv pip install scitex-container[all]</code>
</p>

<!-- scitex-badges:start -->
<p align="center">
  <a href="https://pypi.org/project/scitex-container/"><img src="https://img.shields.io/pypi/v/scitex-container?label=pypi" alt="pypi"></a>
  <a href="https://pypi.org/project/scitex-container/"><img src="https://img.shields.io/pypi/pyversions/scitex-container?label=python" alt="python"></a>
  <a href='https://scitex-container.readthedocs.io/en/latest/'><img src='https://img.shields.io/readthedocs/scitex-container?label=docs' alt='Read the Docs'></a>
  <a href="https://github.com/ywatanabe1989/scitex-container/actions/workflows/rtd-sphinx-build-on-ubuntu-latest.yml"><img src="https://img.shields.io/github/actions/workflow/status/ywatanabe1989/scitex-container/rtd-sphinx-build-on-ubuntu-latest.yml?branch=develop&label=docs" alt="docs"></a>
</p>
<p align="center">
  <a href="https://github.com/ywatanabe1989/scitex-container/actions/workflows/pytest-matrix-on-ubuntu-py3-11-3-12-3-13.yml"><img src="https://img.shields.io/github/actions/workflow/status/ywatanabe1989/scitex-container/pytest-matrix-on-ubuntu-py3-11-3-12-3-13.yml?branch=develop&label=tests" alt="tests"></a>
  <a href="https://github.com/ywatanabe1989/scitex-container/actions/workflows/import-smoke-on-ubuntu-py3-12.yml"><img src="https://img.shields.io/github/actions/workflow/status/ywatanabe1989/scitex-container/import-smoke-on-ubuntu-py3-12.yml?branch=develop&label=install-check" alt="install-check"></a>
  <a href="https://github.com/ywatanabe1989/scitex-container/actions/workflows/newb-docs-quality-on-ubuntu-latest.yml"><img src="https://img.shields.io/github/actions/workflow/status/ywatanabe1989/scitex-container/newb-docs-quality-on-ubuntu-latest.yml?branch=develop&label=quality" alt="quality"></a>
  <a href="https://codecov.io/gh/ywatanabe1989/scitex-container"><img src="https://img.shields.io/codecov/c/github/ywatanabe1989/scitex-container/develop?label=cov" alt="cov"></a>
</p>
<!-- scitex-badges:end -->

---

## Problem and Solution




| # | Problem | Solution |
|---|---------|----------|
| 1 | **"Reproducible" containers drift** -- `Dockerfile` builds a different image each time because `apt-get install python3` floats | **Versioned SIF** -- `scitex-container build` pins the image content hash; `switch-version 2.19.5` is an atomic symlink flip |
| 2 | **Rollback is one command** -- something breaks in prod; reverting to yesterday's container is 15 minutes of yak-shaving with docker tags and manual surgery | **`rollback` is one command** -- previous active SIF restored; sandbox state preserved |
| 3 | **Paper "env" is `pip freeze`** -- useless without the python version, OS libs, CUDA driver | **`env_snapshot()`** -- full reproducibility capsule: container tag + pip freeze + conda env + apt packages + git commits, serialized as a single file for manuscript attachments |

## Quick Start




```bash
# Unified status dashboard
scitex-container show-status

# Build Apptainer SIF from definition file
scitex-container apptainer build scitex-final

# Version management
scitex-container apptainer list
scitex-container apptainer switch 2.19.5
scitex-container apptainer rollback

# Show all commands
scitex-container --help-recursive
```

## Demo




```mermaid
sequenceDiagram
    participant U as user
    participant SC as scitex-container
    participant FS as /opt/containers
    U->>SC: apptainer build --def-name scitex-final
    SC->>FS: scitex-final.sif (pinned)
    U->>SC: apptainer switch 2.19.5
    SC->>FS: current.sif -> scitex-final-2.19.5.sif
    U->>SC: apptainer rollback
    SC->>FS: current.sif -> scitex-final-2.19.6.sif
    U->>SC: save-env-snapshot
    SC-->>U: snapshot.json (SIF hash + pip + dpkg + git + host)
```

<p align="center"><sub><b>Figure 2.</b> Typical session: build a pinned SIF, flip the active version, roll back on failure, and capture a reproducibility snapshot for the manuscript.</sub></p>

## Installation




```bash
uv pip install "scitex-container[all]"
```

Requires Python >= 3.10.

<details>
<summary><b>Per-module extras</b></summary>

<br>

| Extra | Pulls in |
|---|---|
| `mcp` | fastmcp (MCP server for agents) |
| `all` | `mcp` (recommended) |
| `dev` | pytest, pytest-cov, pytest-timeout + every optional dep so the test suite runs |
| `docs` | Sphinx + RTD theme + myst-parser (docs build only) |

```bash
uv pip install "scitex-container[mcp]"   # MCP server only
uv pip install -e ".[dev]"               # editable install for contributors
```

</details>

## Architecture




```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 40, 'curve': 'linear'}, 'themeVariables': {'fontSize': '12px'}}}%%
flowchart LR
    DEF[".def recipe"] --> BUILD["apptainer build"]
    BUILD --> SIF["scitex-v*.sif"]
    SIF --> FREEZE["freeze locks"]
    FREEZE --> VERIFY["verify gate"]
    VERIFY --> STORE["versioned store"]
    STORE --> SWITCH{"switch / rollback"}
    SWITCH --> ACTIVE["current.sif"]
    ACTIVE --> DEPLOY["deploy to prod"]
    ACTIVE --> SB["sandbox create"]
    SB --> MAINT["maintain / update"]
    MAINT --> SIF2["to-sif"]
```

<p align="center"><sub><b>Figure 1.</b> Reproducible container lifecycle: a .def recipe builds a pinned SIF, lock files freeze its contents, the verify gate checks integrity, the versioned store keeps history, and switch/rollback flips the active symlink atomically.</sub></p>

## Four Interfaces




<details open>
<summary><strong>Python API</strong></summary>

<br>

```python
import scitex_container as ctr

# Apptainer container management
ctr.apptainer.build(def_name="scitex-final", sandbox=True)
ctr.apptainer.list_versions(containers_dir="/opt/containers")
ctr.apptainer.switch_version("2.19.5", containers_dir="/opt/containers")
ctr.apptainer.rollback(containers_dir="/opt/containers")

# Reproducible build round-trip (rough build + freeze + lock + verify)
result = ctr.apptainer.build_reproducible(
    layer="sac-base",
    root="/opt/containers",
    def_path="recipes/apptainer-base.def",
)
print(f"Verified: {result.verified}")

# Use-time verify gate
status = ctr.apptainer.check_verified("/opt/containers/sac-base.sif")
print(f"State: {status.state}")

# Host package management
ctr.host.check_packages()

# Docker operations
ctr.docker.rebuild(env="prod")
ctr.docker.restart(env="prod")

# Environment reproducibility snapshot
snapshot = ctr.env_snapshot()
```

<details>
<summary><strong>Reproducible Build API</strong></summary>

<br>

```python
from pathlib import Path
import scitex_container

# Verify container integrity
result = scitex_container.apptainer.verify(
    sif_path="/opt/containers/scitex-final.sif"
)
# Returns: {sif, def_origin, pip_lock, dpkg_lock, overall}

# Full reproducible round-trip
rt_result = scitex_container.apptainer.build_reproducible(
    layer="sac-base",
    root="/opt/containers",
    def_name="apptainer-base",
    verify=True,
    keep=False,
)
# rt_result.verified is True/None; rt_result.diff shows any drift

# Use-time gate
status = scitex_container.apptainer.check_verified(
    "/opt/containers/sac-base.sif",
    require_verified=True,
)
```

### Build storage

Container builds do not silently depend on the host's `/tmp` or home
filesystem. `scitex-container` resolves Apptainer/Singularity build storage in
this order:

1. an explicit runtime override (`APPTAINER_TMPDIR` /
   `SINGULARITY_TMPDIR`),
2. an explicit `TMPDIR`,
3. scratch directories on the physical output-artifact filesystem.

Explicit `APPTAINER_CACHEDIR` / `SINGULARITY_CACHEDIR` values are also
preserved; otherwise the cache is colocated with the selected build storage.
The resolved paths are logged for every build and are preserved through
`sudo`. A reproducible verification also checks that its temp filesystem has
at least the rough SIF's size free before launching the replay. This is a
lower bound: Apptainer needs enough space for the whole uncompressed image and
temporary files.

</details>

</details>

<details>
<summary><strong>CLI Commands</strong></summary>

<br>

```bash
scitex-container show-status              # Unified dashboard
scitex-container apptainer build           # Build SIF from .def
scitex-container apptainer freeze          # Extract pip/dpkg/npm lock files
scitex-container apptainer list            # List versioned SIFs
scitex-container apptainer switch VERSION  # Switch active SIF version
scitex-container apptainer rollback        # Revert to previous version
scitex-container apptainer deploy          # Copy active SIF to production
scitex-container apptainer clean           # Remove old versions
scitex-container apptainer verify          # Verify SIF integrity
scitex-container save-env-snapshot         # Reproducibility snapshot
```

<details>
<summary><strong>Sandbox Operations</strong></summary>

<br>

```bash
scitex-container sandbox create --source scitex-final.sif
scitex-container sandbox maintain -s scitex-sandbox/ -- apt-get update
scitex-container sandbox list -d ./containers
scitex-container sandbox switch 20260301_120000
scitex-container sandbox rollback
scitex-container sandbox clean --keep 3
scitex-container sandbox update -s scitex-sandbox/
```

</details>

<details>
<summary><strong>Host Package Management</strong></summary>

<br>

```bash
scitex-container host install          # Install TeX Live + ImageMagick
scitex-container host check            # Verify host packages
scitex-container host show-mounts      # Show configured bind mounts
```

</details>

<details>
<summary><strong>Docker Operations</strong></summary>

<br>

```bash
scitex-container docker rebuild        # Rebuild Compose services
scitex-container docker restart        # Restart services
```

</details>

</details>

<details>
<summary><strong>MCP Server</strong></summary>

<br>

scitex-container exposes an MCP server so AI agents (Claude, etc.) can manage containers autonomously.

```bash
# Start MCP server
scitex-container-mcp

# Diagnostics and tool listing
scitex-container mcp doctor
scitex-container mcp list-tools -vv
```

| Tool | Description |
|------|-------------|
| `container_build` | Build SIF or sandbox from .def file |
| `container_list_versions` | List versioned SIFs with active marker |
| `container_switch` | Switch active SIF version |
| `container_rollback` | Roll back to previous SIF version |
| `container_deploy` | Copy active SIF to production target dir |
| `container_cleanup` | Remove old SIF versions (keep N most recent) |
| `container_verify` | Verify SIF SHA256, .def origin, and lock files |
| `container_status` | Unified dashboard: Apptainer + host + Docker |
| `container_env_snapshot` | Capture environment snapshot |
| `container_skills_get` | Get content of a bundled skill file |
| `container_skills_list` | List bundled skill files |
| `sandbox_create` | Convert SIF to writable timestamped sandbox |
| `docker_rebuild` | Rebuild Docker images without cache |
| `docker_restart` | Restart Docker containers |
| `host_install` | Install TeXLive / ImageMagick on the host |
| `host_check` | Check which host packages are installed |

</details>

<details>
<summary><strong>Skills</strong></summary>

<br>

Skills provide workflow-oriented guides that AI agents query to discover capabilities and usage patterns.

```bash
scitex-container skills list              # List available skill pages
scitex-container skills get SKILL         # Show main skill page
scitex-dev skills export --package scitex-container  # Export to Claude Code
```

| Skill | Content |
|-------|---------|
| `01_installation` | pip install + runtime deps + smoke verify |
| `02_quick-start` | Build a SIF + snapshot environment |
| `03_python-api` | Top-level Python surface (re-exports + submodules) |
| `04_cli-reference` | Full `scitex-container` subcommand surface |
| `11_mcp-tools` | MCP tools for AI agents |
| `20_environment` | Environment variables |

</details>

## Part of SciTeX




`scitex-container` is part of [**SciTeX**](https://scitex.ai). Install via
the umbrella with `pip install scitex[container]` to use as
`scitex.container` (Python) or `scitex container ...` (CLI).

```python
import scitex_container

# Capture snapshot for Clew integration
snapshot = scitex_container.env_snapshot()
# snapshot includes: container version, SIF hash, lock files, host packages
```

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

<!-- EOF -->
