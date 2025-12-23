"""
Test suite to verify that emoji characters have been removed from chart captions.

This test ensures that the professional presentation cleanup is complete by
verifying that no emoji characters (specifically 📊) appear in chart annotations.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils.visualizer import (
    plot_attendance_trend,
    plot_role_distribution,
    plot_attendance_histogram,
)


class TestEmojiRemoval:
    """Test suite for verifying emoji removal from chart captions."""
    
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
    
    def test_attendance_trend_no_emoji(self, sample_member_data):
        """Test that attendance trend chart has no emoji in annotations."""
        fig = plot_attendance_trend(sample_member_data, data_state="cleaned")
        
        # Check all annotations for emojis
        for annotation in fig.layout.annotations:
            assert '📊' not in annotation.text, f"Found emoji in annotation: {annotation.text}"
            # Also check for common emoji unicode ranges
            assert not any(ord(c) > 0x1F300 and ord(c) < 0x1F9FF for c in annotation.text), \
                f"Found emoji character in annotation: {annotation.text}"
    
    def test_role_distribution_no_emoji(self, sample_member_data):
        """Test that role distribution chart has no emoji in annotations."""
        fig = plot_role_distribution(sample_member_data, data_state="cleaned")
        
        # Check all annotations for emojis
        for annotation in fig.layout.annotations:
            assert '📊' not in annotation.text, f"Found emoji in annotation: {annotation.text}"
            # Also check for common emoji unicode ranges
            assert not any(ord(c) > 0x1F300 and ord(c) < 0x1F9FF for c in annotation.text), \
                f"Found emoji character in annotation: {annotation.text}"
    
    def test_attendance_histogram_no_emoji(self, sample_member_data):
        """Test that attendance histogram has no emoji in annotations."""
        fig = plot_attendance_histogram(sample_member_data, data_state="cleaned")
        
        # Check all annotations for emojis
        for annotation in fig.layout.annotations:
            assert '📊' not in annotation.text, f"Found emoji in annotation: {annotation.text}"
            # Also check for common emoji unicode ranges
            assert not any(ord(c) > 0x1F300 and ord(c) < 0x1F9FF for c in annotation.text), \
                f"Found emoji character in annotation: {annotation.text}"
    
    def test_all_charts_contain_statistics(self, sample_member_data):
        """Test that statistical information is still present after emoji removal."""
        # Attendance trend should have Mean, Median, and Total
        fig_trend = plot_attendance_trend(sample_member_data, data_state="cleaned")
        annotation_text = ' '.join([ann.text for ann in fig_trend.layout.annotations])
        assert 'Mean' in annotation_text
        assert 'Median' in annotation_text
        assert 'Total' in annotation_text
        
        # Role distribution should have Total Members and Unique Roles
        fig_role = plot_role_distribution(sample_member_data, data_state="cleaned")
        annotation_text = ' '.join([ann.text for ann in fig_role.layout.annotations])
        assert 'Total Members' in annotation_text
        assert 'Unique Roles' in annotation_text
        
        # Histogram should have Mean, Median, Std Dev, and Range
        fig_hist = plot_attendance_histogram(sample_member_data, data_state="cleaned")
        annotation_text = ' '.join([ann.text for ann in fig_hist.layout.annotations])
        assert 'Mean' in annotation_text
        assert 'Median' in annotation_text
        assert 'Std Dev' in annotation_text
        assert 'Range' in annotation_text
