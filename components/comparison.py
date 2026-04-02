import streamlit as st
from utils.health_metrics import DataHealthMetrics


def render_comparison(raw_df):
    """Render before/after cleaning comparison section."""
    st.divider()
    st.subheader("Before vs. After Cleaning Comparison")

    # Calculate metrics for both states
    raw_health = DataHealthMetrics(raw_df)
    raw_metrics = raw_health.get_detailed_metrics()
    clean_health = DataHealthMetrics(st.session_state["clean_df"])
    clean_metrics = clean_health.get_detailed_metrics()

    # Create comparison table
    comparison_col1, comparison_col2, comparison_col3, comparison_col4 = st.columns(4)

    with comparison_col1:
        st.markdown("#### Records")
        delta_records = clean_metrics["total_records"] - raw_metrics["total_records"]
        st.metric("Before", raw_metrics["total_records"], help="Total records before cleaning")
        st.metric(
            "After",
            clean_metrics["total_records"],
            delta=f"{delta_records}" if delta_records != 0 else "No change",
            help="Total records after cleaning",
        )

    with comparison_col2:
        st.markdown("#### Duplicates")
        st.metric("Before", raw_metrics["duplicate_records"], help="Duplicate records before cleaning")
        delta_dup = clean_metrics["duplicate_records"] - raw_metrics["duplicate_records"]
        st.metric(
            "After",
            clean_metrics["duplicate_records"],
            delta=f"{delta_dup}" if delta_dup != 0 else None,
            delta_color="inverse",
            help="Duplicate records after cleaning",
        )

    with comparison_col3:
        st.markdown("#### Missing Values")
        st.metric("Before", raw_metrics["null_cells"], help="Missing values before cleaning")
        delta_miss = clean_metrics["null_cells"] - raw_metrics["null_cells"]
        st.metric(
            "After",
            clean_metrics["null_cells"],
            delta=f"{delta_miss}" if delta_miss != 0 else None,
            delta_color="inverse",
            help="Missing values after cleaning",
        )

    with comparison_col4:
        st.markdown("#### Health Score")
        st.metric("Before", f"{raw_metrics['overall_score']}%", help="Overall health score before cleaning")
        improvement = clean_metrics["overall_score"] - raw_metrics["overall_score"]
        st.metric(
            "After",
            f"{clean_metrics['overall_score']}%",
            delta=f"+{improvement:.1f}%",
            help="Overall health score after cleaning",
        )
