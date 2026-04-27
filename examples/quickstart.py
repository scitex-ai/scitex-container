#!/usr/bin/env python3
"""Quickstart for scitex-container: import + show available submodules.

This script does NOT execute any container operations (which would require
Apptainer or Docker on the host). It only verifies the public API is importable.
"""

import scitex_container
from scitex_container import apptainer, docker, host


def main() -> int:
    print(f"scitex_container version: {scitex_container.__version__}")
    print(
        f"top-level submodules: {[n for n in dir(scitex_container) if not n.startswith('_')]}"
    )

    def public(mod):
        return [n for n in dir(mod) if not n.startswith("_")]

    print(f"\napptainer API: {public(apptainer)}")
    print(f"docker API:    {public(docker)}")
    print(f"host API:      {public(host)}")

    # Pure helper - no shell calls
    binds = host.get_texlive_binds()
    print(
        f"\nhost.get_texlive_binds() -> {type(binds).__name__} with {len(binds)} entries"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
