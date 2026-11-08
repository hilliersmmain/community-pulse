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


# O25: every health metric of this frame differs from the others, so a tile that shows the wrong metric fails.
# 4 records, 3 unique, 1 duplicate (a@x.com again), 2 missing cells, Completeness 10/12 = 83.3%, Duplicate Score
# 3/4 = 75.0%, Formatting 87.5% (Name 3 of 4 valid, Email 3 of 3), overall 0.4 * 83.3 + 0.3 * 75 + 0.3 * 87.5 = 82.1%.
DISTINCT_METRICS_DATA = {
    "Name": ["Ann Lee", "Bo Kim", "Ann Lee", "cy_day"],
    "Email": ["a@x.com", "b@x.com", "a@x.com", None],
    "Event_Attendance": [1, 2, 1, None],
}
# The same data as source text, for the AppTest scaffolds.
DISTINCT_METRICS_FRAME = repr(DISTINCT_METRICS_DATA)


VALID_UPLOAD_CSV = b"Name,Email,Role,Join_Date,Event_Attendance\nAnn,a@x.com,Member,2025-01-01,3\n"


def _sidebar_script(upload: bytes | None = None, upload_size: int = 100) -> str:
    """A script that renders the sidebar.

    AppTest cannot drive st.file_uploader, so given ``upload`` (CSV bytes) the script stands one in
    that returns the same upload on every run, as the real widget does while the file sits there.
    """
    lines = [
        "import io",
        "import streamlit as st",
        "import components.sidebar as sidebar",
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

    def test_duplicate_records_help_says_email_not_name(self):
        """Duplicates are found by Email alone (case and spacing ignored); the help text used to say email and name."""
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        help_text = {m.label: m.help for m in at.metric}["Duplicate Records"].lower()
        assert "email" in help_text
        assert "name" not in help_text

    def test_raw_count_tiles_have_no_delta_arrow(self):
        """L3 (YC5): Duplicate Records and Missing Values are counts of the data on screen, not changes, yet
        they carried a negative "inverse" delta, so a raw-data problem was drawn with a green arrow."""
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        by_label = {m.label: m for m in at.metric}
        assert str(by_label["Duplicate Records"].value) == "1"
        assert by_label["Duplicate Records"].delta == ""
        assert by_label["Missing Values"].delta == ""

    def test_each_kpi_tile_shows_its_own_metric(self):
        """O25: the tiles were checked by label only, so two tiles could swap values and the suite stayed green."""
        at = AppTest.from_string(textwrap.dedent(f"""
            import pandas as pd
            from utils.health_metrics import get_health_metrics
            from components.kpi_display import render_kpi_section

            render_kpi_section(get_health_metrics(pd.DataFrame({DISTINCT_METRICS_FRAME})))
            """))
        at.run()
        assert at.exception == []
        assert {m.label: str(m.value) for m in at.metric} == {
            "Total Records": "4",
            "Unique Records": "3",
            "Duplicate Records": "1",
            "Missing Values": "2",
            "Completeness Score": "83.3%",
            "Duplicate Score": "75.0%",
            "Formatting Score": "87.5%",
            "Data Health Score": "82.1%",
        }

    def test_health_score_help_states_the_weights_the_score_uses(self):
        """O23: the help text spells the weights out, so it must change when the constants do."""
        from utils.constants import (
            HEALTH_SCORE_WEIGHT_COMPLETENESS,
            HEALTH_SCORE_WEIGHT_FORMATTING,
            HEALTH_SCORE_WEIGHT_UNIQUENESS,
        )

        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        help_text = {m.label: m.help for m in at.metric}["Data Health Score"]
        assert f"{round(HEALTH_SCORE_WEIGHT_COMPLETENESS * 100)}% Completeness" in help_text
        assert f"{round(HEALTH_SCORE_WEIGHT_UNIQUENESS * 100)}% Uniqueness" in help_text
        assert f"{round(HEALTH_SCORE_WEIGHT_FORMATTING * 100)}% Formatting" in help_text

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

    MORE_MISSING_SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        import streamlit as st
        from components.comparison import render_comparison

        raw_df = pd.DataFrame({"Name": ["Alice", "Bob"], "Email": ["a@x.com", "b@x.com"]})
        st.session_state["clean_df"] = raw_df.assign(Email=["a@x.com", None])
        render_comparison(raw_df)
        """)

    def test_comparison_fewer_missing_values_is_drawn_as_an_improvement(self):
        """Guard: the Missing Values tile uses an inverse delta, so fewer missing cells after cleaning read as good."""
        from streamlit.proto.Metric_pb2 import Metric as MetricProto

        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert at.exception == []
        # The fixture's raw frame has one empty cell (Event_Attendance) and the cleaned frame has none.
        missing_before, missing_after = [m for m in at.metric if m.label in ("Before", "After")][4:6]
        assert str(missing_before.value) == "1"
        assert str(missing_after.value) == "0"
        assert missing_after.delta == "-1"
        assert missing_after.proto.direction == MetricProto.MetricDirection.DOWN
        assert missing_after.proto.color == MetricProto.MetricColor.GREEN

    def test_comparison_more_missing_values_is_drawn_as_a_regression(self):
        from streamlit.proto.Metric_pb2 import Metric as MetricProto

        at = AppTest.from_string(self.MORE_MISSING_SCAFFOLD)
        at.run()
        assert at.exception == []
        missing_after = [m for m in at.metric if m.label == "After"][2]
        assert missing_after.delta == "1"
        assert missing_after.proto.direction == MetricProto.MetricDirection.UP
        assert missing_after.proto.color == MetricProto.MetricColor.RED

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

    ALL_BAD_EMAILS_SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        import streamlit as st
        from utils.session_keys import KEY_CLEANING_STEPS
        from utils.constants import CLEANING_STEPS_DEFAULT
        from components.tab_preparation import render_preparation_tab

        st.session_state.setdefault(KEY_CLEANING_STEPS, CLEANING_STEPS_DEFAULT.copy())
        df = pd.DataFrame({
            "Name": ["Alice", "Bob"],
            "Email": ["not an email 1", "not an email 2"],
            "Role": ["member", "admin"],
            "Join_Date": ["2024-01-01", "2024-01-02"],
            "Event_Attendance": [5, 3],
        })
        render_preparation_tab(df)
        """)

    def test_prep_tab_warns_when_cleaning_removes_every_record(self):
        """W27: with every row dropped the tab said nothing (the Analytics half was fixed earlier)."""
        at = AppTest.from_string(self.ALL_BAD_EMAILS_SCAFFOLD)
        at.run()
        next(b for b in at.button if b.label == "Run Cleaning Algorithms").click()
        at.run()
        assert at.exception == []
        assert at.session_state["cleaned"] is True
        assert len(at.session_state["clean_df"]) == 0
        warnings = [w.value for w in at.warning]
        assert any("removed every record" in w for w in warnings)
        assert any("Fix Email Formats" in w for w in warnings)
        # No success confirmation is queued for a run that left nothing.
        assert "flash_message" not in at.session_state

    def test_row_removing_step_labels_match_the_sidebar_checkboxes(self):
        """The warning names steps by their sidebar checkbox label; a renamed checkbox must rename it here too."""
        from components.sidebar import CLEANING_STEP_CHECKBOXES
        from components.tab_preparation import ROW_REMOVING_STEPS

        checkbox_labels = {key: label for key, label, _help in CLEANING_STEP_CHECKBOXES}
        assert set(ROW_REMOVING_STEPS) == {"fix_emails"}
        assert ROW_REMOVING_STEPS == {key: checkbox_labels[key] for key in ROW_REMOVING_STEPS}

    def test_every_record_removed_message_never_blames_remove_duplicates(self):
        """Remove Duplicates keeps the first row of each group, so only Fix Email Formats can empty the table.

        The message used to name whichever of the two was ticked when the tab drew it, so unticking Fix Email
        Formats after the run made it blame Remove Duplicates.
        """
        from components.tab_preparation import _every_record_removed_message

        for selected in (["remove_duplicates"], ["fix_emails", "remove_duplicates"], []):
            message = _every_record_removed_message(selected)
            assert "Remove Duplicates" not in message
            assert '"Fix Email Formats"' in message

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

    def test_each_explorer_tile_shows_its_own_metric(self):
        """O25: swapping two of these tiles' values used to leave the suite green."""
        at = AppTest.from_string(textwrap.dedent(f"""
            import pandas as pd
            from utils.health_metrics import get_health_metrics
            from components.tab_explorer import render_explorer_tab

            df = pd.DataFrame({DISTINCT_METRICS_FRAME})
            render_explorer_tab(df, "Raw", get_health_metrics(df))
            """))
        at.run()
        assert at.exception == []
        assert {m.label: str(m.value) for m in at.metric} == {
            "Completeness": "83.3%",
            "Uniqueness": "75.0%",
            "Formatting": "87.5%",
            "Overall Health": "82.1%",
        }

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

    def test_analytics_info_does_not_promise_sidebar_toggle(self):
        """W11: the sidebar view toggle never changed the Analytics charts; the info text said it did."""
        at = AppTest.from_string(self.POPULATED_SCAFFOLD)
        at.run()
        assert at.exception == []
        info = " ".join(i.value for i in at.info)
        assert "Toggle to 'Raw Data' in the sidebar" not in info
        assert "sidebar" not in info.lower()
        # The raw-versus-cleaned comparison it should point at is the section further down this page.
        assert "Before/After Cleaning Visual Comparison" in info
        assert "Before/After Cleaning Visual Comparison" in " ".join(h.value for h in at.subheader)

    EMPTY_CLEANED_SCAFFOLD = textwrap.dedent("""
        import pandas as pd
        import streamlit as st
        from components.tab_analytics import render_analytics_tab

        raw_df = pd.DataFrame({
            "Name": ["Alice", "Bob"],
            "Email": ["not an email 1", "not an email 2"],
            "Role": ["member", "admin"],
            "Join_Date": ["2024-01-01", "2024-01-02"],
            "Event_Attendance": [5, 3],
        })
        st.session_state["cleaned"] = True
        st.session_state["clean_df"] = raw_df.iloc[0:0]
        render_analytics_tab(raw_df)
        """)

    def test_analytics_tab_explains_an_empty_cleaned_frame(self):
        """W27: when cleaning removed every row the tab blamed the role filter, which had nothing to select."""
        at = AppTest.from_string(self.EMPTY_CLEANED_SCAFFOLD)
        at.run()
        assert at.exception == []
        assert not any("Select at least one role" in i.value for i in at.info)
        warnings = [w.value for w in at.warning]
        assert any("removed every record" in w for w in warnings)
        assert any("Fix Email Formats" in w for w in warnings)
        assert len(at.multiselect) == 0


