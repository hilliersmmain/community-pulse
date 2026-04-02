import streamlit as st
from utils.ui_helpers import show_tutorial_step
from utils.constants import SCORE_THRESHOLDS


def render_kpi_section(metrics):
    """Render the KPI metrics row."""
    # 1. Dynamic KPI Row with enhanced tooltips
    st.subheader("Key Performance Indicators")
    st.caption("Real-time data quality metrics to track your cleaning progress")

    show_tutorial_step(1)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        col1.metric(
            "Total Records",
            metrics["total_records"],
            help="The complete count of all records in your dataset, including duplicates",
        )
        col1.metric(
            "Unique Records",
            metrics["unique_records"],
            help="Number of distinct records after removing duplicates (higher is better for data quality)",
        )

    with col2:
        col2.metric(
            "Duplicate Records",
            metrics["duplicate_records"],
            delta=f"-{metrics['duplicate_records']}" if metrics["duplicate_records"] > 0 else None,
            delta_color="inverse",
            help="Records that appear more than once, based on email and name matching (lower is better)",
        )
        col2.metric(
            "Missing Values",
            metrics["null_cells"],
            delta=f"-{metrics['null_cells']}" if metrics["null_cells"] > 0 else None,
            delta_color="inverse",
            help="Total count of empty or null cells across all columns (0 is ideal)",
        )

    with col3:
        col3.metric(
            "Completeness Score",
            f"{metrics['completeness_score']}%",
            help="Percentage of cells with valid data (100% = no missing values, ideal for analysis)",
        )
        col3.metric(
            "Duplicate Score",
            f"{metrics['duplicate_score']}%",
            help="Percentage of unique records (100% = no duplicates, clean dataset)",
        )

    with col4:
        col4.metric(
            "Formatting Score",
            f"{metrics['formatting_score']}%",
            help="Percentage of properly formatted data including valid emails, dates, and standardized names (100% is ideal)",
        )
        # Overall health score with color coding
        score = metrics["overall_score"]
        if score >= SCORE_THRESHOLDS["excellent"]:
            score_label = "Excellent"
        elif score >= SCORE_THRESHOLDS["good"]:
            score_label = "Good"
        else:
            score_label = "Needs Work"

        col4.metric(
            "Data Health Score",
            f"{score}%",
            help=f"Overall data quality assessment: {score_label}\n\nCalculated from:\n\u2022 40% Completeness\n\u2022 30% Uniqueness\n\u2022 30% Formatting\n\n90%+ = Excellent | 70-89% = Good | <70% = Needs Improvement",
        )
