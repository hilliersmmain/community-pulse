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

    def test_kpi_health_score_uses_threshold_label(self):
        # The health score on this fixture is ~90% (excellent threshold). The
        # help text encodes the label, so we check it's present.
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        by_label = {m.label: m for m in at.metric}
        score_metric = by_label["Data Health Score"]
        assert score_metric.help is not None
        assert "Excellent" in score_metric.help or "Good" in score_metric.help


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
        assert len(at.session_state["clean_log"]) == 5

        # Cleaning Summary metrics now visible.
        metric_labels = [m.label for m in at.metric]
        assert "Records Removed" in metric_labels
        assert "Data Health Score" in metric_labels

        # Records Removed must match the actual delta and be at least 1.
        by_label = {m.label: m for m in at.metric}
        records_removed = int(by_label["Records Removed"].value)
        assert records_removed == original_len - len(clean_df)
        assert records_removed >= 1

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
        # AppTest does not surface plotly_chart directly in older versions; if
        # the attribute is missing this assertion is skipped.
        chart_attr = getattr(at, "plotly_chart", None)
        if chart_attr is not None:
            assert len(chart_attr) >= 3


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