# ---------------------------------------------------------------------------
# components/sidebar.py
# ---------------------------------------------------------------------------


class TestSidebar:
    """The sidebar exercises the most surface area: data source toggle, the
    cleaning-step expander, the reset button, and the help expander.

    A visitor's raw data lives in session state (``raw_df``), so a test seeds or reads that key."""

    SCAFFOLD = textwrap.dedent("""
        from components.sidebar import render_sidebar
        render_sidebar()
        """)

    @pytest.fixture(autouse=True)
    def _undo_script_patches(self):
        # AppTest runs scripts in this process, so the stand-in file_uploader that _sidebar_script
        # assigns on st.sidebar would outlive its test.
        import streamlit as st

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

    def test_duplicate_step_help_says_email_not_name(self):
        """The checkbox tooltip and the Help & Guide text both describe the Email-only duplicate key."""
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        checkbox_help = at.checkbox(key="cleaning_step_remove_duplicates").help.lower()
        guide = next(m.value for m in at.sidebar.markdown if "Remove Duplicates:" in m.value)
        line = next(row for row in guide.splitlines() if "Remove Duplicates:" in row).lower()
        for text in (checkbox_help, line):
            assert "email" in text
            assert "name" not in text

    def test_sidebar_renders_tutorial_step_zero(self):
        """L2 (YC6): the welcome modal set tutorial_step 0, but no caller rendered step 0, so the tutorial never appeared."""
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 0
        at.run()
        assert at.exception == []
        assert any("Step 1: Generate Data" in i.value for i in at.sidebar.info)
        buttons = {b.label: b for b in at.sidebar.button}
        assert "Skip Tutorial" in buttons
        # The steps after this one anchor on widgets that exist only once data is loaded.
        assert buttons["Next"].disabled is True

    def test_tutorial_step_zero_next_is_enabled_once_data_exists(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 0
        at.session_state["raw_df"] = _sample_dataframe()
        at.run()
        assert at.exception == []
        assert {b.label: b for b in at.sidebar.button}["Next"].disabled is False

    def test_sidebar_without_tutorial_renders_no_tutorial_card(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        assert not any("Step 1: Generate Data" in i.value for i in at.sidebar.info)
        assert not any(b.label in ("Next", "Skip Tutorial") for b in at.sidebar.button)

    def test_quick_stats_show_the_record_count_and_the_overall_score(self):
        """O25: Quick Stats was checked by label only; Records must be every row, Health Score the overall score."""
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["raw_df"] = pd.DataFrame(DISTINCT_METRICS_DATA)
        at.run()
        assert at.exception == []
        assert {m.label: str(m.value) for m in at.sidebar.metric} == {"Records": "4", "Health Score": "82.1%"}

    def test_help_guide_names_only_controls_that_exist(self):
        """W56 text / O05: the guide told visitors to enable "Tutorial Mode" and check "What's New"; neither control exists."""
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        guide = "\n".join(m.value for m in at.sidebar.markdown)
        assert "Quick Start Guide" in guide
        assert "What's New" not in guide
        assert "Tutorial Mode" not in guide

    def test_help_guide_can_start_the_tutorial(self):
        """The tutorial used to be reachable only from the first-visit welcome card."""
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["show_welcome"] = False
        at.run()
        at.button(key="help_start_tutorial").click().run()
        assert at.exception == []
        assert at.session_state["tutorial_mode"] is True
        assert at.session_state["tutorial_step"] == 0
        assert at.session_state["show_welcome"] is False
        assert any("Step 1: Generate Data" in i.value for i in at.sidebar.info)

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

    def test_rerun_with_a_file_in_the_uploader_keeps_cleaned_state(self):
        at = AppTest.from_string(_sidebar_script(upload=VALID_UPLOAD_CSV))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert len(at.session_state["raw_df"]) == 1
        at.session_state["cleaned"] = True  # as if "Run Cleaning Algorithms" was clicked
        at.session_state["clean_df"] = _sample_dataframe()
        at.run()
        assert at.exception == []
        assert at.session_state["cleaned"] is True

    def test_oversize_upload_is_refused_and_not_stored(self):
        at = AppTest.from_string(_sidebar_script(upload=VALID_UPLOAD_CSV, upload_size=6 * 1024 * 1024))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert at.exception == []
        assert any("File too large" in e.value for e in at.sidebar.error)
        assert len(at.sidebar.success) == 0
        assert "raw_df" not in at.session_state

    def test_upload_missing_required_columns_is_refused_and_not_stored(self):
        at = AppTest.from_string(_sidebar_script(upload=b"Name,Foo\nAnn,1\n"))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert at.exception == []
        assert any("Missing required columns" in e.value for e in at.sidebar.error)
        assert len(at.sidebar.success) == 0
        assert "raw_df" not in at.session_state

    def test_overwide_upload_is_refused_before_it_is_parsed(self, monkeypatch):
        """W14: the column cap is checked on the raw header, so a hostile header never reaches pd.read_csv."""
        wide = ",".join(["Name", "Email", "Role", "Join_Date", "Event_Attendance"] + [f"extra_{i}" for i in range(200)])
        parsed: list[object] = []
        real_read_csv = pd.read_csv

        def spy(*args, **kwargs):
            parsed.append(args[0])
            return real_read_csv(*args, **kwargs)

        monkeypatch.setattr(pd, "read_csv", spy)
        at = AppTest.from_string(_sidebar_script(upload=f"{wide}\nx\n".encode()))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert at.exception == []
        assert [e.value for e in at.sidebar.error] == ["Too many columns: uploads are limited to 50 columns."]
        assert len(at.sidebar.success) == 0
        assert "raw_df" not in at.session_state
        assert parsed == []

    def test_semicolon_upload_error_names_the_delimiter(self):
        """W26: the sidebar showed "Missing required columns" naming all five columns the file does have."""
        csv = b"Name;Email;Role;Join_Date;Event_Attendance\nAnn;a@x.com;Member;2025-01-01;3\n"
        at = AppTest.from_string(_sidebar_script(upload=csv))
        at.run()
        at.radio(key="data_source").set_value("Upload CSV").run()
        assert at.exception == []
        errors = [e.value for e in at.sidebar.error]
        assert len(errors) == 1
        assert errors[0].startswith("Missing required columns: Name, Email, Role, Join_Date, Event_Attendance. ")
        assert "semicolon-delimited" in errors[0]
        assert "raw_df" not in at.session_state

    def test_export_radio_switches_between_raw_and_cleaned_downloads(self):
        at = AppTest.from_string(_sidebar_script())
        at.session_state["raw_df"] = _sample_dataframe()
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

    def test_generate_button_honours_the_record_slider(self):
        at = AppTest.from_string(_sidebar_script())
        at.run()
        at.slider(key="num_records").set_value(700).run()
        next(b for b in at.sidebar.button if b.label == "Generate New Data").click()
        at.run()
        assert at.exception == []
        # The default medium messiness adds duplicate rows on top of the requested count.
        assert len(at.session_state["raw_df"]) >= 700

    def test_an_upload_is_invisible_to_every_other_session(self, tmp_path, monkeypatch):
        # One Streamlit server runs every visitor's session in one process, as these two AppTests
        # share this one. An upload used to go to one server-wide file, which every other session
        # showed in Quick Stats and offered for download.
        monkeypatch.chdir(tmp_path)  # any stray relative write lands here, not in the repo
        uploader = AppTest.from_string(_sidebar_script(upload=VALID_UPLOAD_CSV))
        uploader.run()
        uploader.radio(key="data_source").set_value("Upload CSV").run()
        assert uploader.exception == []
        assert len(uploader.download_button) == 2

        other = AppTest.from_string(self.SCAFFOLD)
        other.run()
        assert other.exception == []
        assert len(other.download_button) == 0
        assert "No data available" in [c.value for c in other.caption]
        assert "raw_df" not in other.session_state
        # The uploader's own session keeps what it uploaded.
        assert len(uploader.session_state["raw_df"]) == 1

    def test_json_export_writes_dates_as_iso_strings(self):
        import json
        from components.sidebar import export_json

        df = pd.DataFrame({"Name": ["Ann"], "Join_Date": pd.to_datetime(["2025-06-01"])})
        records = json.loads(export_json(df))
        assert records == [{"Name": "Ann", "Join_Date": "2025-06-01T00:00:00.000"}]


def test_generated_data_is_invisible_to_every_other_session(tmp_path, monkeypatch):
    """The whole app, in two sessions of one process: data one visitor generates must not
    reach another visitor's main page, Quick Stats or export buttons."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
    monkeypatch.chdir(tmp_path)  # any stray relative write lands here, not in the repo
    generator = AppTest.from_file(app_path, default_timeout=60)
    generator.run()
    next(b for b in generator.button if b.label == "Generate New Data").click().run()
    assert generator.exception == []
    assert len(generator.dataframe) == 1

    other = AppTest.from_file(app_path, default_timeout=60)
    other.run()
    assert other.exception == []
    assert len(other.dataframe) == 0
    assert len(other.download_button) == 0
    assert any("Getting Started" in i.value for i in other.info)
    assert "raw_df" not in other.session_state
    # Kept as it reads back from CSV, as the old file round trip left it: timestamps as text.
    assert generator.session_state["raw_df"]["Last_Login"].dtype == object


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
