"""Shared Streamlit session-state keys and helpers."""

from __future__ import annotations

import streamlit as st

KEY_CLEANED = "cleaned"
KEY_CLEAN_DF = "clean_df"
KEY_CLEAN_LOG = "clean_log"
KEY_VIEW_STATE = "view_state"
KEY_CLEANING_STEPS = "cleaning_steps"
KEY_DATA_LOADED_AT = "data_loaded_at"
KEY_DATA_GENERATED_AT = "data_generated_at"
KEY_CLEANING_COMPLETED_AT = "cleaning_completed_at"
KEY_CLEANING_DURATION = "cleaning_duration"


def reset_clean_state() -> None:
    """Clear cleaned artifacts and reset view to raw data."""
    st.session_state[KEY_CLEANED] = False
    for key in (KEY_CLEAN_DF, KEY_CLEAN_LOG, KEY_CLEANING_COMPLETED_AT, KEY_CLEANING_DURATION):
        if key in st.session_state:
            del st.session_state[key]
    st.session_state[KEY_VIEW_STATE] = "raw"
