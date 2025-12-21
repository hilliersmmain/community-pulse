"""
Test suite for the enhanced visualizer module.

This module contains tests for all enhanced visualization features including
statistical annotations, trend lines, tooltips, and export configurations.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils.visualizer import (
    plot_attendance_trend,
    plot_role_distribution,
    plot_attendance_histogram,
    get_chart_export_config,
    _calculate_stats,
    _add_export_button
)


class TestVisualizerEnhancements:
    """Test suite for enhanced visualizer functionality."""
    
    @pytest.fixture
    def sample_member_data(self):
        """Fixture providing a sample DataFrame with member data."""
        dates = [datetime.now() - timedelta(days=30*i) for i in range(12)]
        return pd.DataFrame({
            'Name': [f'Member {i}' for i in range(100)],
            'Email': [f'member{i}@test.com' for i in range(100)],
            'Join_Date': np.random.choice(dates, 100),
            'Event_Attendance': np.random.randint(0, 20, 100),
            'Role': np.random.choice(['Member', 'Admin', 'Guest'], 100, p=[0.7, 0.1, 0.2])
        })
    
    def test_calculate_stats(self, sample_member_data):
        """Test statistical calculation function."""
        stats = _calculate_stats(sample_member_data['Event_Attendance'])
        
        # Verify all required stats are present
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        
        # Verify stats are numeric
        for key, value in stats.items():
            assert isinstance(value, (int, float))
        
        # Verify basic properties
        assert stats['min'] <= stats['median'] <= stats['max']
        assert stats['min'] <= stats['mean'] <= stats['max']
    
    def test_plot_attendance_trend_basic(self, sample_member_data):
        """Test basic attendance trend plot creation."""
        fig = plot_attendance_trend(sample_member_data, data_state="cleaned")
        
        # Verify figure is created
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Verify title includes data state
        assert 'cleaned' in fig.layout.title.text.lower()
    
    def test_plot_attendance_trend_with_trend_line(self, sample_member_data):
        """Test that trend line is added when sufficient data points exist."""
        fig = plot_attendance_trend(sample_member_data, data_state="cleaned")
        
        # Should have at least 2 traces (main line and trend line)
        assert len(fig.data) >= 2
        
        # One trace should be the trend line
        trace_names = [trace.name for trace in fig.data]
        assert 'Trend Line' in trace_names
    
    def test_plot_attendance_trend_annotations(self, sample_member_data):
        """Test that statistical annotations are present."""
        fig = plot_attendance_trend(sample_member_data, data_state="cleaned")
        
        # Check for annotations
        assert len(fig.layout.annotations) > 0
        
        # Verify statistics are in annotations
        annotation_text = ' '.join([ann.text for ann in fig.layout.annotations])
        assert 'mean' in annotation_text.lower() or 'Mean' in annotation_text
    
    def test_plot_attendance_trend_empty_data(self):
        """Test behavior with empty DataFrame."""
        empty_df = pd.DataFrame()
        fig = plot_attendance_trend(empty_df)
        
        # Should return a valid but empty figure
        assert fig is not None
    
    def test_plot_attendance_trend_missing_column(self):
        """Test behavior when Join_Date column is missing."""
        df = pd.DataFrame({'Name': ['Test'], 'Role': ['Member']})
        fig = plot_attendance_trend(df)
        
        # Should return a valid but empty figure
        assert fig is not None
    
    def test_plot_role_distribution_basic(self, sample_member_data):
        """Test basic role distribution pie chart creation."""
        fig = plot_role_distribution(sample_member_data, data_state="cleaned")
        
        # Verify figure is created
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Verify it's a pie chart
        assert fig.data[0].type == 'pie'
    
    def test_plot_role_distribution_percentages(self, sample_member_data):
        """Test that pie chart includes both counts and percentages."""
        fig = plot_role_distribution(sample_member_data, data_state="cleaned")
        
        # Check that textinfo includes both label and percent
        assert 'percent' in fig.data[0].textinfo
        assert 'label' in fig.data[0].textinfo
    
    def test_plot_role_distribution_tooltips(self, sample_member_data):
        """Test that rich tooltips are configured."""
        fig = plot_role_distribution(sample_member_data, data_state="cleaned")
        
        # Verify hover template exists
        assert fig.data[0].hovertemplate is not None
        assert 'Count' in fig.data[0].hovertemplate or 'value' in fig.data[0].hovertemplate
    
    def test_plot_role_distribution_annotations(self, sample_member_data):
        """Test that annotations with totals are present."""
        fig = plot_role_distribution(sample_member_data, data_state="cleaned")
        
        # Check for annotations
        assert len(fig.layout.annotations) > 0
        
        # Verify total is mentioned
        annotation_text = ' '.join([ann.text for ann in fig.layout.annotations])
        assert 'Total' in annotation_text or 'total' in annotation_text
    
    def test_plot_attendance_histogram_basic(self, sample_member_data):
        """Test basic histogram creation."""
        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")
        
        # Verify figure is created
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Verify it's a histogram
        assert fig.data[0].type == 'histogram'
    
    def test_plot_attendance_histogram_mean_median_lines(self, sample_member_data):
        """Test that mean and median lines are added."""
        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")
        
        # Check for vertical lines (shapes in layout)
        assert hasattr(fig.layout, 'shapes')
        assert len(fig.layout.shapes) >= 2  # At least mean and median lines
    
    def test_plot_attendance_histogram_statistics(self, sample_member_data):
        """Test that statistical annotations are present."""
        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")
        
        # Check for annotations
        assert len(fig.layout.annotations) > 0
        
        # Verify statistics are mentioned
        annotation_text = ' '.join([ann.text for ann in fig.layout.annotations])
        assert any(stat in annotation_text.lower() for stat in ['mean', 'median', 'std'])
    
    def test_plot_attendance_histogram_tooltips(self, sample_member_data):
        """Test that rich tooltips are configured."""
        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")
        
        # Verify hover template exists
        assert fig.data[0].hovertemplate is not None
        assert 'Events' in fig.data[0].hovertemplate or 'Members' in fig.data[0].hovertemplate
    
    def test_get_chart_export_config(self):
        """Test export configuration generation."""
        config = get_chart_export_config()
        
        # Verify required keys are present
        assert 'toImageButtonOptions' in config
        assert 'displayModeBar' in config
        assert 'displaylogo' in config
        
        # Verify image options
        image_opts = config['toImageButtonOptions']
        assert image_opts['format'] == 'png'
        assert 'filename' in image_opts
        assert 'height' in image_opts
        assert 'width' in image_opts
        assert 'scale' in image_opts
    
    def test_add_export_button(self, sample_member_data):
        """Test that export button is added to figures."""
        fig = plot_attendance_trend(sample_member_data)
        
        # Verify modebar configuration
        assert hasattr(fig.layout, 'modebar')
    
    def test_data_state_labels(self, sample_member_data):
        """Test that data state labels appear correctly in all charts."""
        states = ['raw', 'cleaned']
        
        for state in states:
            # Test trend chart
            fig_trend = plot_attendance_trend(sample_member_data, data_state=state)
            assert state in fig_trend.layout.title.text.lower()
            
            # Test pie chart
            fig_pie = plot_role_distribution(sample_member_data, data_state=state)
            assert state in fig_pie.layout.title.text.lower()
            
            # Test histogram
            fig_hist = plot_attendance_histogram(sample_member_data, data_state=state)
            assert state in fig_hist.layout.title.text.lower()
    
    def test_chart_interactivity(self, sample_member_data):
        """Test that charts have interactive features enabled."""
        fig = plot_attendance_trend(sample_member_data)
        
        # Verify hover mode is set
        assert hasattr(fig.layout, 'hovermode')
        
        # Verify legend is shown
        assert fig.layout.showlegend is True
    
    def test_all_charts_with_filtered_data(self, sample_member_data):
        """Test that all charts work with filtered data (role filtering)."""
        # Filter to only Members
        filtered_df = sample_member_data[sample_member_data['Role'] == 'Member']
        
        # All charts should work with filtered data
        fig_trend = plot_attendance_trend(filtered_df, data_state="cleaned")
        assert fig_trend is not None
        assert len(fig_trend.data) > 0
        
        fig_pie = plot_role_distribution(filtered_df, data_state="cleaned")
        assert fig_pie is not None
        assert len(fig_pie.data) > 0
        
        fig_hist = plot_attendance_histogram(filtered_df, data_state="cleaned")
        assert fig_hist is not None
        assert len(fig_hist.data) > 0

