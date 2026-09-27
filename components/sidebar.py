import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.data_generator import generate_messy_data
from utils.health_metrics import DataHealthMetrics
from utils.ui_helpers import show_loading_message, show_success_message, show_error_message, get_contextual_message
from utils.data_access import load_csv, save_csv, ensure_data_dir
from utils.upload_validation import validate_upload_dataframe
from utils.session_keys import (
    KEY_CLEANED,
    KEY_CLEAN_DF,
    KEY_VIEW_STATE,
    KEY_CLEANING_STEPS,
    KEY_DATA_LOADED_AT,
    KEY_DATA_GENERATED_AT,
    KEY_CLEANING_COMPLETED_AT,
    KEY_UPLOADED_FILE_ID,
    reset_clean_state,
)
from utils.constants import (
    DATA_PATH,
    DATA_DIR,
    DEFAULT_NUM_RECORDS,
    DEFAULT_MESSINESS,
    MESSINESS_OPTIONS,
    MIN_RECORDS,
    MAX_RECORDS,
    RECORDS_STEP,
    CLEANING_STEPS_DEFAULT,
    MAX_UPLOAD_SIZE_MB,
)

CLEANING_STEP_CHECKBOXES = (
    ("standardize_names", "Standardize Names", "Convert names to Title Case (e.g., 'john doe' → 'John Doe')"),
    ("fix_emails", "Fix Email Formats", "Fix invalid emails (e.g., 'user at domain.com' → 'user@domain.com')"),
    ("remove_duplicates", "Remove Duplicates", "Remove duplicate rows based on Email and Name"),
    ("clean_dates", "Clean Dates", "Standardize date formats to YYYY-MM-DD"),
    ("handle_missing_values", "Handle Missing Values", "Fill missing attendance values with 0"),
)


def _store_upload(file_id: str, upload_df: pd.DataFrame) -> None:
    """Make a validated upload the raw data, once per uploaded file.

    The uploader hands back the same file on every rerun while it stays in the widget;
    saving it again each time would clear the cleaned state after every interaction.
    """
    if st.session_state.get(KEY_UPLOADED_FILE_ID) == file_id:
        return
    ensure_data_dir()
    save_csv(upload_df, DATA_PATH)
    reset_clean_state()
    st.session_state[KEY_DATA_LOADED_AT] = datetime.now()
    st.session_state[KEY_UPLOADED_FILE_ID] = file_id


def export_json(df: pd.DataFrame) -> str:
    """Serialize data for the JSON download, with dates as ISO 8601 strings rather than epoch ms."""
    return df.to_json(orient="records", indent=2, date_format="iso")


