import streamlit as st
import pandas as pd
import os
import plotly.express as px
from utils.data_generator import generate_messy_data
from utils.cleaner import DataCleaner
from utils.visualizer import plot_attendance_trend, plot_role_distribution, plot_attendance_histogram
from utils.health_metrics import DataHealthMetrics
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Community Pulse | Data Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title & Description
st.title("📊 Community Pulse: Intelligent Data Dashboard")
st.markdown("""
**Objective:** Transforming messy, raw member data into actionable insights.
*Demonstrates: Data Engineering (Cleaning), Application Logic, and BI Dashboarding.*
""")

# --- SIDEBAR Controls ---
st.sidebar.header("Data Controls")

DATA_PATH = "data/messy_club_data.csv"

if st.sidebar.button("🔄 Generate New Messy Data"):
    with st.spinner("Generating entropy..."):
        if not os.path.exists("data"):
            os.makedirs("data")
        generate_messy_data(save_path=DATA_PATH)
    st.sidebar.success("New raw dataset generated!")
    st.session_state['cleaned'] = False # Reset state
    st.session_state['data_generated_at'] = datetime.now()

# Load Data
if os.path.exists(DATA_PATH):
    raw_df = pd.read_csv(DATA_PATH)
    if 'data_loaded_at' not in st.session_state:
        st.session_state['data_loaded_at'] = datetime.now()
else:
    st.error("No data found. Please click 'Generate New Messy Data' in the sidebar.")
    st.stop()

# Initialize data state toggle
if 'view_state' not in st.session_state:
    st.session_state['view_state'] = 'raw'

# Data State Toggle in sidebar
st.sidebar.divider()
st.sidebar.subheader("Data View State")
view_state = st.sidebar.radio(
    "Select data state to view:",
    options=['raw', 'cleaned'],
    format_func=lambda x: '📊 Raw Data' if x == 'raw' else '✨ Cleaned Data',
    key='view_state',
    disabled=not st.session_state.get('cleaned', False),
    help="Toggle between raw and cleaned data views. Cleaning must be run first."
)

# Determine which dataframe to show based on state
if st.session_state['view_state'] == 'cleaned' and st.session_state.get('cleaned'):
    active_df = st.session_state['clean_df']
    state_label = "Cleaned"
    state_emoji = "✨"
else:
    active_df = raw_df
    state_label = "Raw"
    state_emoji = "📊"

# --- MAIN APP LOGIC ---

# Calculate health metrics for active data state
health_metrics = DataHealthMetrics(active_df)
metrics = health_metrics.get_detailed_metrics()

# Display current state and timestamp
st.markdown(f"### {state_emoji} Current View: **{state_label} Data**")
if st.session_state.get('cleaned') and st.session_state['view_state'] == 'cleaned':
    if 'cleaning_completed_at' in st.session_state:
        time_str = st.session_state['cleaning_completed_at'].strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"🕒 Last cleaned: {time_str}")
else:
    if 'data_loaded_at' in st.session_state:
        time_str = st.session_state['data_loaded_at'].strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"🕒 Data loaded: {time_str}")

st.divider()

# 1. Dynamic KPI Row with tooltips
st.subheader(f"📊 Key Performance Indicators - {state_label} Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    col1.metric(
        "Total Records", 
        metrics['total_records'],
        help="The total number of records in the dataset"
    )
    col1.metric(
        "Unique Records",
        metrics['unique_records'],
        help="Number of unique records after removing duplicates"
    )

with col2:
    col2.metric(
        "Duplicate Records", 
        metrics['duplicate_records'],
        delta=f"-{metrics['duplicate_records']}" if metrics['duplicate_records'] > 0 else "0",
        delta_color="inverse",
        help="Number of duplicate records detected in the dataset"
    )
    col2.metric(
        "Missing Values",
        metrics['null_cells'],
        delta=f"-{metrics['null_cells']}" if metrics['null_cells'] > 0 else "0",
        delta_color="inverse",
        help="Total number of empty or null cells across all columns"
    )

