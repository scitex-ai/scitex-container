---
description: |
  [TOPIC] scitex-container Python API
  [DETAILS] Top-level public surface — submodules (apptainer/docker/host), env_snapshot, plus MCP-parity re-exports (build, status, verify, sandbox_create, etc.).
tags: [scitex-container-python-api]
---

# Python API

Top-level public surface re-exported from `scitex_container`.
Detailed per-area docs live in numbered companion leaves (13–16).

## Submodules

| Name        | Purpose                                                |
|-------------|--------------------------------------------------------|
| `apptainer` | Build, freeze, verify, version SIFs; sandbox; SLURM    |
| `docker`    | Compose-aware Docker host helpers                      |
| `host`      | Host runtime detection + install                       |

## Top-level callables

| Name             | Purpose                                                  |
|------------------|----------------------------------------------------------|
| `__version__`    | Installed package version                                |
| `env_snapshot()` | Capture OS / Python / pip-freeze / sys-pkg state to YAML |

## MCP-parity re-exports

These mirror the MCP tool surface so AI agents and Python users see the
same names. They dispatch to the appropriate submodule.

| Name                | Dispatches to                                       |
|---------------------|-----------------------------------------------------|
| `build()`           | `apptainer.build`                                   |
| `cleanup()`         | `apptainer.cleanup`                                 |
| `deploy()`          | `apptainer.deploy`                                  |
| `list_versions()`   | `apptainer.list_versions`                           |
| `rollback()`        | `apptainer.rollback`                                |
| `status()`          | `apptainer.status`                                  |
| `switch()`          | `apptainer.switch`                                  |
| `verify()`          | `apptainer.verify`                                  |
| `sandbox_create()`  | `apptainer.sandbox_create`                          |
| `docker_rebuild()`  | `docker.rebuild`                                    |
| `docker_restart()`  | `docker.restart`                                    |
| `host_check()`      | `host.check`                                        |
| `host_install()`    | `host.install`                                      |

## Example

```python
import scitex_container as ctr

ctr.host_check()                                  # detect runtimes
ctr.build("env.def", "env.sif")                   # build SIF
ctr.verify("env.sif", "env.lock.yaml")            # integrity check
ctr.env_snapshot("./snapshots/today.yaml")        # capture host state
```

## Detailed per-area references

- `13_python-api.md` — `apptainer` build/freeze/verify/status, SIF
  versioning, utilities
- `14_python-api-sandbox.md` — sandbox management & versioning
- `15_python-api-builders.md` — SLURM / exec command builders
- `16_python-api-docker-host.md` — `docker`, `host`, top-level
  `env_snapshot`
