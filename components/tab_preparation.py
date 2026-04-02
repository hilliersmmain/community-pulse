import streamlit as st
from datetime import datetime
from utils.cleaner import DataCleaner
from utils.health_metrics import DataHealthMetrics
from utils.ui_helpers import (
    show_empty_state,
    show_tutorial_step,
    show_loading_message,
    show_success_message,
    show_error_message,
    get_contextual_message,
)


def render_preparation_tab(raw_df):
    """Render the Data Preparation tab content."""
    st.subheader("Data Hygiene Pipeline")
    st.caption("Configure and execute intelligent data cleaning operations")

    show_tutorial_step(2)

    col_demo, col_log = st.columns([1, 2])

    with col_demo:
        # Show selected steps
        selected_steps = [k for k, v in st.session_state["cleaning_steps"].items() if v]
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
            try:
                with show_loading_message(
                    get_contextual_message("processing_cleaning", step_count=len(selected_steps))
                ):
                    cleaner = DataCleaner(raw_df)
                    clean_df = cleaner.clean_all(steps=selected_steps)

                    # Save to session state
                    st.session_state["clean_df"] = clean_df
                    st.session_state["clean_log"] = cleaner.log
                    st.session_state["cleaned"] = True
                    st.session_state["cleaning_completed_at"] = datetime.now()
                    st.session_state["cleaning_duration"] = (
                        cleaner.end_timestamp - cleaner.start_timestamp
                    ).total_seconds()

                show_success_message(get_contextual_message("cleaning_success", records_processed=len(raw_df)))
                # Rerun to update UI with new cleaned state
                st.rerun()
            except Exception as e:
                show_error_message(
                    "Data cleaning operation failed. Try selecting different cleaning steps or regenerating your data.",
                    str(e),
                )

    with col_log:
        if st.session_state.get("cleaned"):
            st.markdown("### Execution Log")
            for msg in st.session_state["clean_log"]:
                st.code(f">> {msg}", language="bash")

            # Post-Clean Metrics
            st.divider()
            st.markdown("### Cleaning Summary")

            # Show timestamp and duration
            if "cleaning_completed_at" in st.session_state:
                time_str = st.session_state["cleaning_completed_at"].strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"Completed at: {time_str}")
            if "cleaning_duration" in st.session_state:
                st.caption(f"Duration: {st.session_state['cleaning_duration']:.3f} seconds")

            c1, c2 = st.columns(2)
            original_len = len(raw_df)
            new_len = len(st.session_state["clean_df"])

            # Calculate health scores
            raw_health = DataHealthMetrics(raw_df)
            clean_health = DataHealthMetrics(st.session_state["clean_df"])

            c1.metric(
                "Records Removed",
                original_len - new_len,
                help="Number of records removed during cleaning (duplicates and invalid entries)",
            )
            improvement = clean_health.calculate_overall_health_score() - raw_health.calculate_overall_health_score()
            c2.metric(
                "Data Health Score",
                f"{clean_health.calculate_overall_health_score()}%",
                delta=f"+{improvement:.1f}%",
                help="Overall data quality improvement after cleaning",
            )

            # Note about export options
            st.divider()
            st.info("Export options are available in the sidebar")
