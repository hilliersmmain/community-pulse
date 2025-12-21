import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

# Constants for chart configuration
MIN_POINTS_FOR_TREND = 3
DEFAULT_HISTOGRAM_BINS = 20


def _add_export_button(fig: go.Figure) -> go.Figure:
    """
    Add download button configuration to figure.
    
    Args:
        fig: Plotly figure to enhance
        
    Returns:
        Enhanced figure with export options
    """
    fig.update_layout(
        modebar_add=['toImage'],
        modebar_remove=[],
    )
    return fig


def _calculate_stats(data: pd.Series) -> Dict[str, float]:
    """
    Calculate statistical measures for a data series.
    
    Args:
        data: Pandas series to analyze
        
    Returns:
        Dictionary with mean, median, std, min, max
    """
    return {
        'mean': float(data.mean()),
        'median': float(data.median()),
        'std': float(data.std()),
        'min': float(data.min()),
        'max': float(data.max())
    }


def plot_attendance_trend(df: pd.DataFrame, data_state: str = "cleaned") -> go.Figure:
    """
    Line chart of attendance over time with trend line, annotations, and rich tooltips.
    
    Args:
        df: DataFrame with member data
        data_state: Label indicating if data is "raw" or "cleaned"
        
    Returns:
        Enhanced Plotly figure with interactivity
    """
    # Group by Join_Date month
    if 'Join_Date' not in df.columns: 
        return go.Figure()
    
    # Ensure datetime with error handling for messy data
    temp_df = df.copy()
    temp_df['Join_Date'] = pd.to_datetime(temp_df['Join_Date'], errors='coerce')
    
    # Remove rows with invalid dates
    temp_df = temp_df.dropna(subset=['Join_Date'])
    
    if len(temp_df) == 0:
        return go.Figure()
    
    trend = temp_df.groupby(temp_df['Join_Date'].dt.to_period("M")).size().reset_index(name='New Members')
    trend['Join_Date'] = trend['Join_Date'].astype(str)
    
    # Calculate statistics
    stats = _calculate_stats(trend['New Members'])
    
    # Create figure with custom traces
    fig = go.Figure()
    
    # Add main line with enhanced tooltips
    fig.add_trace(go.Scatter(
        x=trend['Join_Date'],
        y=trend['New Members'],
        mode='lines+markers',
        name='New Members',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate=(
            '<b>Month:</b> %{x}<br>'
            '<b>New Members:</b> %{y}<br>'
            '<b>Cumulative:</b> %{customdata}<br>'
            '<extra></extra>'
        ),
        customdata=trend['New Members'].cumsum()
    ))
    
    # Add trend line (linear regression)
    if len(trend) > MIN_POINTS_FOR_TREND - 1:
        x_numeric = np.arange(len(trend))
        z = np.polyfit(x_numeric, trend['New Members'], 1)
        p = np.poly1d(z)
        trend_line = p(x_numeric)
        
        fig.add_trace(go.Scatter(
            x=trend['Join_Date'],
            y=trend_line,
            mode='lines',
            name='Trend Line',
            line=dict(color='rgba(255, 127, 14, 0.6)', width=2, dash='dash'),
            hovertemplate='<b>Trend:</b> %{y:.1f}<extra></extra>'
        ))
    
    # Add mean line as annotation
    fig.add_hline(
        y=stats['mean'],
        line_dash="dot",
        line_color="green",
        annotation_text=f"Mean: {stats['mean']:.1f}",
        annotation_position="right"
    )
    
    # Update layout with enhanced styling
    fig.update_layout(
        title={
            'text': f'Membership Growth Over Time<br><sub>Data State: {data_state.title()} | Total Members: {len(df)}</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Month (YYYY-MM)',
        yaxis_title='Number of New Members Joined',
        hovermode='x unified',
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        annotations=[
            dict(
                text=f'📊 Mean: {stats["mean"]:.1f} | Median: {stats["median"]:.1f} | Total: {trend["New Members"].sum()}',
                xref="paper", yref="paper",
                x=0.5, y=-0.15,
                showarrow=False,
                font=dict(size=12, color="gray")
            )
        ]
    )
    
    # Add export button
    fig = _add_export_button(fig)
    
    return fig


def plot_role_distribution(df: pd.DataFrame, data_state: str = "cleaned") -> go.Figure:
    """
    Pie chart of member roles with absolute counts and percentages.
    
    Args:
        df: DataFrame with member data
        data_state: Label indicating if data is "raw" or "cleaned"
        
    Returns:
        Enhanced Plotly figure with counts and percentages
    """
    if 'Role' not in df.columns: 
        return go.Figure()
    
    counts = df['Role'].value_counts().reset_index()
    counts.columns = ['Role', 'Count']
    total = counts['Count'].sum()
    counts['Percentage'] = (counts['Count'] / total * 100).round(1)
    
    # Create enhanced pie chart
    fig = go.Figure(data=[go.Pie(
        labels=counts['Role'],
        values=counts['Count'],
        textposition='auto',
        textinfo='label+percent',
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Count: %{value}<br>'
            'Percentage: %{percent}<br>'
            '<extra></extra>'
        ),
        marker=dict(
            colors=px.colors.qualitative.Set2,
            line=dict(color='white', width=2)
        )
    )])
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Member Role Distribution<br><sub>Data State: {data_state.title()} | Total Members: {total}</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        annotations=[
            dict(
                text=f'📊 Total Members: {total}<br>Unique Roles: {len(counts)}',
                xref="paper", yref="paper",
                x=0.5, y=-0.1,
                showarrow=False,
                font=dict(size=12, color="gray")
            )
        ]
    )
    
    # Add export button
    fig = _add_export_button(fig)
    
    return fig


