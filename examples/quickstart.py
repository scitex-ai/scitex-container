#!/usr/bin/env python3
"""Quickstart for scitex-container: import + show available submodules.

This script does NOT execute any container operations (which would require
Apptainer or Docker on the host). It only verifies the public API is importable.

Usage:
    python quickstart.py
"""

import logging

import scitex_container
from scitex_container import apptainer, docker, host

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    logger.info("scitex_container version: %s", scitex_container.__version__)
    logger.info(
        "top-level submodules: %s",
        [n for n in dir(scitex_container) if not n.startswith("_")],
    )

    def public(mod):
        return [n for n in dir(mod) if not n.startswith("_")]

    logger.info("")
    logger.info("apptainer API: %s", public(apptainer))
    logger.info("docker API:    %s", public(docker))
    logger.info("host API:      %s", public(host))

    # Pure helper - no shell calls
    binds = host.get_texlive_binds()
    logger.info("")
    logger.info(
        "host.get_texlive_binds() -> %s with %d entries",
        type(binds).__name__,
        len(binds),
    )

    return 0


if __name__ == "__main__":
    main()