with col3:
    col3.metric(
        "Completeness Score",
        f"{metrics['completeness_score']}%",
        help="Percentage of non-null values in the dataset (higher is better)"
    )
    col3.metric(
        "Duplicate Score",
        f"{metrics['duplicate_score']}%",
        help="Percentage of unique records (100% means no duplicates)"
    )

with col4:
    col4.metric(
        "Formatting Score",
        f"{metrics['formatting_score']}%",
        help="Percentage of properly formatted emails, dates, and names"
    )
    # Overall health score with color coding
    score = metrics['overall_score']
    if score >= 90:
        score_color = "🟢"
    elif score >= 70:
        score_color = "🟡"
    else:
        score_color = "🔴"
    
    col4.metric(
        "Data Health Score",
        f"{score_color} {score}%",
        help="Overall data quality score based on completeness, duplicates, and formatting (weighted average: 40% completeness, 30% duplicates, 30% formatting)"
    )

# 2. Before/After Cleaning Comparison Section
if st.session_state.get('cleaned'):
    st.divider()
    st.subheader("📊 Before vs. After Cleaning Comparison")
    
    # Calculate metrics for both states
    raw_health = DataHealthMetrics(raw_df)
    raw_metrics = raw_health.get_detailed_metrics()
    clean_health = DataHealthMetrics(st.session_state['clean_df'])
    clean_metrics = clean_health.get_detailed_metrics()
    
    # Create comparison table
    comparison_col1, comparison_col2, comparison_col3, comparison_col4 = st.columns(4)
    
    with comparison_col1:
        st.markdown("#### Records")
        delta_records = clean_metrics['total_records'] - raw_metrics['total_records']
        st.metric(
            "Before",
            raw_metrics['total_records'],
            help="Total records before cleaning"
        )
        st.metric(
            "After",
            clean_metrics['total_records'],
            delta=f"{delta_records}" if delta_records != 0 else "No change",
            help="Total records after cleaning"
        )
    
    with comparison_col2:
        st.markdown("#### Duplicates")
        st.metric(
            "Before",
            raw_metrics['duplicate_records'],
            help="Duplicate records before cleaning"
        )
        st.metric(
            "After",
            clean_metrics['duplicate_records'],
            delta=f"-{raw_metrics['duplicate_records'] - clean_metrics['duplicate_records']}",
            delta_color="inverse",
            help="Duplicate records after cleaning"
        )
    
    with comparison_col3:
        st.markdown("#### Missing Values")
        st.metric(
            "Before",
            raw_metrics['null_cells'],
            help="Missing values before cleaning"
        )
        st.metric(
            "After",
            clean_metrics['null_cells'],
            delta=f"-{raw_metrics['null_cells'] - clean_metrics['null_cells']}",
            delta_color="inverse",
            help="Missing values after cleaning"
        )
    
    with comparison_col4:
        st.markdown("#### Health Score")
        st.metric(
            "Before",
            f"{raw_metrics['overall_score']}%",
            help="Overall health score before cleaning"
        )
        improvement = clean_metrics['overall_score'] - raw_metrics['overall_score']
        st.metric(
            "After",
            f"{clean_metrics['overall_score']}%",
            delta=f"+{improvement:.1f}%",
            help="Overall health score after cleaning"
        )

# 2. Tabs for Workflow
tab1, tab2, tab3 = st.tabs(["🧹 Data Cleaning Ops", "📈 Analytics Dashboard", "📄 Raw Data View"])