def plot_attendance_histogram(df: pd.DataFrame, data_state: str = "cleaned") -> go.Figure:
    """
    Histogram of event attendance with statistical annotations.
    
    Args:
        df: DataFrame with member data
        data_state: Label indicating if data is "raw" or "cleaned"
        
    Returns:
        Enhanced Plotly figure with statistics
    """
    if 'Event_Attendance' not in df.columns: 
        return go.Figure()
    
    # Calculate statistics
    stats = _calculate_stats(df['Event_Attendance'])
    
    # Create histogram with custom bins
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['Event_Attendance'],
        nbinsx=DEFAULT_HISTOGRAM_BINS,
        name='Member Count',
        marker=dict(
            color='#1f77b4',
            line=dict(color='white', width=1)
        ),
        hovertemplate=(
            '<b>Events Attended:</b> %{x}<br>'
            '<b>Number of Members:</b> %{y}<br>'
            '<extra></extra>'
        )
    ))
    
    # Add mean line
    fig.add_vline(
        x=stats['mean'],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {stats['mean']:.1f}",
        annotation_position="top"
    )
    
    # Add median line
    fig.add_vline(
        x=stats['median'],
        line_dash="dot",
        line_color="green",
        annotation_text=f"Median: {stats['median']:.1f}",
        annotation_position="bottom"
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Event Attendance Distribution<br><sub>Data State: {data_state.title()} | Total Members: {len(df)}</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Number of Events Attended',
        yaxis_title='Number of Members',
        bargap=0.1,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        hovermode='closest',
        annotations=[
            dict(
                text=f'📊 Mean: {stats["mean"]:.1f} | Median: {stats["median"]:.1f} | Std Dev: {stats["std"]:.1f} | Range: {stats["min"]:.0f}-{stats["max"]:.0f}',
                xref="paper", yref="paper",
                x=0.5, y=-0.15,
                showarrow=False,
                font=dict(size=12, color="gray")
            )
        ]
    )
    
    # Add export button
    fig = _add_export_button(fig)
    
    return fig


def get_chart_export_config() -> Dict[str, Any]:
    """
    Get configuration for chart exports.
    
    Returns:
        Dictionary with export configuration
    """
    return {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'community_pulse_chart',
            'height': 600,
            'width': 1000,
            'scale': 2
        },
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['toImage'],
        'modeBarButtonsToRemove': []
    }
