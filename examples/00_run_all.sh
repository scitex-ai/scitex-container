#!/usr/bin/env bash
# Timestamp: "2026-03-14"
# File: examples/00_run_all.sh
# Author: ywatanabe
#
# Run all scitex-container example scripts sequentially.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Run all scitex-container example scripts sequentially.

Options:
  -h, --help        Show this help message and exit
  --keep-going      Continue running remaining examples even if one fails
  --dry-run         Print the commands that would be run, without executing them

Examples:
  $(basename "$0")
  $(basename "$0") --keep-going
  $(basename "$0") --dry-run
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

KEEP_GOING=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
    -h | --help)
        usage
        exit 0
        ;;
    --keep-going)
        KEEP_GOING=true
        shift
        ;;
    --dry-run)
        DRY_RUN=true
        shift
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

PASS=0
FAIL=0

run_example() {
    local script="$1"
    local description="$2"
    local runner="$3" # "bash" or "python3"

    echo ""
    echo "================================================================"
    echo "Running: $description"
    echo "  Script : $script"
    echo "================================================================"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] Would run: $runner $script"
        return 0
    fi

    if $runner "$script"; then
        echo "[PASS] $description"
        PASS=$((PASS + 1))
    else
        local exit_code=$?
        echo "[FAIL] $description (exit code: $exit_code)" >&2
        FAIL=$((FAIL + 1))
        if [[ "$KEEP_GOING" != "true" ]]; then
            echo "Aborting. Use --keep-going to continue past failures." >&2
            exit "$exit_code"
        fi
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo "scitex-container examples — running all scripts"
echo "Script directory: $SCRIPT_DIR"

run_example "$SCRIPT_DIR/01_list_python_apis.sh" "List Python APIs" bash
run_example "$SCRIPT_DIR/02_cli_help.sh" "CLI recursive help" bash
run_example "$SCRIPT_DIR/03_python_api.py" "Python API demonstration" python3
run_example "$SCRIPT_DIR/04_mcp_tools.sh" "MCP tools inspection" bash
run_example "$SCRIPT_DIR/05_env_snapshot.py" "Environment snapshot" python3

echo ""
echo "================================================================"
echo "Summary: $PASS passed, $FAIL failed"
echo "================================================================"

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi

# EOF
