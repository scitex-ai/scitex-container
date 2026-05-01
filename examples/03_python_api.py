#!/usr/bin/env python3
"""Demonstrate scitex_container Python API usage.

Shows version, module structure, and available functions. Actual container
operations (build, sandbox, etc.) require Apptainer or Docker to be installed
on the host; those sections use try/except so this script runs cleanly in
environments without container tools.

Output artifacts are written to ``CONFIG.SDIR_RUN/`` (managed by stx.session).

Usage:
    python 03_python_api.py
"""

import inspect
import json
import shutil
from pathlib import Path

import scitex as stx
import scitex_container


def _describe(report, mod, logger):
    for name in sorted(mod.__all__):
        obj = getattr(mod, name, None)
        if obj is None:
            continue
        if callable(obj) and not isinstance(obj, type):
            try:
                sig_str = str(inspect.signature(obj))
            except (ValueError, TypeError):
                sig_str = "()"
            doc = inspect.getdoc(obj) or ""
            first_line = doc.split("\n")[0].strip() if doc else ""
            logger.info(f"  {name}{sig_str}")
            if first_line:
                logger.info(f"    {first_line}")
            report[name] = {"signature": sig_str, "doc": first_line}
        elif isinstance(obj, type):
            logger.info(f"  {name}  [class]")
            report[name] = {"kind": "class"}
        else:
            logger.info(f"  {name} = {obj!r}")
            report[name] = {"value": repr(obj)}


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrate scitex_container Python API usage."""
    out_dir = Path(CONFIG.SDIR_RUN)
    out_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Version and top-level structure
    # -----------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("scitex_container Python API demo")
    logger.info("=" * 60)
    logger.info("")

    logger.info(f"Version : {scitex_container.__version__}")
    logger.info(f"Package : {scitex_container.__file__}")
    logger.info("")

    # -----------------------------------------------------------------------
    # List modules exposed by the top-level package
    # -----------------------------------------------------------------------
    logger.info("Top-level public names:")
    for name in scitex_container.__all__:
        obj = getattr(scitex_container, name)
        if inspect.ismodule(obj):
            logger.info(f"  {name}  [module]")
        elif callable(obj):
            try:
                sig = inspect.signature(obj)
            except (ValueError, TypeError):
                sig = "()"
            logger.info(f"  {name}{sig}")
        else:
            logger.info(f"  {name} = {obj!r}")
    logger.info("")

    # -----------------------------------------------------------------------
    # Enumerate the apptainer sub-module
    # -----------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("scitex_container.apptainer - functions and constants:")
    logger.info("-" * 60)
    apptainer_report: dict = {}
    _describe(apptainer_report, scitex_container.apptainer, logger)
    logger.info("")

    # -----------------------------------------------------------------------
    # Enumerate the docker sub-module
    # -----------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("scitex_container.docker - functions:")
    logger.info("-" * 60)
    docker_report: dict = {}
    _describe(docker_report, scitex_container.docker, logger)
    logger.info("")

    # -----------------------------------------------------------------------
    # Enumerate the host sub-module
    # -----------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("scitex_container.host - functions and constants:")
    logger.info("-" * 60)
    host_report: dict = {}
    _describe(host_report, scitex_container.host, logger)
    logger.info("")

    # -----------------------------------------------------------------------
    # Optional: probe for Apptainer availability (no container op, just detection)
    # -----------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Container tool detection:")
    logger.info("-" * 60)
    try:
        cmd = scitex_container.apptainer.detect_container_cmd()
        logger.info(f"  Apptainer command detected: {cmd!r}")
    except Exception as exc:
        logger.info(f"  Apptainer not detected: {exc}")

    # Docker: check via shutil.which since there is no dedicated detector
    docker_bin = shutil.which("docker")
    logger.info(f"  Docker binary: {docker_bin or 'not found'}")
    logger.info("")

    # -----------------------------------------------------------------------
    # Save API report as JSON artifact
    # -----------------------------------------------------------------------
    report = {
        "version": scitex_container.__version__,
        "apptainer": apptainer_report,
        "docker": docker_report,
        "host": host_report,
    }
    report_path = out_dir / "api_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    logger.info(f"API report written to: {report_path}")

    return 0


if __name__ == "__main__":
    main()
