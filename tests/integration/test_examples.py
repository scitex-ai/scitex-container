"""Smoke test for examples/quickstart.py only.

Per scitex-dev SciTeX standard (~/.dotfiles/skills/general — quickstart-only
contract), only quickstart.py must execute under the bare-package umbrella.
The other example scripts (03_python_api.py, 05_env_snapshot.py) are
allowed to opt into @stx.session and are validated by their own per-example
smoke tests under tests/examples/.
"""

import subprocess
import sys
from pathlib import Path

QUICKSTART = Path(__file__).resolve().parents[2] / "examples" / "quickstart.py"


def test_quickstart_smoke(tmp_path):
    assert QUICKSTART.is_file(), f"missing quickstart: {QUICKSTART}"
    r = subprocess.run(
        [sys.executable, str(QUICKSTART)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"quickstart.py failed: {r.stderr}"
