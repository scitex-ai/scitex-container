---
description: |
  [TOPIC] scitex-container CLI Reference
  [DETAILS] Top-level subcommands of `scitex-container` — apptainer, docker, host, sandbox, save-env-snapshot, show-status, mcp.
tags: [scitex-container-cli-reference]
---

# CLI Reference

`scitex-container` is the entry point installed by
`pip install scitex-container`.

```text
scitex-container [OPTIONS] COMMAND [ARGS]...
```

## Top-level options

| Flag                | Purpose                                              |
|---------------------|------------------------------------------------------|
| `-V / --version`    | Show the version and exit                            |
| `--help-recursive`  | Show help for all commands recursively               |
| `--json`            | Emit machine-readable JSON output (where supported)  |
| `-h / --help`       | Show this message and exit                           |

## Configuration precedence

```
CLI flags  →  ./config.yaml  →  $SCITEX_CONTAINER_CONFIG
           →  ~/.scitex/container/config.yaml  →  built-in defaults
```

## Commands

| Command             | Purpose                                                  |
|---------------------|----------------------------------------------------------|
| `apptainer`         | Apptainer (SIF) container operations — build / freeze / verify / status / version / rollback / deploy |
| `docker`            | Manage Docker Compose services — rebuild / restart / status |
| `host`              | Host-side packages + mount configuration — check / install |
| `sandbox`           | Manage Apptainer sandbox directories                     |
| `save-env-snapshot` | Capture environment snapshot for reproducibility (YAML)  |
| `show-status`       | Unified status dashboard (Apptainer + host + Docker)     |
| `mcp`               | MCP (Model Context Protocol) server management           |
| `list-python-apis`  | List public Python APIs                                  |

## Companion entry point

`pip install 'scitex-container[mcp]'` also installs:

| Console script             | Purpose                                       |
|----------------------------|-----------------------------------------------|
| `scitex-container-mcp`     | Standalone MCP server (14 tools)              |

## Examples

```bash
# Apptainer lifecycle
scitex-container apptainer build env.def env.sif
scitex-container apptainer freeze env.sif env.lock.yaml
scitex-container apptainer verify env.sif env.lock.yaml
scitex-container apptainer status env.sif

# Sandbox
scitex-container sandbox create ./mysandbox env.sif
scitex-container sandbox shell ./mysandbox

# Docker (workstation)
scitex-container docker rebuild
scitex-container docker restart

# Host setup + status
scitex-container host check
scitex-container host install --runtime apptainer
scitex-container show-status

# Reproducibility snapshot
scitex-container save-env-snapshot ./snapshots/today.yaml
```

## See also

- `17_cli-reference-detailed.md` — historical detailed CLI reference
- `11_mcp-tools.md` — MCP tool surface for AI agents
- `20_environment.md` — environment variables
