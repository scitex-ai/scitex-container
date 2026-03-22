---
name: scitex-container
description: Unified container management for Apptainer and Docker - build, run, push, sandbox management, and SLURM integration for reproducible research. Use when working with containers for HPC or reproducible environments.
allowed-tools: mcp__scitex__container_*
---

# Container Management with scitex-container

## Quick Start

```bash
# Build container from definition
scitex-container build ./Singularity.def -o container.sif

# Run command in container
scitex-container run container.sif python train.py

# Push to registry
scitex-container push container.sif oras://registry/image:tag
```

```python
from scitex_container import apptainer, docker

# List SIF versions
versions = apptainer.list_versions()

# Switch active version
apptainer.switch_version("v2.1")

# Freeze container metadata (hash, def, lock files)
apptainer.freeze("container.sif")

# Docker operations
docker.restart()
docker.status()
```

## Python API

### apptainer module

| Function | Purpose |
|----------|---------|
| `build_exec_args()` | Build Apptainer exec command with mounts |
| `build_host_mount_binds()` | Format host mount bindings |
| `build_sbatch_command()` | Build SLURM sbatch command with container |
| `build_srun_command()` | Build SLURM srun command with container |
| `build_shell_in_allocation_command()` | Shell command in SLURM allocation |
| `build_dev_pythonpath()` | Construct PYTHONPATH for development repos |
| `build_instance_start_script()` | Generate instance startup script |
| `detect_container_cmd()` | Detect Apptainer/Singularity CLI |
| `find_containers_dir()` | Auto-locate containers directory |
| `freeze()` | Capture SIF metadata (hash, .def, lock files) |
| `list_versions()` | List all SIF versions |
| `get_active_version()` | Get active SIF version |
| `switch_version()` | Switch active SIF version |
| `list_sandboxes()` | List all sandbox versions |
| `get_active_sandbox()` | Get active sandbox version |
| `switch_sandbox()` | Switch active sandbox |
| `rollback_sandbox()` | Roll back to previous sandbox |
| `sandbox_to_sif()` | Convert sandbox to SIF image |
| `sandbox_update()` | Update packages in sandbox |
| `sandbox_maintain()` | Run maintenance in sandbox with fakeroot |
| `sandbox_configure_ps1()` | Configure sandbox shell prompt |
| `cleanup_sandboxes()` | Remove old sandbox versions |
| `cleanup_sifs()` | Remove old SIF versions |
| `is_sandbox()` | Check if path is a sandbox |

### docker module

| Function | Purpose |
|----------|---------|
| `rebuild()` | Rebuild Docker images without cache |
| `restart()` | Restart Docker containers (compose down/up) |
| `status()` | Get Docker container status |
| `get_dev_mounts()` | Convert dev repo list to mount arguments |

### host module

| Function | Purpose |
|----------|---------|
| `get_mount_config()` | Get texlive/imagemagick mount configuration |
| `get_texlive_binds()` | Get TeXLive binary mount paths |

## CLI Commands

```bash
# Build & Run
scitex-container build <def-file> [-o output.sif]
scitex-container build --docker Dockerfile [-o output.sif]
scitex-container run <container> <command>
scitex-container exec <container> <command>
scitex-container shell <container>

# Registry
scitex-container push <container> <target>
scitex-container pull <source> [-o output.sif]

# Version management
scitex-container inspect <container>
scitex-container list
scitex-container freeze <sif_path> [--output <dir>]
scitex-container verify <sif_path> [--def <file>] [--lock-dir <dir>]

# Sandbox management
scitex-container sandbox create --source <path> [--dir <dir>]
scitex-container sandbox list [--dir <dir>]
scitex-container sandbox switch <version> [--dir <dir>]
scitex-container sandbox rollback [--dir <dir>]
scitex-container sandbox cleanup [--keep N] [--dir <dir>]
scitex-container sandbox update [--sandbox-dir <path>] [--pkg <pkg>]
scitex-container sandbox maintain [--sandbox-dir <path>] <command>
scitex-container sandbox configure-ps1 [--sandbox-dir <path>]
scitex-container sandbox purge-sifs [--dir <dir>] [--keep N]

# MCP server
scitex-container mcp start
scitex-container mcp list-tools
scitex-container mcp doctor
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `SCITEX_CLOUD_APPTAINER_PS1` | Override sandbox shell prompt |
| `SCITEX_CLOUD` | Set to `true` inside containers |
| `SCITEX_PROJECT` | Current project name in container |
| `SCITEX_USER` | Current username in container |

## MCP Tools (for AI agents)

| Tool | Purpose |
|------|---------|
| `container_build` | Build container from definition file |
| `container_list` | List container versions |
| `container_switch` | Switch active container version |
| `container_rollback` | Roll back to previous version |
| `container_deploy` | Deploy container to registry |
| `container_cleanup` | Remove old versions |
| `container_status` | Get container status |
| `container_verify` | Verify container integrity |
| `container_env_snapshot` | Capture environment metadata |
| `sandbox_create` | Create sandbox from SIF |
| `docker_rebuild` | Rebuild Docker images |
| `docker_restart` | Restart Docker containers |
| `host_install` | Install host dependencies |
| `host_check` | Check host requirements |

## Supported Runtimes

| Runtime | Build | Run | Push/Pull |
|---------|:---:|:---:|:---:|
| Apptainer/Singularity | Yes | Yes | ORAS |
| Docker | Yes | Yes | Docker Hub |
