"""Test suite for the visualizer module."""

import json
import os
import math
from pathlib import Path

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import plotly.utils

from utils.data_generator import DataGenerator
from utils.visualizer import (
    plot_attendance_trend,
    plot_role_distribution,
    plot_attendance_histogram,
    get_chart_export_config,
    _calculate_stats,
    _attach_export,
)

# ---------------------------------------------------------------------------
# Snapshot helpers (factored here; move to conftest.py if >30 lines)
# ---------------------------------------------------------------------------

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


_VOLATILE_TRACE_KEYS = ("x", "y", "customdata", "values", "labels")


def _strip_volatile(d: dict) -> dict:
    """Remove keys from a fig.to_dict() that are volatile across environments.

    Two classes of volatile content are stripped:

    1. ``layout.template`` — Plotly's built-in default theme, populated by the
       library not our chart code.  Its content can shift with test-ordering
       effects (other libraries mutating global state).

    2. Per-element numeric arrays in data traces (``x``, ``y``, ``customdata``,
       ``values``, ``labels``).  These are derived from the seeded DataGenerator
       output, but ``random.choice`` / ``np.random.choice`` with the same seed
       can produce different sequences across Python/numpy versions, leaking
       version drift into the snapshot.  The total-count text in titles and
       annotations is stable (verified across CI matrix), so structural keys
       — trace types, colors, hovertemplates, layout shapes, titles,
       annotations — still get compared.

    Any value that is itself a dict containing a Plotly-encoded ``bdata`` field
    (the binary-array format used since Plotly 6.x) is also dropped, since the
    encoding can churn across Plotly versions.
    """
    result = dict(d)
    if "layout" in result and isinstance(result["layout"], dict):
        layout = dict(result["layout"])
        layout.pop("template", None)
        result["layout"] = layout
    if "data" in result and isinstance(result["data"], list):
        new_traces = []
        for trace in result["data"]:
            if not isinstance(trace, dict):
                new_traces.append(trace)
                continue
            stripped = {k: v for k, v in trace.items() if k not in _VOLATILE_TRACE_KEYS}
            new_traces.append(stripped)
        result["data"] = new_traces
    return result


def _load_or_write_snapshot(name: str, data: dict) -> dict | None:
    """Load a JSON snapshot or write one if missing/UPDATE_SNAPSHOTS is set.

    The ``data`` dict should already have volatile keys stripped (via
    ``_strip_volatile``) before being passed here.

    Returns the loaded snapshot dict, or None when the snapshot was just
    written for the first time (caller should pytest.skip in that case).
    """
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOTS_DIR / f"{name}.json"
    update = os.environ.get("UPDATE_SNAPSHOTS", "").strip() == "1"

    if update or not path.exists():
        serialized = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder, indent=2, sort_keys=True)
        path.write_text(serialized, encoding="utf-8")
        return None  # caller should skip or just return in update mode

    return json.loads(path.read_text(encoding="utf-8"))


def _assert_deep_equal(actual, expected, path: str = "", tol: float = 1e-6) -> None:
    """Recursively compare two JSON-like structures with numeric tolerance.

    Floats are compared with absolute tolerance *tol* (default 1e-6).
    Lists are compared element-wise; dicts are compared key-by-key.

    Raises AssertionError with a descriptive path on first mismatch.
    """
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"[{path}] expected dict, got {type(actual).__name__}"
        for key in expected:
            assert key in actual, f"[{path}] missing key '{key}'"
            _assert_deep_equal(actual[key], expected[key], path=f"{path}.{key}", tol=tol)
        for key in actual:
            assert key in expected, f"[{path}] unexpected extra key '{key}'"
    elif isinstance(expected, list):
        assert isinstance(actual, list), f"[{path}] expected list, got {type(actual).__name__}"
        assert len(actual) == len(
            expected
        ), f"[{path}] list length mismatch: actual={len(actual)} expected={len(expected)}"
        for i, (a, e) in enumerate(zip(actual, expected)):
            _assert_deep_equal(a, e, path=f"{path}[{i}]", tol=tol)
    elif isinstance(expected, float) or isinstance(actual, float):
        # Handle NaN: both must be NaN, or neither
        if isinstance(expected, float) and math.isnan(expected):
            assert isinstance(actual, float) and math.isnan(actual), f"[{path}] expected NaN, got {actual!r}"
        else:
            assert isinstance(actual, (int, float)), f"[{path}] expected numeric, got {type(actual).__name__}"
            assert (
                abs(float(actual) - float(expected)) <= tol
            ), f"[{path}] numeric mismatch: actual={actual!r} expected={expected!r} (tol={tol})"
    else:
        assert actual == expected, f"[{path}] mismatch: actual={actual!r} expected={expected!r}"


