# SciTeX Container

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Unified container management for Apptainer and Docker</b></p>

<p align="center">
  <a href="https://badge.fury.io/py/scitex-container"><img src="https://badge.fury.io/py/scitex-container.svg" alt="PyPI version"></a>
  <a href="https://scitex-container.readthedocs.io/"><img src="https://readthedocs.org/projects/scitex-container/badge/?version=latest" alt="Documentation"></a>
  <a href="https://github.com/ywatanabe1989/scitex-container/actions/workflows/ci.yml"><img src="https://github.com/ywatanabe1989/scitex-container/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
</p>

<p align="center">
  <a href="https://scitex-container.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-container</code>
</p>

---

## Problem

Research computing environments depend on containers (Apptainer/Singularity for High-Performance Computing (HPC), Docker for cloud services), yet managing them involves disparate tools, manual version tracking, and no simple way to verify reproducibility. Switching between container runtimes, managing sandbox development, and keeping host-side dependencies aligned with container expectations are recurring pain points.

## Solution

`scitex-container` provides a single Python package with three interfaces — Python API, Command-Line Interface (CLI), and Model Context Protocol (MCP) server — to manage Apptainer and Docker containers uniformly. It handles building, versioning, sandboxing, host-package verification, and environment snapshots for reproducibility, all through one consistent interface.

## Installation

Requires Python >= 3.10.

```bash
pip install scitex-container
```

With MCP server support (for AI agent integration):

```bash
pip install scitex-container[mcp]
```

Full installation:

```bash
pip install scitex-container[all]
```

## Quick Start

```bash
# Unified status dashboard
scitex-container status

# Build Apptainer SIF from definition file
scitex-container build --def-name scitex-final

# Version management
scitex-container list
scitex-container switch 2.19.5
scitex-container rollback

# Show all commands
scitex-container --help-recursive
```

## Three Interfaces

### Python API

```python
import scitex_container

# Apptainer container management
scitex_container.apptainer.build(def_name="scitex-final", sandbox=True)
scitex_container.apptainer.list_versions(containers_dir="/opt/containers")
scitex_container.apptainer.switch_version("2.19.5", containers_dir="/opt/containers")
scitex_container.apptainer.rollback(containers_dir="/opt/containers")

# Host package management
scitex_container.host.check_packages()

# Docker operations
scitex_container.docker.rebuild(env="prod")
scitex_container.docker.restart(env="prod")

# Environment reproducibility snapshot
snapshot = scitex_container.env_snapshot()
```

<details>
<summary><strong>Verification API</strong></summary>

<br>

```python
from pathlib import Path
import scitex_container

# Verify container integrity
result = scitex_container.apptainer.verify(sif_path="/opt/containers/scitex-final.sif")
# Returns: {sif, def_origin, pip_lock, dpkg_lock, overall}

# Command builder for scitex-cloud terminal integration
args = scitex_container.apptainer.build_exec_args(
    container_path="/opt/containers/scitex-final.sif",
    username="user01",
    host_user_dir=Path("/data/users/user01"),
    host_project_dir=Path("/data/projects/proj01"),
    project_slug="proj01",
    texlive_prefix="/usr",
)
```

</details>

### CLI Commands

```bash
scitex-container status                 # Unified dashboard
scitex-container build scitex-final     # Build SIF
scitex-container list                   # List versions
scitex-container switch 2.19.5         # Switch version
scitex-container rollback              # Revert to previous
scitex-container verify                # Verify SIF integrity
scitex-container env-snapshot          # Reproducibility snapshot
```

<details>
<summary><strong>Sandbox Operations</strong></summary>

<br>

```bash
scitex-container sandbox create --sif scitex-final.sif
scitex-container sandbox maintain --sandbox scitex-sandbox/
```

</details>

<details>
<summary><strong>Host Package Management</strong></summary>

<br>

```bash
scitex-container host install          # Install TeX Live + ImageMagick
scitex-container host check            # Verify host packages
scitex-container host mounts           # Show configured bind mounts
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

### MCP Server

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
| `status` | Unified container/host status dashboard |
| `build` | Build SIF from definition file |
| `list` | List available container versions |
| `switch` | Switch active container version |
| `rollback` | Roll back to previous version |
| `sandbox_create` | Create writable sandbox from SIF |
| `docker_rebuild` | Rebuild Docker Compose services |
| `host_install` | Install host-side packages |
| `env_snapshot` | Capture reproducibility snapshot |
| `verify` | Verify SIF integrity against lock files |

## Part of SciTeX

scitex-container is part of [SciTeX](https://scitex.ai). When used inside the orchestrator package `scitex`, container operations integrate with the broader ecosystem — for example, `scitex-clew` can consume environment snapshots produced by `scitex-container` to track reproducibility provenance across experiments.

```python
import scitex_container

# Capture snapshot for Clew integration
snapshot = scitex_container.env_snapshot()
# snapshot includes: container version, SIF hash, lock files, host packages
```

The SciTeX ecosystem follows the Four Freedoms for researchers, inspired by [the Free Software Definition](https://www.gnu.org/philosophy/free-sw.en.html):

- **Freedom 0** — Run your research without restriction
- **Freedom 1** — Study and adapt the tools you depend on
- **Freedom 2** — Share your work and its infrastructure with colleagues
- **Freedom 3** — Improve the tools and share improvements with the community

---

> AGPL-3.0 — because research infrastructure deserves the same freedoms as the software it runs on.

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

<!-- EOF -->
