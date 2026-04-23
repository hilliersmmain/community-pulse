import streamlit as st
import os
from datetime import datetime
from utils.ui_helpers import initialize_session_state, show_welcome_modal, show_empty_state, MESSAGES
from utils.health_metrics import DataHealthMetrics
from utils.constants import DATA_PATH, CUSTOM_CSS
from utils.data_access import load_csv
from utils.session_keys import KEY_DATA_LOADED_AT, KEY_VIEW_STATE, KEY_CLEANED, KEY_CLEAN_DF, KEY_CLEANING_COMPLETED_AT
from components.sidebar import render_sidebar
from components.kpi_display import render_kpi_section
from components.comparison import render_comparison
from components.tab_preparation import render_preparation_tab
from components.tab_analytics import render_analytics_tab
from components.tab_explorer import render_explorer_tab

st.set_page_config(
    page_title="Community Pulse | Data Dashboard", page_icon="🔵", layout="wide", initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

initialize_session_state()

if st.session_state.get("show_welcome", False):
    show_welcome_modal()

st.title("Community Pulse Dashboard")
st.markdown(
    """
<div style="margin-bottom: 2rem;">
    <p style="font-size: 1.1rem; line-height: 1.6;">
        Data quality management and member analytics platform.
        Transform raw data into actionable insights with automated cleaning pipelines.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

render_sidebar()

# Load Data
if os.path.exists(DATA_PATH):
    raw_df = load_csv(DATA_PATH)
    if KEY_DATA_LOADED_AT not in st.session_state:
        st.session_state[KEY_DATA_LOADED_AT] = datetime.now()
else:
    show_empty_state(
        icon=MESSAGES["no_data_generated"]["icon"],
        title=MESSAGES["no_data_generated"]["title"],
        message=MESSAGES["no_data_generated"]["message"],
    )
    st.info("""
    **Getting Started:**

    1. Look for the **sidebar on the left**
    2. Adjust your data generation settings (number of records, messiness level)
    3. Click the **"Generate New Data"** button
    4. Your dashboard will automatically populate with sample data!

    **What is data messiness?**
    - **Low**: Simulates a well-maintained CRM system
    - **Medium**: Typical data export with some quality issues
    - **High**: Legacy system with significant data quality problems
    """)
    st.stop()

# Initialize view state
if KEY_VIEW_STATE not in st.session_state:
    st.session_state[KEY_VIEW_STATE] = "raw"

# Determine which dataframe to show based on state
if st.session_state.get(KEY_CLEANED) and st.session_state[KEY_VIEW_STATE] == "cleaned":
    active_df = st.session_state[KEY_CLEAN_DF]
    state_label = "Cleaned"
else:
    active_df = raw_df
    state_label = "Raw"

# Calculate health metrics for active data state
health_metrics = DataHealthMetrics(active_df)
metrics = health_metrics.get_detailed_metrics()

# Display current state and timestamp
st.markdown(f"### Current View: **{state_label} Data**")
if st.session_state.get(KEY_CLEANED) and st.session_state[KEY_VIEW_STATE] == "cleaned":
    if KEY_CLEANING_COMPLETED_AT in st.session_state:
        time_str = st.session_state[KEY_CLEANING_COMPLETED_AT].strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last cleaned: {time_str}")
else:
    if KEY_DATA_LOADED_AT in st.session_state:
        time_str = st.session_state[KEY_DATA_LOADED_AT].strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Data loaded: {time_str}")

st.divider()

render_kpi_section(metrics)

if st.session_state.get(KEY_CLEANED):
    render_comparison(raw_df)

# Tabs for Workflow
tab1, tab2, tab3 = st.tabs(["Data Preparation", "Analytics", "Data Explorer"])

with tab1:
    render_preparation_tab(raw_df)

with tab2:
    render_analytics_tab(raw_df)

with tab3:
    render_explorer_tab(active_df, state_label, metrics)
