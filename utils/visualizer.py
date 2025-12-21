import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_attendance_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart of attendance over time (based on Join Date)."""
    # Group by Join_Date month
    if 'Join_Date' not in df.columns: return go.Figure()
    
    # Ensure datetime
    temp_df = df.copy()
    temp_df['Join_Date'] = pd.to_datetime(temp_df['Join_Date'])
    
    trend = temp_df.groupby(temp_df['Join_Date'].dt.to_period("M")).size().reset_index(name='New Members')
    trend['Join_Date'] = trend['Join_Date'].astype(str)
    
    fig = px.line(trend, x='Join_Date', y='New Members', title='Membership Growth Over Time', markers=True)
    fig.update_layout(xaxis_title='Month', yaxis_title='New Members Joined')
    return fig

def plot_role_distribution(df: pd.DataFrame) -> go.Figure:
    """Pie chart of member roles."""
    if 'Role' not in df.columns: return go.Figure()
    
    counts = df['Role'].value_counts().reset_index()
    counts.columns = ['Role', 'Count']
    
    fig = px.pie(counts, values='Count', names='Role', title='Member Role Distribution')
    return fig

def plot_attendance_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram of event attendance."""
    if 'Event_Attendance' not in df.columns: return go.Figure()
    
    fig = px.histogram(df, x="Event_Attendance", nbins=20, title="Event Attendance Distribution")
    fig.update_layout(xaxis_title="Events Attended", yaxis_title="Count of Members")
    return fig
