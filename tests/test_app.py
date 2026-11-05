"""End-to-end test for ``app.py``: the one script that wires the sidebar, tabs and views together.

The component tests render each piece on its own; none of them runs ``app.py``, so the view-state
logic that decides which dataframe the dashboard shows lives here and nowhere else.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from streamlit.testing.v1 import AppTest


def _click(at: AppTest, label: str) -> None:
    next(b for b in at.button if b.label == label).click()
    at.run()
    assert at.exception == []


def test_cleaned_view_shows_the_cleaned_rows(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # any stray relative write lands here, not in the repo

    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()
    assert at.exception == []

    _click(at, "Generate New Data")
    raw_rows = len(at.session_state["raw_df"])

    _click(at, "Run Cleaning Algorithms")
    clean_rows = len(at.session_state["clean_df"])
    # Cleaning must change the row count, or the raw and cleaned views could not be told apart below.
    assert clean_rows < raw_rows

    at.sidebar.radio(key="view_state").set_value("cleaned").run()
    assert at.exception == []

    headings = [m.value for m in at.markdown]
    assert "### Current View: **Cleaned Data**" in headings
    # The Data Explorer table is the only dataframe on the page and shows the active view.
    assert len(at.dataframe) == 1
    assert len(at.dataframe[0].value) == clean_rows


def test_generate_confirmation_survives_the_rerun(tmp_path, monkeypatch):
    """W24: the button confirms success and then calls st.rerun(), which wipes whatever the run drew."""
    monkeypatch.chdir(tmp_path)  # any stray relative write lands here, not in the repo
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()

    _click(at, "Generate New Data")
    assert [t.value for t in at.toast] == ["Successfully generated 500 records with medium messiness level."]

    at.run()  # the confirmation is one-shot: the next interaction does not repeat it
    assert at.exception == []
    assert len(at.toast) == 0


def test_cleaning_confirmation_survives_the_rerun():
    """W24: the same wipe hit "Run Cleaning Algorithms", whose success banner never reached the visitor."""
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.session_state["raw_df"] = pd.DataFrame(
        {
            "Name": ["alice", "BOB", "alice", "Carol"],
            "Email": ["a@x.com", "bad-email", "a@x.com", "c@x.com"],
            "Role": ["member", "admin", "member", "guest"],
            "Join_Date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-02-15"],
            "Event_Attendance": [5, None, 5, 7],
        }
    )
    at.run()

    _click(at, "Run Cleaning Algorithms")
    assert [t.value for t in at.toast] == ["Data cleaning completed successfully! 4 records processed."]

    at.run()
    assert at.exception == []
    assert len(at.toast) == 0


def _button(at: AppTest, label: str):
    return next(b for b in at.button if b.label == label)


def test_tutorial_runs_from_the_welcome_card_to_completion(tmp_path, monkeypatch):
    """L2 (YC6): "Start Tutorial" set step 0, which nothing rendered, and the completion branch sat behind a
    return that no caller could pass, so the tutorial neither started nor finished."""
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()

    _click(at, "Start Tutorial")
    assert at.session_state["tutorial_mode"] is True
    assert any("Step 1: Generate Data" in i.value for i in at.sidebar.info)
    assert _button(at, "Next").disabled is True  # the next steps need data on the page

    _click(at, "Generate New Data")
    assert any("Step 1: Generate Data" in i.value for i in at.sidebar.info)
    assert _button(at, "Next").disabled is False

    for expected in (
        "Step 2: Review KPIs",
        "Step 3: Configure Cleaning",
        "Step 4: Run Cleaning",
        "Step 5: View Analytics",
    ):
        _click(at, "Next")
        assert any(expected in i.value for i in at.info), expected

    _click(at, "Next")
    assert at.session_state["tutorial_mode"] is False
    assert at.session_state["tutorial_step"] == 0
    assert [t.value for t in at.toast] == ["Tutorial completed! You're now ready to use Community Pulse effectively."]
    assert not any(b.label in ("Next", "Previous", "Skip Tutorial") for b in at.button)