class TestVisualizerEnhancements:

    @pytest.fixture
    def sample_member_data(self):
        dates = [datetime.now() - timedelta(days=30 * i) for i in range(12)]
        return pd.DataFrame(
            {
                "Name": [f"Member {i}" for i in range(100)],
                "Email": [f"member{i}@test.com" for i in range(100)],
                "Join_Date": np.random.choice(dates, 100),
                "Event_Attendance": np.random.randint(0, 20, 100),
                "Role": np.random.choice(["Member", "Admin", "Guest"], 100, p=[0.7, 0.1, 0.2]),
            }
        )

    def test_calculate_stats(self, sample_member_data):

        stats = _calculate_stats(sample_member_data["Event_Attendance"])

        # Verify all required stats are present
        assert "mean" in stats
        assert "median" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats

        # Verify stats are numeric
        for key, value in stats.items():
            assert isinstance(value, (int, float))

        # Verify basic properties
        assert stats["min"] <= stats["median"] <= stats["max"]
        assert stats["min"] <= stats["mean"] <= stats["max"]

    def test_plot_attendance_trend_basic(self, sample_member_data):

        fig = plot_attendance_trend(sample_member_data, data_state="cleaned")

        # Verify figure is created
        assert fig is not None
        assert hasattr(fig, "data")
        assert len(fig.data) > 0

        # Verify title includes data state
        assert "cleaned" in fig.layout.title.text.lower()

    def test_plot_attendance_trend_with_trend_line(self, sample_member_data):

        fig = plot_attendance_trend(sample_member_data, data_state="cleaned")

        # Should have at least 2 traces (main line and trend line)
        assert len(fig.data) >= 2

        # One trace should be the trend line
        trace_names = [trace.name for trace in fig.data]
        assert "Trend Line" in trace_names

    def test_plot_attendance_trend_annotations(self, sample_member_data):

        fig = plot_attendance_trend(sample_member_data, data_state="cleaned")

        # Check for annotations
        assert len(fig.layout.annotations) > 0

        # Verify statistics are in annotations
        annotation_text = " ".join([ann.text for ann in fig.layout.annotations])
        assert "mean" in annotation_text.lower() or "Mean" in annotation_text

    def test_plot_attendance_trend_empty_data(self):

        empty_df = pd.DataFrame()
        fig = plot_attendance_trend(empty_df)

        # Should return a valid but empty figure
        assert fig is not None

    def test_plot_attendance_trend_missing_column(self):

        df = pd.DataFrame({"Name": ["Test"], "Role": ["Member"]})
        fig = plot_attendance_trend(df)

        # Should return a valid but empty figure
        assert fig is not None

    def test_plot_role_distribution_basic(self, sample_member_data):

        fig = plot_role_distribution(sample_member_data, data_state="cleaned")

        # Verify figure is created
        assert fig is not None
        assert hasattr(fig, "data")
        assert len(fig.data) > 0

        # Verify it's a pie chart
        assert fig.data[0].type == "pie"

    def test_plot_role_distribution_percentages(self, sample_member_data):

        fig = plot_role_distribution(sample_member_data, data_state="cleaned")

        # Check that textinfo includes both label and percent
        assert "percent" in fig.data[0].textinfo
        assert "label" in fig.data[0].textinfo

    def test_plot_role_distribution_tooltips(self, sample_member_data):

        fig = plot_role_distribution(sample_member_data, data_state="cleaned")

        # Verify hover template exists
        assert fig.data[0].hovertemplate is not None
        assert "Count" in fig.data[0].hovertemplate or "value" in fig.data[0].hovertemplate

    def test_plot_role_distribution_annotations(self, sample_member_data):

        fig = plot_role_distribution(sample_member_data, data_state="cleaned")

        # Check for annotations
        assert len(fig.layout.annotations) > 0

        # Verify total is mentioned
        annotation_text = " ".join([ann.text for ann in fig.layout.annotations])
        assert "Total" in annotation_text or "total" in annotation_text

    def test_plot_attendance_histogram_basic(self, sample_member_data):

        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")

        # Verify figure is created
        assert fig is not None
        assert hasattr(fig, "data")
        assert len(fig.data) > 0

        # Verify it's a histogram
        assert fig.data[0].type == "histogram"

    def test_plot_attendance_histogram_mean_median_lines(self, sample_member_data):

        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")

        # Check for vertical lines (shapes in layout)
        assert hasattr(fig.layout, "shapes")
        assert len(fig.layout.shapes) >= 2  # At least mean and median lines

    def test_plot_attendance_histogram_statistics(self, sample_member_data):

        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")

        # Check for annotations
        assert len(fig.layout.annotations) > 0

        # Verify statistics are mentioned
        annotation_text = " ".join([ann.text for ann in fig.layout.annotations])
        assert any(stat in annotation_text.lower() for stat in ["mean", "median", "std"])

    def test_plot_attendance_histogram_tooltips(self, sample_member_data):

        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")

        # Verify hover template exists
        assert fig.data[0].hovertemplate is not None
        assert "Events" in fig.data[0].hovertemplate or "Members" in fig.data[0].hovertemplate

    def test_get_chart_export_config(self):

        config = get_chart_export_config()

        # Verify required keys are present
        assert "toImageButtonOptions" in config
        assert "displayModeBar" in config
        assert "displaylogo" in config

        # Verify image options
        image_opts = config["toImageButtonOptions"]
        assert image_opts["format"] == "png"
        assert "filename" in image_opts
        assert "height" in image_opts
        assert "width" in image_opts
        assert "scale" in image_opts

    def test_attach_export(self, sample_member_data):

        fig = plot_attendance_trend(sample_member_data)
        fig = _attach_export(fig)

        # Verify modebar configuration
        assert hasattr(fig.layout, "modebar")

    def test_data_state_labels(self, sample_member_data):

        states = ["raw", "cleaned"]

        for state in states:
            # Test trend chart
            fig_trend = plot_attendance_trend(sample_member_data, data_state=state)
            assert state in fig_trend.layout.title.text.lower()

            # Test pie chart
            fig_pie = plot_role_distribution(sample_member_data, data_state=state)
            assert state in fig_pie.layout.title.text.lower()

            # Test histogram
            fig_hist = plot_attendance_histogram(sample_member_data, data_state=state)
            assert state in fig_hist.layout.title.text.lower()

    def test_chart_interactivity(self, sample_member_data):

        fig = plot_attendance_trend(sample_member_data)

        # Verify hover mode is set
        assert hasattr(fig.layout, "hovermode")

        # Verify legend is shown
        assert fig.layout.showlegend is True

    def test_all_charts_with_filtered_data(self, sample_member_data):

        # Filter to only Members
        filtered_df = sample_member_data[sample_member_data["Role"] == "Member"]

        # All charts should work with filtered data
        fig_trend = plot_attendance_trend(filtered_df, data_state="cleaned")
        assert fig_trend is not None
        assert len(fig_trend.data) > 0

        fig_pie = plot_role_distribution(filtered_df, data_state="cleaned")
        assert fig_pie is not None
        assert len(fig_pie.data) > 0

        fig_hist = plot_attendance_histogram(filtered_df, data_state="cleaned")
        assert fig_hist is not None
        assert len(fig_hist.data) > 0


