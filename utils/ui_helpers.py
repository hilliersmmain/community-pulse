"""UI Helper Module"""

import streamlit as st
from typing import Callable, Optional

from utils.session_keys import KEY_FLASH, KEY_RAW_DF


def initialize_session_state():
    """Initialize session state variables for UI features."""
    if "show_welcome" not in st.session_state:
        st.session_state["show_welcome"] = True
    if "tutorial_mode" not in st.session_state:
        st.session_state["tutorial_mode"] = False
    if "tutorial_step" not in st.session_state:
        st.session_state["tutorial_step"] = 0


def show_welcome_modal():
    """Display a welcome modal for first-time users."""
    if not st.session_state.get("show_welcome", False):
        return False

    with st.container():
        st.markdown(
            """
        <style>
        .welcome-modal {
            padding: 2rem;
            border-radius: 0.5rem;
            background: #f1f3f5;
            color: #333;
            margin-bottom: 2rem;
            border-left: 5px solid #1f77b4;
        }
        .welcome-title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .welcome-subtitle {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }
        .feature-list {
            margin: 1rem 0;
        }
        .feature-item {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="welcome-modal">
            <div class="welcome-title">Welcome to Community Pulse</div>
            <div class="welcome-subtitle">
                Transform messy member data into actionable insights in minutes.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### What You Can Do")
            st.markdown("""
            - **Generate** realistic messy data
            - **Clean** automatically with AI-powered tools
            - **Visualize** insights with interactive charts
            - **Export** cleaned data in multiple formats
            """)

        with col2:
            st.markdown("### Quick Start")
            st.markdown("""
            1. Click **"Generate New Data"** in the sidebar
            2. Navigate to **"Data Preparation"** tab
            3. Click **"Run Cleaning Algorithms"**
            4. Explore insights in **"Analytics"**
            """)

        with col3:
            st.markdown("### Pro Tips")
            st.markdown("""
            - Hover over **info icons** for help
            - Toggle between **raw** and **cleaned** views
            - Click **Start Tutorial** below for a step-by-step tour
            """)

        st.divider()

        col_dismiss, col_tutorial, col_start = st.columns([1, 1, 1])

        with col_dismiss:
            if st.button("Dismiss", width="stretch"):
                st.session_state["show_welcome"] = False
                st.rerun()

        with col_tutorial:
            if st.button("Start Tutorial", type="secondary", width="stretch"):
                st.session_state["show_welcome"] = False
                st.session_state["tutorial_mode"] = True
                st.session_state["tutorial_step"] = 0
                st.rerun()

        with col_start:
            if st.button("Get Started", type="primary", width="stretch"):
                st.session_state["show_welcome"] = False
                st.rerun()

    return True


def show_empty_state(
    icon: str = "",
    title: str = "No Data Available",
    message: str = "Get started by generating some data.",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None,
):
    """Display an empty state message with optional action button."""
    st.markdown(
        f"""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        background: #f8f9fa;
        border-radius: 0.5rem;
        margin: 2rem 0;
    ">
        <div style="font-size: 2rem; margin-bottom: 1rem; color: #ccc;">{icon}</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #333; margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="font-size: 1rem; color: #666; margin-bottom: 1.5rem;">
            {message}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, type="primary", width="stretch"):
                action_callback()


def format_score_delta(change: float) -> str:
    """Format a health-score change as a signed percentage: "+1.5%", "-0.2%"."""
    return f"{change:+.1f}%"


def show_info_tooltip(text: str, tooltip: str) -> str:
    """Create inline text with a tooltip icon."""
    return f"{text} :gray[ⓘ]"


TUTORIAL_STEPS = {
    0: {
        "title": "Step 1: Generate Data",
        "message": "Use the sidebar controls to generate messy sample data. Adjust the number of records and messiness level to simulate real-world scenarios.",
    },
    1: {
        "title": "Step 2: Review KPIs",
        "message": "Check the Key Performance Indicators to understand the current data quality. Red metrics indicate issues that need attention.",
    },
    2: {
        "title": "Step 3: Configure Cleaning",
        "message": "Go to the Data Preparation tab and configure which cleaning steps to apply. Each step targets specific data quality issues.",
    },
    3: {
        "title": "Step 4: Run Cleaning",
        "message": "Click 'Run Cleaning Algorithms' to automatically fix data quality issues. Watch the execution log for details.",
    },
    4: {
        "title": "Step 5: View Analytics",
        "message": "Navigate to the Analytics tab to visualize insights from your cleaned data. Use filters to focus on specific segments.",
    },
}

