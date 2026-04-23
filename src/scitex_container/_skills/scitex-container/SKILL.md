---
description: Unified container management for Apptainer/Singularity and Docker — build SIFs, manage sandboxes, version/rollback, SLURM integration, freeze lock files, verify integrity, environment snapshots. Use when working with containers for HPC or reproducible environments.
allowed-tools: mcp__scitex__container_*, mcp__scitex__sandbox_*, mcp__scitex__docker_*, mcp__scitex__host_*
---

# scitex-container Skills Index

## Installation & import (two equivalent paths)

The same module is reachable via two install paths. Both forms work at
runtime; which one a user has depends on their install choice.

```python
# Standalone — pip install scitex-container
import scitex_container
scitex_container.build(...)

# Umbrella — pip install scitex
import scitex.container
scitex.container.build(...)
```

`pip install scitex-container` alone does NOT expose the `scitex` namespace;
`import scitex.container` raises `ModuleNotFoundError`. To use the
`scitex.container` form, also `pip install scitex`.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and empirical verification table.
