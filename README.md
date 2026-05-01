# SciTeX Container

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-container.svg)](https://pypi.org/project/scitex-container/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-container.svg)](https://pypi.org/project/scitex-container/)
[![Tests](https://github.com/ywatanabe1989/scitex-container/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-container/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-container/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-container/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-container/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-container)
[![Docs](https://readthedocs.org/projects/scitex-container/badge/?version=latest)](https://scitex-container.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center">
  <a href="https://scitex-container.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-container</code>
</p>

---

## Problem and Solution

| # | Problem | Solution |
|---|---------|----------|
| 1 | **"Reproducible" containers drift** -- `Dockerfile` builds a different image each time because `apt-get install python3` floats | **Versioned SIF** -- `scitex-container build` pins the image content hash; `switch-version 2.19.5` is an atomic symlink flip |
| 2 | **Rollback requires docker tags + manual surgery** -- something breaks in prod; reverting to yesterday's container is 15 minutes of yak-shaving | **`rollback` is one command** -- previous active SIF restored; sandbox state preserved |
| 3 | **Paper "env" is `pip freeze`** -- useless without the python version, OS libs, CUDA driver | **`env_snapshot()`** -- full reproducibility capsule: container tag + pip freeze + conda env + apt packages + git commits, serialized as a single file for manuscript attachments |

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

## Four Interfaces

<details open>
<summary><strong>Python API</strong></summary>

<br>

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

</details>

<details>
<summary><strong>CLI Commands</strong></summary>

<br>

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
| `quick-start` | Install and first-use examples |
| `python-api` | Full Python API with signatures |
| `cli-reference` | CLI commands reference |
| `mcp-tools` | MCP tools for AI agents |
| `environment` | Environment variables |

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
