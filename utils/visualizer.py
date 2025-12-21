import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging
from typing import Optional
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def plot_attendance_trend(df: pd.DataFrame) -> go.Figure:
    """
    Line chart of attendance over time (based on Join Date).
    
    Args:
        df: DataFrame containing Join_Date column
    
    Returns:
        go.Figure: Plotly figure object
    """
    # Group by Join_Date month
    if 'Join_Date' not in df.columns: return go.Figure()
    
    # Ensure datetime
    temp_df = df.copy()
    try:
        temp_df['Join_Date'] = pd.to_datetime(temp_df['Join_Date'], errors='coerce')
    except Exception as e:
        logger.error(f"Error parsing dates in plot_attendance_trend: {e}")
        return go.Figure()
    
    # Remove NaT values
    temp_df = temp_df.dropna(subset=['Join_Date'])
    
    if len(temp_df) == 0:
        logger.warning("No valid dates found for attendance trend plot")
        return go.Figure()
    
    trend = temp_df.groupby(temp_df['Join_Date'].dt.to_period("M")).size().reset_index(name='New Members')
    trend['Join_Date'] = trend['Join_Date'].astype(str)
    
    fig = px.line(trend, x='Join_Date', y='New Members', title='Membership Growth Over Time', markers=True)
    fig.update_layout(xaxis_title='Month', yaxis_title='New Members Joined')
    return fig

def plot_role_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Pie chart of member roles.
    
    Args:
        df: DataFrame containing Role column
    
    Returns:
        go.Figure: Plotly figure object
    """
    if 'Role' not in df.columns: return go.Figure()
    
    counts = df['Role'].value_counts().reset_index()
    counts.columns = ['Role', 'Count']
    
    fig = px.pie(counts, values='Count', names='Role', title='Member Role Distribution')
    return fig

def plot_attendance_histogram(df: pd.DataFrame) -> go.Figure:
    """
    Histogram of event attendance.
    
    Args:
        df: DataFrame containing Event_Attendance column
    
    Returns:
        go.Figure: Plotly figure object
    """
    if 'Event_Attendance' not in df.columns: return go.Figure()
    
    fig = px.histogram(df, x="Event_Attendance", nbins=20, title="Event Attendance Distribution")
    fig.update_layout(xaxis_title="Events Attended", yaxis_title="Count of Members")
    return fig

def calculate_attendance_prediction(df: pd.DataFrame, months: int = config.PREDICTION_WINDOW_MONTHS) -> Optional[float]:
    """
    Calculate predicted attendance increase using moving average.
    
    Args:
        df: DataFrame containing Join_Date column
        months: Number of months to use for moving average calculation
    
    Returns:
        float: Predicted percentage increase, or None if insufficient data
    """
    if 'Join_Date' not in df.columns or len(df) == 0:
        logger.warning("Cannot calculate prediction: missing Join_Date or empty dataframe")
        return None
    
    try:
        # Ensure datetime
        temp_df = df.copy()
        temp_df['Join_Date'] = pd.to_datetime(temp_df['Join_Date'])
        
        # Group by month and count
        monthly_counts = temp_df.groupby(temp_df['Join_Date'].dt.to_period("M")).size()
        
        if len(monthly_counts) < months + 1:
            logger.warning(f"Insufficient data for {months}-month prediction: only {len(monthly_counts)} months available")
            return None
        
        # Calculate moving average for last N months
        recent_avg = monthly_counts.tail(months).mean()
        previous_avg = monthly_counts.tail(months + 1).head(months).mean()
        
        if previous_avg == 0:
            logger.warning("Cannot calculate prediction: previous average is zero")
            return None
        
        # Calculate percentage change
        prediction = ((recent_avg - previous_avg) / previous_avg) * 100
        
        logger.info(f"Attendance prediction calculated: {prediction:.1f}% change")
        return prediction
        
    except Exception as e:
        logger.error(f"Error calculating attendance prediction: {e}")
        return None
