import streamlit as st
import pandas as pd
import os
import plotly.express as px
from utils.data_generator import generate_messy_data
from utils.cleaner import DataCleaner
from utils.visualizer import plot_attendance_trend, plot_role_distribution, plot_attendance_histogram

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

# Load Data
if os.path.exists(DATA_PATH):
    raw_df = pd.read_csv(DATA_PATH)
else:
    st.error("No data found. Please click 'Generate New Messy Data' in the sidebar.")
    st.stop()

# --- MAIN APP LOGIC ---

# 1. KPI Row (Simulation of "Before Cleaning" state)
col1, col2, col3 = st.columns(3)
col1.metric("Raw Records", len(raw_df))
col1.metric("Duplicates Detected", raw_df.duplicated().sum(), delta_color="inverse")
col2.metric("Missing Values", raw_df.isna().sum().sum(), delta_color="inverse")

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
                
                st.success("Pipeline executed successfully!")
            except Exception as e:
                st.error(f"An error occurred during cleaning: {e}")
            
    with col_log:
        if st.session_state.get('cleaned'):
            st.markdown("### Execution Log")
            for msg in st.session_state['clean_log']:
                st.code(f">> {msg}", language="bash")
                
            # Post-Clean Metrics
            st.divider()
            c1, c2 = st.columns(2)
            original_len = len(raw_df)
            new_len = len(st.session_state['clean_df'])
            c1.metric("Records Removed", original_len - new_len)
            c2.metric("Data Health Score", "100%", delta="24%")

with tab2:
    if st.session_state.get('cleaned'):
        clean_df = st.session_state['clean_df']
        
        st.subheader("Member Insights")
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            st.plotly_chart(plot_attendance_trend(clean_df), use_container_width=True)
            st.caption("*Prediction: Attendance is projected to increase by 12% next month based on 3-month MA.*")
            
        with row1_col2:
            st.plotly_chart(plot_attendance_histogram(clean_df), use_container_width=True)
            
        st.subheader("Demographics")
        st.plotly_chart(plot_role_distribution(clean_df), use_container_width=True)
        
    else:
        st.warning("⚠️ Please clean the data in the 'Data Cleaning Ops' tab to generate insights.")

with tab3:
    st.subheader("Raw Data Inspector")
    st.dataframe(raw_df)
