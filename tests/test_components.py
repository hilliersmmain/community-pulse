"""Tests for Streamlit UI components.

Components are exercised through ``streamlit.testing.v1.AppTest``, which loads
a small scaffold script that imports the component, supplies the data it needs,
and lets us assert on rendered widgets and session state.

We avoid touching Streamlit internals — only the public AppTest API is used.
"""

from __future__ import annotations

import os
import sys
import textwrap

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.constants import CLEANING_STEPS_DEFAULT

from streamlit.testing.v1 import AppTest

# ---------------------------------------------------------------------------
# Smoke tests: every component module imports cleanly and exports a callable.
# ---------------------------------------------------------------------------


class TestComponentImports:
    def test_import_sidebar(self):
        from components.sidebar import render_sidebar

        assert callable(render_sidebar)

    def test_import_kpi_display(self):
        from components.kpi_display import render_kpi_section

        assert callable(render_kpi_section)

    def test_import_comparison(self):
        from components.comparison import render_comparison

        assert callable(render_comparison)

    def test_import_tab_preparation(self):
        from components.tab_preparation import render_preparation_tab

        assert callable(render_preparation_tab)

    def test_import_tab_analytics(self):
        from components.tab_analytics import render_analytics_tab

        assert callable(render_analytics_tab)

    def test_import_tab_explorer(self):
        from components.tab_explorer import render_explorer_tab

        assert callable(render_explorer_tab)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _sample_dataframe() -> pd.DataFrame:
    """A small, deliberately messy dataframe for cleaning-pipeline tests."""
    return pd.DataFrame(
        {
            "Name": ["alice", "BOB", "alice", "Carol"],
            "Email": ["a@x.com", "bad-email", "a@x.com", "c@x.com"],
            "Role": ["member", "admin", "member", "guest"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-02-15"],
            "Event_Attendance": [5, None, 5, 7],
        }
    )


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return _sample_dataframe()


VALID_UPLOAD_CSV = b"Name,Email,Role,Join_Date,Event_Attendance\nAnn,a@x.com,Member,2025-01-01,3\n"


def _sidebar_script(tmp_path, upload: bytes | None = None, upload_size: int = 100) -> str:
    """A script that renders the sidebar with ``tmp_path`` as its data folder.

    AppTest cannot drive st.file_uploader, so given ``upload`` (CSV bytes) the script stands one in
    that returns the same upload on every run, as the real widget does while the file sits there.
    """
    lines = [
        "import io",
        "import streamlit as st",
        "import components.sidebar as sidebar",
        "import utils.data_access as data_access",
        "",
        f"sidebar.DATA_PATH = {str(tmp_path / 'data.csv')!r}",
        f"data_access.DATA_DIR = {str(tmp_path)!r}",
    ]
    if upload is not None:
        lines += [
            "",
            "class StubUpload(io.BytesIO):",
            '    file_id = "upload-1"',
            f"    size = {upload_size}",
            "",
            f"CSV = {upload!r}",
            "st.sidebar.file_uploader = lambda *args, **kwargs: StubUpload(CSV)",
        ]
    lines += ["", "sidebar.render_sidebar()"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# components/kpi_display.py
# ---------------------------------------------------------------------------


class TestKPIDisplay:
    """``render_kpi_section`` should emit eight metric tiles from health metrics."""

    SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        from utils.health_metrics import get_health_metrics
        from components.kpi_display import render_kpi_section

        df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Alice"],
            "Email": ["a@x.com", "b@x.com", "a@x.com"],
            "Role": ["member", "admin", "member"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-01-01"],
            "Event_Attendance": [5, 3, 5],
        })
        render_kpi_section(get_health_metrics(df))
        """)

    def test_kpi_section_renders_eight_metrics(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert at.exception == []
        labels = [m.label for m in at.metric]
        assert "Total Records" in labels
        assert "Unique Records" in labels
        assert "Duplicate Records" in labels
        assert "Missing Values" in labels
        assert "Completeness Score" in labels
        assert "Duplicate Score" in labels
        assert "Formatting Score" in labels
        assert "Data Health Score" in labels

    def test_kpi_section_total_records_matches_input(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        by_label = {m.label: m for m in at.metric}
        # Streamlit renders metric values as strings.
        assert str(by_label["Total Records"].value) == "3"
        # Two unique rows because one row is duplicated.
        assert str(by_label["Unique Records"].value) == "2"
        assert str(by_label["Duplicate Records"].value) == "1"

    # The help text ends with a static legend ("90%+ = Excellent | 70-89% = Good | ..."), so a bare
    # "Excellent" or "Good" matches for any score. Only the "assessment: <label>" line is dynamic.
    @pytest.mark.parametrize(
        ("score", "label"),
        [
            (95.0, "Excellent"),
            (90.0, "Excellent"),
            (89.9, "Good"),
            (75.0, "Good"),
            (70.0, "Good"),
            (69.9, "Needs Work"),
            (50.0, "Needs Work"),
        ],
    )
    def test_kpi_health_score_uses_threshold_label(self, score, label):
        script = textwrap.dedent(f"""
            from components.kpi_display import render_kpi_section

            render_kpi_section({{
                "total_records": 10,
                "unique_records": 10,
                "duplicate_records": 0,
                "null_cells": 0,
                "completeness_score": 100.0,
                "duplicate_score": 100.0,
                "formatting_score": 100.0,
                "overall_score": {score!r},
            }})
            """)
        at = AppTest.from_string(script)
        at.run()
        assert at.exception == []
        score_metric = {m.label: m for m in at.metric}["Data Health Score"]
        assert f"assessment: {label}" in score_metric.help


# ---------------------------------------------------------------------------
# components/comparison.py
# ---------------------------------------------------------------------------


class TestComparison:
    """``render_comparison`` reads ``clean_df`` from session_state and shows
    before/after metric pairs."""

    SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        import streamlit as st
        from components.comparison import render_comparison

        raw_df = pd.DataFrame({
            "Name": ["alice", "BOB", "alice", "carol"],
            "Email": ["a@x.com", "bad-email", "a@x.com", "c@x.com"],
            "Role": ["member", "admin", "member", "guest"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-02-15"],
            "Event_Attendance": [5, None, 5, 7],
        })
        clean_df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Carol"],
            "Email": ["a@x.com", "b@x.com", "c@x.com"],
            "Role": ["member", "admin", "guest"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-02-15"],
            "Event_Attendance": [5, 0, 7],
        })
        st.session_state["clean_df"] = clean_df
        render_comparison(raw_df)
        """)

    def test_comparison_renders_before_after_pairs(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert at.exception == []
        # Four sections (Records, Duplicates, Missing Values, Health Score),
        # each emits a Before + After metric -> 8 metrics total.
        labels = [m.label for m in at.metric]
        assert labels.count("Before") == 4
        assert labels.count("After") == 4

    def test_comparison_records_delta_reflects_dedup(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        # Records went 4 -> 3, so the Records section's "After" tile should
        # have delta='-1'.
        records_pairs = [m for m in at.metric if m.label in ("Before", "After")]
        # The first 'Before' is records=4, the first 'After' is records=3
        # (Streamlit renders metric values as strings).
        assert str(records_pairs[0].value) == "4"
        assert str(records_pairs[1].value) == "3"
        assert records_pairs[1].delta == "-1"

    def test_comparison_fewer_duplicates_is_drawn_as_an_improvement(self):
        from streamlit.proto.Metric_pb2 import Metric as MetricProto

        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert at.exception == []
        # "After" tiles come in section order: Records, Duplicates, Missing Values, Health Score.
        # The fixture goes from one duplicate to none, and fewer duplicates is the good direction.
        duplicates_after = [m for m in at.metric if m.label == "After"][1]
        assert str(duplicates_after.value) == "0"
        assert duplicates_after.delta == "-1"
        assert duplicates_after.proto.color == MetricProto.MetricColor.GREEN

    WORSE_SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        import streamlit as st
        from components.comparison import render_comparison

        raw_df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Carol"],
            "Email": ["a@x.com", "b@x.com", "c@x.com"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-02-15"],
        })
        st.session_state["clean_df"] = raw_df.assign(Email=["a at x", "b at x", "c@x.com"])
        render_comparison(raw_df)
        """)

    def test_comparison_shows_a_lower_score_as_a_drop(self):
        from streamlit.proto.Metric_pb2 import Metric as MetricProto

        at = AppTest.from_string(self.WORSE_SCAFFOLD)
        at.run()
        assert at.exception == []
        health_after = [m for m in at.metric if m.label == "After"][-1]
        # Used to render as "+-7.0%", which Streamlit draws as a green up arrow.
        assert health_after.delta.startswith("-")
        assert health_after.proto.direction == MetricProto.MetricDirection.DOWN

    def test_comparison_unchanged_record_count_shows_no_arrow(self):
        from streamlit.proto.Metric_pb2 import Metric as MetricProto

        at = AppTest.from_string(self.WORSE_SCAFFOLD)
        at.run()
        records_after = [m for m in at.metric if m.label == "After"][0]
        assert records_after.delta == "No change"
        assert records_after.proto.direction == MetricProto.MetricDirection.NONE
        assert records_after.proto.color == MetricProto.MetricColor.GRAY


# ---------------------------------------------------------------------------
# components/tab_preparation.py — the headline component test for this task
# ---------------------------------------------------------------------------


class TestTabPreparation:
    """End-to-end: load the prep tab, click 'Run Cleaning Algorithms', verify
    the cleaning state is updated and the summary tiles appear."""

    SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        import streamlit as st
        from utils.session_keys import KEY_CLEANING_STEPS
        from utils.constants import CLEANING_STEPS_DEFAULT
        from components.tab_preparation import render_preparation_tab

        st.session_state.setdefault(KEY_CLEANING_STEPS, CLEANING_STEPS_DEFAULT.copy())
        df = pd.DataFrame({
            "Name": ["alice", "BOB", "alice", "carol"],
            "Email": ["a@x.com", "bad-email", "a@x.com", "c@x.com"],
            "Role": ["member", "admin", "member", "guest"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-02-15"],
            "Event_Attendance": [5, None, 5, 7],
        })
        render_preparation_tab(df)
        """)

    def test_prep_tab_initial_render_shows_run_button(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert at.exception == []
        labels = [b.label for b in at.button]
        assert "Run Cleaning Algorithms" in labels
        # Before clicking, no Cleaning Summary metrics yet.
        metric_labels = [m.label for m in at.metric]
        assert "Records Removed" not in metric_labels

    def test_prep_tab_run_cleaning_button_executes_pipeline(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        original_len = 4
        for b in at.button:
            if b.label == "Run Cleaning Algorithms":
                b.click()
                break
        at.run()

        # Cleaned state was written to session.
        assert at.session_state["cleaned"] is True
        assert "clean_df" in at.session_state
        clean_df = at.session_state["clean_df"]
        # The fixture has 4 rows; cleaning drops at least one duplicate alice
        # and the BOB row whose email is invalid -> at most 2 rows remain.
        assert 0 < len(clean_df) < original_len
        # Cleaning log captured one entry per pipeline step.
        assert len(at.session_state["clean_log"]) == len(CLEANING_STEPS_DEFAULT)

        # Cleaning Summary metrics now visible.
        metric_labels = [m.label for m in at.metric]
        assert "Records Removed" in metric_labels
        assert "Data Health Score" in metric_labels

        # Records Removed must match the actual delta and be at least 1.
        by_label = {m.label: m for m in at.metric}
        records_removed = int(by_label["Records Removed"].value)
        assert records_removed == original_len - len(clean_df)
        assert records_removed >= 1

    def test_prep_tab_shows_a_health_gain_as_a_rise(self):
        from streamlit.proto.Metric_pb2 import Metric as MetricProto

        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        next(b for b in at.button if b.label == "Run Cleaning Algorithms").click()
        at.run()
        assert at.exception == []

        # Cleaning the fixture raises its health score, so the tile must read as a gain.
        health = {m.label: m for m in at.metric}["Data Health Score"]
        assert health.delta.startswith("+")
        assert health.proto.direction == MetricProto.MetricDirection.UP

    @pytest.mark.parametrize(
        ("step", "log", "rows"),
        [
            # Only the ticked step may run: names are title-cased and all four rows stay ...
            ("standardize_names", ["Standardized Names to Title Case."], 4),
            # ... and the only duplicate pair (alice twice) goes, leaving three.
            ("remove_duplicates", ["Removed 1 duplicate rows."], 3),
        ],
    )
    def test_prep_tab_runs_only_the_selected_steps(self, step, log, rows):
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["cleaning_steps"] = {name: name == step for name in CLEANING_STEPS_DEFAULT}
        at.run()
        next(b for b in at.button if b.label == "Run Cleaning Algorithms").click()
        at.run()
        assert at.exception == []

        assert at.session_state["clean_log"] == log
        assert len(at.session_state["clean_df"]) == rows

    def test_prep_tab_no_steps_disables_run_button(self):
        # When the user disables every cleaning step, the Run button should be
        # disabled (Streamlit still renders it; we assert via .disabled).
        script = textwrap.dedent("""
            import pandas as pd
            import streamlit as st
            from utils.session_keys import KEY_CLEANING_STEPS
            from components.tab_preparation import render_preparation_tab

            st.session_state[KEY_CLEANING_STEPS] = {
                "standardize_names": False,
                "fix_emails": False,
                "remove_duplicates": False,
                "clean_dates": False,
                "handle_missing_values": False,
            }
            df = pd.DataFrame({
                "Name": ["a"],
                "Email": ["a@x.com"],
                "Role": ["m"],
                "Join_Date": ["2024-01-01"],
                "Event_Attendance": [1],
            })
            render_preparation_tab(df)
            """)
        at = AppTest.from_string(script)
        at.run()
        run_btn = next((b for b in at.button if b.label == "Run Cleaning Algorithms"), None)
        assert run_btn is not None
        assert run_btn.disabled is True


# ---------------------------------------------------------------------------
# components/tab_explorer.py
# ---------------------------------------------------------------------------


class TestTabExplorer:
    SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        from utils.health_metrics import get_health_metrics
        from components.tab_explorer import render_explorer_tab

        df = pd.DataFrame({
            "Name": ["Alice", "Bob"],
            "Email": ["a@x.com", "b@x.com"],
            "Role": ["member", "admin"],
            "Join_Date": ["2024-01-01", "2024-01-02"],
            "Event_Attendance": [5, 3],
        })
        render_explorer_tab(df, "Cleaned", get_health_metrics(df))
        """)

    def test_explorer_renders_subheader_with_state_label(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert at.exception == []
        subheaders = [s.value for s in at.subheader]
        assert any("Cleaned" in s for s in subheaders)

    def test_explorer_renders_four_health_metrics(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        labels = [m.label for m in at.metric]
        assert "Completeness" in labels
        assert "Uniqueness" in labels
        assert "Formatting" in labels
        assert "Overall Health" in labels

    def test_explorer_renders_dataframe(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        # AppTest exposes dataframes as ``at.dataframe``; we expect exactly one.
        assert len(at.dataframe) == 1


# ---------------------------------------------------------------------------
# components/tab_analytics.py
# ---------------------------------------------------------------------------


class TestTabAnalytics:
    """Two paths through ``render_analytics_tab`` matter: the empty state when
    no cleaned data exists, and the populated state with charts and filters."""

    EMPTY_SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        from components.tab_analytics import render_analytics_tab

        df = pd.DataFrame({
            "Name": ["Alice"],
            "Email": ["a@x.com"],
            "Role": ["member"],
            "Join_Date": ["2024-01-01"],
            "Event_Attendance": [5],
        })
        render_analytics_tab(df)
        """)

    POPULATED_SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        import streamlit as st
        from components.tab_analytics import render_analytics_tab

        raw_df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Carol", "Dave"],
            "Email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"],
            "Role": ["member", "admin", "member", "guest"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            "Event_Attendance": [5, 3, 7, 2],
        })
        st.session_state["cleaned"] = True
        st.session_state["clean_df"] = raw_df.copy()
        render_analytics_tab(raw_df)
        """)

    def test_analytics_tab_empty_state_when_not_cleaned(self):
        at = AppTest.from_string(self.EMPTY_SCAFFOLD)
        at.run()
        assert at.exception == []
        rendered = "\n".join(m.value for m in at.markdown)
        # The empty-state title from MESSAGES["no_data_cleaned"]
        assert "Data Not Cleaned Yet" in rendered

    def test_analytics_tab_populated_renders_charts_and_filter(self):
        at = AppTest.from_string(self.POPULATED_SCAFFOLD)
        at.run()
        assert at.exception == []
        # Multiselect for Role filter.
        assert len(at.multiselect) >= 1
        role_filter = at.multiselect[0]
        assert "Role" in role_filter.label or "role" in role_filter.label.lower()
        # Plotly charts rendered (trend, histogram, role distribution + the
        # before/after tab content).
        # We don't assert exact count to stay resilient to small changes —
        # only that at least three charts are present.
        if not hasattr(at, "plotly_chart"):
            pytest.skip("AppTest does not surface plotly_chart in this Streamlit version")
        assert len(at.plotly_chart) >= 3


# ---------------------------------------------------------------------------
# components/sidebar.py
# ---------------------------------------------------------------------------


class TestSidebar:
    """The sidebar exercises the most surface area: data source toggle, the
    cleaning-step expander, the reset button, and the help expander.

    We only verify the pieces that are deterministic without an on-disk CSV
    and without triggering ``st.rerun``-protected button paths."""

    SCAFFOLD = textwrap.dedent("""
        from components.sidebar import render_sidebar
        render_sidebar()
        """)

    @pytest.fixture(autouse=True)
    def _undo_script_patches(self, monkeypatch):
        # AppTest runs scripts in this process, so what _sidebar_script assigns (the data paths on
        # the sidebar modules, a stand-in file_uploader on st.sidebar) would outlive its test.
        import streamlit as st
        import components.sidebar as sidebar
        import utils.data_access as data_access

        monkeypatch.setattr(sidebar, "DATA_PATH", sidebar.DATA_PATH)
        monkeypatch.setattr(data_access, "DATA_DIR", data_access.DATA_DIR)
        yield
        st.sidebar.__dict__.pop("file_uploader", None)

    def test_sidebar_renders_without_exception(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert at.exception == []

    def test_sidebar_initializes_default_session_keys(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        # The sidebar must seed these keys on first render.
        assert "num_records" in at.session_state
        assert "messiness_level" in at.session_state
        assert "cleaning_steps" in at.session_state
        # Cleaning steps default to the documented 5-step pipeline.
        assert set(at.session_state["cleaning_steps"].keys()) == {
            "standardize_names",
            "fix_emails",
            "remove_duplicates",
            "clean_dates",
            "handle_missing_values",
        }

    def test_sidebar_cleaning_step_count_caption_present(self):
        # 5 steps default to True, so the caption should reflect "5 step(s)".
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        captions = [c.value for c in at.sidebar.caption] if hasattr(at.sidebar, "caption") else []
        # Fall back to scanning all caption-like elements via .markdown if the
        # sidebar accessor isn't structured this way in older Streamlit.
        all_text = " ".join(c.value for c in at.caption)
        assert "5 step(s)" in all_text or any("5 step(s)" in c for c in captions)

    def test_reset_to_raw_data_does_not_raise(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["cleaned"] = True
        at.session_state["clean_df"] = _sample_dataframe()
        at.run()
        at.button(key="reset_to_raw").click().run()
        # Used to raise: `st.session_state.view_state` cannot be modified after the
        # widget with key `view_state` is instantiated.
        assert at.exception == []
        assert at.session_state["cleaned"] is False
        assert at.session_state["view_state"] == "raw"

    def test_every_generation_setting_change_sticks(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        # Keyless widgets used to drop every second change.
        for records in (600, 700, 800):
            at.slider(key="num_records").set_value(records).run()
            assert at.session_state["num_records"] == records
        for level in ("high", "low", "medium"):
            at.selectbox(key="messiness_level").set_value(level).run()
            assert at.session_state["messiness_level"] == level
        for enabled in (False, True, False):
            at.checkbox(key="cleaning_step_fix_emails").set_value(enabled).run()
            assert at.session_state["cleaning_steps"]["fix_emails"] is enabled
        assert at.exception == []

    def test_generation_settings_survive_a_trip_to_upload_mode(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        at.slider(key="num_records").set_value(700).run()
        at.selectbox(key="messiness_level").set_value("high").run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        at.radio(key="data_source").set_value("Generate Sample").run()
        assert at.slider(key="num_records").value == 700
        assert at.selectbox(key="messiness_level").value == "high"

    def test_rerun_with_a_file_in_the_uploader_keeps_cleaned_state(self, tmp_path):
        at = AppTest.from_string(_sidebar_script(tmp_path, upload=VALID_UPLOAD_CSV))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert (tmp_path / "data.csv").exists()
        at.session_state["cleaned"] = True  # as if "Run Cleaning Algorithms" was clicked
        at.session_state["clean_df"] = _sample_dataframe()
        at.run()
        assert at.exception == []
        assert at.session_state["cleaned"] is True

    def test_oversize_upload_is_refused_and_not_saved(self, tmp_path):
        at = AppTest.from_string(_sidebar_script(tmp_path, upload=VALID_UPLOAD_CSV, upload_size=6 * 1024 * 1024))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert at.exception == []
        assert any("File too large" in e.value for e in at.sidebar.error)
        assert len(at.sidebar.success) == 0
        assert not (tmp_path / "data.csv").exists()

    def test_upload_missing_required_columns_is_refused_and_not_saved(self, tmp_path):
        at = AppTest.from_string(_sidebar_script(tmp_path, upload=b"Name,Foo\nAnn,1\n"))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert at.exception == []
        assert any("Missing required columns" in e.value for e in at.sidebar.error)
        assert len(at.sidebar.success) == 0
        assert not (tmp_path / "data.csv").exists()

    def test_export_radio_switches_between_raw_and_cleaned_downloads(self, tmp_path):
        _sample_dataframe().to_csv(tmp_path / "data.csv", index=False)
        at = AppTest.from_string(_sidebar_script(tmp_path))
        at.session_state["cleaned"] = True
        at.session_state["clean_df"] = _sample_dataframe().iloc[[0, 3]]
        at.run()
        assert at.exception == []

        def download_labels():
            return [b.label for b in at.sidebar.download_button]

        # The label is the only thing AppTest shows of a download button, and it names the dataset.
        assert download_labels() == ["Download CSV (Raw)", "Download JSON (Raw)"]
        next(r for r in at.sidebar.radio if r.label == "Export data:").set_value("cleaned").run()
        assert at.exception == []
        assert download_labels() == ["Download CSV (Cleaned)", "Download JSON (Cleaned)"]

    def test_generate_button_honours_the_record_slider(self, tmp_path):
        at = AppTest.from_string(_sidebar_script(tmp_path))
        at.run()
        at.slider(key="num_records").set_value(700).run()
        next(b for b in at.sidebar.button if b.label == "Generate New Data").click()
        at.run()
        assert at.exception == []
        # The default medium messiness adds duplicate rows on top of the requested count.
        assert len(pd.read_csv(tmp_path / "data.csv")) >= 700

    def test_json_export_writes_dates_as_iso_strings(self):
        import json
        from components.sidebar import export_json

        df = pd.DataFrame({"Name": ["Ann"], "Join_Date": pd.to_datetime(["2025-06-01"])})
        records = json.loads(export_json(df))
        assert records == [{"Name": "Ann", "Join_Date": "2025-06-01T00:00:00.000"}]


def test_no_deprecated_use_container_width():
    """Streamlit deprecated use_container_width for width= and schedules its removal;
    a release without it would raise TypeError on the first render that passes it."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sources = [os.path.join(root, "app.py")]
    for package in ("components", "utils", "community_pulse"):
        package_dir = os.path.join(root, package)
        sources += [os.path.join(package_dir, name) for name in os.listdir(package_dir) if name.endswith(".py")]
    offenders = [path for path in sources if "use_container_width" in open(path, encoding="utf-8").read()]
    assert offenders == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