TUTORIAL_COMPLETED = "Tutorial completed! You're now ready to use Community Pulse effectively."


def show_tutorial_step(step: int) -> bool:
    """Render the tutorial card for *step* if the tutorial is on and has reached it.

    Each caller passes the step it anchors (the sidebar 0, the KPI row 1, the Data Preparation tab 2 and
    3, the Analytics tab 4), so one card and one set of buttons render per run. "Next" on the last step
    ends the tutorial and queues the completion message, which app.py shows on the run after the rerun.
    """
    if not st.session_state.get("tutorial_mode", False):
        return False

    current_step = st.session_state.get("tutorial_step", 0)
    if current_step != step or current_step not in TUTORIAL_STEPS:
        return False

    step_info = TUTORIAL_STEPS[current_step]
    st.info(f"""
    **{step_info['title']}**

    {step_info['message']}
    """)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Skip Tutorial"):
            st.session_state["tutorial_mode"] = False
            st.session_state["tutorial_step"] = 0
            st.rerun()

    with col2:
        if current_step > 0:
            if st.button("Previous"):
                st.session_state["tutorial_step"] = current_step - 1
                st.rerun()

    with col3:
        # Steps 1 to 4 anchor on the KPI row and the tabs, which exist only once data is loaded.
        waiting_for_data = current_step == 0 and KEY_RAW_DF not in st.session_state
        if st.button(
            "Next",
            type="primary",
            disabled=waiting_for_data,
            help="Generate or upload data first" if waiting_for_data else None,
        ):
            if current_step == max(TUTORIAL_STEPS):
                st.session_state["tutorial_mode"] = False
                st.session_state["tutorial_step"] = 0
                queue_flash(TUTORIAL_COMPLETED)
            else:
                st.session_state["tutorial_step"] = current_step + 1
            st.rerun()

    return True


def queue_flash(message: str) -> None:
    """Keep *message* for the next run: ``st.rerun()`` discards everything the current run drew."""
    st.session_state[KEY_FLASH] = message


def show_flash() -> None:
    """Show the message queued by ``queue_flash`` as a toast, once."""
    message = st.session_state.pop(KEY_FLASH, None)
    if message:
        st.toast(message)


def show_loading_message(message: str = "Processing your data..."):
    """Display a context-aware loading message."""
    return st.spinner(f"{message}")


def show_success_message(message: str, icon: str = ""):
    """Display a success message with icon."""
    st.success(f"{message}")


def show_error_message(message: str, details: Optional[str] = None):
    """Display a context-aware error message."""
    st.error(f"{message}")
    if details:
        with st.expander("Error Details"):
            st.code(details)


def show_warning_message(message: str, context: Optional[str] = None):
    """Display a context-aware warning message."""
    st.warning(f"{message}")
    if context:
        st.info(f"Tip: {context}")


# Context-aware message templates
MESSAGES = {
    "no_data_generated": {
        "icon": "",
        "title": "No Data Generated Yet",
        "message": "Start by clicking 'Generate New Data' in the sidebar to create sample data for analysis.",
    },
    "no_data_cleaned": {
        "icon": "",
        "title": "Data Not Cleaned Yet",
        "message": "Navigate to the 'Data Preparation' tab and run the cleaning pipeline to process your data.",
    },
    "no_filters_selected": {
        "icon": "",
        "title": "No Filters Selected",
        "message": "Select at least one role from the filter dropdown to view analytics for specific segments.",
    },
    "empty_analytics": {
        "icon": "",
        "title": "No Analytics Available",
        "message": "Clean your data first to generate insights and visualizations.",
    },
    "cleaning_success": "Data cleaning completed successfully! {records_processed} records processed.",
    "data_generated": "Successfully generated {num_records} records with {messiness} messiness level.",
    "export_ready": "Your data is ready to export. Choose CSV or JSON format from the sidebar.",
    "loading_data": "Loading your data, please wait...",
    "processing_cleaning": "Running {step_count} cleaning operations...",
    "calculating_metrics": "Calculating data health metrics...",
    "rendering_charts": "Rendering interactive visualizations...",
}


def get_contextual_message(key: str, **kwargs) -> str:
    """Get a context-aware message template."""
    template = MESSAGES.get(key, "")
    if isinstance(template, str):
        return template.format(**kwargs)
    return ""