def render_sidebar() -> None:
    """Render the complete sidebar with all controls."""
    st.sidebar.header("Data Controls")

    # Both are widget keys. Streamlit drops a widget's key on any run that doesn't render the
    # widget (while "Upload CSV" is selected), so write them back each run to keep the choice.
    st.session_state["num_records"] = st.session_state.get("num_records", DEFAULT_NUM_RECORDS)
    st.session_state["messiness_level"] = st.session_state.get("messiness_level", DEFAULT_MESSINESS)

    with st.sidebar.expander("Quick Stats", expanded=True):
        stats_df = None
        if st.session_state.get(KEY_CLEANED) and KEY_CLEAN_DF in st.session_state:
            stats_df = st.session_state[KEY_CLEAN_DF]
            is_cleaned = True
        elif os.path.exists(DATA_PATH):
            try:
                stats_df = load_csv(DATA_PATH)
                is_cleaned = False
            except Exception:
                st.caption("Unable to load quick stats.")

        if stats_df is not None:
            health = DataHealthMetrics(stats_df)
            metrics = health.get_detailed_metrics()

            st.metric("Records", metrics["total_records"])

            score_val = f"{metrics['overall_score']}%"
            if is_cleaned:
                st.metric("Health Score", score_val)
            else:
                st.metric("Health Score", score_val, help="Score based on raw data")

            if KEY_DATA_LOADED_AT in st.session_state:
                st.caption(f"Last loaded: {st.session_state[KEY_DATA_LOADED_AT].strftime('%H:%M:%S')}")

            if st.session_state.get(KEY_CLEANED) and KEY_CLEANING_COMPLETED_AT in st.session_state:
                st.caption(f"Last cleaned: {st.session_state[KEY_CLEANING_COMPLETED_AT].strftime('%H:%M:%S')}")
        else:
            st.caption("No data available")

    st.sidebar.divider()

    # --- 2. DATA SOURCE SELECTOR ---
    data_source = st.sidebar.radio(
        "Data Source",
        options=["Generate Sample", "Upload CSV"],
        help="Choose how to load data into the dashboard",
        horizontal=True,
        key="data_source",
    )

    if data_source == "Generate Sample":
        st.sidebar.subheader("Data Generation")

        num_records = st.sidebar.slider(
            "Number of Records",
            min_value=MIN_RECORDS,
            max_value=MAX_RECORDS,
            step=RECORDS_STEP,
            key="num_records",
            help="Select how many sample records to generate. More records = more realistic analysis, but slower processing.",
        )

        messiness_level = st.sidebar.selectbox(
            "Messiness Level",
            options=MESSINESS_OPTIONS,
            key="messiness_level",
            help="Control data quality simulation:\n\u2022 Low: 3% duplicates, 2% errors (clean CRM)\n\u2022 Medium: 10% duplicates, 5% errors (typical export)\n\u2022 High: 20% duplicates, 15% errors (legacy system)",
        )

        if st.sidebar.button("Generate New Data", type="primary", help="Create fresh sample data"):
            with show_loading_message(get_contextual_message("loading_data")):
                try:
                    ensure_data_dir()
                    generate_messy_data(num_records=num_records, save_path=DATA_PATH, messiness_level=messiness_level)
                    show_success_message(
                        get_contextual_message("data_generated", num_records=num_records, messiness=messiness_level)
                    )
                    reset_clean_state()
                    st.session_state[KEY_DATA_GENERATED_AT] = datetime.now()
                    st.session_state[KEY_DATA_LOADED_AT] = datetime.now()
                    st.rerun()
                except Exception as e:
                    show_error_message(
                        "Unable to generate sample data. Please try again with different settings.", str(e)
                    )
    else:
        st.sidebar.subheader("Upload Data")
        uploaded_file = st.sidebar.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            help="Upload a CSV with required columns: Name, Email, Role, Join_Date, Event_Attendance",
        )

        if uploaded_file is not None:
            try:
                upload_size_mb = uploaded_file.size / (1024 * 1024)
                if upload_size_mb > MAX_UPLOAD_SIZE_MB:
                    st.sidebar.error(f"File too large ({upload_size_mb:.2f}MB). Max allowed is {MAX_UPLOAD_SIZE_MB}MB.")
                else:
                    upload_df = pd.read_csv(uploaded_file)

                    validation = validate_upload_dataframe(upload_df)
                    if not validation.is_valid:
                        for error in validation.errors:
                            st.sidebar.error(error)
                    else:
                        _store_upload(uploaded_file.file_id, upload_df)
                        st.sidebar.success(f"Uploaded {len(upload_df)} records successfully to `{DATA_DIR}`.")
            except Exception as e:
                st.sidebar.error("Error reading file. Please ensure it is a valid CSV.")
                st.sidebar.caption(f"Details: {e}")
        else:
            st.sidebar.info("Upload a CSV file to get started")

    st.sidebar.divider()

    # --- 3. CLEANING PIPELINE CONTROLS ---
    st.sidebar.subheader("Cleaning Pipeline")

    # Initialize cleaning steps in session state
    st.session_state.setdefault(KEY_CLEANING_STEPS, CLEANING_STEPS_DEFAULT.copy())

    with st.sidebar.expander("Configure Cleaning Steps", expanded=False):
        steps = st.session_state[KEY_CLEANING_STEPS]
        for step, label, help_text in CLEANING_STEP_CHECKBOXES:
            # A keyed checkbox seeded once; passing value= each run would make every
            # change give the widget a new identity, and the next change would be lost.
            widget_key = f"cleaning_step_{step}"
            st.session_state.setdefault(widget_key, steps[step])
            steps[step] = st.checkbox(label, key=widget_key, help=help_text)

    # Show preview of selected steps
    selected_steps = [k for k, v in st.session_state[KEY_CLEANING_STEPS].items() if v]
    if selected_steps:
        st.sidebar.caption(f"\u2713 {len(selected_steps)} step(s) selected")
    else:
        st.sidebar.warning("No cleaning steps selected")

    st.sidebar.divider()

    # --- 4. EXPORT OPTIONS ---
    st.sidebar.subheader("Export Options")

    # Check if we have cleaned data to export
    export_df = None
    export_label = "Raw"

    if st.session_state.get(KEY_CLEANED) and st.session_state.get(KEY_CLEAN_DF) is not None:
        export_choice = st.sidebar.radio(
            "Export data:",
            options=["raw", "cleaned"],
            format_func=lambda x: "Raw Data" if x == "raw" else "Cleaned Data",
            help="Choose which dataset to export",
        )
        if export_choice == "cleaned":
            export_df = st.session_state[KEY_CLEAN_DF]
            export_label = "Cleaned"
        else:
            if os.path.exists(DATA_PATH):
                export_df = load_csv(DATA_PATH)
                export_label = "Raw"
    else:
        if os.path.exists(DATA_PATH):
            export_df = load_csv(DATA_PATH)
            export_label = "Raw"

    if export_df is not None:
        # CSV Export
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            label=f"Download CSV ({export_label})",
            data=csv_data,
            file_name=f"community_data_{export_label.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

        # JSON Export
        json_data = export_json(export_df)
        st.sidebar.download_button(
            label=f"Download JSON ({export_label})",
            data=json_data,
            file_name=f"community_data_{export_label.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

    else:
        st.sidebar.info("Generate data to enable export options")

    st.sidebar.divider()

    # --- 5. RESET & VIEW STATE ---
    st.sidebar.subheader("Data View")

    # Data State Toggle
    if st.session_state.get(KEY_CLEANED):
        st.sidebar.radio(
            "Current view:",
            options=["raw", "cleaned"],
            format_func=lambda x: "Raw Data" if x == "raw" else "Cleaned Data",
            key="view_state",
            help="Toggle between raw and cleaned data views",
        )
    else:
        st.sidebar.info("Clean data first to enable view toggle")
        st.session_state.setdefault(KEY_VIEW_STATE, "raw")

    # Reset to Raw Data button
    if st.session_state.get(KEY_CLEANED):
        # A callback runs before the next script run, so it can set view_state before the
        # radio above claims that key; writing it after the radio renders raises.
        st.sidebar.button(
            "Reset to Raw Data",
            help="Clear cleaned data and return to raw state",
            key="reset_to_raw",
            on_click=reset_clean_state,
        )

    st.sidebar.divider()

    # --- 6. HELP/GUIDE SECTION ---
    with st.sidebar.expander("Help & Guide", expanded=False):
        st.markdown("""
    ### Quick Start Guide

    **For First-Time Users:**

    1. **Generate Data**
       Use the slider to set record count (100-1000)
       Choose messiness level based on your scenario

    2. **Clean Data**
       Navigate to 'Data Preparation' tab
       Configure cleaning steps (or use defaults)
       Click 'Run Cleaning Algorithms'

    3. **Analyze Results**
       View insights in 'Analytics' tab
       Use filters to focus on specific segments
       Compare raw vs. cleaned data

    4. **Export**
       Download cleaned data as CSV or JSON
       Use export buttons in charts for visualizations

    ---

    ### Pro Tips

    - **Data Messiness Levels:**
      - **Low:** Well-maintained CRM (~3% issues)
      - **Medium:** Typical export (~10% issues)
      - **High:** Legacy system (~20% issues)

    - **Quick Stats Panel:**
      Shows real-time data health at a glance
      Updates automatically after cleaning

    - **View Toggle:**
      Switch between raw/cleaned data
      Compare before/after improvements

    - **Tutorial Mode:**
      Enable for step-by-step guidance
      Perfect for learning the workflow

    ---

    ### Cleaning Steps Explained

    - **Standardize Names:** Fixes capitalization (e.g., "john doe" \u2192 "John Doe")
    - **Fix Emails:** Corrects format issues and removes invalid entries
    - **Remove Duplicates:** Eliminates duplicate records based on email/name
    - **Clean Dates:** Standardizes date formats to YYYY-MM-DD
    - **Handle Missing:** Fills missing attendance values with 0

    ---

    ### Need Help?

    - Hover over **info icons** for context-specific help
    - Enable **Tutorial Mode** for guided walkthrough
    - Check **What's New** for latest features
    - All metrics include detailed tooltips
    """)
