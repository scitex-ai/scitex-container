#!/usr/bin/env python3
"""Regression test: importing conftest must not touch site-packages or env."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONFTEST_PATH = Path(__file__).resolve().parents[1] / "conftest.py"

_CHILD_CODE = """\
import os
import runpy
import site
import sys

os.environ["COVERAGE_PROCESS_START"] = "__SENTINEL_PROCESS_START__"
os.environ["COVERAGE_FILE"] = "__SENTINEL_COVERAGE_FILE__"

dirs = []
try:
    dirs.extend(site.getsitepackages())
except AttributeError:
    pass
try:
    dirs.append(site.getusersitepackages())
except AttributeError:
    pass

def _snapshot():
    snap = {}
    for d in dirs:
        try:
            snap[d] = sorted(os.listdir(d))
        except (FileNotFoundError, NotADirectoryError):
            snap[d] = None
    return snap

before = _snapshot()
runpy.run_path(sys.argv[1], run_name="conftest")
after = _snapshot()

assert before == after, f"site-packages changed: {[k for k in before if before.get(k) != after.get(k)]}"
assert os.environ.get("COVERAGE_PROCESS_START") == "__SENTINEL_PROCESS_START__", "COVERAGE_PROCESS_START was overwritten"
assert os.environ.get("COVERAGE_FILE") == "__SENTINEL_COVERAGE_FILE__", "COVERAGE_FILE was overwritten"
"""


def test_conftest_leaves_site_packages_untouched():
    # Arrange
    conftest = str(Path(__file__).resolve().parents[1] / "conftest.py")
    assert Path(conftest).is_file()
    cmd = [sys.executable, "-c", _CHILD_CODE, conftest]

    # Act
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    # Assert
    assert result.returncode == 0, (
        f"child failed with exit {result.returncode}\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )


# EOF
