#!/usr/bin/env python3
# Timestamp: "2026-03-14"
# File: examples/03_python_api.py
# Author: ywatanabe
"""Demonstrate scitex_container Python API usage.

Shows version, module structure, and available functions.
Actual container operations (build, sandbox, etc.) require Apptainer or Docker
to be installed on the host; those sections use try/except so this script
runs cleanly in environments without container tools.

Output artifacts are written to examples/03_python_api_out/.
"""

import inspect
import json
import shutil
from pathlib import Path

import scitex_container

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

OUT_DIR = Path(__file__).parent / "03_python_api_out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Version and top-level structure
# ---------------------------------------------------------------------------

print("=" * 60)
print("scitex_container Python API demo")
print("=" * 60)
print()
print(f"Version : {scitex_container.__version__}")
print(f"Package : {scitex_container.__file__}")
print()

# ---------------------------------------------------------------------------
# List modules exposed by the top-level package
# ---------------------------------------------------------------------------

print("Top-level public names:")
for name in scitex_container.__all__:
    obj = getattr(scitex_container, name)
    if inspect.ismodule(obj):
        print(f"  {name}  [module]")
    elif callable(obj):
        try:
            sig = inspect.signature(obj)
        except (ValueError, TypeError):
            sig = "()"
        print(f"  {name}{sig}")
    else:
        print(f"  {name} = {obj!r}")
print()

# ---------------------------------------------------------------------------
# Enumerate the apptainer sub-module
# ---------------------------------------------------------------------------

print("-" * 60)
print("scitex_container.apptainer — functions and constants:")
print("-" * 60)

apptainer_report = {}
for name in sorted(scitex_container.apptainer.__all__):
    obj = getattr(scitex_container.apptainer, name, None)
    if obj is None:
        continue
    if callable(obj) and not isinstance(obj, type):
        try:
            sig_str = str(inspect.signature(obj))
        except (ValueError, TypeError):
            sig_str = "()"
        doc = inspect.getdoc(obj) or ""
        first_line = doc.split("\n")[0].strip() if doc else ""
        print(f"  {name}{sig_str}")
        if first_line:
            print(f"    {first_line}")
        apptainer_report[name] = {"signature": sig_str, "doc": first_line}
    elif isinstance(obj, type):
        print(f"  {name}  [class]")
        apptainer_report[name] = {"kind": "class"}
    else:
        print(f"  {name} = {obj!r}")
        apptainer_report[name] = {"value": repr(obj)}
print()

# ---------------------------------------------------------------------------
# Enumerate the docker sub-module
# ---------------------------------------------------------------------------

print("-" * 60)
print("scitex_container.docker — functions:")
print("-" * 60)

docker_report = {}
for name in sorted(scitex_container.docker.__all__):
    obj = getattr(scitex_container.docker, name, None)
    if obj is None:
        continue
    if callable(obj) and not isinstance(obj, type):
        try:
            sig_str = str(inspect.signature(obj))
        except (ValueError, TypeError):
            sig_str = "()"
        doc = inspect.getdoc(obj) or ""
        first_line = doc.split("\n")[0].strip() if doc else ""
        print(f"  {name}{sig_str}")
        if first_line:
            print(f"    {first_line}")
        docker_report[name] = {"signature": sig_str, "doc": first_line}
    else:
        print(f"  {name}  [other]")
        docker_report[name] = {"kind": "other"}
print()

# ---------------------------------------------------------------------------
# Enumerate the host sub-module
# ---------------------------------------------------------------------------

print("-" * 60)
print("scitex_container.host — functions and constants:")
print("-" * 60)

host_report = {}
for name in sorted(scitex_container.host.__all__):
    obj = getattr(scitex_container.host, name, None)
    if obj is None:
        continue
    if callable(obj) and not isinstance(obj, type):
        try:
            sig_str = str(inspect.signature(obj))
        except (ValueError, TypeError):
            sig_str = "()"
        doc = inspect.getdoc(obj) or ""
        first_line = doc.split("\n")[0].strip() if doc else ""
        print(f"  {name}{sig_str}")
        if first_line:
            print(f"    {first_line}")
        host_report[name] = {"signature": sig_str, "doc": first_line}
    elif isinstance(obj, type):
        print(f"  {name}  [class]")
        host_report[name] = {"kind": "class"}
    else:
        print(f"  {name} = {obj!r}")
        host_report[name] = {"value": repr(obj)}
print()

# ---------------------------------------------------------------------------
# Optional: probe for Apptainer availability (no container op, just detection)
# ---------------------------------------------------------------------------

print("-" * 60)
print("Container tool detection:")
print("-" * 60)

try:
    cmd = scitex_container.apptainer.detect_container_cmd()
    print(f"  Apptainer command detected: {cmd!r}")
except Exception as exc:
    print(f"  Apptainer not detected: {exc}")

# Docker: check via shutil.which since there is no dedicated detector

docker_bin = shutil.which("docker")
print(f"  Docker binary: {docker_bin or 'not found'}")
print()

# ---------------------------------------------------------------------------
# Save API report as JSON artifact
# ---------------------------------------------------------------------------

report = {
    "version": scitex_container.__version__,
    "apptainer": apptainer_report,
    "docker": docker_report,
    "host": host_report,
}

report_path = OUT_DIR / "api_report.json"
report_path.write_text(json.dumps(report, indent=2))
print(f"API report written to: {report_path}")

# EOF
