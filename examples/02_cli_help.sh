#!/usr/bin/env bash
# Timestamp: "2026-03-14"
# File: examples/02_cli_help.sh
# Author: ywatanabe
#
# Show the full recursive CLI help for scitex-container, covering all
# subcommands and subgroups in one pass.
#
# Runs: scitex-container --help-recursive

set -euo pipefail

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Print recursive CLI help for every scitex-container command and subcommand.

Runs: scitex-container --help-recursive

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

echo "=== scitex-container: recursive CLI help ==="
echo ""
echo "Command: scitex-container --help-recursive"
echo ""

# --help-recursive exits with 0; the set -e flag is safe here.
scitex-container --help-recursive || true

# EOF
