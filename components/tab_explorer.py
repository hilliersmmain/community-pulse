import streamlit as st


def render_explorer_tab(active_df, state_label, metrics):
    """Render the Data Explorer tab content."""
    st.subheader(f"{state_label} Data Inspector")

    # Show health metrics for the current view
    st.markdown("### Data Health Overview")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    metric_col1.metric("Completeness", f"{metrics['completeness_score']}%", help="Percentage of non-null values")
    metric_col2.metric("Uniqueness", f"{metrics['duplicate_score']}%", help="Percentage of unique records")
    metric_col3.metric("Formatting", f"{metrics['formatting_score']}%", help="Validity of data formats")
    metric_col4.metric("Overall Health", f"{metrics['overall_score']}%", help="Composite health score")

    st.divider()
    st.dataframe(active_df, use_container_width=True)
