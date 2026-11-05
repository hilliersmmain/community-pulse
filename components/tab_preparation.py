import streamlit as st
import pandas as pd
from datetime import datetime
from utils.cleaner import DataCleaner
from utils.health_metrics import get_health_score
from utils.session_keys import (
    KEY_CLEANED,
    KEY_CLEAN_DF,
    KEY_CLEAN_LOG,
    KEY_CLEANING_COMPLETED_AT,
    KEY_CLEANING_DURATION,
    KEY_CLEANING_STEPS,
)
from utils.ui_helpers import (
    show_empty_state,
    show_tutorial_step,
    show_loading_message,
    show_error_message,
    get_contextual_message,
    format_score_delta,
    queue_flash,
)

# The cleaning steps that drop rows, by their sidebar checkbox label (components/sidebar.py,
# CLEANING_STEP_CHECKBOXES; a test keeps the two in step).
ROW_REMOVING_STEPS = {"fix_emails": "Fix Email Formats", "remove_duplicates": "Remove Duplicates"}


def _every_record_removed_message(selected_steps: list[str]) -> str:
    """Say which of the selected steps can drop rows, so the visitor knows what to turn off."""
    culprits = [label for step, label in ROW_REMOVING_STEPS.items() if step in selected_steps]
    named = " or ".join(f'"{label}"' for label in culprits or ROW_REMOVING_STEPS.values())
    return (
        "Cleaning removed every record, so there is nothing to analyse or export. "
        f"Try turning off {named} in the sidebar, or check the Email column, then run the cleaning again."
    )


def _run_cleaning(raw_df: pd.DataFrame, selected_steps: list[str]) -> None:
    """Run the selected steps, keep the result in session state, then rerun so the page shows it."""
    try:
        with show_loading_message(get_contextual_message("processing_cleaning", step_count=len(selected_steps))):
            cleaner = DataCleaner(raw_df)
            clean_df = cleaner.clean_all(steps=selected_steps)

            st.session_state[KEY_CLEAN_DF] = clean_df
            st.session_state[KEY_CLEAN_LOG] = cleaner.log
            st.session_state[KEY_CLEANED] = True
            st.session_state[KEY_CLEANING_COMPLETED_AT] = datetime.now()
            if cleaner.end_timestamp is not None:
                st.session_state[KEY_CLEANING_DURATION] = (
                    cleaner.end_timestamp - cleaner.start_timestamp
                ).total_seconds()

        if len(clean_df):
            # st.rerun() wipes what this run drew, so the confirmation waits for the next run.
            queue_flash(get_contextual_message("cleaning_success", records_processed=len(raw_df)))
        st.rerun()
    except Exception as e:
        show_error_message(
            "Data cleaning operation failed. Try selecting different cleaning steps or regenerating your data.",
            str(e),
        )


def _render_cleaning_summary(raw_df: pd.DataFrame, selected_steps: list[str]) -> None:
    """The execution log and the before/after tiles for the cleaning that has run."""
    clean_df = st.session_state[KEY_CLEAN_DF]
    if clean_df.empty:
        st.warning(_every_record_removed_message(selected_steps))

    st.markdown("### Execution Log")
    for msg in st.session_state[KEY_CLEAN_LOG]:
        st.code(f">> {msg}", language="bash")

    st.divider()
    st.markdown("### Cleaning Summary")

    if KEY_CLEANING_COMPLETED_AT in st.session_state:
        time_str = st.session_state[KEY_CLEANING_COMPLETED_AT].strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Completed at: {time_str}")
    if KEY_CLEANING_DURATION in st.session_state:
        st.caption(f"Duration: {st.session_state[KEY_CLEANING_DURATION]:.3f} seconds")

    c1, c2 = st.columns(2)

    # Health scores served from @st.cache_data; each distinct DataFrame
    # gets its own cache entry, so raw and cleaned never collide.
    raw_score = get_health_score(raw_df)
    clean_score = get_health_score(clean_df)

    c1.metric(
        "Records Removed",
        len(raw_df) - len(clean_df),
        help="Number of records removed during cleaning (duplicates and invalid entries)",
    )
    c2.metric(
        "Data Health Score",
        f"{clean_score}%",
        delta=format_score_delta(clean_score - raw_score),
        help="Overall data quality improvement after cleaning",
    )

    st.divider()
    st.info("Export options are available in the sidebar")


def render_preparation_tab(raw_df: pd.DataFrame) -> None:
    """Render the Data Preparation tab content."""
    st.subheader("Data Hygiene Pipeline")
    st.caption("Configure and execute intelligent data cleaning operations")

    show_tutorial_step(2)

    col_demo, col_log = st.columns([1, 2])

    with col_demo:
        selected_steps = [k for k, v in st.session_state[KEY_CLEANING_STEPS].items() if v]
        if selected_steps:
            st.success(f"Ready to apply **{len(selected_steps)} cleaning step(s)**")
            st.caption("Configure steps in the sidebar to customize your cleaning pipeline")
        else:
            show_empty_state(
                icon="",
                title="No Cleaning Steps Selected",
                message="Enable at least one cleaning step in the sidebar to process your data.",
            )

        show_tutorial_step(3)

        if st.button(
            "Run Cleaning Algorithms",
            type="primary",
            disabled=len(selected_steps) == 0,
            help="Execute the configured cleaning pipeline on your dataset",
        ):
            _run_cleaning(raw_df, selected_steps)

    with col_log:
        if st.session_state.get(KEY_CLEANED):
            _render_cleaning_summary(raw_df, selected_steps)