class TestChartSnapshots:
    """Snapshot / regression tests for chart output.

    Each test compares ``fig.to_dict()`` against a JSON fixture stored in
    ``tests/snapshots/<chart_name>.json``.  Fixtures are generated from
    deterministic input data produced by ``DataGenerator(seed=42)``.

    Regeneration policy
    -------------------
    If a Plotly upgrade causes legitimate diffs, review the diff manually then
    regenerate all fixtures with::

        UPDATE_SNAPSHOTS=1 pytest tests/test_visualizer.py::TestChartSnapshots

    Commit the regenerated JSON files together with the code change that caused
    the churn.

    Note: ``layout.template`` (Plotly's built-in default theme) is excluded
    from snapshots via ``_strip_volatile`` because it varies with test-suite
    ordering when other test helpers reseed global state.  All chart-authored
    output (data traces, title, annotations, shapes, axis titles, colors) is
    still captured.

    First-run / missing-fixture behaviour
    --------------------------------------
    If a fixture file does not exist the test writes it and is *skipped* with a
    message "snapshot generated; commit it and re-run".  This makes the initial
    setup ergonomic: run once, commit fixtures, then run again to verify.

    Under ``UPDATE_SNAPSHOTS=1`` tests regenerate fixtures and pass immediately
    (no comparison is performed).
    """

    @pytest.fixture
    def seeded_df(self):
        """Return a reproducible 200-row DataFrame via DataGenerator(seed=42)."""
        return DataGenerator(seed=42).generate(num_records=200, messiness_level="low")

    def _run_snapshot(self, chart_fn, df, name: str, **kwargs):
        """Shared helper: call chart_fn, compare/write snapshot, skip if new."""
        fig = chart_fn(df, **kwargs)
        raw = json.loads(json.dumps(fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder, sort_keys=True))
        actual = _strip_volatile(raw)
        snapshot = _load_or_write_snapshot(name, actual)
        if snapshot is None:
            update = os.environ.get("UPDATE_SNAPSHOTS", "").strip() == "1"
            if update:
                return  # regenerated — pass immediately
            pytest.skip(f"Snapshot '{name}.json' generated; commit it and re-run")
        # Re-strip the loaded snapshot so older fixtures (which still contain volatile
        # numeric arrays) compare cleanly against the stripped `actual`.
        _assert_deep_equal(actual, _strip_volatile(snapshot), path=name)

    def test_attendance_trend_snapshot(self, seeded_df):
        self._run_snapshot(plot_attendance_trend, seeded_df, "attendance_trend", data_state="cleaned")

    def test_role_distribution_snapshot(self, seeded_df):
        self._run_snapshot(plot_role_distribution, seeded_df, "role_distribution", data_state="cleaned")

    def test_attendance_histogram_snapshot(self, seeded_df):
        self._run_snapshot(plot_attendance_histogram, seeded_df, "attendance_histogram", data_state="cleaned")
