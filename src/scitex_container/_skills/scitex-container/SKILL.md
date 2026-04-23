---
description: Unified container management for Apptainer/Singularity + Docker — 14 MCP tools for the reproducible-science lifecycle. `container_*` (build SIF from .def, list, switch active container, rollback to prior version, deploy, cleanup old images, status, verify SHA256 + .def origin + lock file, env_snapshot for lock/freeze), `sandbox_create` (writable Apptainer sandbox), `docker_rebuild` / `docker_restart` (dev/prod compose envs), `host_install` / `host_check` (install Apptainer/Docker on the host, probe versions). Python API — submodules `apptainer`, `docker`, `host` + `env_snapshot()` (pip freeze + conda list + apt + system info captured into a reproducible lock). Drop-in replacement for hand-rolled `apptainer build/exec` shell loops, manual `docker compose up -d --build` scripts, `pip freeze > requirements.txt` + `conda env export` + `dpkg -l` combined-by-hand provenance, and ad-hoc SIF versioning. Use whenever the user asks to "build an Apptainer SIF", "rebuild Docker containers", "snapshot my environment", "rollback to a previous container", "check host container setup", "verify SIF integrity", "install Apptainer on this machine", "create a writable sandbox", "freeze my dependencies with system state", "deploy a container for SLURM/HPC", or mentions SIF, Apptainer, Singularity, Docker compose, Dockerfile, .def file, lock file, env_snapshot, reproducible environment.
allowed-tools: mcp__scitex__container_*, mcp__scitex__sandbox_*, mcp__scitex__docker_*, mcp__scitex__host_*
---

# scitex-container Skills Index

## Installation & import (two equivalent paths)

The same module is reachable via two install paths. Both forms work at
runtime; which one a user has depends on their install choice.

```python
# Standalone — pip install scitex-container
import scitex_container
scitex_container.env_snapshot(...)

# Umbrella — pip install scitex
import scitex.container
scitex.container.env_snapshot(...)
```

`pip install scitex-container` alone does NOT expose the `scitex` namespace;
`import scitex.container` raises `ModuleNotFoundError`. To use the
`scitex.container` form, also `pip install scitex`.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and empirical verification table.

## Sub-skills

### Core
- [01_quick-start.md](01_quick-start.md) — Basic usage
- [02_python-api.md](02_python-api.md) — Python API reference

### Workflows
- [10_cli-reference.md](10_cli-reference.md) — CLI commands
- [11_mcp-tools.md](11_mcp-tools.md) — MCP tools for AI agents

### Standards
- [20_environment.md](20_environment.md) — Environment variables
