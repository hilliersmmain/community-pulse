import streamlit as st
from utils.visualizer import (
    plot_attendance_trend,
    plot_role_distribution,
    plot_attendance_histogram,
    get_chart_export_config,
)
from utils.ui_helpers import (
    show_empty_state,
    show_tutorial_step,
    show_loading_message,
    get_contextual_message,
    MESSAGES,
)


def render_analytics_tab(raw_df):
    """Render the Analytics tab content."""
    show_tutorial_step(4)

    if st.session_state.get("cleaned"):
        clean_df = st.session_state["clean_df"]

        st.subheader("Member Insights & Analytics")
        st.caption("Explore your cleaned data with interactive visualizations")

        # Show which data state is being visualized
        st.info(
            "Viewing analytics for **cleaned data**. Toggle to 'Raw Data' in the sidebar to compare quality before cleaning."
        )

        # Role Filter
        st.markdown("### Filters")
        if "Role" not in clean_df.columns:
            st.warning("`Role` column is missing in cleaned data. Run cleaning again or upload a valid schema.")
            return
        available_roles = clean_df["Role"].unique().tolist()
        selected_roles = st.multiselect(
            "Filter by Role:",
            options=available_roles,
            default=available_roles,
            help="Select one or more member roles to focus your analysis on specific segments",
        )

        # Apply filter
        if selected_roles:
            filtered_df = clean_df[clean_df["Role"].isin(selected_roles)]
        else:
            show_empty_state(
                icon=MESSAGES["no_filters_selected"]["icon"],
                title=MESSAGES["no_filters_selected"]["title"],
                message=MESSAGES["no_filters_selected"]["message"],
            )
            st.info("Select at least one role to render analytics.")
            return

        st.divider()

        # Get export configuration
        export_config = get_chart_export_config()

        # Determine data state label - always "cleaned" when on Analytics Dashboard with cleaned data
        data_state = "cleaned"

        # Row 1: Attendance Trend and Histogram
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            with show_loading_message(get_contextual_message("rendering_charts")):
                fig_trend = plot_attendance_trend(filtered_df, data_state=data_state)
                st.plotly_chart(fig_trend, use_container_width=True, config=export_config)
            st.caption(
                "**Tip:** Click the camera icon to export as PNG. Hover over data points for detailed information."
            )

        with row1_col2:
            with show_loading_message(get_contextual_message("rendering_charts")):
                fig_hist = plot_attendance_histogram(filtered_df, data_state=data_state)
                st.plotly_chart(fig_hist, use_container_width=True, config=export_config)
            st.caption(
                "**Tip:** Red dashed line = mean attendance, green dotted line = median. Use these to identify outliers."
            )

        st.divider()

        # Row 2: Role Distribution
        st.subheader("Demographics")
        with show_loading_message(get_contextual_message("rendering_charts")):
            fig_role = plot_role_distribution(filtered_df, data_state=data_state)
            st.plotly_chart(fig_role, use_container_width=True, config=export_config)
        st.caption("**Tip:** Click legend items to show/hide specific roles. Double-click to isolate a single role.")

        # Before/After Comparison Section
        if st.session_state.get("cleaned"):
            st.divider()
            st.subheader("Before/After Cleaning Visual Comparison")

            # Create comparison tabs
            compare_tab1, compare_tab2 = st.tabs(["Side-by-Side Comparison", "Toggle View"])

            with compare_tab1:
                st.markdown("#### Compare Raw vs. Cleaned Data Visualizations")

                # Side by side comparison
                comp_col1, comp_col2 = st.columns(2)

                with comp_col1:
                    st.markdown("##### Raw Data")
                    with st.spinner("Loading raw data charts..."):
                        raw_trend = plot_attendance_trend(raw_df, data_state="raw")
                        st.plotly_chart(
                            raw_trend, use_container_width=True, config=export_config, key="raw_trend_compare"
                        )

                with comp_col2:
                    st.markdown("##### Cleaned Data")
                    with st.spinner("Loading cleaned data charts..."):
                        clean_trend = plot_attendance_trend(clean_df, data_state="cleaned")
                        st.plotly_chart(
                            clean_trend, use_container_width=True, config=export_config, key="clean_trend_compare"
                        )

            with compare_tab2:
                st.markdown("#### Interactive Toggle Comparison")
                comparison_state = st.radio(
                    "Select data state to visualize:",
                    options=["raw", "cleaned"],
                    format_func=lambda x: "Raw Data" if x == "raw" else "Cleaned Data",
                    horizontal=True,
                )

                if comparison_state == "raw":
                    compare_df = raw_df
                    state_label = "raw"
                else:
                    compare_df = clean_df
                    state_label = "cleaned"

                # Show all three charts for selected state
                with st.spinner(f"Loading {state_label} data visualizations..."):
                    st.plotly_chart(
                        plot_attendance_trend(compare_df, data_state=state_label),
                        use_container_width=True,
                        config=export_config,
                        key=f"{state_label}_trend_toggle",
                    )

                    toggle_col1, toggle_col2 = st.columns(2)
                    with toggle_col1:
                        st.plotly_chart(
                            plot_attendance_histogram(compare_df, data_state=state_label),
                            use_container_width=True,
                            config=export_config,
                            key=f"{state_label}_hist_toggle",
                        )
                    with toggle_col2:
                        st.plotly_chart(
                            plot_role_distribution(compare_df, data_state=state_label),
                            use_container_width=True,
                            config=export_config,
                            key=f"{state_label}_role_toggle",
                        )

    else:
        show_empty_state(
            icon=MESSAGES["no_data_cleaned"]["icon"],
            title=MESSAGES["no_data_cleaned"]["title"],
            message=MESSAGES["no_data_cleaned"]["message"],
        )

        st.info("""
        **Quick Steps to Generate Analytics:**

        1. Go to the **"Data Preparation"** tab above
        2. Configure which cleaning steps you want to apply (or leave defaults)
        3. Click the **"Run Cleaning Algorithms"** button
        4. Return here to see your interactive charts and insights!

        **What you'll see after cleaning:**
        - Time-series attendance trends
        - Distribution analysis histograms
        - Member demographics pie charts
        - Before/after comparison views
        """)
