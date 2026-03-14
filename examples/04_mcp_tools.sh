#!/usr/bin/env bash
# Timestamp: "2026-03-14"
# File: examples/04_mcp_tools.sh
# Author: ywatanabe
#
# Inspect the scitex-container MCP (Model Context Protocol) integration.
#
# Runs:
#   scitex-container mcp list-tools -vv
#   scitex-container mcp doctor

set -euo pipefail

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Inspect the scitex-container MCP server: list registered tools and run
the health-check doctor command.

Runs:
  scitex-container mcp list-tools -vv
  scitex-container mcp doctor

Options:
  -h, --help    Show this help message and exit
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
    case "$1" in
    -h | --help)
        usage
        exit 0
        ;;
    *)
        echo "ERROR: Unknown option: $1" >&2
        usage >&2
        exit 1
        ;;
    esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

run_cmd() {
    local description="$1"
    shift
    echo ""
    echo "--- $description ---"
    echo "Command: $*"
    echo ""
    # Allow non-zero exit (doctor exits 1 when FastMCP is absent)
    "$@" || {
        local rc=$?
        echo ""
        echo "  (command exited with code $rc — FastMCP may not be installed)"
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo "=== scitex-container: MCP tools inspection ==="

run_cmd \
    "List all registered MCP tools (verbose with signatures and docstrings)" \
    scitex-container mcp list-tools -vv

run_cmd \
    "MCP doctor — health-check for FastMCP and tool registration" \
    scitex-container mcp doctor

echo ""
echo "=== Done ==="

# EOF
