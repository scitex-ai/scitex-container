#!/usr/bin/env bash
# Timestamp: "2026-03-14"
# File: examples/01_list_python_apis.sh
# Author: ywatanabe
#
# Show available Python APIs in scitex_container (apptainer, docker, host modules)
# using the CLI command: scitex-container list-python-apis -vv

set -euo pipefail

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Show scitex_container Python API listing with full signatures and docstrings.

Runs: scitex-container list-python-apis -vv

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
# Main
# ---------------------------------------------------------------------------

echo "=== scitex-container: Python API listing ==="
echo ""
echo "Command: scitex-container list-python-apis -vv"
echo ""

scitex-container list-python-apis -vv

# EOF
