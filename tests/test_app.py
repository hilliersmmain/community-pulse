"""End-to-end test for ``app.py``: the one script that wires the sidebar, tabs and views together.

The component tests render each piece on its own; none of them runs ``app.py``, so the view-state
logic that decides which dataframe the dashboard shows lives here and nowhere else.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

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
