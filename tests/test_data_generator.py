"""
Test suite for the data_generator module.

This module contains tests for data generation functionality
including validation of messiness, data structure, and file output.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
import tempfile

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_generator import generate_messy_data
import config


class TestDataGenerator:
    """Test suite for data generation functionality."""
    
    def test_generates_correct_number_of_records(self):
        """Test that generator creates approximately the requested number of records (plus duplicates)."""
        num_records = 100
        df = generate_messy_data(num_records=num_records, save_path=None)
        
        # Should have roughly num_records + 10% duplicates
        expected_min = num_records
        expected_max = num_records * 1.15  # Allow for some variance
        
        assert expected_min <= len(df) <= expected_max
    
    def test_contains_required_columns(self):
        """Test that generated data has all required columns."""
        df = generate_messy_data(num_records=50, save_path=None)
        
        required_columns = ['ID', 'Name', 'Email', 'Join_Date', 'Last_Login', 
                           'Event_Attendance', 'Role', 'Event_Registered', 'Registration_Date']
        
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_generates_duplicates(self):
        """Test that duplicates are intentionally generated."""
        df = generate_messy_data(num_records=100, save_path=None)
        
        # Should have some duplicates
        duplicate_count = df.duplicated().sum()
        assert duplicate_count > 0, "No duplicates were generated"
    
    def test_generates_invalid_emails(self):
        """Test that some invalid email formats are generated."""
        df = generate_messy_data(num_records=200, save_path=None)
        
        # Check for emails without @ symbol (invalid format)
        invalid_emails = df['Email'].astype(str).str.contains(' at ').sum()
        assert invalid_emails > 0, "No invalid emails were generated"
    
    def test_generates_mixed_case_names(self):
        """Test that names have mixed capitalization."""
        df = generate_messy_data(num_records=100, save_path=None)
        
        # Check for uppercase and lowercase names
        has_upper = df['Name'].astype(str).str.isupper().any()
        has_lower = df['Name'].astype(str).str.islower().any()
        
        # Should have at least some mixed case issues
        assert has_upper or has_lower, "No mixed case names were generated"
    
    def test_generates_missing_values(self):
        """Test that missing values are intentionally created."""
        df = generate_messy_data(num_records=100, save_path=None)
        
        # Should have some missing values in Event_Attendance or Last_Login
        missing_count = df[['Event_Attendance', 'Last_Login']].isna().sum().sum()
        assert missing_count > 0, "No missing values were generated"
    
    def test_generates_inconsistent_date_formats(self):
        """Test that various date formats are generated."""
        df = generate_messy_data(num_records=100, save_path=None)
        
        # Check for string dates (which indicates format inconsistency)
        string_dates = df['Join_Date'].apply(lambda x: isinstance(x, str)).sum()
        assert string_dates > 0, "All dates are in the same format"
    
    def test_saves_to_file(self):
        """Test that data can be saved to a CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            temp_path = tmp.name
        
        try:
            df = generate_messy_data(num_records=50, save_path=temp_path)
            
            # Verify file exists
            assert os.path.exists(temp_path), "CSV file was not created"
            
            # Verify file can be read
            loaded_df = pd.read_csv(temp_path)
            assert len(loaded_df) == len(df), "Loaded data has different length"
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_role_distribution(self):
        """Test that roles are distributed with expected probabilities."""
        df = generate_messy_data(num_records=500, save_path=None)
        
        # Check that all expected roles exist
        expected_roles = list(config.ROLE_PROBABILITIES.keys())
        actual_roles = df['Role'].unique()
        
        for role in expected_roles:
            assert role in actual_roles, f"Expected role '{role}' not found in generated data"
    
    def test_event_choices_present(self):
        """Test that all event choices appear in generated data."""
        df = generate_messy_data(num_records=300, save_path=None)
        
        # Check that events from config appear in data
        actual_events = df['Event_Registered'].unique()
        
        # At least some of the configured events should appear
        assert len(actual_events) > 0, "No events were generated"
        
        # Check that events are from the configured list
        for event in actual_events:
            assert event in config.EVENT_CHOICES, f"Unexpected event: {event}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
