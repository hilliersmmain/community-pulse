"""
Test suite for the visualizer module.

This module contains tests for visualization functions
including chart generation and predictive analytics.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.visualizer import (
    plot_attendance_trend,
    plot_role_distribution,
    plot_attendance_histogram,
    calculate_attendance_prediction
)


class TestVisualizer:
    """Test suite for visualization functionality."""
    
    @pytest.fixture
    def sample_clean_data(self):
        """Fixture providing a clean DataFrame for testing visualizations."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        return pd.DataFrame({
            'Name': [f'Person {i}' for i in range(100)],
            'Email': [f'person{i}@test.com' for i in range(100)],
            'Join_Date': dates,
            'Event_Attendance': np.random.randint(0, 20, 100),
            'Role': np.random.choice(['Member', 'Admin', 'Guest'], 100)
        })
    
    @pytest.fixture
    def empty_dataframe(self):
        """Fixture providing an empty DataFrame."""
        return pd.DataFrame()
    
    @pytest.fixture
    def single_record_dataframe(self):
        """Fixture providing a DataFrame with a single record."""
        return pd.DataFrame({
            'Name': ['John Doe'],
            'Email': ['john@test.com'],
            'Join_Date': [pd.Timestamp('2023-01-01')],
            'Event_Attendance': [5],
            'Role': ['Member']
        })
    
    def test_plot_attendance_trend_returns_figure(self, sample_clean_data):
        """Test that attendance trend plot returns a Plotly figure."""
        fig = plot_attendance_trend(sample_clean_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0  # Should have data traces
    
    def test_plot_attendance_trend_empty_data(self, empty_dataframe):
        """Test attendance trend with empty DataFrame."""
        fig = plot_attendance_trend(empty_dataframe)
        
        # Should return an empty figure without crashing
        assert isinstance(fig, go.Figure)
    
    def test_plot_attendance_trend_missing_column(self):
        """Test attendance trend with missing Join_Date column."""
        df = pd.DataFrame({
            'Name': ['John Doe'],
            'Email': ['john@test.com']
        })
        
        fig = plot_attendance_trend(df)
        
        # Should return an empty figure
        assert isinstance(fig, go.Figure)
    
    def test_plot_role_distribution_returns_figure(self, sample_clean_data):
        """Test that role distribution plot returns a Plotly figure."""
        fig = plot_role_distribution(sample_clean_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_plot_role_distribution_empty_data(self, empty_dataframe):
        """Test role distribution with empty DataFrame."""
        fig = plot_role_distribution(empty_dataframe)
        
        assert isinstance(fig, go.Figure)
    
    def test_plot_role_distribution_missing_column(self):
        """Test role distribution with missing Role column."""
        df = pd.DataFrame({
            'Name': ['John Doe'],
            'Email': ['john@test.com']
        })
        
        fig = plot_role_distribution(df)
        
        # Should return an empty figure
        assert isinstance(fig, go.Figure)
    
    def test_plot_attendance_histogram_returns_figure(self, sample_clean_data):
        """Test that attendance histogram returns a Plotly figure."""
        fig = plot_attendance_histogram(sample_clean_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_plot_attendance_histogram_empty_data(self, empty_dataframe):
        """Test attendance histogram with empty DataFrame."""
        fig = plot_attendance_histogram(empty_dataframe)
        
        assert isinstance(fig, go.Figure)
    
    def test_plot_attendance_histogram_missing_column(self):
        """Test attendance histogram with missing Event_Attendance column."""
        df = pd.DataFrame({
            'Name': ['John Doe'],
            'Email': ['john@test.com']
        })
        
        fig = plot_attendance_histogram(df)
        
        # Should return an empty figure
        assert isinstance(fig, go.Figure)
    
    def test_calculate_attendance_prediction_with_data(self):
        """Test attendance prediction with sufficient data."""
        # Create data with clear trend over 6 months
        dates = []
        for month in range(6):
            # Add varying number of members per month
            month_date = datetime(2023, month + 1, 1)
            for _ in range(10 + month * 2):  # Increasing trend
                dates.append(month_date)
        
        df = pd.DataFrame({
            'Join_Date': dates,
            'Name': [f'Person {i}' for i in range(len(dates))]
        })
        
        prediction = calculate_attendance_prediction(df, months=3)
        
        # Should return a numeric prediction
        assert prediction is not None
        assert isinstance(prediction, (int, float))
    
    def test_calculate_attendance_prediction_insufficient_data(self):
        """Test prediction with insufficient data."""
        # Only 2 months of data, need 3 for prediction
        df = pd.DataFrame({
            'Join_Date': [datetime(2023, 1, 1), datetime(2023, 2, 1)],
            'Name': ['Person 1', 'Person 2']
        })
        
        prediction = calculate_attendance_prediction(df, months=3)
        
        # Should return None when insufficient data
        assert prediction is None
    
    def test_calculate_attendance_prediction_empty_data(self, empty_dataframe):
        """Test prediction with empty DataFrame."""
        prediction = calculate_attendance_prediction(empty_dataframe)
        
        assert prediction is None
    
    def test_calculate_attendance_prediction_missing_column(self):
        """Test prediction with missing Join_Date column."""
        df = pd.DataFrame({
            'Name': ['John Doe'],
            'Email': ['john@test.com']
        })
        
        prediction = calculate_attendance_prediction(df)
        
        assert prediction is None
    
    def test_single_record_visualizations(self, single_record_dataframe):
        """Test all visualizations work with single record."""
        # All should handle single record gracefully
        fig1 = plot_attendance_trend(single_record_dataframe)
        fig2 = plot_role_distribution(single_record_dataframe)
        fig3 = plot_attendance_histogram(single_record_dataframe)
        
        assert isinstance(fig1, go.Figure)
        assert isinstance(fig2, go.Figure)
        assert isinstance(fig3, go.Figure)
    
    def test_malformed_dates(self):
        """Test handling of malformed date data."""
        df = pd.DataFrame({
            'Join_Date': ['not-a-date', '2023-01-01', None, 'invalid'],
            'Name': ['P1', 'P2', 'P3', 'P4']
        })
        
        # Should not crash
        fig = plot_attendance_trend(df)
        assert isinstance(fig, go.Figure)
        
        # Prediction should handle malformed dates
        prediction = calculate_attendance_prediction(df)
        # May return None or a value depending on how many valid dates


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
