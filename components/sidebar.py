import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.data_generator import generate_messy_data
from utils.health_metrics import DataHealthMetrics
from utils.ui_helpers import show_loading_message, show_success_message, show_error_message, get_contextual_message
from utils.constants import (
    DATA_PATH,
    DEFAULT_NUM_RECORDS,
    DEFAULT_MESSINESS,
    MESSINESS_OPTIONS,
    MIN_RECORDS,
    MAX_RECORDS,
    RECORDS_STEP,
    CLEANING_STEPS_DEFAULT,
    REQUIRED_COLUMNS,
)


def render_sidebar():
    """Render the complete sidebar with all controls."""
    st.sidebar.header("Data Controls")

    if "num_records" not in st.session_state:
        st.session_state["num_records"] = DEFAULT_NUM_RECORDS
    if "messiness_level" not in st.session_state:
        st.session_state["messiness_level"] = DEFAULT_MESSINESS

    with st.sidebar.expander("Quick Stats", expanded=True):
        stats_df = None
        if st.session_state.get("cleaned") and "clean_df" in st.session_state:
            stats_df = st.session_state["clean_df"]
            is_cleaned = True
        elif os.path.exists(DATA_PATH):
            try:
                stats_df = pd.read_csv(DATA_PATH)
                is_cleaned = False
            except Exception:
                pass

        if stats_df is not None:
            health = DataHealthMetrics(stats_df)
            metrics = health.get_detailed_metrics()

            st.metric("Records", metrics["total_records"])

            score_val = f"{metrics['overall_score']}%"
            if is_cleaned:
                st.metric("Health Score", score_val)
            else:
                st.metric("Health Score", score_val, help="Score based on raw data")

            if "data_loaded_at" in st.session_state:
                st.caption(f"Last loaded: {st.session_state['data_loaded_at'].strftime('%H:%M:%S')}")

            if st.session_state.get("cleaned") and "cleaning_completed_at" in st.session_state:
                st.caption(f"Last cleaned: {st.session_state['cleaning_completed_at'].strftime('%H:%M:%S')}")
        else:
            st.caption("No data available")

    st.sidebar.divider()

    # --- 2. DATA SOURCE SELECTOR ---
    data_source = st.sidebar.radio(
        "Data Source",
        options=["Generate Sample", "Upload CSV"],
        help="Choose how to load data into the dashboard",
        horizontal=True,
    )

    if data_source == "Generate Sample":
        st.sidebar.subheader("Data Generation")

        num_records = st.sidebar.slider(
            "Number of Records",
            min_value=MIN_RECORDS,
            max_value=MAX_RECORDS,
            value=st.session_state["num_records"],
            step=RECORDS_STEP,
            help="Select how many sample records to generate. More records = more realistic analysis, but slower processing.",
        )
        st.session_state["num_records"] = num_records

        messiness_level = st.sidebar.selectbox(
            "Messiness Level",
            options=MESSINESS_OPTIONS,
            index=MESSINESS_OPTIONS.index(st.session_state["messiness_level"]),
            help="Control data quality simulation:\n\u2022 Low: 3% duplicates, 2% errors (clean CRM)\n\u2022 Medium: 10% duplicates, 5% errors (typical export)\n\u2022 High: 20% duplicates, 15% errors (legacy system)",
        )
        st.session_state["messiness_level"] = messiness_level

        if st.sidebar.button("Generate New Data", type="primary", help="Create fresh sample data"):
            with show_loading_message(get_contextual_message("loading_data")):
                if not os.path.exists("data"):
                    os.makedirs("data")
                try:
                    generate_messy_data(num_records=num_records, save_path=DATA_PATH, messiness_level=messiness_level)
                    show_success_message(
                        get_contextual_message("data_generated", num_records=num_records, messiness=messiness_level)
                    )
                    st.session_state["cleaned"] = False  # Reset state
                    st.session_state["data_generated_at"] = datetime.now()
                    st.session_state["data_loaded_at"] = datetime.now()
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
            help="Upload a CSV file with community data. Required columns: Name, Email",
        )

        if uploaded_file is not None:
            try:
                upload_df = pd.read_csv(uploaded_file)

                # Validate required columns
                missing_cols = [col for col in REQUIRED_COLUMNS if col not in upload_df.columns]
                if missing_cols:
                    st.sidebar.error(f"Missing required columns: {', '.join(missing_cols)}")
                else:
                    # Save to CSV so the rest of the app can load it
                    if not os.path.exists("data"):
                        os.makedirs("data")
                    upload_df.to_csv(DATA_PATH, index=False)
                    st.session_state["cleaned"] = False
                    st.session_state["data_loaded_at"] = datetime.now()
                    st.sidebar.success(f"Uploaded {len(upload_df)} records successfully!")
            except Exception as e:
                st.sidebar.error(f"Error reading file: {e}")
        else:
            st.sidebar.info("Upload a CSV file to get started")

    st.sidebar.divider()

    # --- 3. CLEANING PIPELINE CONTROLS ---
    st.sidebar.subheader("Cleaning Pipeline")

    # Initialize cleaning steps in session state
    if "cleaning_steps" not in st.session_state:
        st.session_state["cleaning_steps"] = CLEANING_STEPS_DEFAULT.copy()

    with st.sidebar.expander("Configure Cleaning Steps", expanded=False):
        st.session_state["cleaning_steps"]["standardize_names"] = st.checkbox(
            "Standardize Names",
            value=st.session_state["cleaning_steps"]["standardize_names"],
            help="Convert names to Title Case (e.g., 'john doe' \u2192 'John Doe')",
        )

        st.session_state["cleaning_steps"]["fix_emails"] = st.checkbox(
            "Fix Email Formats",
            value=st.session_state["cleaning_steps"]["fix_emails"],
            help="Fix invalid emails (e.g., 'user at domain.com' \u2192 'user@domain.com')",
        )

        st.session_state["cleaning_steps"]["remove_duplicates"] = st.checkbox(
            "Remove Duplicates",
            value=st.session_state["cleaning_steps"]["remove_duplicates"],
            help="Remove duplicate rows based on Email and Name",
        )

        st.session_state["cleaning_steps"]["clean_dates"] = st.checkbox(
            "Clean Dates",
            value=st.session_state["cleaning_steps"]["clean_dates"],
            help="Standardize date formats to YYYY-MM-DD",
        )

        st.session_state["cleaning_steps"]["handle_missing_values"] = st.checkbox(
            "Handle Missing Values",
            value=st.session_state["cleaning_steps"]["handle_missing_values"],
            help="Fill missing attendance values with 0",
        )

    # Show preview of selected steps
    selected_steps = [k for k, v in st.session_state["cleaning_steps"].items() if v]
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

    if st.session_state.get("cleaned") and st.session_state.get("clean_df") is not None:
        export_choice = st.sidebar.radio(
            "Export data:",
            options=["raw", "cleaned"],
            format_func=lambda x: "Raw Data" if x == "raw" else "Cleaned Data",
            help="Choose which dataset to export",
        )
        if export_choice == "cleaned":
            export_df = st.session_state["clean_df"]
            export_label = "Cleaned"
        else:
            if os.path.exists(DATA_PATH):
                export_df = pd.read_csv(DATA_PATH)
                export_label = "Raw"
    else:
        if os.path.exists(DATA_PATH):
            export_df = pd.read_csv(DATA_PATH)
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
        json_data = export_df.to_json(orient="records", indent=2)
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
    if st.session_state.get("cleaned"):
        st.sidebar.radio(
            "Current view:",
            options=["raw", "cleaned"],
            format_func=lambda x: "Raw Data" if x == "raw" else "Cleaned Data",
            key="view_state",
            help="Toggle between raw and cleaned data views",
        )
    else:
        st.sidebar.info("Clean data first to enable view toggle")
        if "view_state" not in st.session_state:
            st.session_state["view_state"] = "raw"

    # Reset to Raw Data button
    if st.session_state.get("cleaned"):
        if st.sidebar.button("Reset to Raw Data", help="Clear cleaned data and return to raw state"):
            st.session_state["cleaned"] = False
            if "clean_df" in st.session_state:
                del st.session_state["clean_df"]
            if "clean_log" in st.session_state:
                del st.session_state["clean_log"]
            # Delete view_state key so it can be reset
            if "view_state" in st.session_state:
                del st.session_state["view_state"]
            st.sidebar.success("Reset to raw data!")
            st.rerun()

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
       Navigate to 'Data Cleaning Ops' tab
       Configure cleaning steps (or use defaults)
       Click 'Run Cleaning Algorithms'

    3. **Analyze Results**
       View insights in 'Analytics Dashboard' tab
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
