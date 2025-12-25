import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px
from utils.data_generator import generate_messy_data
from utils.cleaner import DataCleaner
from utils.visualizer import plot_attendance_trend, plot_role_distribution, plot_attendance_histogram, get_chart_export_config
from utils.health_metrics import DataHealthMetrics
from utils.ui_helpers import (
    initialize_session_state,
    show_welcome_modal,
    show_empty_state,
    show_tutorial_step,
    show_whats_new,
    show_loading_message,
    show_success_message,
    show_error_message,
    get_contextual_message,
    MESSAGES
)
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Community Pulse | Data Dashboard",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main header styling */
    .main h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #1f77b4;
    }

    /* Padding fix for top of page */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* Metric cards enhancement */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 500;
    }
    
    /* Card/Widget styling */
    div.css-1r6slb0, div.stMetric {
        padding: 1rem;
        border-radius: 8px;
    }
    
    /* Success/info box enhancement */
    .element-container div[data-testid="stMarkdownContainer"] > div[data-testid="stMarkdown"] {
        font-size: 0.95rem;
    }
    
    /* Chart container shadow */
    .js-plotly-plot {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for UI features
initialize_session_state()

# Show welcome modal for first-time users
if st.session_state.get('show_welcome', False):
    show_welcome_modal()

# Title & Description
st.title("Community Pulse Dashboard")
st.markdown("""
<div style="margin-bottom: 2rem;">
    <p style="font-size: 1.1rem; line-height: 1.6;">
        Data quality management and member analytics platform. 
        Transform raw data into actionable insights with automated cleaning pipelines.
    </p>
</div>
""", unsafe_allow_html=True)

# What's New panel
show_whats_new()

# --- SIDEBAR Controls ---
st.sidebar.header("Data Controls")

DATA_PATH = "data/messy_club_data.csv"

# Initialize session state variables
if 'num_records' not in st.session_state:
    st.session_state['num_records'] = 500
if 'messiness_level' not in st.session_state:
    st.session_state['messiness_level'] = 'medium'

# --- 1. QUICK STATS SECTION ---
with st.sidebar.expander("Quick Stats", expanded=True):
    # Determine which dataset to use for stats
    stats_df = None
    stats_label = "metrics['overall_score']"
    
    if st.session_state.get('cleaned') and 'clean_df' in st.session_state:
        stats_df = st.session_state['clean_df']
        is_cleaned = True
    elif os.path.exists(DATA_PATH):
        try:
            stats_df = pd.read_csv(DATA_PATH)
            is_cleaned = False
        except:
            pass
            
    if stats_df is not None:
        health = DataHealthMetrics(stats_df)
        metrics = health.get_detailed_metrics()
        
        st.metric("Records", metrics['total_records'])
        
        # Health Score with dynamic label
        score_val = f"{metrics['overall_score']}%"
        if is_cleaned:
            st.metric("Health Score", score_val)
        else:
            st.metric("Health Score", score_val, help="Score based on raw data")
        
        # Last data load time
        if 'data_loaded_at' in st.session_state:
            st.caption(f"Last loaded: {st.session_state['data_loaded_at'].strftime('%H:%M:%S')}")
        
        # Last cleaning time
        if st.session_state.get('cleaned') and 'cleaning_completed_at' in st.session_state:
            st.caption(f"Last cleaned: {st.session_state['cleaning_completed_at'].strftime('%H:%M:%S')}")
    else:
        st.caption("No data available")

st.sidebar.divider()

# --- 2. DATA GENERATION CONTROLS ---
st.sidebar.subheader("Data Generation")

num_records = st.sidebar.slider(
    "Number of Records",
    min_value=100,
    max_value=1000,
    value=st.session_state['num_records'],
    step=50,
    help="Select how many sample records to generate. More records = more realistic analysis, but slower processing."
)
st.session_state['num_records'] = num_records

messiness_level = st.sidebar.selectbox(
    "Messiness Level",
    options=['low', 'medium', 'high'],
    index=['low', 'medium', 'high'].index(st.session_state['messiness_level']),
    help="Control data quality simulation:\n• Low: 3% duplicates, 2% errors (clean CRM)\n• Medium: 10% duplicates, 5% errors (typical export)\n• High: 20% duplicates, 15% errors (legacy system)"
)
st.session_state['messiness_level'] = messiness_level

if st.sidebar.button("Generate New Data", type="primary", help="Create fresh sample data"):
    with show_loading_message(get_contextual_message("loading_data")):
        if not os.path.exists("data"):
            os.makedirs("data")
        try:
            generate_messy_data(
                num_records=num_records,
                save_path=DATA_PATH,
                messiness_level=messiness_level
            )
            show_success_message(
                get_contextual_message("data_generated", 
                num_records=num_records, 
                messiness=messiness_level)
            )
            st.session_state['cleaned'] = False # Reset state
            st.session_state['data_generated_at'] = datetime.now()
            st.session_state['data_loaded_at'] = datetime.now()
            st.rerun()
        except Exception as e:
            show_error_message(
                "Unable to generate sample data. Please try again with different settings.",
                str(e)
            )

st.sidebar.divider()

# --- 3. CLEANING PIPELINE CONTROLS ---
st.sidebar.subheader("Cleaning Pipeline")

# Initialize cleaning steps in session state
if 'cleaning_steps' not in st.session_state:
    st.session_state['cleaning_steps'] = {
        'standardize_names': True,
        'fix_emails': True,
        'remove_duplicates': True,
        'clean_dates': True,
        'handle_missing_values': True
    }

with st.sidebar.expander("Configure Cleaning Steps", expanded=False):
    st.session_state['cleaning_steps']['standardize_names'] = st.checkbox(
        "Standardize Names",
        value=st.session_state['cleaning_steps']['standardize_names'],
        help="Convert names to Title Case (e.g., 'john doe' → 'John Doe')"
    )
    
    st.session_state['cleaning_steps']['fix_emails'] = st.checkbox(
        "Fix Email Formats",
        value=st.session_state['cleaning_steps']['fix_emails'],
        help="Fix invalid emails (e.g., 'user at domain.com' → 'user@domain.com')"
    )
    
    st.session_state['cleaning_steps']['remove_duplicates'] = st.checkbox(
        "Remove Duplicates",
        value=st.session_state['cleaning_steps']['remove_duplicates'],
        help="Remove duplicate rows based on Email and Name"
    )
    
    st.session_state['cleaning_steps']['clean_dates'] = st.checkbox(
        "Clean Dates",
        value=st.session_state['cleaning_steps']['clean_dates'],
        help="Standardize date formats to YYYY-MM-DD"
    )
    
    st.session_state['cleaning_steps']['handle_missing_values'] = st.checkbox(
        "Handle Missing Values",
        value=st.session_state['cleaning_steps']['handle_missing_values'],
        help="Fill missing attendance values with 0"
    )

# Show preview of selected steps
selected_steps = [k for k, v in st.session_state['cleaning_steps'].items() if v]
if selected_steps:
    st.sidebar.caption(f"✓ {len(selected_steps)} step(s) selected")
else:
    st.sidebar.warning("No cleaning steps selected")

st.sidebar.divider()

# --- 4. EXPORT OPTIONS ---
st.sidebar.subheader("Export Options")

# Check if we have cleaned data to export
export_df = None
export_label = "Raw"

if st.session_state.get('cleaned') and st.session_state.get('clean_df') is not None:
    export_choice = st.sidebar.radio(
        "Export data:",
        options=['raw', 'cleaned'],
        format_func=lambda x: 'Raw Data' if x == 'raw' else 'Cleaned Data',
        help="Choose which dataset to export"
    )
    if export_choice == 'cleaned':
        export_df = st.session_state['clean_df']
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
    csv_data = export_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label=f"Download CSV ({export_label})",
        data=csv_data,
        file_name=f"community_data_{export_label.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
    
    # JSON Export
    json_data = export_df.to_json(orient='records', indent=2)
    st.sidebar.download_button(
        label=f"Download JSON ({export_label})",
        data=json_data,
        file_name=f"community_data_{export_label.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )
    
    # PDF Export (Coming Soon)
    # st.sidebar.button(
    #     "📑 Export to PDF",
    #     help="PDF export coming soon!",
    #     disabled=True
    # )
    
    # Export Report (Coming Soon)
    # st.sidebar.button(
    #     "📊 Export Report",
    #     help="Generate a comprehensive data quality report (coming soon!)",
    #     disabled=True
    # )
else:
    st.sidebar.info("Generate data to enable export options")

st.sidebar.divider()

# --- 5. RESET & VIEW STATE ---
st.sidebar.subheader("Data View")

# Data State Toggle
if st.session_state.get('cleaned'):
    view_state = st.sidebar.radio(
        "Current view:",
        options=['raw', 'cleaned'],
        format_func=lambda x: 'Raw Data' if x == 'raw' else 'Cleaned Data',
        key='view_state',
        help="Toggle between raw and cleaned data views"
    )
else:
    st.sidebar.info("Clean data first to enable view toggle")
    if 'view_state' not in st.session_state:
        st.session_state['view_state'] = 'raw'

# Reset to Raw Data button
if st.session_state.get('cleaned'):
    if st.sidebar.button("Reset to Raw Data", help="Clear cleaned data and return to raw state"):
        st.session_state['cleaned'] = False
        if 'clean_df' in st.session_state:
            del st.session_state['clean_df']
        if 'clean_log' in st.session_state:
            del st.session_state['clean_log']
        # Delete view_state key so it can be reset
        if 'view_state' in st.session_state:
            del st.session_state['view_state']
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
    
    - **Standardize Names:** Fixes capitalization (e.g., "john doe" → "John Doe")
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


# Load Data
if os.path.exists(DATA_PATH):
    raw_df = pd.read_csv(DATA_PATH)
    if 'data_loaded_at' not in st.session_state:
        st.session_state['data_loaded_at'] = datetime.now()
else:
    # Show empty state when no data is available
    show_empty_state(
        icon=MESSAGES["no_data_generated"]["icon"],
        title=MESSAGES["no_data_generated"]["title"],
        message=MESSAGES["no_data_generated"]["message"]
    )
    
    # Add helpful tips
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
if 'view_state' not in st.session_state:
    st.session_state['view_state'] = 'raw'

# Determine which dataframe to show based on state
if st.session_state.get('cleaned') and st.session_state['view_state'] == 'cleaned':
    active_df = st.session_state['clean_df']
    state_label = "Cleaned"
else:
    active_df = raw_df
    state_label = "Raw"

# --- MAIN APP LOGIC ---

# Calculate health metrics for active data state
health_metrics = DataHealthMetrics(active_df)
metrics = health_metrics.get_detailed_metrics()

# Display current state and timestamp
st.markdown(f"### Current View: **{state_label} Data**")
if st.session_state.get('cleaned') and st.session_state['view_state'] == 'cleaned':
    if 'cleaning_completed_at' in st.session_state:
        time_str = st.session_state['cleaning_completed_at'].strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last cleaned: {time_str}")
else:
    if 'data_loaded_at' in st.session_state:
        time_str = st.session_state['data_loaded_at'].strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Data loaded: {time_str}")

st.divider()

# 1. Dynamic KPI Row with enhanced tooltips
st.subheader(f"Key Performance Indicators")
st.caption("Real-time data quality metrics to track your cleaning progress")

show_tutorial_step(1)

col1, col2, col3, col4 = st.columns(4)

with col1:
    col1.metric(
        "Total Records", 
        metrics['total_records'],
        help="The complete count of all records in your dataset, including duplicates"
    )
    col1.metric(
        "Unique Records",
        metrics['unique_records'],
        help="Number of distinct records after removing duplicates (higher is better for data quality)"
    )

with col2:
    col2.metric(
        "Duplicate Records", 
        metrics['duplicate_records'],
        delta=f"-{metrics['duplicate_records']}" if metrics['duplicate_records'] > 0 else None,
        delta_color="inverse",
        help="Records that appear more than once, based on email and name matching (lower is better)"
    )
    col2.metric(
        "Missing Values",
        metrics['null_cells'],
        delta=f"-{metrics['null_cells']}" if metrics['null_cells'] > 0 else None,
        delta_color="inverse",
        help="Total count of empty or null cells across all columns (0 is ideal)"
    )

with col3:
    col3.metric(
        "Completeness Score",
        f"{metrics['completeness_score']}%",
        help="Percentage of cells with valid data (100% = no missing values, ideal for analysis)"
    )
    col3.metric(
        "Duplicate Score",
        f"{metrics['duplicate_score']}%",
        help="Percentage of unique records (100% = no duplicates, clean dataset)"
    )

with col4:
    col4.metric(
        "Formatting Score",
        f"{metrics['formatting_score']}%",
        help="Percentage of properly formatted data including valid emails, dates, and standardized names (100% is ideal)"
    )
    # Overall health score with color coding
    score = metrics['overall_score']
    if score >= 90:
        score_label = "Excellent"
    elif score >= 70:
        score_label = "Good"
    else:
        score_label = "Needs Work"
    
    col4.metric(
        "Data Health Score",
        f"{score}%",
        help=f"Overall data quality assessment: {score_label}\n\nCalculated from:\n• 40% Completeness\n• 30% Uniqueness\n• 30% Formatting\n\n90%+ = Excellent | 70-89% = Good | <70% = Needs Improvement"
    )

# 2. Before/After Cleaning Comparison Section
if st.session_state.get('cleaned'):
    st.divider()
    st.subheader("Before vs. After Cleaning Comparison")
    
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
        delta_dup = clean_metrics['duplicate_records'] - raw_metrics['duplicate_records']
        st.metric(
            "After",
            clean_metrics['duplicate_records'],
            delta=f"{delta_dup}" if delta_dup != 0 else None,
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
        delta_miss = clean_metrics['null_cells'] - raw_metrics['null_cells']
        st.metric(
            "After",
            clean_metrics['null_cells'],
            delta=f"{delta_miss}" if delta_miss != 0 else None,
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
tab1, tab2, tab3 = st.tabs(["Data Preparation", "Analytics", "Data Explorer"])

with tab1:
    st.subheader("Data Hygiene Pipeline")
    st.caption("Configure and execute intelligent data cleaning operations")
    
    show_tutorial_step(2)
    
    col_demo, col_log = st.columns([1, 2])
    
    with col_demo:
        # Show selected steps
        selected_steps = [k for k, v in st.session_state['cleaning_steps'].items() if v]
        if selected_steps:
            st.success(f"Ready to apply **{len(selected_steps)} cleaning step(s)**")
            st.caption("Configure steps in the sidebar to customize your cleaning pipeline")
        else:
            show_empty_state(
                icon="",
                title="No Cleaning Steps Selected",
                message="Enable at least one cleaning step in the sidebar to process your data."
            )
        
        show_tutorial_step(3)
        
        if st.button("Run Cleaning Algorithms", type="primary", disabled=len(selected_steps) == 0, help="Execute the configured cleaning pipeline on your dataset"):
            try:
                with show_loading_message(get_contextual_message("processing_cleaning", step_count=len(selected_steps))):
                    cleaner = DataCleaner(raw_df)
                    clean_df = cleaner.clean_all(steps=selected_steps)
                    
                    # Save to session state
                    st.session_state['clean_df'] = clean_df
                    st.session_state['clean_log'] = cleaner.log
                    st.session_state['cleaned'] = True
                    st.session_state['cleaning_completed_at'] = datetime.now()
                    st.session_state['cleaning_duration'] = (cleaner.end_timestamp - cleaner.start_timestamp).total_seconds()
                
                show_success_message(
                    get_contextual_message("cleaning_success", records_processed=len(raw_df))
                )
                # Rerun to update UI with new cleaned state
                st.rerun()
            except Exception as e:
                show_error_message(
                    "Data cleaning operation failed. Try selecting different cleaning steps or regenerating your data.",
                    str(e)
                )
            
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
                st.caption(f"Completed at: {time_str}")
            if 'cleaning_duration' in st.session_state:
                st.caption(f"Duration: {st.session_state['cleaning_duration']:.3f} seconds")
            
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
            
            # Note about export options
            st.divider()
            st.info("Export options are available in the sidebar")


with tab2:
    show_tutorial_step(4)
    
    if st.session_state.get('cleaned'):
        clean_df = st.session_state['clean_df']
        
        st.subheader("Member Insights & Analytics")
        st.caption("Explore your cleaned data with interactive visualizations")
        
        # Show which data state is being visualized
        st.info("Viewing analytics for **cleaned data**. Toggle to 'Raw Data' in the sidebar to compare quality before cleaning.")
        
        # Role Filter
        st.markdown("### Filters")
        available_roles = clean_df['Role'].unique().tolist()
        selected_roles = st.multiselect(
            "Filter by Role:",
            options=available_roles,
            default=available_roles,
            help="Select one or more member roles to focus your analysis on specific segments"
        )
        
        # Apply filter
        if selected_roles:
            filtered_df = clean_df[clean_df['Role'].isin(selected_roles)]
        else:
            filtered_df = clean_df
            show_empty_state(
                icon=MESSAGES["no_filters_selected"]["icon"],
                title=MESSAGES["no_filters_selected"]["title"],
                message=MESSAGES["no_filters_selected"]["message"]
            )
            st.stop()
        
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
            st.caption("**Tip:** Click the camera icon to export as PNG. Hover over data points for detailed information.")
            
        with row1_col2:
            with show_loading_message(get_contextual_message("rendering_charts")):
                fig_hist = plot_attendance_histogram(filtered_df, data_state=data_state)
                st.plotly_chart(fig_hist, use_container_width=True, config=export_config)
            st.caption("**Tip:** Red dashed line = mean attendance, green dotted line = median. Use these to identify outliers.")
        
        st.divider()
        
        # Row 2: Role Distribution
        st.subheader("Demographics")
        with show_loading_message(get_contextual_message("rendering_charts")):
            fig_role = plot_role_distribution(filtered_df, data_state=data_state)
            st.plotly_chart(fig_role, use_container_width=True, config=export_config)
        st.caption("**Tip:** Click legend items to show/hide specific roles. Double-click to isolate a single role.")
        
        # Before/After Comparison Section
        if st.session_state.get('cleaned'):
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
                    with st.spinner('Loading raw data charts...'):
                        raw_trend = plot_attendance_trend(raw_df, data_state="raw")
                        st.plotly_chart(raw_trend, use_container_width=True, config=export_config, key="raw_trend_compare")
                
                with comp_col2:
                    st.markdown("##### Cleaned Data")
                    with st.spinner('Loading cleaned data charts...'):
                        clean_trend = plot_attendance_trend(clean_df, data_state="cleaned")
                        st.plotly_chart(clean_trend, use_container_width=True, config=export_config, key="clean_trend_compare")
            
            with compare_tab2:
                st.markdown("#### Interactive Toggle Comparison")
                comparison_state = st.radio(
                    "Select data state to visualize:",
                    options=['raw', 'cleaned'],
                    format_func=lambda x: 'Raw Data' if x == 'raw' else 'Cleaned Data',
                    horizontal=True
                )
                
                if comparison_state == 'raw':
                    compare_df = raw_df
                    state_label = "raw"
                else:
                    compare_df = clean_df
                    state_label = "cleaned"
                
                # Show all three charts for selected state
                with st.spinner(f'Loading {state_label} data visualizations...'):
                    st.plotly_chart(plot_attendance_trend(compare_df, data_state=state_label), 
                                  use_container_width=True, config=export_config, key=f"{state_label}_trend_toggle")
                    
                    toggle_col1, toggle_col2 = st.columns(2)
                    with toggle_col1:
                        st.plotly_chart(plot_attendance_histogram(compare_df, data_state=state_label), 
                                      use_container_width=True, config=export_config, key=f"{state_label}_hist_toggle")
                    with toggle_col2:
                        st.plotly_chart(plot_role_distribution(compare_df, data_state=state_label), 
                                      use_container_width=True, config=export_config, key=f"{state_label}_role_toggle")
        
    else:
        show_empty_state(
            icon=MESSAGES["no_data_cleaned"]["icon"],
            title=MESSAGES["no_data_cleaned"]["title"],
            message=MESSAGES["no_data_cleaned"]["message"]
        )
        
        st.info("""
        **Quick Steps to Generate Analytics:**
        
        1. Go to the **"Data Cleaning Ops"** tab above
        2. Configure which cleaning steps you want to apply (or leave defaults)
        3. Click the **"Run Cleaning Algorithms"** button
        4. Return here to see your interactive charts and insights!
        
        **What you'll see after cleaning:**
        - Time-series attendance trends
        - Distribution analysis histograms
        - Member demographics pie charts
        - Before/after comparison views
        """)

with tab3:
    st.subheader(f"{state_label} Data Inspector")
    
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
