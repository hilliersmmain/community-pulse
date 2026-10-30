"""Tests for the demo_charts.py script that renders the documentation PNGs."""

import runpy
import sys
from pathlib import Path

import plotly.io as pio

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

EXPECTED_PNGS = [
    "attendance_histogram_enhanced.png",
    "attendance_trend_enhanced.png",
    "comparison_cleaned.png",
    "comparison_raw.png",
    "role_distribution_enhanced.png",
]


def test_script_writes_all_five_documentation_charts(tmp_path, monkeypatch):
    # The script writes to a relative demo_outputs/ directory and calls sys.exit(1) on any failure,
    # which would surface here as SystemExit. Image export is swapped for a recorder: what matters
    # is which files the script asks for, and rendering needs a Chrome binary.
    monkeypatch.chdir(tmp_path)
    written = []
    monkeypatch.setattr(pio, "write_image", lambda fig, path, **kwargs: written.append(str(path)))

    runpy.run_path(str(ROOT / "community_pulse" / "demo_charts.py"), run_name="__main__")

    assert (tmp_path / "demo_outputs").is_dir()
    assert sorted(written) == [f"demo_outputs/{name}" for name in EXPECTED_PNGS]
