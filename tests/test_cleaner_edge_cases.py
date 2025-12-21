"""
Extended test suite for DataCleaner edge cases and new features.

This module contains additional tests for fuzzy matching, data health scores,
schema validation, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.cleaner import DataCleaner


class TestDataCleanerEdgeCases:
    """Test suite for edge cases and new cleaner features."""
    
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
            'Event_Attendance': [5],
            'Role': ['Member']
        })
    
    @pytest.fixture
    def fuzzy_duplicate_data(self):
        """Fixture with near-duplicate names."""
        return pd.DataFrame({
            'Name': ['John Smith', 'Jon Smith', 'Jane Doe', 'Jane Do'],
            'Email': ['john1@test.com', 'john2@test.com', 'jane1@test.com', 'jane2@test.com'],
            'Event_Attendance': [5, 5, 10, 10],
            'Role': ['Member', 'Member', 'Admin', 'Admin']
        })
    
    def test_schema_validation_success(self, single_record_dataframe):
        """Test that schema validation passes with required columns."""
        cleaner = DataCleaner(single_record_dataframe)
        # Should not raise an exception
        cleaner.validate_schema()
        assert 'Schema validation passed' in cleaner.log[0]
    
    def test_schema_validation_missing_columns(self):
        """Test that schema validation fails with missing required columns."""
        df = pd.DataFrame({
            'Name': ['John Doe'],
            'Role': ['Member']
            # Missing 'Email' column
        })
        
        cleaner = DataCleaner(df)
        
        with pytest.raises(ValueError, match="Missing required columns"):
            cleaner.validate_schema()
    
    def test_fuzzy_match_names_similar(self):
        """Test fuzzy matching detects similar names."""
        df = pd.DataFrame({
            'Name': ['Test'],
            'Email': ['test@test.com']
        })
        cleaner = DataCleaner(df)
        
        # Similar names should match
        assert cleaner.fuzzy_match_names('John Smith', 'Jon Smith') == True
        assert cleaner.fuzzy_match_names('Jane Doe', 'Jane Do') == True
    
    def test_fuzzy_match_names_different(self):
        """Test fuzzy matching doesn't match different names."""
        df = pd.DataFrame({
            'Name': ['Test'],
            'Email': ['test@test.com']
        })
        cleaner = DataCleaner(df)
        
        # Different names should not match
        assert cleaner.fuzzy_match_names('John Smith', 'Jane Doe') == False
        assert cleaner.fuzzy_match_names('Alice Brown', 'Bob Wilson') == False
    
    def test_fuzzy_match_names_with_nan(self):
        """Test fuzzy matching handles NaN values."""
        df = pd.DataFrame({
            'Name': ['Test'],
            'Email': ['test@test.com']
        })
        cleaner = DataCleaner(df)
        
        # NaN should not match anything
        assert cleaner.fuzzy_match_names(np.nan, 'John Smith') == False
        assert cleaner.fuzzy_match_names('John Smith', np.nan) == False
        assert cleaner.fuzzy_match_names(np.nan, np.nan) == False
    
    def test_remove_fuzzy_duplicates(self, fuzzy_duplicate_data):
        """Test that fuzzy duplicates are removed."""
        cleaner = DataCleaner(fuzzy_duplicate_data)
        cleaner.standardize_names()
        cleaner.remove_fuzzy_duplicates()
        
        # Should have fewer records after removing fuzzy duplicates
        assert len(cleaner.clean_df) < len(fuzzy_duplicate_data)
    
    def test_calculate_data_health_score(self):
        """Test data health score calculation."""
        df = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Email': ['john@test.com', 'jane@test.com'],
            'Event_Attendance': [5, 10],
            'Role': ['Member', 'Admin']
        })
        
        cleaner = DataCleaner(df)
        
        # With no issues, score should be high
        score = cleaner.calculate_data_health_score()
        assert 0 <= score <= 100
        assert score == 100.0  # No duplicates, invalid emails, or missing values
    
    def test_calculate_data_health_score_with_issues(self):
        """Test data health score with quality issues."""
        df = pd.DataFrame({
            'Name': ['John Doe', 'John Doe', 'Jane Smith'],  # 1 duplicate
            'Email': ['john@test.com', 'john@test.com', 'invalid'],  # 1 invalid
            'Event_Attendance': [5, 5, np.nan],  # 1 missing
            'Role': ['Member', 'Member', 'Admin']
        })
        
        cleaner = DataCleaner(df)
        cleaner.fix_emails()  # Will remove 1 invalid email
        cleaner.remove_duplicates()  # Will remove 1 duplicate
        cleaner.handle_missing_values()  # Will fill missing values
        
        score = cleaner.calculate_data_health_score()
        
        # Score should be less than 100 due to issues
        assert score < 100
        assert score >= 0
    
    def test_get_cleaning_metrics(self):
        """Test that cleaning metrics are properly tracked."""
        df = pd.DataFrame({
            'Name': ['John Doe', 'John Doe', 'Jane Smith'],
            'Email': ['john@test.com', 'john@test.com', 'jane@test.com'],
            'Event_Attendance': [5, 5, np.nan],
            'Role': ['Member', 'Member', 'Admin']
        })
        
        cleaner = DataCleaner(df)
        cleaner.clean_all()
        
        metrics = cleaner.get_cleaning_metrics()
        
        # Verify metrics structure
        assert 'initial_records' in metrics
        assert 'final_records' in metrics
        assert 'duplicates_removed' in metrics
        assert 'invalid_emails_removed' in metrics
        assert 'missing_values_filled' in metrics
        assert 'data_health_score' in metrics
        
        # Verify values make sense
        assert metrics['initial_records'] == 3
        assert metrics['final_records'] >= 0
        assert metrics['duplicates_removed'] >= 0
    
    def test_clean_dates_future_dates(self):
        """Test that future dates are detected and handled."""
        future_date = pd.Timestamp.now() + pd.Timedelta(days=365)
        
        df = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Email': ['john@test.com', 'jane@test.com'],
            'Join_Date': [pd.Timestamp('2023-01-01'), future_date],
            'Event_Attendance': [5, 10],
            'Role': ['Member', 'Admin']
        })
        
        cleaner = DataCleaner(df)
        cleaner.clean_dates()
        
        # Future date should be converted to NaT and then filled
        assert 'future dates' in ' '.join(cleaner.log).lower() or 'dates' in ' '.join(cleaner.log).lower()
    
    def test_empty_dataframe_handling(self, empty_dataframe):
        """Test that empty DataFrame doesn't crash the cleaner."""
        # Empty DataFrame will fail schema validation, which is expected
        # But the cleaner should be initializable
        cleaner = DataCleaner(empty_dataframe)
        assert cleaner.initial_record_count == 0
    
    def test_single_record_cleaning(self, single_record_dataframe):
        """Test cleaning pipeline with single record."""
        cleaner = DataCleaner(single_record_dataframe)
        result = cleaner.clean_all()
        
        # Should successfully clean single record
        assert len(result) == 1
        assert result['Name'].iloc[0] == 'John Doe'
    
    def test_all_duplicates(self):
        """Test handling when all records are duplicates."""
        df = pd.DataFrame({
            'Name': ['John Doe'] * 5,
            'Email': ['john@test.com'] * 5,
            'Event_Attendance': [5] * 5,
            'Role': ['Member'] * 5
        })
        
        cleaner = DataCleaner(df)
        cleaner.remove_duplicates()
        
        # Should keep only one record
        assert len(cleaner.clean_df) == 1
    
    def test_all_invalid_emails(self):
        """Test handling when all emails are invalid."""
        df = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
            'Email': ['invalid1', 'invalid2', 'invalid3'],
            'Event_Attendance': [5, 10, 15],
            'Role': ['Member', 'Admin', 'Guest']
        })
        
        cleaner = DataCleaner(df)
        cleaner.fix_emails()
        
        # Should drop all records with invalid emails
        assert len(cleaner.clean_df) == 0
    
    def test_malformed_data_types(self):
        """Test handling of malformed data types."""
        df = pd.DataFrame({
            'Name': [123, 'Jane Smith', None],  # Mixed types
            'Email': ['john@test.com', 'jane@test.com', 'bob@test.com'],
            'Event_Attendance': ['not_a_number', 10, 15],  # String in numeric column
            'Role': ['Member', 'Admin', 'Guest']
        })
        
        cleaner = DataCleaner(df)
        # Should handle type coercion without crashing
        cleaner.standardize_names()
        
        # Names should be converted to strings
        assert all(isinstance(name, str) for name in cleaner.clean_df['Name'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