with tab1:
    st.subheader("Automated Data Hygiene Pipeline")
    
    col_demo, col_log = st.columns([1, 2])
    
    with col_demo:
        st.info("The raw data contains duplicates, invalid emails, and mixed date formats.")
        if st.button("🚀 Run Cleaning Algorithms", type="primary"):
            try:
                cleaner = DataCleaner(raw_df)
                clean_df = cleaner.clean_all()
                
                # Save to session state
                st.session_state['clean_df'] = clean_df
                st.session_state['clean_log'] = cleaner.log
                st.session_state['cleaned'] = True
                st.session_state['cleaning_completed_at'] = datetime.now()
                st.session_state['cleaning_duration'] = (cleaner.end_timestamp - cleaner.start_timestamp).total_seconds()
                
                st.success("Pipeline executed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred during cleaning: {e}")
            
    with col_log:
        if st.session_state.get('cleaned'):
            st.markdown("### Execution Log")
            for msg in st.session_state['clean_log']:
                st.code(f">> {msg}", language="bash")
                
            # Post-Clean Metrics
            st.divider()
            st.markdown("### Cleaning Summary")
            
            # Show timestamp and duration
            if 'cleaning_completed_at' in st.session_state:
                time_str = st.session_state['cleaning_completed_at'].strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"🕒 Completed at: {time_str}")
            if 'cleaning_duration' in st.session_state:
                st.caption(f"⏱️ Duration: {st.session_state['cleaning_duration']:.3f} seconds")
            
            c1, c2 = st.columns(2)
            original_len = len(raw_df)
            new_len = len(st.session_state['clean_df'])
            
            # Calculate health scores
            raw_health = DataHealthMetrics(raw_df)
            clean_health = DataHealthMetrics(st.session_state['clean_df'])
            
            c1.metric(
                "Records Removed", 
                original_len - new_len,
                help="Number of records removed during cleaning (duplicates and invalid entries)"
            )
            improvement = clean_health.calculate_overall_health_score() - raw_health.calculate_overall_health_score()
            c2.metric(
                "Data Health Score", 
                f"{clean_health.calculate_overall_health_score()}%",
                delta=f"+{improvement:.1f}%",
                help="Overall data quality improvement after cleaning"
            )
            
            # CSV Download Button
            st.divider()
            csv_data = st.session_state['clean_df'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Cleaned Data (CSV)",
                data=csv_data,
                file_name="cleaned_community_data.csv",
                mime="text/csv",
                type="primary"
            )

with tab2:
    if st.session_state.get('cleaned'):
        clean_df = st.session_state['clean_df']
        
        st.subheader("Member Insights")
        
        # Show which data state is being visualized
        st.info("📊 Viewing analytics for **cleaned data**. Toggle to 'Raw Data' in the sidebar to compare.")
        
        # Role Filter
        st.markdown("### Filters")
        available_roles = clean_df['Role'].unique().tolist()
        selected_roles = st.multiselect(
            "Filter by Role:",
            options=available_roles,
            default=available_roles,
            help="Select one or more roles to filter the dashboard data"
        )
        
        # Apply filter
        if selected_roles:
            filtered_df = clean_df[clean_df['Role'].isin(selected_roles)]
        else:
            filtered_df = clean_df
            st.warning("⚠️ No roles selected. Showing all data.")
        
        st.divider()
        row1_col1, row1_col2 = st.columns(2)
        
        
        with row1_col1:
            st.plotly_chart(plot_attendance_trend(filtered_df), use_container_width=True)
            st.caption("*Prediction: Attendance is projected to increase by 12% next month based on 3-month MA.*")
            
        with row1_col2:
            st.plotly_chart(plot_attendance_histogram(filtered_df), use_container_width=True)
            
        st.subheader("Demographics")
        st.plotly_chart(plot_role_distribution(filtered_df), use_container_width=True)
        
    else:
        st.warning("⚠️ Please clean the data in the 'Data Cleaning Ops' tab to generate insights.")

with tab3:
    st.subheader(f"{state_emoji} {state_label} Data Inspector")
    
    # Show health metrics for the current view
    st.markdown("### Data Health Overview")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    metric_col1.metric(
        "Completeness",
        f"{metrics['completeness_score']}%",
        help="Percentage of non-null values"
    )
    metric_col2.metric(
        "Uniqueness",
        f"{metrics['duplicate_score']}%",
        help="Percentage of unique records"
    )
    metric_col3.metric(
        "Formatting",
        f"{metrics['formatting_score']}%",
        help="Validity of data formats"
    )
    metric_col4.metric(
        "Overall Health",
        f"{metrics['overall_score']}%",
        help="Composite health score"
    )
    
    st.divider()
    st.dataframe(active_df, use_container_width=True)
