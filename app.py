import streamlit as st
import pandas as pd
import os
import logging
from io import StringIO
import plotly.express as px
from utils.data_generator import generate_messy_data
from utils.cleaner import DataCleaner
from utils.visualizer import plot_attendance_trend, plot_role_distribution, plot_attendance_histogram, calculate_attendance_prediction
import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

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

DATA_PATH = os.path.join(config.DEFAULT_DATA_DIR, config.DEFAULT_DATA_FILE)

# CSV File Upload
st.sidebar.subheader("📤 Upload Your Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=config.ALLOWED_FILE_EXTENSIONS,
    help=f"Maximum file size: {config.MAX_UPLOAD_SIZE_MB}MB"
)

if uploaded_file is not None:
    try:
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > config.MAX_UPLOAD_SIZE_MB:
            st.sidebar.error(f"File too large! Maximum size is {config.MAX_UPLOAD_SIZE_MB}MB")
        else:
            # Read uploaded file
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            raw_df = pd.read_csv(stringio)
            
            # Sanitization check - look for potential CSV injection
            for col in raw_df.columns:
                if raw_df[col].dtype == 'object':
                    # Check for formulas (Excel injection patterns)
                    dangerous_patterns = raw_df[col].astype(str).str.startswith(('=', '+', '-', '@'))
                    if dangerous_patterns.any():
                        st.sidebar.warning(f"⚠️ Potential CSV injection detected in column '{col}'. Sanitizing...")
                        # Remove dangerous prefixes
                        raw_df[col] = raw_df[col].astype(str).str.replace(r'^[=+\-@]', '', regex=True)
            
            # Save to session state
            st.session_state['uploaded_data'] = raw_df
            st.session_state['cleaned'] = False
            st.sidebar.success(f"✅ Uploaded {len(raw_df)} records!")
            logger.info(f"User uploaded CSV with {len(raw_df)} records")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        logger.error(f"Error reading uploaded file: {e}")

st.sidebar.divider()
st.sidebar.subheader("🔄 Or Generate Sample Data")

if st.sidebar.button("Generate New Messy Data"):
    with st.spinner("Generating entropy..."):
        if not os.path.exists(config.DEFAULT_DATA_DIR):
            os.makedirs(config.DEFAULT_DATA_DIR)
        generate_messy_data(save_path=DATA_PATH)
    st.sidebar.success("New raw dataset generated!")
    st.session_state['cleaned'] = False # Reset state
    if 'uploaded_data' in st.session_state:
        del st.session_state['uploaded_data']  # Clear uploaded data

# Load Data
if 'uploaded_data' in st.session_state:
    raw_df = st.session_state['uploaded_data']
elif os.path.exists(DATA_PATH):
    raw_df = pd.read_csv(DATA_PATH)
else:
    st.error("No data found. Please upload a CSV or click 'Generate New Messy Data' in the sidebar.")
    st.stop()

# --- MAIN APP LOGIC ---

# 1. KPI Row (Simulation of "Before Cleaning" state)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Raw Records", len(raw_df))

# Calculate metrics before cleaning
duplicates_detected = raw_df.duplicated().sum()
col1.metric("Duplicates Detected", duplicates_detected, delta_color="inverse")

missing_values = raw_df.isna().sum().sum()
col2.metric("Missing Values", missing_values, delta_color="inverse")

# Email validity calculation
if 'Email' in raw_df.columns:
    valid_emails = raw_df['Email'].astype(str).str.contains('@', na=False).sum()
    email_validity_rate = (valid_emails / len(raw_df) * 100) if len(raw_df) > 0 else 0
    col3.metric("Email Validity", f"{email_validity_rate:.1f}%")

# Duplicate percentage
duplicate_pct = (duplicates_detected / len(raw_df) * 100) if len(raw_df) > 0 else 0
col4.metric("Duplicate Rate", f"{duplicate_pct:.1f}%", delta_color="inverse")

# 2. Tabs for Workflow
tab1, tab2, tab3 = st.tabs(["🧹 Data Cleaning Ops", "📈 Analytics Dashboard", "📄 Raw Data View"])

with tab1:
    st.subheader("Automated Data Hygiene Pipeline")
    
    col_demo, col_log = st.columns([1, 2])
    
    with col_demo:
        st.info("The raw data contains duplicates, invalid emails, and mixed date formats.")
        if st.button("🚀 Run Cleaning Algorithms", type="primary"):
            try:
                with st.spinner("Running data cleaning pipeline..."):
                    cleaner = DataCleaner(raw_df)
                    clean_df = cleaner.clean_all()
                    
                    # Get detailed metrics
                    metrics = cleaner.get_cleaning_metrics()
                    
                    # Save to session state
                    st.session_state['clean_df'] = clean_df
                    st.session_state['clean_log'] = cleaner.log
                    st.session_state['cleaning_metrics'] = metrics
                    st.session_state['cleaned'] = True
                    
                st.success("Pipeline executed successfully!")
                logger.info("Data cleaning pipeline completed successfully")
            except ValueError as ve:
                st.error(f"Validation error: {ve}")
                logger.error(f"Validation error during cleaning: {ve}")
            except Exception as e:
                st.error(f"An error occurred during cleaning: {e}")
                logger.error(f"Error during cleaning pipeline: {e}")
            
    with col_log:
        if st.session_state.get('cleaned'):
            st.markdown("### Execution Log")
            for msg in st.session_state['clean_log']:
                st.code(f">> {msg}", language="bash")
                
            # Post-Clean Metrics
            st.divider()
            metrics = st.session_state.get('cleaning_metrics', {})
            c1, c2, c3 = st.columns(3)
            
            original_len = metrics.get('initial_records', len(raw_df))
            new_len = metrics.get('final_records', len(st.session_state['clean_df']))
            c1.metric("Records Removed", original_len - new_len)
            
            # Calculate actual Data Health Score
            health_score = metrics.get('data_health_score', 0)
            c2.metric("Data Health Score", f"{health_score:.1f}%", 
                     delta=f"+{health_score - 76:.1f}%" if health_score > 76 else f"{health_score - 76:.1f}%")
            
            # Show duplicate percentage from metrics
            dup_rate = metrics.get('duplicate_rate', 0)
            c3.metric("Duplicate Rate", f"{dup_rate:.1f}%", delta_color="inverse")
            
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
            
            # Calculate real prediction
            prediction = calculate_attendance_prediction(filtered_df, config.PREDICTION_WINDOW_MONTHS)
            if prediction is not None:
                direction = "increase" if prediction > 0 else "decrease"
                st.caption(f"*Prediction: Attendance is projected to {direction} by {abs(prediction):.1f}% next month based on {config.PREDICTION_WINDOW_MONTHS}-month MA.*")
            else:
                st.caption("*Prediction: Insufficient data for trend analysis (need more historical data).*")
            
        with row1_col2:
            st.plotly_chart(plot_attendance_histogram(filtered_df), use_container_width=True)
            
        st.subheader("Demographics")
        st.plotly_chart(plot_role_distribution(filtered_df), use_container_width=True)
        
    else:
        st.warning("⚠️ Please clean the data in the 'Data Cleaning Ops' tab to generate insights.")

with tab3:
    st.subheader("Raw Data Inspector")
    st.dataframe(raw_df)
