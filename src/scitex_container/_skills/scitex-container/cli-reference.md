# CLI Commands

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
