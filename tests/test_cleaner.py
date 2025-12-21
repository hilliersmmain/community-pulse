"""
Test suite for the DataCleaner class.

This module contains comprehensive tests for all data cleaning operations
including duplicate removal, email fixing, name standardization, date cleaning,
and missing value handling.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.cleaner import DataCleaner


class TestDataCleaner:
    """Test suite for DataCleaner class functionality."""
    
    @pytest.fixture
    def sample_data_with_duplicates(self):
        """Fixture providing a DataFrame with duplicate records."""
        return pd.DataFrame({
            'Name': ['John Doe', 'John Doe', 'Jane Smith'],
            'Email': ['john@example.com', 'john@example.com', 'jane@example.com'],
            'Event_Attendance': [5, 5, 10],
            'Role': ['Member', 'Member', 'Admin']
        })
    
    @pytest.fixture
    def sample_data_with_invalid_emails(self):
        """Fixture providing a DataFrame with invalid email formats."""
        return pd.DataFrame({
            'Name': ['Alice Brown', 'Bob Jones', 'Carol White'],
            'Email': ['alice at example.com', 'bob@test.com', 'invalid-email'],
            'Event_Attendance': [3, 7, 2],
            'Role': ['Member', 'Guest', 'Member']
        })
    
    @pytest.fixture
    def sample_data_with_mixed_case_names(self):
        """Fixture providing a DataFrame with inconsistent name capitalization."""
        return pd.DataFrame({
            'Name': ['john doe', 'JANE SMITH', 'Bob Wilson'],
            'Email': ['john@test.com', 'jane@test.com', 'bob@test.com'],
            'Event_Attendance': [1, 2, 3],
            'Role': ['Member', 'Admin', 'Guest']
        })
    
    @pytest.fixture
    def sample_data_with_bad_dates(self):
        """Fixture providing a DataFrame with mixed date formats."""
        return pd.DataFrame({
            'Name': ['Alex Turner', 'Sam Lee', 'Chris Evans'],
            'Email': ['alex@test.com', 'sam@test.com', 'chris@test.com'],
            'Join_Date': ['2023-01-15', 'Unknown', '12/25/2022'],
            'Event_Attendance': [4, 5, 6],
            'Role': ['Member', 'Member', 'Admin']
        })
    
    @pytest.fixture
    def sample_data_with_missing_values(self):
        """Fixture providing a DataFrame with missing attendance values."""
        return pd.DataFrame({
            'Name': ['David Kim', 'Emma Davis', 'Frank Miller'],
            'Email': ['david@test.com', 'emma@test.com', 'frank@test.com'],
            'Event_Attendance': [8, np.nan, np.nan],
            'Role': ['Admin', 'Member', 'Guest']
        })
    
    def test_remove_duplicates(self, sample_data_with_duplicates):
        """Test that duplicate rows are properly removed based on email."""
        cleaner = DataCleaner(sample_data_with_duplicates)
        cleaner.remove_duplicates()
        
        # Should have 2 rows instead of 3 (one duplicate removed)
        assert len(cleaner.clean_df) == 2
        
        # Verify the log message was recorded
        assert any('duplicate' in msg.lower() for msg in cleaner.log)
        
        # Verify unique emails only
        assert cleaner.clean_df['Email'].nunique() == 2
    
    def test_fix_emails(self, sample_data_with_invalid_emails):
        """Test that invalid email formats are fixed or removed."""
        cleaner = DataCleaner(sample_data_with_invalid_emails)
        cleaner.fix_emails()
        
        # Should have 2 rows (one valid initially, one fixed from ' at ', one invalid removed)
        assert len(cleaner.clean_df) == 2
        
        # All remaining emails should be valid (contain @)
        assert all('@' in str(email) for email in cleaner.clean_df['Email'])
        
        # Verify log message
        assert any('email' in msg.lower() for msg in cleaner.log)
        
        # Verify the ' at ' was converted to '@'
        emails = cleaner.clean_df['Email'].tolist()
        assert 'alice@example.com' in emails
    
    def test_standardize_names(self, sample_data_with_mixed_case_names):
        """Test that names are converted to Title Case."""
        cleaner = DataCleaner(sample_data_with_mixed_case_names)
        cleaner.standardize_names()
        
        # All names should be in Title Case
        expected_names = ['John Doe', 'Jane Smith', 'Bob Wilson']
        assert cleaner.clean_df['Name'].tolist() == expected_names
        
        # Verify log message
        assert any('name' in msg.lower() and 'title case' in msg.lower() for msg in cleaner.log)
    
    def test_clean_dates(self, sample_data_with_bad_dates):
        """Test that dates are parsed and standardized correctly."""
        cleaner = DataCleaner(sample_data_with_bad_dates)
        cleaner.clean_dates()
        
        # All Join_Date values should be datetime or NaT
        assert pd.api.types.is_datetime64_any_dtype(cleaner.clean_df['Join_Date'])
        
        # Verify log message
        assert any('date' in msg.lower() for msg in cleaner.log)
        
        # Check that valid dates were parsed correctly
        valid_dates = cleaner.clean_df['Join_Date'].dropna()
        assert len(valid_dates) >= 1  # At least one date should be valid
    
    def test_handle_missing_values(self, sample_data_with_missing_values):
        """Test that missing attendance values are filled with 0."""
        cleaner = DataCleaner(sample_data_with_missing_values)
        cleaner.handle_missing_values()
        
        # No missing values should remain in Event_Attendance
        assert cleaner.clean_df['Event_Attendance'].isna().sum() == 0
        
        # Missing values should be replaced with 0
        expected = [8.0, 0.0, 0.0]
        assert cleaner.clean_df['Event_Attendance'].tolist() == expected
        
        # Verify log message
        assert any('attendance' in msg.lower() for msg in cleaner.log)
    
    def test_clean_all_pipeline(self):
        """Test the complete cleaning pipeline with realistic messy data."""
        # Create a comprehensive messy dataset
        messy_data = pd.DataFrame({
            'Name': ['john doe', 'JANE SMITH', 'john doe', 'bob wilson'],  # Duplicates + mixed case
            'Email': ['john at test.com', 'jane@test.com', 'john at test.com', 'invalid'],  # Invalid emails
            'Join_Date': ['2023-01-15', 'Unknown', '2023-01-15', '2022-12-25'],  # Bad dates
            'Event_Attendance': [5, np.nan, 5, 10],  # Missing values
            'Role': ['Member', 'Admin', 'Member', 'Guest']
        })
        
        cleaner = DataCleaner(messy_data)
        result = cleaner.clean_all()
        
        # Verify pipeline ran successfully
        assert len(result) >= 1  # At least some records should remain
        
        # Verify all steps were logged
        assert len(cleaner.log) >= 4  # Should have logs from multiple cleaning steps
        
        # Verify names are Title Case
        assert all(name.istitle() for name in result['Name'])
        
        # Verify no missing attendance values
        assert result['Event_Attendance'].isna().sum() == 0
        
        # Verify dates are datetime type
        assert pd.api.types.is_datetime64_any_dtype(result['Join_Date'])
    
    def test_timestamps_are_set(self):
        """Test that cleaning operations set timestamps correctly."""
        messy_data = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Email': ['john@test.com', 'jane@test.com'],
            'Event_Attendance': [5, 10],
            'Role': ['Member', 'Admin']
        })
        
        cleaner = DataCleaner(messy_data)
        
        # Check start timestamp is set
        assert cleaner.start_timestamp is not None
        assert isinstance(cleaner.start_timestamp, datetime)
        
        # End timestamp should be None before cleaning
        assert cleaner.end_timestamp is None
        
        # Run cleaning
        cleaner.clean_all()
        
        # Check end timestamp is set after cleaning
        assert cleaner.end_timestamp is not None
        assert isinstance(cleaner.end_timestamp, datetime)
        
        # End timestamp should be after start timestamp
        assert cleaner.end_timestamp >= cleaner.start_timestamp


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
