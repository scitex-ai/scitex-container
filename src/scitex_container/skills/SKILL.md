---
name: scitex-container
description: Unified container management for Apptainer and Docker - build, run, push, and manage containers for reproducible research. Use when working with containers for HPC or reproducible environments.
allowed-tools: mcp__scitex__container_*
---

# Container Management with scitex-container

## Quick Start

```bash
# Build container
scitex-container build ./Singularity.def -o container.sif

# Run in container
scitex-container run container.sif python train.py

# Push to registry
scitex-container push container.sif oras://registry/image:tag
```

## CLI Commands

```bash
# Build
scitex-container build <def-file> [-o output.sif]
scitex-container build --docker Dockerfile [-o output.sif]

# Run
scitex-container run <container> <command>
scitex-container exec <container> <command>
scitex-container shell <container>

# Registry
scitex-container push <container> <target>
scitex-container pull <source> [-o output.sif]

# Info
scitex-container inspect <container>
scitex-container list

# Skills
scitex-container skills list
```

## Supported Runtimes

| Runtime | Build | Run | Push/Pull |
|---------|:---:|:---:|:---:|
| Apptainer/Singularity | Yes | Yes | ORAS |
| Docker | Yes | Yes | Docker Hub |
