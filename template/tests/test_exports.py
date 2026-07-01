from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_support_export_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/export_support_context.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (ROOT / "exports" / "customer-support" / "example-orthopedic-dog-bed.json").exists()
